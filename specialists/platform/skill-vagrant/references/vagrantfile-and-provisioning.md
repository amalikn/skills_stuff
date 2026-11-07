# Vagrantfile and provisioning

How a Vagrantfile is read, how several machines share one, what the Parallels provider block does and when each provisioner, customize step and trigger runs. Captures named `[file]` are in
[documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Load order and merging](#load-order-and-merging)
- [Multi-machine](#multi-machine)
- [The Parallels provider block](#the-parallels-provider-block)
- [Customize events: what runs on every boot](#customize-events-what-runs-on-every-boot)
- [Provisioners](#provisioners)
- [Triggers](#triggers)
- [cloud-init](#cloud-init)
- [Plugins and environment variables](#plugins-and-environment-variables)
- [Lint before up](#lint-before-up)
- [Worked example](#worked-example)

## Load order and merging

Vagrant loads, in order: the Vagrantfile packaged with the box, the one in the Vagrant home (`~/.vagrant.d`), the project's, then multi-machine overrides, then provider-specific overrides; each level
merges into the last. Most settings override; networks are appended; several `Vagrant.configure` blocks in one file merge in order (VERIFIED_PRIMARY, [vagrant-vagrantfile.md]). Consequence: a box's
own Vagrantfile and a stray `~/.vagrant.d/Vagrantfile` can add settings the project file does not show. `VAGRANT_CWD` changes where Vagrant looks for the Vagrantfile and how relative paths in it
expand (VERIFIED_PRIMARY, [vagrant-env-vars.md]); scripts that drive a lab `cd` into the Vagrant directory or set it.

## Multi-machine

`config.vm.define "<name>"` declares a machine; `primary: true` makes it the default for commands given no name (only one may be primary); `autostart: false` keeps it out of a bare `vagrant up`
(VERIFIED_PRIMARY, [vagrant-multi-machine.md]). Settings outside the `define` blocks apply to every machine, and outer provisioners run before inner ones ("outside in", see below). Name the machine in
every scripted command (`vagrant ssh <name> -c ...`), so a second machine added later cannot change which one a script reaches.

## The Parallels provider block

```ruby
smc.vm.provider "parallels" do |p|
  p.name = vagrant_name      # the name in Parallels Desktop and in prlctl; default is <folder>_<timestamp>
  p.memory = 4096            # MiB
  p.cpus = 4
  # p.linked_clone = false   # full clone instead of the default linked clone (new machines only)
  # p.update_guest_tools = true   # reinstall Parallels Tools on a version mismatch (2-6 min, restarts the VM)
  # p.check_guest_tools = false   # skip the Tools version check entirely
end
```

All of these are vagrant-parallels options (VERIFIED_PRIMARY, [vp-configuration.md]). Set `p.name`: without it the VM is named after the folder plus a timestamp, and every `prlctl` command and guard
has to look the name up. When the Parallels provider is installed it has a higher priority than the built-in providers, so `vagrant up` picks it; `--provider=parallels` makes that explicit
(VERIFIED_PRIMARY, [vp-usage.md]).

## Customize events: what runs on every boot

`p.customize [...]` runs a `prlctl` command (`:id` is replaced by the VM's ID) at an event (VERIFIED_PRIMARY, [vp-configuration.md]):

| Event         | When                                                   |
| ------------- | ------------------------------------------------------ |
| `post-import` | once, just after the VM is cloned from the base box    |
| `pre-boot`    | before every boot (the default when no event is given) |
| `post-boot`   | after boot, before the communicator connects           |
| `post-comm`   | after the communicator connects                        |

A `customize` without an event runs on **every** `vagrant up` and `vagrant reload`. That is right for idempotent settings (`--memsize`) and wrong for anything that adds something (`--device-add hdd`
adds another disk each boot). Put additions under `"post-import"`, or add them once with `prlctl` when the stage that needs them starts. The worked example records this decision in its header: "A
second virtual disk for the identity partition (S6) is added when S6 starts, not here: provider customize runs on every boot." `vagrantfile_lint.py` warns on a `--device-add` customize without
`post-import`.

## Provisioners

- Provisioners run on the first `vagrant up`, on `vagrant provision`, and on `vagrant reload --provision`; `run: "always"` runs one on every up and reload, `run: "never"` only when named with
  `--provision-with` (VERIFIED_PRIMARY, [vagrant-provisioning-basic.md]).
- Order is "outside in": provisioners outside a `define` run before those inside it, whatever their position in the file; `preserve_order: true` keeps file order when overriding (VERIFIED_PRIMARY,
  [vagrant-provisioning-basic.md]).
- The shell provisioner takes `inline` or `path`, `args`, `env` (`sensitive: true` hides its values from output), `privileged` (sudo, default true), `reboot`, `reset` and `upload_path`
  (VERIFIED_PRIMARY, [vagrant-provisioner-shell.md]).
- The file provisioner uploads as the SSH user, not root: upload to `/tmp` and move with a shell step (VERIFIED_PRIMARY, [vagrant-provisioner-file.md]).
- Write every provisioner to be idempotent (`grep -q ... || echo ... >>`, `dpkg-query -W` before `apt-get install`), so `vagrant provision` is a safe re-run, and print a short report at the end so the
  provision log is evidence.
- Pin what the provisioner installs when the lab must be reproducible: an exact `apt-get install pkg=version`, a pinned pip version, or an apt snapshot date ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md#pin-the-archive-not-only-the-box)).

## Triggers

`config.trigger.before` / `.after` run a host command (`run`) or a guest command (`run_remote`) or Ruby (`ruby`) around an action, a command or a hook (`type` `:action`, `:command`, `:hook`);
`only_on` limits to named machines; `on_error`, `exit_codes`, `abort`, `warn`, `info` shape failure handling (VERIFIED_PRIMARY, [vagrant-triggers-configuration.md], [vagrant-triggers-usage.md]). Use a
trigger for host-side bookkeeping a lab needs on every `up` or `destroy` (record the box version, refuse to destroy a machine holding unsaved results). Keep it short and deadline-bound: a hanging
trigger hangs `vagrant up`.

## cloud-init

`config.vm.cloud_init` attaches user data (`text/cloud-config`, `text/x-shellscript` and the other listed content types; the only `type` is `:user_data`) from a `path` or `inline` (VERIFIED_PRIMARY,
[vagrant-cloud-init-configuration.md], [vagrant-cloud-init-usage.md]). HashiCorp's examples use the VirtualBox provider; whether vagrant-parallels 2.4.9 delivers cloud-init data is UNVERIFIED (no
statement in its docs; bento issue 1655 reports "cloud init not working" on a bento box, [vp-issue-1655.md]). For Parallels labs, shell provisioners are the proven path.

## Plugins and environment variables

`vagrant plugin install <name>`, `vagrant plugin list`, `vagrant plugin update`; third-party plugins "can introduce instabilities" (VERIFIED_PRIMARY, [vagrant-plugins-usage.md]). Useful environment
variables (VERIFIED_PRIMARY, [vagrant-env-vars.md]): `VAGRANT_CWD`, `VAGRANT_HOME` (boxes live here, default `~/.vagrant.d`; it gets large), `VAGRANT_DEFAULT_PROVIDER`,
`VAGRANT_BOX_UPDATE_CHECK_DISABLE`, `VAGRANT_CHECKPOINT_DISABLE` (no version check calls home), `VAGRANT_DOTFILE_PATH`, `VAGRANT_LOG`. `VAGRANT_EXPERIMENTAL` enables named experimental features;
Vagrant does not validate the names (VERIFIED_PRIMARY, [vagrant-experimental.md]).

## Lint before up

`just lint-vagrantfile <path>` (`scripts/vagrantfile_lint.py`) checks the rules above without running Vagrant: every box has an exact `box_version`, a provider block is set, every machine in a
multi-machine file has a provider `name`, `--device-add` customizes run at `post-import`, and no credential, token or private key is written in the file. It reads the file as text; it does not
evaluate Ruby, so a value computed at run time is reported as unknown, never as passing.

## Worked example

smc-resiliency's Pi spike lab (canonical `vagrant_stuff/smc-pi-spike01/Vagrantfile` @ 8591b72; project copy @ 4e436e8d): one primary machine, three `autostart: false` helpers, provisioning as heredoc
shell scripts with a report at the end, each machine named for Parallels:

```ruby
config.vm.define vagrant_name, primary: true do |smc|
  smc.vm.hostname = vagrant_name
  smc.vm.network "private_network", ip: "<lab address>", auto_config: false   # eth1: the site trunk, configured by the image under test
  smc.vm.provision "shell", inline: $BASE
  smc.vm.provision "shell", inline: $S2
  smc.vm.provider "parallels" do |p|
    p.name = vagrant_name
    p.memory = 4096
    p.cpus = 4
  end
end
config.vm.define client_name, autostart: false do |client|
```
