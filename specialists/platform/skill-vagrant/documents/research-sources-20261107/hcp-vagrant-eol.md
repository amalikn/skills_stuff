<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/hcp/docs/vagrant/hcp-vagrant-eol
**Retrieved**: 2026-11-07 15:59 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/hcp/docs/vagrant/hcp-vagrant-eol:
# Deprecation of HCP Vagrant \| HashiCorp Cloud Platform \| HashiCorp Developer

HCP Vagrant is being deprecated and limited features will be available from the community edition effective November 2, 2026.
Most notably this change will now require customers using Vagrant boxes to be responsible for the
hosting costs incurred on given providers.

Customers with running instances will have until December 31, 2026, to find a new provider and rehost
their boxes, while support for new box creation from the HashiCorp Platform will end October 1,
2026. Additional capabilities will be released to help with the transition including an ability to
export boxes to a local drive, guidance on how to host Vagrant boxes in S3 along with details on
the folder structure to support the variety of providers and architectures, and how to take a
snapshot of all existing Vagrant boxes and put them into a static archive with URL redirects until
the official deprecation.

| Milestone | Date |
| --- | --- |
| End of new Box/Registry creation | October 1, 2026 |
| End of support and maintenance | November 2, 2026 |
| End of operations | December 31, 2026 |

This deprecation applies to HCP Vagrant. The [community edition in GitHub](https://github.com/hashicorp/vagrant) including the CLI will
remain available to customers which will enable the ability to build boxes locally or share boxes
in a new customer hosted location.

This deprecation is a phased process that concludes with end of support.

* New Vagrant boxes can no longer be created in HCP Vagrant as of October 1, 2026.
* Existing deployments will continue to operate until the end of support date of November 2, 2026.
* At the end of support, all deployments will be decommissioned effective December 31, 2026.

1. Review the timeline and begin your planning process.
2. Take inventory of where HCP Vagrant Registry is used across your organization.
3. Start evaluating where those boxes should live in the future.
4. Plan your migration.

**Q. What are the hosting costs I will now be responsible for?**

A. The hosting costs users will now be responsible for will depend on the provider and hosting
service they choose. Common pricing for hosting charges across some providers can be found
following these links: [AWS storage fees](https://aws.amazon.com/s3/pricing/), [IBM Cloud storage fees](https://cloud.ibm.com/objectstorage/create#pricing-onerate), and [Azure storage fees](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/#pricing).

**Q. What happens to my ability to create new Vagrant boxes after October 1, 2026?**

A. You will still be able to create new Vagrant boxes using the Vagrant command-line tool. However,
you will no longer be able to create new Vagrant boxes or share box environments via HCP Vagrant
and Vagrant Public Registry interfaces. The main difference is that customers will be responsible
for finding a new location to host their boxes.
