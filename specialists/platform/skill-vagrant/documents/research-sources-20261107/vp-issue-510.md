<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/510
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #510 Upgraded macOS to Sequoia, can't spin up a the same VM

State: CLOSED; opened 2025-07-08T16:07:00Z; closed 2025-07-08T19:42:11Z

## Body

Hello,

I've been using Parallels to host a local development environment for Laravel using Homestead for years, but after upgrading my macOS to Sequoia 15.5 I can no longer spin up my VM—`vagrant up` hangs when trying to SSH to the VM:

```
Bringing machine 'homestead' up with 'parallels' provider...
==> homestead: Registering VM image from the base box 'laravel/homestead'...
==> homestead: Creating new virtual machine as a linked clone of the box image...
==> homestead: Unregistering the box VM image...
==> homestead: Setting the default configuration for VM...
==> homestead: Checking if box 'laravel/homestead' version '14.0.2' is up to date...
==> homestead: Setting the name of the VM: homestead
==> homestead: Preparing network interfaces based on configuration...
    homestead: Adapter 0: shared
    homestead: Adapter 1: hostonly
==> homestead: Clearing any previously set network interfaces...
==> homestead: Forwarding ports...
    homestead: 8000 => 8000
    homestead: 443 => 44300
    homestead: 9200 => 9200
    homestead: 5432 => 5432
==> homestead: Running 'pre-boot' VM customizations...
==> homestead: Booting VM...
==> homestead: Waiting for machine to boot. This may take a few minutes...
    homestead: SSH address: 10.211.55.7:22
    homestead: SSH username: vagrant
    homestead: SSH auth method: private key
    homestead: Warning: Host unreachable. Retrying...
    homestead: Warning: Host unreachable. Retrying...
    homestead: Warning: Host unreachable. Retrying...
    ...
Timed out while waiting for the machine to boot. This means that
Vagrant was unable to communicate with the guest machine within
the configured ("config.vm.boot_timeout" value) time period.

If you look above, you should be able to see the error(s) that
Vagrant had when attempting to connect to the machine. These errors
are usually good hints as to what may be wrong.

If you're using a custom box, make sure that networking is properly
working and you're able to connect to the machine. It is a common
problem that networking isn't setup properly in these boxes.
Verify that authentication configurations are also setup properly,
as well.

If the box appears to be booting properly, you may want to increase
the timeout ("config.vm.boot_timeout") value.
```

Environment:

| Component | Version |
|---|---|
| macOS Host (M1 Pro) | macOS Sequoia 15.5 |
| Parallels Desktop| 20.4.0 (55980) |
| Vagrant | 2.4.7 |
| vagrant-parallels plugin | 2.4.7 |

Here's what I've tried and verified:

1) I can `vagrant ssh` to the machine.
2) I copied the output of `vagrant ssh-config` to my `~/.ssh/config` file, and I can `ssh homestead` to the machine.
3) I can `ssh vagrant@10.211.55.7` successfully, though it prompts me to add to known hosts and asks for a password.
4) I reset all my Parallels configurations back to the defaults and restarted Parallels.

## Comment by nikhiltri at 2025-07-08T19:42:11Z

I fixed this. For me, it was because macOS didn't allow my terminal to access the local network. In macOS settings I went to Privacy & Security -> Local Network, and made sure iTerm and Visual Studio Code were checked. 
