---
title: Keep the pinned box before the box registry closes
type: plan
status: proposed
tags: [boxes, registry]
created: 2026-11-07
---

# Plan: Keep the pinned box before the box registry closes

Status: proposed (2026-11-07), awaiting the operator.

## Why

HCP Vagrant, which serves `bento/...` boxes, ends operations on 2026-12-31 (`documents/research-sources-20261107/hcp-vagrant-eol.md`). A lab pinned to `bento/ubuntu-24.04` `202510.26.0`
cannot be rebuilt from the pin after that unless the box is kept or rehosted.

## Steps

1. Operator chooses a storage place outside any git repo (the box is about 3.5 GB).
2. `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0` in that place; record the file's sha256 beside it.
3. Record the location and hash in the engaging project (smc-resiliency) and a Learned entry in `references/boxes-and-pinning.md`.
4. Test the restore on a scratch name (`vagrant box add --name lab/ubuntu-24.04-202510.26.0 <file>`) without touching the running lab.
5. Watch for where bento publishes after 2026-12-31 and update the reference.

## Done when

The file, its hash and a tested restore command are recorded; no running VM was touched.
