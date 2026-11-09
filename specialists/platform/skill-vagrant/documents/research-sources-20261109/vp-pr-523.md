<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/pull/523
**Retrieved**: 2026-11-09 11:25 AEDT
**HTTP status**: 200 via GitHub API (`gh pr view --json`)

---

# #523 Add an AddArmor override rule before mounting FUSE 3 filesystems

State: MERGED; opened 2026-06-08T12:44:53Z; closed 2026-06-12T14:01:14Z

## Body

Ubuntu 26.04 (maybe earlier versions already?) ships with an AppArmor profile for `fusermount3` that blocks FUSE mounts by default. This causes `prl_fsd`-based shared folder mounts to fail with `permission denied` upon boot (#522).

I have noticed that the override file already contains two lines:

```
mount fstype=@{fuse_types} options=(nosuid,nodev,rw,noatime) -> /media/{,**/},
mount fstype=@{fuse_types} options=(nosuid,nodev,ro,noatime) -> /media/{,**/},
```

I am not sure where those come from, but it might be that those are added by Parallels Tools to address https://forum.parallels.com/threads/ubuntu-25-04.367139/. In that case, I'd say adding extra lines for those mounts is a perfect fit.

