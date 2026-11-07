<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://search.opentofu.org/provider/bmatcuk/vagrant/latest
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: jina-reader(ok))

---

[This is the **beta** preview of the OpenTofu Registry Search. The data in this interface may not be up to date. →](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#)

# [Registry](https://search.opentofu.org/)

[Home](https://search.opentofu.org/)[Providers](https://search.opentofu.org/providers)[Modules](https://search.opentofu.org/modules)[Docs](https://search.opentofu.org/docs)

[](https://x.com/opentofuorg)[](https://opentofu.org/slack)

1.   [](https://search.opentofu.org/)
2.   [Providers](https://search.opentofu.org/providers)
3.   [bmatcuk/vagrant](https://search.opentofu.org/provider/bmatcuk/vagrant/v4.1.0)

*   [Overview](https://search.opentofu.org/provider/bmatcuk/vagrant/latest)
*   Resources

![Image 1: bmatcuk avatar](https://github.com/bmatcuk.png)

Provider
# bmatcuk/vagrant

Owner[bmatcuk](https://github.com/bmatcuk)

Published
7/31/2021

Repository[bmatcuk/terraform-provider-vagrant](https://github.com/bmatcuk/terraform-provider-vagrant/tree/v4.1.0)

License

[MIT](https://github.com/bmatcuk/terraform-provider-vagrant/blob/v4.1.0/LICENSE)

✓ Latest version

### Vagrant Provider[#](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#vagrant-provider)

A Vagrant provider for terraform 0.12+.

A note about lippertmarkus/vagrant in the registry: when I originally wrote this provider, the terraform registry didn't exist. My terraform needs waned and I didn't hear about the registry until some time later. lippertmarkus forked my provider and published to the registry as a convenience. Thanks! But, it's just an older version of this exact same codebase. So, I recommend you use bmatcuk/vagrant to get the latest updates instead.

#### Installation[#](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#installation)

Add bmatcuk/vagrant to [required_providers](https://www.terraform.io/docs/language/providers/requirements.html#requiring-providers):

terraform {

 required_providers {

 vagrant = {

 source = "bmatcuk/vagrant"

 version = "~> 4.0.0"

 }

 }

}

#### Example Usage[#](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#example-usage)

provider "vagrant" {

 # no config

}

#### Removing Machines[#](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#removing-machines)

Sadly, due to some limitations in vagrant, it's not possible to automatically remove a portion of machines from a Vagrantfile. In other words, if your Vagrantfile defines 5 machines and you remove 2 of them from the Vagrantfile, they will be left running in your vagrant provider (ie, virtualbox or whatever) with no way of removing them via vagrant (or terraform).

If you intend of removing some machines, you should manually run `vagrant destroy MACHINE_NAME` on those machines you wish to remove _before_ editing the Vagrantfile. Then update your Vagrantfile and allow terraform to do the rest.

If you forget, you can manually cleanup these old VMs by launching your vagrant provider's UI and deleting the machines. Then run `vagrant global-status --prune` to cleanup vagrant's cache of these machines.

#### Debugging[#](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#debugging)

If terrafrom is failing on the vagrant step, you can get additional output by running terraform with logging output enabled. Try something like:

env TF_LOG=TRACE terraform apply ...

And, of course, you can always run vagrant on your Vagrantfile directly.

[Edit this page](https://github.com/bmatcuk/terraform-provider-vagrant/blob/v4.1.0/docs/index.md)

#### Versions

#### Latest

[v4.1.0 Latest 7/31/2021](https://search.opentofu.org/provider/bmatcuk/vagrant/latest)

#### Older versions

*   v4.x 4/14/2021
*   v3.x 4/4/2021

#### Use this provider

Add this to your configuration and run `tofu init`

terraform {

 required_providers {

 vagrant = {

 source = "bmatcuk/vagrant"

 version = "4.1.0"

 }

 }

}

provider "vagrant" {

 # Configuration options

}

### On this page

*   [Installation](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#installation)
*   [Example Usage](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#example-usage)
*   [Removing Machines](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#removing-machines)
*   [Debugging](https://search.opentofu.org/provider/bmatcuk/vagrant/latest#debugging)

Copyright © OpenTofu a Series of LF Projects, LLC and its contributors. Documentation materials are licensed under various open sources license from other authors, see the referenced license files for details. For web site terms of use, trademark policy, privacy policy and other project policies please see [lfprojects.org/policies](https://lfprojects.org/policies).
