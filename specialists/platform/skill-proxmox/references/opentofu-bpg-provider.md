---
Title: OpenTofu with bpg/proxmox
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/opentofu-bpg-provider.md
Last reviewed: 2026-11-19
Summary: OpenTofu with the bpg/proxmox provider: versions, token authentication, when the ssh block is needed, import_from versus download_file, a UEFI VM resource, lock file and state.
---

# OpenTofu with the bpg/proxmox provider

Infrastructure as code for Proxmox VE with OpenTofu (or Terraform) and the `bpg/proxmox` provider. The Telmate provider is **not used** (operator policy). Sources: [provider
index](../documents/research-sources-20261107/bpg-provider-index.md), [vm resource](../documents/research-sources-20261107/bpg-provider-virtual_environment_vm.md),
[download_file](../documents/research-sources-20261107/bpg-provider-virtual_environment_download_file.md),
[user_token](../documents/research-sources-20261107/bpg-provider-virtual_environment_user_token.md), [acl](../documents/research-sources-20261107/bpg-provider-virtual_environment_acl.md), [latest
release](../documents/research-sources-20261107/bpg-provider-releases-latest.json), [OpenTofu lock file](../documents/research-sources-20261107/opentofu-dependency-lock.md), [local
backend](../documents/research-sources-20261107/opentofu-backend-local.md); context7 `/bpg/terraform-provider-proxmox` agrees on `import_from` and the SSH table (queried 2026-11-07).

## Contents

