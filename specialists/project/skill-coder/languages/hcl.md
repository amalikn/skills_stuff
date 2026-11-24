---
Title: HCL override (OpenTofu and Terraform)
Category: reference
Status: current
Authority: local-supplement
Scope: OpenTofu or Terraform configuration (HCL) in any project
Last reviewed: 2026-11-19
Summary: >-
  OpenTofu config is declarative infrastructure: providers pinned with a committed lock file, state and plugin data outside the repo,
  secrets only from the environment, `tofu fmt` and tflint as the linters, a plan before every apply, writes behind the project's gate.
---

# HCL override (OpenTofu and Terraform)

## Contents

- [Authoritative sources](#authoritative-sources)
- [Tools](#tools)
- [Core rule mapping](#core-rule-mapping)
- [Learned](#learned)

## Authoritative sources

OpenTofu documentation (`tofu fmt`, `tofu init -backend-config`, dependency lock file, `TF_DATA_DIR`), the tflint README and its terraform ruleset, and the provider's own docs (for Proxmox:
bpg/proxmox, through skill-proxmox).

## Tools

| Job       | Tool                                                                                              | Note                                                             |
| --------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| Toolchain | `tofu` at the version the project pins; `required_version` in `versions.tf`                       | The lock file `.terraform.lock.hcl` is committed                 |
| Format    | `tofu fmt -check` (`tofu fmt` to fix)                                                             | Two-space HCL is the formatter's own style                       |
| Lint      | tflint with `.tflint.hcl` (`plugin "terraform" { preset = "recommended" }`), `tflint --init` once | Pinned in mise (`tflint = "<version>"`)                          |
| Validate  | `tofu validate`, then `tofu plan`                                                                 | A plan is the dry run; apply only behind the project's `--apply` |

## Core rule mapping

| Core rule               | In HCL                                                                                                                                                  |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Writes need `--apply`   | The wrapper runs `tofu plan` by default and `tofu apply -auto-approve` only with `--apply`                                                              |
| No secrets in code      | Provider credentials only from the environment (for bpg/proxmox `PROXMOX_VE_API_TOKEN`), set by the wrapper from the password store for the one command |
| No deployment literals  | Hosts, IDs and sizes are variables with defaults in one `*.auto.tfvars`; a `validation` block refuses values outside the allowed range                  |
| State is not source     | `backend "local" {}` with the path from `-backend-config`, and `TF_DATA_DIR` in the project's working cache, never in the repo                          |
| One linter per language | `tofu fmt -check` and tflint, both in the project's `lint` recipe                                                                                       |

## Learned

> **Learned 2026-11-07** · OpenTofu 1.13.9, bpg/proxmox 0.120.0, tflint 0.65.0 · VERIFIED_PRIMARY · Source: smc-resiliency
> `lab/infra/proxmox/tofu/` and `lab/infra/proxmox/x86_lab.sh` (2026-11-07) · Falsifier: a plan that reads a token from a file in the repo, or state written under the config folder A lab VM rig
> written from scratch: `versions.tf` pins `~> 0.118` and the lock file resolves the exact provider; the wrapper sets the token from KeePass and the data folder outside the repo for each run:
> ```bash
> token="$(kp show -a UserName "$KP_ENTRY")=$(kp show -s -a Password "$KP_ENTRY")"
> PROXMOX_VE_API_TOKEN="$token" TF_DATA_DIR="$X86_WC/.terraform" timeout 1800 tofu -chdir="$TF" "$@"
> ```
> A `validation` block on the VM map (`vm_id` 900 to 909, names `smc-x86-*`) keeps the token's allowed range in the code as well as in the server's ACLs. A `dynamic "network_device"` block adds an
> optional second NIC per VM without a second resource type.

> **Learned 2026-11-24** · OpenTofu 1.13.10, tflint 0.65.0, VS Code HashiCorp Terraform extension 2.40.1 · VERIFIED_PRIMARY · Source: home NAS project `tofu/encryption.tofu`
> (2026-11-24); OpenTofu v1.13.9 docs, Files and Directories, "Extension Precedence"; open-vsx `OpenTofu/vscode-opentofu` 0.6.3 · Falsifier: tflint reporting a finding inside
> a `.tofu` file, or the HashiCorp extension parsing one
> OpenTofu-only syntax (`terraform { encryption { ... } }`) shows as "Blocks of type encryption are not expected here" in the HashiCorp Terraform extension. Put it in a
> `.tofu` file: OpenTofu loads `.tofu` with the `.tf` files (a same-named `.tofu` replaces its `.tf`), Terraform tools skip it. Move the variables only that block uses into
> the same file, or tflint (which reads `.tf` only) reports them as unused. `tofu fmt -check` and `tofu validate` read `.tofu`, so they stay the authority; tflint covers
> the `.tf` files. Editor: the official extension is `OpenTofu.vscode-opentofu` ("OpenTofu (official)"); recommend it and mark `hashicorp.terraform` unwanted in
> `.vscode/extensions.json`. Proof the file is loaded: a deliberate syntax error in it fails `tofu validate` (a wrong reference inside `encryption` does not).
> ```hcl
> # tofu/encryption.tofu (home NAS, 2026-11-24)
> terraform {
>   encryption {
>     key_provider "pbkdf2" "state" {
>       passphrase = var.state_passphrase
>     }
>   }
> }
> variable "state_passphrase" {
>   type      = string
>   sensitive = true
> }
> ```
