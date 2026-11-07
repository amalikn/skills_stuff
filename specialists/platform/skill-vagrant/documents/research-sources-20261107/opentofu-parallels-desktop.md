<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://search.opentofu.org/provider/parallels/parallels-desktop/latest
**Retrieved**: 2026-11-07 16:03 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: jina-reader(ok))

---

[This is the **beta** preview of the OpenTofu Registry Search. The data in this interface may not be up to date. →](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#)

# [Registry](https://search.opentofu.org/)

[Home](https://search.opentofu.org/)[Providers](https://search.opentofu.org/providers)[Modules](https://search.opentofu.org/modules)[Docs](https://search.opentofu.org/docs)

[](https://x.com/opentofuorg)[](https://opentofu.org/slack)

1.   [](https://search.opentofu.org/)
2.   [Providers](https://search.opentofu.org/providers)
3.   [parallels/parallels-desktop](https://search.opentofu.org/provider/parallels/parallels-desktop/v0.7.6)

*   [Overview](https://search.opentofu.org/provider/parallels/parallels-desktop/latest)
*   Resources
*   Data Sources
*   Guides

![Image 1: parallels avatar](https://github.com/parallels.png)

Provider
# parallels/parallels-desktop

Owner[parallels](https://github.com/parallels)

Published
10/19/2026

Stars
7

Forks
5

Repository[parallels/terraform-provider-parallels-desktop](https://github.com/parallels/terraform-provider-parallels-desktop/tree/v0.7.6)

License

[MIT](https://github.com/parallels/terraform-provider-parallels-desktop/blob/v0.7.6/LICENSE)

✓ Latest version

### parallels-desktop Provider[#](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#parallels-desktop-provider)

Parallels Desktop provider allows you to manage Parallels Desktop virtual machines in a remote environment. You will need a business edition license to use this provider. To get your license, please visit [Parallels Desktop](https://www.parallels.com/products/desktop/).

You can also join our community on [Discord](https://discord.gg/aFsrjbkN) channel.

#### Example Usage[#](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#example-usage)

provider "parallels-desktop" {

 license = "xxxx-xxxx-xxxx-xxxx"

 # Optional, will disable TLS validation when doing calls to the API using HTTPS

 # this is useful when the API is using a self-signed certificate

 disable_tls_validation = true

}

#### Schema[#](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#schema)

##### Required[#](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#required)

*   [`license`](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#attr-license) (String, Sensitive) Parallels Desktop Pro or Business license

##### Optional[#](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#optional)

*   [`disable_tls_validation`](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#attr-disable_tls_validation) (Boolean) Disable TLS validation
*   [`my_account_password`](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#attr-my_account_password) (String, Sensitive) Parallels Desktop My Account password
*   [`my_account_user`](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#attr-my_account_user) (String) Parallels Desktop My Account user

[Edit this page](https://github.com/parallels/terraform-provider-parallels-desktop/blob/v0.7.6/docs/index.md)

#### Versions

#### Latest

[v0.7.6 Latest 10/19/2026](https://search.opentofu.org/provider/parallels/parallels-desktop/latest)

#### Older versions

*   v0.x 10/19/2026

#### Use this provider

Add this to your configuration and run `tofu init`

terraform {

 required_providers {

 parallels-desktop = {

 source = "parallels/parallels-desktop"

 version = "0.7.6"

 }

 }

}

provider "parallels-desktop" {

 # Configuration options

}

### On this page

*   [Example Usage](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#example-usage)
*   [Schema](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#schema)
    *   [Required](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#required)
    *   [Optional](https://search.opentofu.org/provider/parallels/parallels-desktop/latest#optional)

Copyright © OpenTofu a Series of LF Projects, LLC and its contributors. Documentation materials are licensed under various open sources license from other authors, see the referenced license files for details. For web site terms of use, trademark policy, privacy policy and other project policies please see [lfprojects.org/policies](https://lfprojects.org/policies).