- [Provider and versions](#provider-and-versions)
- [Authentication](#authentication)
- [When the ssh block is needed](#when-the-ssh-block-is-needed)
- [Getting a disk image: import_from versus download_file](#getting-a-disk-image-import_from-versus-download_file)
- [A UEFI VM resource](#a-uefi-vm-resource)
- [Lock file and state](#lock-file-and-state)
- [Worked example](#worked-example)

## Provider and versions

- Source `bpg/proxmox`; the maintainers target PVE 9.x (8.x mostly works, untested; 7.x unsupported). Legacy resources are named `proxmox_virtual_environment_<name>`, newer ones `proxmox_<name>`; both
  ship in one binary. `VERIFIED_SECONDARY` (context7 library rules).
- Latest release on 2026-11-07: **v0.120.0** (published 2026-11-02). `VERIFIED_PRIMARY` (GitHub releases API capture).
- Pin with a pessimistic constraint (`version = "~> 0.118"`) and let the committed lock file fix the exact version.

## Authentication

- Credentials come from the environment, never a file: `PROXMOX_VE_ENDPOINT` and `PROXMOX_VE_API_TOKEN` (`user@realm!tokenid=<secret>`); username/password, ticket and CSRF variables exist for other
  modes. The docs call environment variables "the recommended approach for credentials". `VERIFIED_PRIMARY` (provider index, Environment Variables).
- A wrapper reads the secret from the password manager into `PROXMOX_VE_API_TOKEN` for one command and prints nothing.
- Use a privilege-separated, pool-scoped token ([access-control.md](access-control.md)). The provider's sample role is "likely too permissive"; keep `SDN.Use` (or `SDN.Audit`) so bridges are
  visible. `VERIFIED_PRIMARY`
  (provider index).
- Some operations are refused to any token (root-only); the provider can mint a short-lived `root@pam` ticket over its SSH connection for them. Design around them instead. `VERIFIED_PRIMARY` (provider
  index, Operations restricted to root@pam).

## When the ssh block is needed

```text
  tofu plan / apply (bpg/proxmox)
     |
     +-- HTTPS :8006, API token ---------> VMs and containers, storage, networks, pools, users,
     |   (always)                          ACLs, import_from disks, download_file
     |
     +-- SSH to the node (only for) -----> proxmox_virtual_environment_file uploads (snippets),
         ssh { username = ... } with        disk import via source_file.path, container idmap
         a token; non-root needs sudo
```

SSH is **only** needed to upload snippets and certain file types (`proxmox_virtual_environment_file`), to import disks via `source_file.path`, and for container `idmap`. It is **not** needed to create
or change VMs and containers, manage storage, networks, pools or users, import disks with `import_from`, or download files with `download_file`. `VERIFIED_PRIMARY` (provider index, SSH Connection).
When it is needed, the provider uses SSH as the API's PAM user by default; with a token, set `ssh { username = ... }`, and a non-root SSH user needs password-less `sudo` for the listed commands on
every node. `VERIFIED_PRIMARY`.

## Getting a disk image: import_from versus download_file

| Approach                                                 | What it does                                       | Rights the token needs                             | Use when                        |
| -------------------------------------------------------- | -------------------------------------------------- | -------------------------------------------------- | ------------------------------- |
| `proxmox_virtual_environment_download_file`              | The node fetches a URL into `<storage>:import/`    | `Datastore.AllocateTemplate` +                     | The token may make the node     |
|   with `content_type = "import"`                         |   (optional checksum)                              |   `Sys.Audit`/`Sys.Modify` on `/`, or              |   fetch URLs                    |
|                                                          |                                                    |   `Sys.AccessNetwork` on the node                  |                                 |
| `disk { import_from = "<storage>:import/<file>" }` on an | Copies the image into the VM's new disk            | Datastore and VM rights only                       | A root step placed the file     |
|   existing file                                          |                                                    |                                                    |   (least privilege)             |
| `disk { file_id = ... }`                                 | For compressed images downloaded with              | as download                                        | Compressed images               |
|                                                          |   `content_type = "iso"`                           |                                                    |   (`import_from` cannot         |
|                                                          |   and `decompression_algorithm`                    |                                                    |   take them)                    |

`import_from` needs an uncompressed image of `import` content; its ID is `<datastore_id>:import/<file_name>`, and the storage must have `import` enabled first (not on by default). `VERIFIED_PRIMARY`
(vm resource, download_file). Rights: [storage.md](storage.md#the-import-content-type).

## A UEFI VM resource

```hcl
resource "proxmox_virtual_environment_vm" "lab" {
  machine         = "q35"
  bios            = "ovmf"
  stop_on_destroy = true            # no guest agent: shutdown would hang
  agent { enabled = false }
  efi_disk {
    datastore_id      = var.datastore_id
    file_format       = "qcow2"
    type              = "4m"
    pre_enrolled_keys = false       # Secure Boot off
  }
  disk {
    datastore_id = var.datastore_id
    import_from  = var.image_file_id  # "local:import/<image>.qcow2"
    interface    = "scsi0"
    size         = 16
    discard      = "on"
  }
  network_device {
    bridge      = var.bridge
    mac_address = each.value.mac      # pinned: an IPAM/DHCP binding survives destroy and recreate
  }
  serial_device {}                    # serial0: socket
  initialization {
    ip_config { ipv4 { address = "dhcp" } }
    user_account {
      username = "smc"
      keys     = [trimspace(file(pathexpand(var.ssh_public_key_file)))]
    }
  }
}
```

Attributes `VERIFIED_PRIMARY` (vm resource): `efi_disk.type` and `pre_enrolled_keys`, `stop_on_destroy` ("Whether to stop rather than shutdown on VM destroy"), `serial_device`, `agent.enabled`. What
PVE stores: [qemu-vms.md](qemu-vms.md#worked-example-config).

## Lock file and state

- Commit `.terraform.lock.hcl`: it records the provider version and hashes so every run uses the same build; review its changes like code. `VERIFIED_PRIMARY` (OpenTofu dependency lock file).
- Keep state **outside the repository**: the local backend takes `path`, which a wrapper passes at init (`tofu init -backend-config="path=<working-cache>/terraform.tfstate"`), and `TF_DATA_DIR` moves
  `.terraform/` (plugins) to the working cache too. State can hold sensitive values; it never belongs in git. `VERIFIED_PRIMARY` (local backend `path`); the `TF_DATA_DIR` use is from the worked
  example.
- Constrain what the configuration may touch with variable validation (for example a VMID range and a name prefix) so a typo cannot reach another workload.

## Worked example

smc-resiliency `spike/x86/` (uncommitted on 2026-11-07; since moved to `lab/infra/proxmox/`): `x86_lab.sh` (`setup | init | plan | up | down | ip`, writes only with `--apply`), `pve_lab_setup.sh`
(the root step) and `tofu/*.tf`. The
wrapper's core:

```bash
tofu_run() {
  local token
  token="$(kp show -a UserName "$KP_ENTRY" | tr -d '\n')=$(kp show -s -a Password "$KP_ENTRY" | tr -d '\n')"
  mkdir -p "$X86_WC"
  PROXMOX_VE_API_TOKEN="$token" TF_DATA_DIR="$X86_WC/.terraform" timeout 1800 tofu -chdir="$TF" "$@"
}
init) tofu_run init -input=false -backend-config="path=$X86_WC/terraform.tfstate" ;;
```

`providers.tf` has no `ssh` block ("every resource here uses the API alone"); `versions.tf` pins `bpg/proxmox ~> 0.118` with an empty `backend "local" {}`; `variables.tf` validates names `smc-x86-*`
and IDs 900 to 909.

> **Learned 2026-11-07 (i)** · bpg/proxmox 0.120.0, OpenTofu, Proxmox VE 9.1.5 · VERIFIED_PRIMARY · Source: smc-resiliency `spike/x86/tofu/.terraform.lock.hcl` and the lab run reported by the
> coordinating session (2026-11-07) · Falsifier: a lock file under `~> 0.118` that resolves another version on the same day
> Under `~> 0.118` the provider resolved to 0.120.0 (recorded in the lock file, which the project commits; still untracked on 2026-11-07). A plan and apply for one q35/OVMF VM with `import_from`
> took about 12 s (reported by the coordinating session, not re-measured here) against a single lab node with a
> pool-scoped token and no SSH block.

> **Learned 2026-11-07 (b)** · bpg/proxmox 0.120.0 · VERIFIED_PRIMARY · Source: smc-resiliency `lab/infra/proxmox/tofu/main.tf` (X2) · Falsifier:
> adding the watchdog block in place without a VM reboot
> A `watchdog` block (`enabled = true; model = "i6300esb"; action = "reset"`) added in place to a running VM made the provider reboot it; pin
> `boot_order = ["scsi0", "net0"]` too, since OVMF rewrites BootOrder from Proxmox's `boot: order=` on every boot.

> **Learned 2026-11-24 (b)** · OpenTofu 1.13.10, bpg/proxmox 0.123.1 · VERIFIED_PRIMARY · Source: home NAS project `tofu/versions.tf`, `tofu validate` run 2026-11-24;
> OpenTofu v1.13.9 docs (state encryption, pbkdf2 key provider); provider docs argument reference · Falsifier: a `validate` that rejects `var.*` in a pbkdf2 key provider,
> or a provider release with a CA-file argument
> - State and plan encryption fits the local-backend pattern: the passphrase is a sensitive variable the wrapper sets from the password manager
>   (`TF_VAR_state_passphrase`), with `enforced = true` so a missing variable fails instead of writing plaintext. Keep the state file in the project's persistent data
>   folder (not the rebuildable working cache: losing state loses the mapping to real objects).
> - `~> 0.120` resolved 0.123.1 on 2026-11-24. `proxmox_virtual_environment_version` is deprecated: use data source `proxmox_version`.
> - The provider has no CA-file option, only `insecure` / `PROXMOX_VE_INSECURE`: with the node's self-signed certificate either skip verification on a trusted LAN
>   or give the node a publicly trusted certificate (ACME). Host objects (APT repositories, ACME plugin and certificate, network, storage, firewall, DNS) have resources;
>   notification targets and matchers have none (negative finding in `docs/resources`).
> ```hcl
> # home NAS project tofu/encryption.tofu (2026-11-24; a .tofu file so Terraform tooling skips it: skill-coder languages/hcl.md)
> encryption {
>   key_provider "pbkdf2" "state" {
>     passphrase = var.state_passphrase
>   }
>   method "aes_gcm" "state" {
>     keys = key_provider.pbkdf2.state
>   }
>   state {
>     method   = method.aes_gcm.state
>     enforced = true
>   }
>   plan {
>     method   = method.aes_gcm.state
>     enforced = true
>   }
> }
> ```

> **Learned 2026-11-25** · OpenTofu 1.13.10, bpg/proxmox 0.123.1 · VERIFIED_PRIMARY (`tofu validate` and the offline `tofu test` passed; provider-doc facts as an agent
> reported them, schema checked against 0.123.1; the vendor-data merge on a node is UNVERIFIED) · Source: continuum-app `deploy/nas/tofu/vms.tofu` and
> `deploy/nas/tofu/tests/offline_plan.tftest.hcl` (5f723db, 3baf4da) · Falsifier: a 0.123.x `validate` rejecting `dns { servers = [...] }`, or a node whose guest gets
> only one of vendor data and the generated user data
> - `initialization { dns { servers = [...] } }` takes a list (the list form validates); `vendor_data_file_id` sits beside `user_account` in the same block. Proxmox is
>   expected to merge the vendor data with the user data it generates from `user_account` (not yet seen on a node).
> - `proxmox_virtual_environment_pool_membership` is deprecated in 0.123.1: put `pool_id` on the VM and check the pool exists with the pool data source in a
>   `precondition`.
> - `tofu test` with `mock_provider "proxmox"` runs the whole configuration offline (no node, no token): variable validations, rule counts and per-VM attributes are
>   asserted on a plan; a second `run` with bad `variables` and `expect_failures` proves a validation can fail.
>
> ```hcl
> initialization {                       # deploy/nas/tofu/vms.tofu (3baf4da)
>   datastore_id        = var.os_datastore_id
>   vendor_data_file_id = "${var.snippets_datastore_id}:snippets/${each.value.vendor_data}"
>   ip_config { ipv4 { address = each.value.ipv4_address
>                      gateway = each.value.ipv4_gateway } }
>   dns { servers = each.value.dns_servers }
>   user_account { username = "ubuntu"
>                  keys     = [trimspace(var.ssh_public_key)] }
> }
> # tests/offline_plan.tftest.hcl: no node contact
> mock_provider "proxmox" {
>   mock_data "proxmox_virtual_environment_nodes" { defaults = { names = ["node1"] } }
> }
> run "plan_three_vms" {
>   command = plan
>   assert {
>     condition     = length(proxmox_virtual_environment_firewall_rules.vm["netbird"].rule) == 7
>     error_message = "Unexpected firewall rule counts."
>   }
> }
> ```

> **Learned 2026-11-25** · bpg/proxmox 0.123.1, PVE 9.2.2 · VERIFIED_PRIMARY (node /var/log/pve/tasks/index: `vzreboot` of CTs 100 to 102 by the
> OpenTofu token at the apply of a static-address change; provider schema read with `tofu providers schema -json`) · Source: home NAS project,
> scripts/nas_node_bootstrap.sh and tofu/host/firewall.tf at 38688f6 · Falsifier: a container network update applied without a reboot task
> (1) A plan line "will be updated in-place" on `proxmox_virtual_environment_container` (network, here the IP) still reboots the container; a service
> left disabled inside it then stays down. Automation that auto-applies "create or update" plans should stop on in-place guest updates unless allowed.
> (2) `proxmox_virtual_environment_cluster_firewall` left without `ebtables` writes `ebtables: 0`, overriding the PVE default 1; set it explicitly.
> (3) Exact attributes for the pinned version, offline: init a scratch module against the project's downloaded plugin and dump the schema.
> ```bash
> grep -qE '# proxmox_virtual_environment_(container|vm)\.[a-z0-9_]+(\[[^]]*\])? will be updated in-place' "$plan_log" && exit 1  # unless allowed
> tofu -chdir=scratch init -plugin-dir="$TF_DATA_DIR/providers" && tofu -chdir=scratch providers schema -json > schema.json
> ```

> **Learned 2026-11-25 (b)** · bpg/proxmox 0.123.1, OpenTofu 1.13, PVE 9.2.2 · VERIFIED_PRIMARY (installed provider schema; plan showed
> `data_wo = (write-only attribute)`; certificate issued in 89 s) · Source: home NAS tofu/host/main.tf and nas.auto.tfvars at 7651961 · Falsifier: a
> provider release without `data_wo` on proxmox_acme_dns_plugin
> `proxmox_acme_dns_plugin` takes the DNS API token as `data_wo` with `data_wo_version` (bump it after a rotation), so the token never enters state;
> `data` stores it. Check the account name before the first order: a variable defaulting to "default" orders against an account that a GUI or host
> script created under another name (here `malik`).
> ```hcl
> data_wo         = { CF_Token = var.cloudflare_api_token }
> data_wo_version = 1
> ```

> **Learned 2026-11-26** · bpg/proxmox 0.123.1, PVE 9.2.2 · VERIFIED_PRIMARY (node task log and plans) · Source: home NAS tofu/guest_firewall.tf,
> tofu/host/main.tf, scripts/mac/nas_tofu.sh at 60e2ca4 and 99aea2d · Falsifier: a CT network change applied without a vzreboot task; an ACME domain change applied without force
> (1) `firewall = true` added to a running VM's `network_device` applies live (no qmstop or reboot); the same flag on a container's
> `network_interface` reboots the container (`vzreboot`). (2) Changing `proxmox_acme_certificate` domains fails with "Custom certificate exists but
> 'force' is not set"; `force = true` would re-order on every apply, so do a one-off `pvenode acme cert order --force` on the node, then
> `tofu state rm` and `tofu import <addr> <node>`: the provider does not re-read `domains` on refresh, so a refresh-only apply leaves a perpetual diff.
> ```hcl
> # home NAS tofu/apps_vm.tf (60e2ca4)
> network_device {
>   bridge   = "vmbr0"
>   firewall = contains(var.guest_firewall, "apps")
> }
> ```
