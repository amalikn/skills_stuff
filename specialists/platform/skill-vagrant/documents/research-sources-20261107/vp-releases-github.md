<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/releases
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://github.com/Parallels/vagrant-parallels/releases:
# Releases · Parallels/vagrant-parallels

## v2.4.10

## What's Changed

* Bump concurrent-ruby from 1.2.2 to 1.3.7 in /website/docs in the bundler group across 1 directory by [@dependabot](https://github.com/dependabot)[bot] in [#524](https://github.com/Parallels/vagrant-parallels/pull/524)
* Only pass 'big\_writes' FUSE mount option on libfuse2 guests by [@hartlink](https://github.com/hartlink) in [#525](https://github.com/Parallels/vagrant-parallels/pull/525)

## New Contributors

* [@hartlink](https://github.com/hartlink) made their first contribution in [#525](https://github.com/Parallels/vagrant-parallels/pull/525)

**Full Changelog**: [2.4.8...v2.4.10](https://github.com/Parallels/vagrant-parallels/compare/2.4.8...v2.4.10)

## v2.4.7

## v2.4.6

## v2.4.5

```
updated version
```

## v2.4.4

* Add a check for prl\_fsd and use that to mount if it exists.  
  [[GH-487](https://github.com/Parallels/vagrant-parallels/pull/487)]
* Updated the documentation to reflect the new version of the provider.  
  [[GH-488](https://github.com/Parallels/vagrant-parallels/pull/488)]

## v2.4.3

```
Merge pull request #486 from Parallels/POS-24-enterpise-license

Add 'enterprise' edition support for Parallels CLI functionality check
```

## v2.4.2 - Minor bug fixes

## Use 'clonefile' copy for APFS disks

## v2.4.0 - Shared Folders for .macvm VMs on Apple M-series hosts

IMPROVEMENTS:

* Implement shared folder support for `.macvm` VMs [[GH-448](https://github.com/Parallels/vagrant-parallels/pull/448)]

BUG FIXES:

* Fix shared folder mount error on `.macvm` VMs [[GH-445](https://github.com/Parallels/vagrant-parallels/pull/445)]

## v2.3.1

BUG FIXES:

* Fix the detection of VM IP. Wait for the IP to become available to avoid connection issues and Vagrant warnings. [[GH-440](https://github.com/Parallels/vagrant-parallels/issues/440)]
