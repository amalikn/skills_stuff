<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/cloud-init/usage
**Retrieved**: 2026-11-07 15:51 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/cloud-init/usage:
# Vagrant Cloud-Init Usage \| Vagrant \| HashiCorp Developer

Below are some very simple examples of how to use Vagrant Cloud-Init with the VirtualBox provider.

For more detailed information about these config values and how to use cloud-init,
please read the [official documentation for cloud-init](https://cloudinit.readthedocs.io/en/latest/index.html).

A cloud\_init config can be defined as a "hash" of key values, or as a block. Below
are two examples of this for defining a cloud\_init config:

```
# Simplified form
config.vm.cloud_init content_type: "text/x-shellscript", path: "./foo/bar.sh"

# Block form
config.vm.cloud_init do |cloud_init|
  cloud_init.content_type = "text/cloud-config"
  cloud_init.inline = <<-EOF
    package_update: true
    packages:
      - nginx
  EOF
end
```

The first part will be read from a local file `./foo/bar`, and the second part
will be attached using the inline content. Both "block" and "hash" forms are supported,
and should work interchangeably.

Individual machines may have their own cloud-init data:

```
config.vm.define "web" do |web|
  web.vm.cloud_init content_type: "text/cloud-config",
    inline: <<-EOF
      package_update: true
      packages:
        - nginx
    EOF
  end
end

config.vm.define "db" do |db|
  db.vm.cloud_init content_type: "text/cloud-config",
    inline: <<-EOF
      package_update: true
      packages:
        - postgresql
    EOF
end
```
