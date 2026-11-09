---
Title: Licensing and editions
Category: reference
Status: current
Authority: >-
  skill-vagrant canonical reference; claims carry evidence labels and cite captures in documents/
Scope: skill-vagrant: local Vagrant and Parallels labs on macOS Apple silicon
Last reviewed: 2026-11-09
Summary: Vagrant licence by version (MIT, BUSL 1.1 for 2.4.0 to 2.4.9, MIT on main since 2026-11-02), what BUSL allowed, the registry vs the CLI, and the Parallels editions that have a CLI.
---

# Licensing and editions

What licence the Vagrant you run is under, what that allows, and which Parallels Desktop edition the lab needs. This is a technical summary of the primary texts, not legal advice; a commercial
question goes to the operator with the captures below. Captures named `[file]` are in [documents/research-sources-20261107/](../documents/research-sources-20261107/readme.md).

## Contents

- [Vagrant: MIT, then BUSL 1.1, then MIT again](#vagrant-mit-then-busl-11-then-mit-again)
- [What BUSL 1.1 allowed](#what-busl-11-allowed)
- [What it means for a lab](#what-it-means-for-a-lab)
- [The box registry is not the CLI](#the-box-registry-is-not-the-cli)
- [vagrant-parallels](#vagrant-parallels)
- [Parallels Desktop editions](#parallels-desktop-editions)

## Vagrant: MIT, then BUSL 1.1, then MIT again

| Vagrant version                             | Licence                                             | Evidence (VERIFIED_PRIMARY)                                                                      |
| ------------------------------------------- | --------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| up to 2.3.7                                 | MIT ("Copyright (c) 2010 HashiCorp, Inc.")          | [vagrant-license-v2.3.7-github.md]                                                               |
| 2.4.0 to 2.4.9 (latest release, 2025-08-21) | Business Source License 1.1; "Licensed Work:        | [vagrant-license-v2.4.9-github.md]; the installed 2.4.9 gem carries the same text                |
|                                             |   Vagrant 2.4.3 or later" in the 2.4.9 text         |   (observed 2026-11-07)                                                                          |
| `main` after 2026-11-02                     | MIT ("Copyright IBM Corp. 2026")                    | commit ab4fc5e3db "Revert license update ... returning to the MIT license",                      |
|                                             |                                                     |   [vagrant-license-revert-commit-github.md], [vagrant-license-github.md]                         |

HashiCorp announced the move of its products to BSL on 2023-08-10 ([hashicorp-bsl-blog.md], [hashicorp-license-faq.md]). The MIT revert is on `main` only: as of 2026-11-07 no release carries it (the
latest tag is v2.4.9; later entries are `2.4.10.dev` pre-releases). Whether the next release ships under MIT is UNVERIFIED until it is tagged; check the LICENSE file at the tag.

## What BUSL 1.1 allowed

From HashiCorp's FAQ (VERIFIED_PRIMARY, [hashicorp-license-faq.md], FAQ 8, last updated 2023-10-17): "All non-production uses are permitted. All production uses are allowed other than hosting or
embedding the Licensed Work to compete with HashiCorp's paid version of the same Licensed Work, whether hosted or self-managed." The Vagrant 2.4.9 licence's Additional Use Grant says the same in its
own words and defines "competitive offering", "Product" and "Embedded" ([vagrant-license-v2.4.9-github.md]). Releases before the change stay under their old licence: "The license change is not
retroactive" (FAQ 10). Under BSL the code converts to an open licence on its Change Date or four years after first BSL publication (FAQ 19).

## What it means for a lab

Running Vagrant to build and use local lab VMs is neither hosting nor embedding Vagrant in a competing product, so it is permitted under both licences (inference from the texts above; UNVERIFIED as
legal advice). Points that would need the operator: shipping Vagrant inside a product or service offered to others, or redistributing a modified Vagrant. Record the version a lab used; the licence
follows the version.

## The box registry is not the CLI

The HCP Vagrant Box Registry (where `bento/...` boxes are downloaded from) is a hosted service with its own end of life: no new boxes from 2026-10-01, end of support 2026-11-02, end of operations
2026-12-31; "The community edition in GitHub including the CLI will remain available" (VERIFIED_PRIMARY, [hcp-vagrant-eol.md]). See [boxes-and-pinning.md](boxes-and-pinning.md#the-box-registry) for what a lab does about it.

## vagrant-parallels

The provider plugin is open source under the MIT licence (VERIFIED_PRIMARY, [vp-readme-github.md]). Latest release v2.4.10 on 2026-10-28; the lab Mac ran 2.4.9 (observed 2026-11-07) and runs 2.4.10 since 2026-11-09 (`vagrant plugin update`, operator).

> **Learned 2026-11-09** · Vagrant releases · VERIFIED_PRIMARY · Source: `gh release list -R hashicorp/vagrant` on 2026-11-09 · Falsifier: a Vagrant release tag after v2.4.9 dated on or before 2026-11-09
> On 2026-11-09 there is still no Vagrant release after v2.4.9. The newest entry is the pre-release `2.4.10.dev+000834-2757db88` (2026-06-01), which is older than the MIT revert on `main`
> (2026-11-02). Every installable release is therefore still BUSL 1.1. Check the LICENSE file at the next tag before calling a release MIT.

## Parallels Desktop editions

| Statement                                                                                                                         | Source (VERIFIED_PRIMARY)                   |
| --------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| "In Pro and Business/Enterprise Editions, you can control Parallels Desktop and virtual machines from the command-line interface" | [parallels-cli-utility.md]                  |
| "Only **Pro**, **Enterprise** and **Business** editions of Parallels Desktop for Mac can be used with this Vagrant provider"      | [vp-installation.md]                        |
| "Vagrant plugin is available in Parallels Desktop Pro and Business Editions only"                                                 | [parallels-kb-vagrant.md]                   |
| The provider refuses other editions: "Other editions do not have command line functionality and can not be used with Vagrant"     | [vp-issue-485.md] (error text)              |
| Enterprise licences were refused until vagrant-parallels 2.4.3 "Add 'enterprise' edition support"                                 | [vp-issue-485.md], [vp-changelog-github.md] |
| A trial has "all the same features as Parallels Desktop For Mac Pro version" (forum answer, so VERIFIED_SECONDARY)                | [hashicorp-discuss-parallels-trial.md]      |

So a Standard-edition Mac cannot run this lab at all; check the edition first (`prlsrvctl info --license --json`, read `edition` only). The `parallels/parallels-desktop` OpenTofu provider asks for a
licence key in its configuration ([tool-choice-and-lab-symmetry.md](tool-choice-and-lab-symmetry.md#opentofu-providers-that-touch-vagrant-or-parallels)).
