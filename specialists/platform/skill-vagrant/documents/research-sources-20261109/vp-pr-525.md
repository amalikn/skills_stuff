<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/pull/525
**Retrieved**: 2026-11-09 11:25 AEDT
**HTTP status**: 200 via GitHub API (`gh pr view --json`)

---

# #525 Only pass 'big_writes' FUSE mount option on libfuse2 guests

State: MERGED; opened 2026-09-01T04:40:54Z; closed 2026-09-07T12:08:47Z

## Body

libfuse3 removed the 'big_writes' mount option since big writes have been negotiated automatically via FUSE_BIG_WRITES since Linux kernel 2.6.26. Passing it on guests using libfuse3 (e.g. Ubuntu 24.04+, which ships fusermount3) causes prl_fsd to fail with:

    fuse: unknown option(s): `-o big_writes'

which breaks 'vagrant up'/'vagrant reload' shared folder mounting entirely on those guests.

This detects libfuse3 via the presence of the fusermount3 binary and skips the option only in that case, preserving the existing behavior (and its write-throughput benefit) on older libfuse2 guests such as Ubuntu 18.04.

Tested on: Ubuntu 24.04 LTS arm64, kernel 6.8.0-101-generic, Parallels Guest Tools 27.0.0.58628.

## Comment by q0rban at 2026-09-03T16:44:36Z

I encountered the same issue after upgrading Parallels Desktop to `27.0.1`.  Applying this patch fixed it.

```
# Determine the directory of currently installed vagrant-parallels version
ver=$(vagrant plugin list | awk '/^vagrant-parallels / { gsub(/[(),]/, "", $2); print $2 }')
dir=$(ls -d "${VAGRANT_HOME:-$HOME/.vagrant.d}"/gems/*/gems/vagrant-parallels-"$ver" | sort -V | tail -1)
echo "$dir"

# Apply the patch from 525.
curl --location --output /tmp/pr525.diff https://github.com/Parallels/vagrant-parallels/pull/525.diff
patch -p1 -d "$dir" < /tmp/pr525.diff
```

## Comment by cjlapao at 2026-09-07T12:09:15Z

@hartlink thanks for the pr, this will be in the next release cycle

## Comment by ronanchilvers at 2026-09-09T15:38:06Z

Any chance of a new release to pull this in? We're seeing exactly this issue with Parallels Desktop 27.X and Debian Trixie guests.

## Comment by stephenreay at 2026-10-07T07:55:49Z

@cjlapao any idea when this will release? 


## Comment by ronanchilvers at 2026-10-07T08:32:46Z

@cjlapao +1 on @stephenreay's question - it would be good to be able to use this as it's causing us problems

