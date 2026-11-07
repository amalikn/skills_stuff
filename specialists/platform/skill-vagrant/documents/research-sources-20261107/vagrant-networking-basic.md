<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/networking/basic_usage
**Retrieved**: 2026-11-07 15:51 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/networking/basic_usage:
# Basic Usage - Networking \| Vagrant \| HashiCorp Developer

Vagrant offers multiple options for how you are able to connect your
guest machines to the network, but there is a standard usage pattern as
well as some points common to all network configurations that
are important to know.

All networks are configured within your [Vagrantfile](/vagrant/docs/vagrantfile)
using the `config.vm.network` method call. For example, the Vagrantfile
below defines some port forwarding:

```
Vagrant.configure("2") do |config|
  # ...
  config.vm.network "forwarded_port", guest: 80, host: 8080
end
```

Every network type has an identifier such as `"forwarded_port"` in the above
example. Following this is a set of configuration arguments that can differ
for each network type. In the case of forwarded ports, two numeric arguments
are expected: the port on the guest followed by the port on the host that
the guest port can be accessed by.

Multiple networks can be defined by having multiple `config.vm.network`
calls within the Vagrantfile. The exact meaning of this can differ for
each [provider](/vagrant/docs/providers), but in general the order specifies
the order in which the networks are enabled.

Networks are automatically configured and enabled after they've been defined
in the Vagrantfile as part of the `vagrant up` or `vagrant reload` process.

A hostname may be defined for a Vagrant VM using the `config.vm.hostname`
setting. By default, this will modify `/etc/hosts`, adding the hostname
on a loopback interface that is not in use. For example:

```
Vagrant.configure("2") do |config|
  # ...
  config.vm.hostname = "myhost.local"
end
```

will add the entry `127.0.X.1 myhost myhost.local` to `/etc/hosts`.

A public or private network with an assigned IP may be flagged for hostname.
In this case, the hostname will be added to the flagged network. Note, that
if there are multiple networks only one may be flagged for hostname. For
example:

```
Vagrant.configure("2") do |config|
  # ...
  config.vm.hostname = "myhost.local"
  config.vm.network "public_network", ip: "192.168.0.1", hostname: true
  config.vm.network "public_network", ip: "192.168.0.2"
end
```

will add the entry `192.168.0.1 myhost myhost.local` to `/etc/hosts`.
