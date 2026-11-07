<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://parallels.github.io/vagrant-parallels/docs/installation/
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://parallels.github.io/vagrant-parallels/docs/installation/:
# Installing Provider

First, make sure that you have [Parallels Desktop for Mac](https://www.parallels.com/products/desktop/)
and [Vagrant](https://www.vagrantup.com/downloads.html) properly installed.
We recommend you using the latest versions of these products.

Since the Parallels provider is a Vagrant plugin, installing it is easy:

```
$ vagrant plugin install vagrant-parallels
```

The Vagrant plugin installer will automatically download and install
`vagrant-parallels` plugin.

## Requirements

* Vagrant v1.8 or higher
* Parallels Desktop for Mac version 11 or higher

Only **Pro**, **Enterprise** and **Business** editions of
**Parallels Desktop for Mac** can be used with this Vagrant provider.
