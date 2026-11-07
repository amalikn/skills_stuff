<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/cli/provision
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/cli/provision:
# vagrant provision - Command-Line Interface \| Vagrant \| HashiCorp Developer

**Command: `vagrant provision [vm-name]`**

Runs any configured [provisioners](/vagrant/docs/provisioning)
against the running Vagrant managed machine.

This command is a great way to quickly test any provisioners, and is especially
useful for incremental development of shell scripts, Chef cookbooks, or Puppet
modules. You can just make simple modifications to the provisioning scripts
on your machine, run a `vagrant provision`, and check for the desired results.
Rinse and repeat.

* [`--provision-with x,y,z`](/vagrant/docs/cli/provision#provision-with-x-y-z) - This will only run the given provisioners. For
  example, if you have a `:shell` and `:chef_solo` provisioner and run
  `vagrant provision --provision-with shell`, only the shell provisioner will
  be run.
