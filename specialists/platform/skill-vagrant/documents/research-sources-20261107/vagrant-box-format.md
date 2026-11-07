<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/boxes/format
**Retrieved**: 2026-11-07 15:51 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/boxes/format:
# Box File Format \| Vagrant \| HashiCorp Developer

A Vagrant `.box` file is a [tarball](https://en.wikipedia.org/wiki/Tar_(computing))
(`tar`, `tar.gz`, `zip`) that contains all the information for a provider
to launch a Vagrant machine.

There are four different components that make up a box:

* VM artifacts (required) - This is the VM image and other artifacts
  in the format accepted by the provider the box is intended for.
  For example, a box targeting the VirtualBox provider might have a `.ofv`
  file and some `.vmdk` files.
* metadata.json (required) - Contains a map with information about the box.
  Most importantly the target provider.
* info.json - This is a JSON document that can provide additional
  information about the box that displays when a user runs
  `vagrant box list -i`. More information is provided [here](/vagrant/docs/boxes/info).
* Vagrantfile - The Vagrantfile embedded in the Vagrant box will provide
  some defaults for users of the box. For more information on how
  Vagrant merges Vagrantfiles including ones sourced within the
  box file see the [Vagrantfile docs](/vagrant/vagrant-cloud)

Note

HCP Vagrant is being [deprecated](/hcp/docs/vagrant/hcp-vagrant-eol). Customers using Vagrant boxes hosted on the HCP Vagrant registry must find a new provider and re-host their boxes. As of October 1, 2026, new boxes can no longer be created in HCP Vagrant. Existing box deployments will continue to operate until the end of operations date of December 31, 2026. After that time, all deployments will be decommissioned.

So, if you extract a box and look at it's contents it will look like:

```
# contents of the hashicorp/bionic64 box
# ref: https://app.vagrantup.com/hashicorp/boxes/bionic64
$ ls hashicorp_bionic_box  
Vagrantfile                     metadata.json
box.ovf                         ubuntu-18.04-amd64-disk001.vmdk
```

Within the archive, Vagrant does expect a single file:
`metadata.json`. There is only one `metadata.json` per box file.
`metadata.json` must contain at least the "provider" key with the
provider the box is for. Vagrant uses this to verify the provider of
the box. For example, if your box was for VirtualBox, the
`metadata.json` would look like this:

```
{
  "provider": "virtualbox"
}
```

If there is no `metadata.json` file or the file does not contain valid JSON
with at least a "provider" key, then Vagrant will error when adding the box,
because it cannot verify the provider.

Other keys/values may be added to the metadata without issue. The value
of the metadata file is passed opaquely into Vagrant and plugins can make
use of it. Values currently used by Vagrant core:

* [`provider`](/vagrant/docs/boxes/format#provider) - (string) Provider for the box
* [`architecture`](/vagrant/docs/boxes/format#architecture) - (string) Architecture of the box
