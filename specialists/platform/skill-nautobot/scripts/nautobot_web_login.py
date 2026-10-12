#!/usr/bin/env python3
"""Check that a username and password open Nautobot's web UI: fetch /login/, post the form with its CSRF token, and report whether a
session was granted. Read-only; prints no secret.

Written 2026-10-12 to prove the KeePass entries for a rebuilt Nautobot host before handing them over; useful after any rebuild, restore
or password rotation, because a valid API token says nothing about the web login.

Run: `just web_login --base-url http://host:8080 --username admin --password-cmd 'kp show -s -a Password "group/entry"'`
(or set NAUTOBOT_LOGIN_PASSWORD instead of --password-cmd). Exit 0 when the login opens, 1 when it does not, 2 on a usage error.
"""

from __future__ import annotations

import argparse
import http.cookiejar
import os
import re
import shlex
import subprocess
import sys
import urllib.parse
import urllib.request

CSRF = re.compile(r'name="csrfmiddlewaretoken" value="([^"]+)"')


def check_login(base_url: str, username: str, password: str, timeout: float = 15) -> tuple[bool, str]:
    """Log in through Nautobot's login form.

    Args:
        base_url: Nautobot's root URL, e.g. http://16.176.60.227:18080.
        username: the login name.
        password: the password.
        timeout: seconds per HTTP request.

    Returns:
        (opened, landed_path): opened is True when a session cookie was set and the response left /login/.

    Raises:
        ValueError: when the login page carries no CSRF token (not a Nautobot login page).
        urllib.error.URLError: when Nautobot cannot be reached.
    """
    base = base_url.rstrip("/")
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    page = opener.open(f"{base}/login/", timeout=timeout).read().decode("utf-8", "replace")
    match = CSRF.search(page)
    if not match:
        raise ValueError(f"{base}/login/ has no csrfmiddlewaretoken; is this Nautobot?")
    data = urllib.parse.urlencode({"csrfmiddlewaretoken": match.group(1), "username": username, "password": password, "next": "/"}).encode()
    req = urllib.request.Request(f"{base}/login/", data=data, headers={"Referer": f"{base}/login/"})
    resp = opener.open(req, timeout=timeout)
    landed = urllib.parse.urlparse(resp.geturl()).path
    opened = "sessionid" in {c.name for c in jar} and not landed.startswith("/login")
    return opened, landed


def read_password(password_cmd: str | None) -> str:
    """Get the password from a command's stdout, else from NAUTOBOT_LOGIN_PASSWORD.

    Args:
        password_cmd: a shell-style command that prints the password (e.g. a KeePass lookup), or None.

    Returns:
        The password without its trailing newline.

    Raises:
        SystemExit: with status 2 when neither source gives a password.
    """
    if password_cmd:
        out = subprocess.run(shlex.split(password_cmd), capture_output=True, text=True, check=False)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.rstrip("\n")
        raise SystemExit("nautobot_web_login: --password-cmd gave no password")
    pw = os.environ.get("NAUTOBOT_LOGIN_PASSWORD", "")
    if not pw:
        raise SystemExit(2)
    return pw


def main(argv: list[str] | None = None) -> int:
    """Parse arguments, run the login check and print one line.

    Args:
        argv: arguments, defaulting to sys.argv[1:].

    Returns:
        0 when the login opens, 1 when it does not.
    """
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base-url", required=True)
    ap.add_argument("--username", required=True)
    ap.add_argument("--password-cmd", help="command printing the password; else NAUTOBOT_LOGIN_PASSWORD")
    args = ap.parse_args(argv)
    opened, landed = check_login(args.base_url, args.username, read_password(args.password_cmd))
    print(f"{args.username}@{args.base_url}: {'LOGIN OK' if opened else 'LOGIN FAILED'} (landed {landed})")
    return 0 if opened else 1


if __name__ == "__main__":
    sys.exit(main())
