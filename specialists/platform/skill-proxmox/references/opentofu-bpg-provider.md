---
Title: OpenTofu with bpg/proxmox
Category: reference
Status: current
Authority: canonical
Scope: skill-proxmox references/opentofu-bpg-provider.md
Last reviewed: 2026-11-07
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

smc-resiliency `spike/x86/` (uncommitted on 2026-11-07): `x86_lab.sh` (`setup | init | plan | up | down | ip`, writes only with `--apply`), `pve_lab_setup.sh` (the root step) and `tofu/*.tf`. The
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
