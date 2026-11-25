---
Title: python override - learned network
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/python.md (HTTP, S3 and other network clients)
Last reviewed: 2026-11-25
Summary: Learned entries about Python network clients; started 2026-11-25 when learned-other.md reached its line budget.
---

# python: learned network

> **Learned 2026-11-25** · Python, many S3 objects through the aws CLI · VERIFIED_PRIMARY (measured, same store, same Mac) · Source: continuum-app
> `scripts/deploy/store_pull.py` (8fe7432), continuum efficiency log 2026-11-25 · Falsifier: an `aws s3 cp --recursive --include` batch whose cost does not grow
> with the bucket's size. Copying 8,720 named objects (1.87 GB) from SeaweedFS by batched `aws s3 cp s3://b/ dest/ --recursive --exclude '*' --include k1
> ...` took 582 s, 9 minutes of it CPU: every batch re-lists the whole bucket and matches each key against every pattern. A stdlib client (SigV4 over
> urllib, one paged ListObjectsV2, eight threads of GetObject) did the same copy in 37 s. To fetch a known list of keys, GET them; do not filter a recursive
> copy. Give the child an isolated config (`AWS_CONFIG_FILE`, `AWS_SHARED_CREDENTIALS_FILE=/dev/null`) if the CLI is kept, so the user's profiles never apply.

