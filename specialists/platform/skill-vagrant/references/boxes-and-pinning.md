# Boxes and pinning

A box is the base image a Vagrant machine is cloned from. A lab that must give the same result next month pins the exact box version, and records why that version.

## Contents

- [Pin the version, not the name](#pin-the-version-not-the-name)
- [Constraints](#constraints)
- [Architecture on Apple silicon](#architecture-on-apple-silicon)
- [Update checks](#update-checks)
- [Bento boxes](#bento-boxes)
- [The box registry](#the-box-registry)
- [Removing boxes](#removing-boxes)
- [Worked example](#worked-example)

## Pin the version, not the name

`config.vm.box_version` "defaults to '>= 0' (the latest version available)"; with constraints, Vagrant "will use the latest available box satisfying these constraints" (VERIFIED_PRIMARY,
[vagrant-machine-settings.md], [vagrant-box-versioning.md]). So a Vagrantfile with only `config.vm.box` silently moves to a newer image when one is published and the machine is recreated. A lab pins
one exact version:

```ruby
config.vm.box = "bento/ubuntu-24.04"
config.vm.box_version = "202510.26.0"     # exact: no operator, no range
```

The pin decides the image at creation time only: an existing machine keeps the disk it was cloned from until it is destroyed and brought up again.

## Constraints

Constraints combine `= X`, `> X`, `< X`, `>= X`, `<= X` and `~> X` with commas; `~> 1.1.5` means `>= 1.1.5, < 1.2.0` (VERIFIED_PRIMARY, [vagrant-box-versioning.md]). A range (`>=`, `~>`) is not a pin:
`vagrantfile_lint.py` warns on it. Bento versions are dates (`YYYYMM.DD.N`), not semantic versions, so `~>` has no compatibility meaning for them (UNVERIFIED as a bento policy; the registry rows show
the date shape, [bento-ubuntu-2404-api.md]).

## Architecture on Apple silicon

`config.vm.box_architecture` accepts values such as `"amd64"` and `"arm64"`; `:auto` (the default) detects the host and fetches that architecture; `nil` fetches the box flagged as the default
architecture (VERIFIED_PRIMARY, [vagrant-machine-settings.md]). On an Apple silicon Mac the Parallels provider needs an arm64 box. Older bento names carried `-arm64` (`bento/ubuntu-22.04-arm64`);
`bento/ubuntu-24.04` publishes one version with several architectures per provider (VERIFIED_PRIMARY, registry API on 2026-11-07: version 202510.26.0 has `parallels` for `arm64` and `amd64`,
[bento-ubuntu-2404-api.md]).

## Update checks

`config.vm.box_check_update` (default true) checks for a newer box on every `vagrant up` and only tells the user; `VAGRANT_BOX_UPDATE_CHECK_DISABLE` turns the check off globally and does not affect
`vagrant box update` (VERIFIED_PRIMARY, [vagrant-machine-settings.md], [vagrant-env-vars.md]). The check never changes a pinned machine; it is noise for a pinned lab and a signal for a review of the
pin.

## Bento boxes

Bento is Progress Chef's set of Packer templates for Vagrant base boxes; a subset is built and published to the `bento` organisation; building needs Packer and, for Parallels boxes, Parallels Desktop
Pro (VERIFIED_PRIMARY, [bento-readme-github.md]). A bento box is a vanilla OS install plus the provider's guest tools; anything a lab needs beyond that is provisioning in the Vagrantfile.

History worth knowing before pinning: several bento Ubuntu releases shipped with a fixed `/etc/machine-id`, so every VM from that box asked DHCP with the same identity and got the same address (bento
issues 1421 for ubuntu-20.04 202206.03.0, 1473 for 20.04-arm64 202301.20.0, 1562 for 22.04-arm64 202401.31.0 on Parallels; VERIFIED_PRIMARY, [vp-issue-1421.md], [vp-issue-1473.md], [vp-issue-1562.md];
vagrant-parallels issue 441, [vp-issue-441.md]). After pinning a new version, bring up two machines from it and compare `/etc/machine-id`; see [clones-snapshots-and-identity.md](clones-snapshots-and-identity.md).

The guest's point release and kernel come with the box: bento/ubuntu-24.04 202510.26.0 boots Ubuntu 24.04.3 with kernel 6.8.0-86 (USER_STATED, lab observation 2026-11-07, recorded in
[compatibility.yaml](../compatibility.yaml)). A later `apt upgrade` in provisioning moves both; pin the archive as well when that matters ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md)).

## The box registry

The public box catalog is the HCP Vagrant Box Registry (formerly Vagrant Cloud) (VERIFIED_PRIMARY, [vagrant-hcp-box-registry.md], [vagrant-box-catalog.md]).
Its v2 API answers `GET https://vagrantcloud.com/api/v2/box/<user>/<name>` with every version, its status and its providers and architectures (observed
2026-11-07, [bento-ubuntu-2404-api.md]); `vagrant_lab_inventory.py --latest` reads it to compare a pin with the newest release. Box versions are
`unreleased`, `active` or `revoked` ([vagrant-box-versioning-cloud.md]).

**The registry is being shut down.** HashiCorp's notice (VERIFIED_PRIMARY, [hcp-vagrant-eol.md], also on every Vagrant Cloud docs page): no new boxes
from 2026-10-01, end of support and maintenance 2026-11-02, end of operations 2026-12-31, "all deployments will be decommissioned". The Vagrant CLI
stays; boxes must be hosted by their owners. Consequences for a lab:

- A pin such as `bento/ubuntu-24.04` `202510.26.0` resolves only while the registry (or a replacement location bento announces) serves it. Where bento
  will publish after 2026-12-31 is UNVERIFIED (its README still points to Vagrant Cloud, [bento-readme-github.md]).
- Keep the pinned box locally now: `vagrant box repackage NAME PROVIDER VERSION` writes the installed box to the current directory "so you can
  redistribute it" (VERIFIED_PRIMARY, [vagrant-cli-box.md]); store it outside the repo (it is gigabytes) with its sha256, and record where.
- Rebuild path: `vagrant box add <name> <file-or-url>` with a box metadata file for versioned self-hosting, or build the box with bento's Packer
  templates.

## Removing boxes

With vagrant-parallels, a new machine is a linked clone of the box image by default; "the box deletion will make all its linked clones not working"
(VERIFIED_PRIMARY, [vp-configuration.md]). Before `vagrant box remove` or `vagrant box prune`, list which machines were created from that box version
(`vagrant_lab_inventory.py` joins machine homes to their Vagrantfile pins). `vagrant box prune --dry-run` prints what it would remove; `--force
--keep-active-boxes` keeps boxes in use (VERIFIED_PRIMARY, [vagrant-cli-box.md]). With the registry closing, a pruned version may not be downloadable
again.

## Worked example

The smc-resiliency Pi spike lab pins one box for four machines (canonical `vagrant_stuff/smc-pi-spike01/Vagrantfile` @ 8591b72, copy in `smc-resiliency/spike/vm/vagrant/smc-pi-spike01/Vagrantfile` @
4e436e8d):

```ruby
Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-24.04"
  config.vm.box_version = "202510.26.0"
```
