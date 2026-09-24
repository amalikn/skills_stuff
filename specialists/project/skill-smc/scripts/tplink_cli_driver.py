#!/usr/bin/env python3
"""Drive a TP-Link JetStream/Omada switch CLI over SSH from an SMC box (runs ON the SMC).

Invoked by tplink-switch.sh, which pipes the login password and the enable password (empty when none is
configured) as the first two stdin lines and this file as the rest, then runs
`read -r SSHPASS; read -r ENABLEPASS; export SSHPASS ENABLEPASS; python3 - <ip> <user> <cmd>...` on the SMC.
Neither password appears in any command line, process list or tool transcript.

Privilege scenarios handled, and reported on stderr as `privilege: ...`:
- already-privileged: the login lands at a `#` prompt, so no `enable` is sent.
- enable-no-password: `enable` goes straight to `#` (kalumburu SG2428P, 2026-09-24).
- enable-password: `enable` asks for a password; ENABLEPASS is sent, or the login password when ENABLEPASS is
  empty. One attempt only. A second password prompt or a `>` prompt afterwards is a failure (exit 6).
Login variants: an OpenSSH password prompt, and an in-CLI `User:`/`Username:` then `Password:` login.

Why a pty driver and not `ssh host cmd` (all verified on SG2428P 5.30.1, kalumburu, 2026-09-24):
- The switch (`TPSSH-1.0.0`) runs no exec channel and closes a session that has no real tty.
- It needs `HostKeyAlgorithms=+ssh-rsa` (without it, it drops the session before offering auth) and
  `MACs=hmac-sha2-256` (Ubuntu 22.04's default MAC list does not negotiate with it).
- Enter is CR, not LF, and the first keystroke after login is swallowed, so a blank CR goes first.
- `show system-info` and most `show` commands need `enable`, which asked for no password there.

Exit codes: 0 ok, 2 usage, 3 auth failed, 4 connect/timeout, 5 no prompt, 6 enable failed.
"""
import os
import pty
import re
import select
import sys
import time

PW_PROMPT = re.compile(rb"[Pp]assword: ?$")
USER_PROMPT = re.compile(rb"(?:User(?:name)?|[Ll]ogin): ?$")
DENIED = re.compile(rb"Permission denied|Authentication failed|Too many")
PROMPT = re.compile(rb"(?:^|[\r\n])[^\r\n]{1,64}[>#] ?$")
PRIV_PROMPT = re.compile(rb"(?:^|[\r\n])[^\r\n]{1,64}# ?$")
MORE = re.compile(rb"Press any key to continue[^\r\n]*|--More--|-- ?More ?--")
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]|\x08+ *\x08*")


def clean(raw):
    """Strip ANSI, then honour carriage returns: the pager erases its prompt with CR + spaces + CR."""
    lines = []
    for line in ANSI.sub("", raw.decode(errors="replace")).split("\n"):
        segs = [seg for seg in line.split("\r") if seg.strip()]
        lines.append(segs[-1] if segs else "")
    return lines


def main():
    if len(sys.argv) < 4:
        print("usage: tplink_cli_driver.py <ip> <user> <cmd> [cmd ...]", file=sys.stderr)
        sys.exit(2)
    ip, user, cmds = sys.argv[1], sys.argv[2], sys.argv[3:]
    pw = os.environ.pop("SSHPASS", "")
    enable_pw = os.environ.pop("ENABLEPASS", "") or pw
    argv = [
        "ssh", "-F", "/dev/null", "-tt",
        "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null", "-o", "LogLevel=ERROR",
        "-o", "ConnectTimeout=8", "-o", "HostKeyAlgorithms=+ssh-rsa", "-o", "MACs=hmac-sha2-256",
        "-o", "PubkeyAuthentication=no", "-o", "PreferredAuthentications=password",
        "-o", "NumberOfPasswordPrompts=1", f"{user}@{ip}",
    ]
    pid, fd = pty.fork()
    if pid == 0:
        os.execvp(argv[0], argv)

    buf = b""

    def read_until(patterns, timeout):
        nonlocal buf
        end = time.time() + timeout
        while time.time() < end:
            for i, pat in enumerate(patterns):
                m = pat.search(buf)
                if m:
                    return i, m
            ready, _, _ = select.select([fd], [], [], 0.3)
            if ready:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    chunk = b""
                if not chunk:
                    return -1, None
                buf += chunk
        return -2, None

    def send(text):
        os.write(fd, text.encode())

    idx, _ = read_until([PW_PROMPT, PROMPT, DENIED, USER_PROMPT], 25)
    if idx == 3:  # in-CLI login: User: then Password:
        send(user + "\r")
        buf = b""
        idx, _ = read_until([PW_PROMPT, PROMPT, DENIED], 15)
    if idx == 0:
        send(pw + "\n")
        buf = b""
        idx, _ = read_until([PROMPT, DENIED, PW_PROMPT, USER_PROMPT], 20)
        if idx != 0:
            print(f"{ip}: authentication failed" if idx in (1, 2, 3) else f"{ip}: no prompt after login", file=sys.stderr)
            sys.exit(3 if idx in (1, 2, 3) else 5)
    elif idx != 1:
        print(f"{ip}: connect failed or timed out", file=sys.stderr)
        sys.exit(3 if idx == 2 else 4)

    # First keystroke after login is swallowed: settle the line, then elevate if not already at '#'.
    buf = b""
    send("\r")
    read_until([PROMPT], 10)
    if PRIV_PROMPT.search(buf):
        privilege = "already-privileged"
    else:
        buf = b""
        send("enable\r")
        idx, _ = read_until([PRIV_PROMPT, PW_PROMPT, PROMPT], 10)
        if idx == 0:
            privilege = "enable-no-password"
        elif idx == 1:
            buf = b""
            send(enable_pw + "\r")
            idx, _ = read_until([PRIV_PROMPT, PW_PROMPT, PROMPT], 10)
            if idx != 0:
                send("\x03\r")
                print(f"{ip}: enable password rejected (one attempt made; set TPLINK_KP_ENABLE_ENTRY if it "
                      "differs from the login password)", file=sys.stderr)
                sys.exit(6)
            privilege = "enable-password"
        else:
            print(f"{ip}: enable did not reach a '#' prompt", file=sys.stderr)
            sys.exit(6)
    print(f"{ip}: privilege: {privilege}", file=sys.stderr)

    rc = 0
    for cmd in cmds:
        buf = b""
        out = b""
        send(cmd + "\r")
        while True:
            idx, m = read_until([MORE, PROMPT], 60)
            if idx == 0:
                out += buf[:m.start()]
                buf = buf[m.end():]
                send(" ")
                continue
            if idx == 1:
                out += buf[:m.start()]
            else:
                out += buf
                rc = 5
            break
        lines = clean(out)
        if lines and lines[0].strip().endswith(cmd.strip()):
            lines = lines[1:]
        print(f"### {ip}: {cmd}")
        print("\n".join(line for line in lines if line.strip()))
        if rc:
            print(f"{ip}: timed out waiting for the prompt after '{cmd}'", file=sys.stderr)
            break

    send("exit\r")
    time.sleep(0.5)
    send("exit\r")
    time.sleep(0.5)
    try:
        os.kill(pid, 15)
    except ProcessLookupError:
        pass
    sys.exit(rc)


if __name__ == "__main__":
    main()
