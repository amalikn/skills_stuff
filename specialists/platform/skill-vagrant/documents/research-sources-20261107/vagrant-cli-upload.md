<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/cli/upload
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/cli/upload:
# vagrant upload - Command-Line Interface \| Vagrant \| HashiCorp Developer

**Command: `vagrant upload source [destination] [name|id]`**

This command uploads files and directories from the host to the guest
machine.

* [`destination`](/vagrant/docs/cli/upload#destination) - Path on the guest machine to upload file or directory.
* [`source`](/vagrant/docs/cli/upload#source) - Path to file or directory on host to upload to guest machine.
* [`--compress`](/vagrant/docs/cli/upload#compress) - Compress the file or directory before uploading to guest machine.
* [`--compression-type type`](/vagrant/docs/cli/upload#compression-type-type) - Type of compression to use when compressing
  file or directory for upload. Defaults to `zip` for Windows guests and
  `tgz` for non-Windows guests. Valid values: `tgz`, `zip`.
* [`--temporary`](/vagrant/docs/cli/upload#temporary) - Create a temporary location on the guest machine and upload
  files to that location.

[Edit this page on GitHub](https://github.com/hashicorp/web-unified-docs/blob/main/content/vagrant/v2.4.9/content/docs/cli/upload.mdx)
