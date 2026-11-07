<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/networking/forwarded_ports
**Retrieved**: 2026-11-07 15:51 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/networking/forwarded_ports:
# Forwarded Ports - Networking \| Vagrant \| HashiCorp Developer

**Network identifier: `forwarded_port`**

Vagrant forwarded ports allow you to access a port on your host machine and have
all data forwarded to a port on the guest machine, over either TCP or UDP.

For example: If the guest machine is running a web server listening on port 80,
you can make a forwarded port mapping to port 8080 (or anything) on your host
machine. You can then open your browser to `localhost:8080` and browse the
website, while all actual network data is being sent to the guest.

The forwarded port configuration expects two parameters, the port on the
guest and the port on the host. Example:

```
Vagrant.configure("2") do |config|
  config.vm.network "forwarded_port", guest: 80, host: 8080
end
```

This will allow accessing port 80 on the guest via port 8080 on the host.

For most providers, forwarded ports by default bind to all interfaces. This
means that other devices on your network can access the forwarded ports.
If you want to restrict access, see the `guest_ip` and `host_ip` settings
below.

This is a complete list of the options that are available for forwarded
ports. Only the `guest` and `host` options are required. Below this section,
there are more detailed examples of using these options.

* [`auto_correct`](/vagrant/docs/networking/forwarded_ports#auto_correct) (boolean) - If true, the host port will be changed
  automatically in case it collides with a port already in use. By
  default, this is false.
* [`guest`](/vagrant/docs/networking/forwarded_ports#guest) (int) - The port on the guest that you want to be exposed on
  the host. This can be any port.
* [`guest_ip`](/vagrant/docs/networking/forwarded_ports#guest_ip) (string) - The guest IP to bind the forwarded port to. If
  this is not set, the port will go to every IP interface. By default,
  this is empty.
* [`host`](/vagrant/docs/networking/forwarded_ports#host) (int) - The port on the host that you want to use to access the
  port on the guest. This must be greater than port 1024 unless Vagrant
  is running as root (which is not recommended).
* [`host_ip`](/vagrant/docs/networking/forwarded_ports#host_ip) (string) - The IP on the host you want to bind the forwarded
  port to. If not specified, it will be bound to every IP. By default,
  this is empty.
* [`protocol`](/vagrant/docs/networking/forwarded_ports#protocol) (string) - Either "udp" or "tcp". This specifies the protocol
  that will be allowed through the forwarded port. By default this is "tcp".
* [`id`](/vagrant/docs/networking/forwarded_ports#id) (string) - Name of the rule (can be visible in VirtualBox). By
  default this is "protocol""guest" (example : "tcp123").

By default, any defined port will only forward the TCP protocol. As an optional
third parameter, you may specify `protocol: 'udp'` in order to pass UDP
traffic. If a given port needs to be able to listen to the same port on both
protocols, you must define the port twice with each protocol specified, like
so:

```
Vagrant.configure("2") do |config|
  config.vm.network "forwarded_port", guest: 2003, host: 12003, protocol: "tcp"
  config.vm.network "forwarded_port", guest: 2003, host: 12003, protocol: "udp"
end
```

It is common when running multiple Vagrant machines to unknowingly create
forwarded port definitions that collide with each other (two separate
Vagrant projects forwarded to port 8080, for example). Vagrant includes
built-in mechanism to detect this and correct it, automatically.

Port collision detection is always done. Vagrant will not allow you to
define a forwarded port where the port on the host appears to be accepting
traffic or connections.

Port collision auto-correction must be manually enabled for each forwarded
port, since it is often surprising when it occurs and can lead the Vagrant
user to think that the port was not properly forwarded. Enabling auto correct
is easy:

```
Vagrant.configure("2") do |config|
  config.vm.network "forwarded_port", guest: 80, host: 8080,
    auto_correct: true
end
```

The final `:auto_correct` parameter set to true tells Vagrant to auto
correct any collisions. During a `vagrant up` or `vagrant reload`, Vagrant
will output information about any collisions detections and auto corrections
made, so you can take notice and act accordingly.

You can define allowed port range assignable by Vagrant when port collision is
detected via [config.vm.usable\_port\_range](/vagrant/docs/vagrantfile/machine_settings) property.

```
Vagrant.configure("2") do |config|
  config.vm.usable_port_range = 8000..8999
end
```
