<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/526
**Retrieved**: 2026-11-09 11:25 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #526 'vagrant up'/'vagrant reload' fails to mount shared folders on Ubuntu 24.04+

State: OPEN; opened 2026-09-03T20:34:30Z; closed open

## Body

This is blocking work at my company.

Description copied from @hartlink's PR that fixes the issue: https://github.com/Parallels/vagrant-parallels/pull/525

libfuse3 removed the 'big_writes' mount option since big writes have been negotiated automatically via FUSE_BIG_WRITES since Linux kernel 2.6.26. Passing it on guests using libfuse3 (e.g. Ubuntu 24.04+, which ships fusermount3) causes prl_fsd to fail with:

`fuse: unknown option(s): `-o big_writes'`

which breaks 'vagrant up'/'vagrant reload' shared folder mounting entirely on those guests.


