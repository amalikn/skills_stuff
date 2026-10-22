# 20261022 mid-flow reject

smc-resiliency's proposed flow `release-publish` (page 12, draw.io desktop 32.5.5, rendered from smc-resiliency commit ffa84a0; no site names,
addresses or serials).

- [release-publish-page.png](release-publish-page.png): the gate `package-gate` (step 3) sends Yes along the lane below to `evidence` (step 5) and
  No to `rejected` (step 4), a terminal listed straight after the gate; the later gate `approve` (step 7) still ends in `manifest` and `refused`.
  Audit clean, no crossing.
