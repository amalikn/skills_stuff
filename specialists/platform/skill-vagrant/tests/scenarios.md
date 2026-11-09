---
Title: Vagrant scenarios
Category: evaluation
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant evaluation
Last reviewed: 2026-11-09
Summary: Evaluation scenarios V-S01 to V-S14: prompt, trigger, first reference, required decisions and prohibited conclusions for each claim the pack makes.
---

# Vagrant scenarios

Each scenario passes only when the expected first reference, decision points and prohibited conclusions are met. Lab names and addresses in prompts are placeholders.

## V-S01 — Make the lab rebuild the same VM

Prompt: A Vagrantfile has `config.vm.box = "bento/ubuntu-24.04"` and nothing else about the box; make next month's rebuild identical. Trigger: yes.
First reference: `boxes-and-pinning.md`. Decide an exact `box_version`, the architecture, and keeping the box file. Prohibit a range constraint called a pin, or claiming an existing machine changes
  when the pin changes.

## V-S02 — Two VMs, one address

Prompt: A second VM made from the lab VM gets the same IP and `vagrant ssh` sometimes lands on it. Trigger: yes. First reference: `clones-snapshots-and-identity.md`, then
`networking-and-synced-folders.md`. Identify the shared `/etc/machine-id` and the DUID. Prohibit "give it a new MAC" as the fix.

## V-S03 — Prove which VM answered

Prompt: A driver script runs destructive steps over `vagrant ssh lab-a`; a clone of lab-a exists. Make it safe. Trigger: yes. First reference: `lab-safety-and-guards.md`. Require an in-guest marker
check in the same remote command and a distinct exit code. Prohibit trusting the name or the address.

## V-S04 — Guest does not answer

Prompt: `prlctl exec lab-a true` hangs, `vagrant ssh` times out. Trigger: yes. First reference: `parallels-prlctl.md`. Take `prlctl capture` first, then decide reset versus wait. Prohibit an immediate
reset without a capture, or reading "Unable to open new session" after a reset as a failed command.

## V-S05 — A disk appears on every boot

Prompt: Each `vagrant reload` adds another virtual disk to the VM. Trigger: yes. First reference: `vagrantfile-and-provisioning.md`. Name the `pre-boot` default of `customize` and the `post-import`
event. Prohibit a provisioner-side workaround.

## V-S06 — A NIC the image under test configures

Prompt: The image under test must own `eth1` with VLANs; a client VM must sit on the same wire. Trigger: yes. First reference: `networking-and-synced-folders.md`. Use `private_network` with
`auto_config: false` on both, adapter 0 left as Shared. Prohibit reconfiguring `eth0`.

## V-S07 — Describe the Mac lab in OpenTofu

Prompt: Should the local Parallels lab move to OpenTofu like the Proxmox lab? Trigger: yes. First reference: `tool-choice-and-lab-symmetry.md`. Name both registry providers and their limits, and how
to keep the two labs comparable (apt snapshot date). Prohibit "no provider exists" and "match the base images".

## V-S08 — Can we use Vagrant

Prompt: Is our Vagrant use affected by the HashiCorp licence change, and which Parallels edition do we need? Trigger: yes. First reference: `licensing-and-editions.md`. Give the version-to-licence
table, the FAQ production-use grant and the Pro/Business/Enterprise requirement. Prohibit legal advice beyond the texts, or calling the MIT revert released.

## V-S09 — Exact command

Prompt: Give the command to see a lab VM's console and to run one command in it without the network. Trigger: yes. First reference: `operations-cookbook.md`. `prlctl capture --file`, `prlctl exec`
with a deadline. Prohibit a command without `timeout`.

## V-S10 — Shared folders broke after a Parallels update

Prompt: After updating Parallels Desktop, `vagrant up` says prl_fs is not available. Trigger: yes. First reference: `upgrade-and-troubleshooting.md`. Check the vagrant-parallels version (2.4.4
`prl_fsd`) and the guest release (26.04 AppArmor). Prohibit reinstalling the guest first.

## V-S11 — The project copy drifted

Prompt: The project's copy of the lab Vagrantfile has a change the canonical file lacks. Trigger: yes. First reference: `lab-safety-and-guards.md`. Move the change to the canonical file first, then
copy over; run the copy check. Prohibit editing the check or copying the project file over the canonical one without review.

## V-S12 — Closeout

Prompt: The session learned that `prlctl exec` errors for 40 s after a reset. Record it. Trigger: yes. First reference: `evolution-and-write-back.md`. A Learned entry in the focused reference with
source and falsifier, and a CHANGELOG line naming file and date. Prohibit a memory-only note.

## V-S13 — The box registry closes

Prompt: Will `vagrant up` still work in January for a lab pinned to a bento box? Trigger: yes. First reference: `boxes-and-pinning.md`. The HCP Vagrant end-of-life dates, `vagrant box repackage`,
local hosting. Prohibit "the CLI is deprecated".

## V-S14 — Negative control

Prompt: Resize a Proxmox VM's disk with OpenTofu. Trigger: no (skill-proxmox). First reference: none here. Prohibit loading this pack as primary.

## V-S15 — Which provider came up

Prompt: `vagrant up` in a new lab folder started a VirtualBox VM, but the lab was meant for Parallels. Why, and how is it fixed for good? Trigger: yes.
First reference: `providers-and-choice.md`. Name the selection order (`--provider`, `VAGRANT_DEFAULT_PROVIDER`, the `config.vm.provider` order, plugin
priority) and fix it in the Vagrantfile or the driver. Prohibit "uninstall VirtualBox".

## V-S16 — VirtualBox private network on a Mac

Prompt: A VirtualBox `private_network` with a lab address fails at `vagrant up` on an Apple silicon Mac. Trigger: yes. First reference: `virtualbox.md`.
Name macOS host-only networks, the allowed range and `/etc/vbox/networks.conf` as an operator host change, or an internal network for a VM-only wire;
check the VirtualBox and Vagrant versions (7.2 needs 2.4.9). Prohibit an amd64 box as a fix.

## V-S17 — VirtualBox licence

Prompt: Is VirtualBox free to use for this company's lab? Trigger: yes. First reference: `virtualbox.md`. Separate the GPLv3 base package from the PUEL
Extension Pack, say Vagrant needs only the base, and leave the business-use decision to the operator. Prohibit "all of VirtualBox is free for business".

## V-S18 — QEMU on macOS 27

Prompt: `vagrant up --provider=qemu` says port 50022 is already in use, but nothing listens on it. Trigger: yes. First reference: `qemu-and-libvirt.md`.
Name the vagrant-qemu 0.6.4 fix for macOS 27 and the plugin update; for a second NIC name `advanced_network` and its modes. Prohibit killing processes
on the port.
