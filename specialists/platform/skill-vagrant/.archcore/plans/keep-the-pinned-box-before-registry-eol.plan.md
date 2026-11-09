---
title: Keep the pinned box before the box registry closes
type: plan
status: accepted
tags: [boxes, registry, provider]
created: 2026-11-07
Last reviewed: 2026-11-09
---

# Plan: Keep the pinned box before the box registry closes

Status: accepted 2026-11-09 by the operator (proposed 2026-11-07).

## Why

HCP Vagrant, which serves `bento/...` boxes, ends operations on 2026-12-31 (`documents/research-sources-20261107/hcp-vagrant-eol.md`). A lab pinned to `bento/ubuntu-24.04` `202510.26.0`
cannot be rebuilt from the pin after that unless the box is kept or rehosted.

## Steps

1. Operator chooses a storage place outside any git repo (the box is about 3.5 GB).
2. `vagrant box repackage bento/ubuntu-24.04 parallels 202510.26.0` and `vagrant box repackage bento/ubuntu-24.04 virtualbox 202510.26.0` in
   that place (both are installed, observed 2026-11-09); record each file's sha256 beside it. Other boxes a lab still rebuilds from (see
   `vagrant box list`) follow the same step.
3. Record the location and hash in the engaging project (smc-resiliency) and a Learned entry in `references/boxes-and-pinning.md`.
4. Test the restore on a scratch name (`vagrant box add --name lab/ubuntu-24.04-202510.26.0 <file>`) without touching the running lab.
5. Watch for where bento publishes after 2026-12-31 and update the reference.

## Done when

The file, its hash and a tested restore command are recorded; no running VM was touched.

## Status 2026-11-09

52 days to end of operations. bento has not announced a new home: RFC chef/bento#1699 (GitLab package registry plus a `metadata.json` on GitLab
Pages) is still open (`documents/research-sources-20261109/bento-issue-1699.md`). The VirtualBox build of the same box version is installed too,
so step 2 now covers two providers. Still waiting on the operator's storage location (step 1).

## Status 2026-11-09 (b)

Steps 1 to 4 done: storage on the operator's external storage disk (operator, 2026-11-09), both builds repackaged with sha256 and a manifest
beside them, restore tested on a scratch name with no running VM touched (`references/boxes-and-pinning.md`, Learned 2026-11-09 (b)). Step 5
(watch where bento publishes after 2026-12-31) stays open.
