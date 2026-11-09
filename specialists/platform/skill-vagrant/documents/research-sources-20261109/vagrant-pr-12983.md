<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/hashicorp/vagrant/pull/12983
**Retrieved**: 2026-11-09 11:34 AEDT
**HTTP status**: 200 via GitHub API (`gh pr view --json`)

---

# #12983 Add hostonlynets support to VirtualBox driver

State: MERGED; merged 2022-11-08T21:52:20Z

## Body

This PR adds support to the VirtualBox 7 driver for
`hostonlynets`. This was introduced to VirtualBox
on macOS for interacting with the vmnet framework. 
Usage of `hostonlynets` is isolated to only the
macOS platform via checks in the overrides so on
non-macOS platforms will still see the existing
behavior.

Fixes #12959

