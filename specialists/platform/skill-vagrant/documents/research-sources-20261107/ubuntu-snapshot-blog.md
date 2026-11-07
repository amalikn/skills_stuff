<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://ubuntu.com/blog/ubuntu-snapshots-on-azure-ensuring-predictability-and-consistency-in-cloud-deployments
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://ubuntu.com/blog/ubuntu-snapshots-on-azure-ensuring-predictability-and-consistency-in-cloud-deployments:
# Ubuntu Snapshots on Microsoft Azure: Ensuring predictability and consistency in cloud deployments \| Ubuntu

---

Canonical has become the first Linux provider to integrate a snapshot service with Microsoft Azure’s update mechanisms. This collaboration with Microsoft allows cloud administrators a safer and more predictable way to deploy updates across their fleets of Ubuntu instances on Azure.

## The importance of consistency in update rollouts

While Ubuntu [takes a number of steps](https://ubuntu.com/blog/ubuntu-updates-releases-and-repositories-explained) to reduce the risk that a security update negatively impacts our users, it is always possible that an update to any software can cause a problem in a specific deployment. Many large enterprises, therefore, follow a software update deployment model where new updates are tested in staging or canary environments and gradually rolled out across production instances. This lets those enterprises test the updates with their specific workloads and limit the impact if an update causes issues in production. Microsoft promotes practices like these as part of [Safe Deployment Practices (SDP) and Ring-based deployments](https://learn.microsoft.com/en-us/devops/operate/safe-deployment-practices#ring-based-deployment).

On Ubuntu, like in most Linux distributions, new security updates are included in the archives whenever they are available. That means that, if you simply install all available updates from the Ubuntu archives in a staging environment and then gradually do the same across production instances, the available packages can change over time. What is installed on instances at the end of the rollout process can therefore be different to the packages that were installed on the initial instance that you tested. That undermines the value of the testing and gradual rollout and can increase the risk of an update impacting production services.

## The snapshot service

To tackle the issue of inconsistent updates, we are introducing the Ubuntu snapshot service. Available at snapshot.ubuntu.com, it provides a complete archive of the Ubuntu repository, starting from February 2023. This system empowers administrators to update an Ubuntu Virtual Machine (VM) or container based on the state of the archive as it was at a specific date and time. With the snapshot service, every update or deployment during a rollout, from the first to the last, can see identical packages, ensuring the packages that were tested in staging precisely match those being deployed across the production estate.

To use the snapshot service, users must append the desired snapshot date to the repository URL as a parameter when making a query. For instance, adding lines like:

`deb https://snapshot.ubuntu.com/ubuntu/20230401T000000Z lunar main` in `/etc/apt/sources.list` will retrieve a snapshot of the Ubuntu archive for the indicated timestamp.

## Empowering Safe Deployment Practices on Azure

One of the standout benefits of this collaboration is the simplification of Safe Deployment Practice (SDP) adherence for Ubuntu users running Linux workloads on Azure. SDP represents more than just an automated function; it embodies a set of principles with value for every cloud administrator. Many Azure customers are already using Azure tools such as Auto Patching through Azure Guest Patching Service and Azure Kubernetes Service and the inclusion of snapshot support into these services unlocks the benefits of SDP for those users without them needing to learn new tools. For users of these services, the platform will incrementally roll out the same updates on a customer’s fleet across regions in accordance with SDP.

For more details, see [Microsoft’s official announcement](https://aka.ms/azgpsakscanonicalsnapshots).

## Benefits

**Predictable Updates**: With the snapshot service, developers and administrators can test against a specific snapshot, ensuring that the versions tested are the exact same as the versions deployed in production.

**Consistency Across Deployments**: Whether the first node or the last node in a cluster, all nodes receive the same updates, ensuring uniformity.

**Simplified Update Landscape**: The combined strength of Canonical’s snapshot service and Azure’s integration simplifies the traditionally complex landscape of cloud-based updates.

**Improved Resilience and Security:** Through close collaboration with AzGPS and AKS, Ubuntu workloads on Azure VM and VMSS gain enhanced resilience and security features.

**Facilitated SDP Implementation**: The combined strength of Canonical’s snapshot service and Azure’s integration makes it easier for administrators to implement SDP.

## A word from Microsoft

Brendan Burns, Corporate Vice President, Cloud Native/Linux/OSS, Microsoft Azure, says:

> “We’re pleased to release an integrated solution for Microsoft Azure customers to enable Safe Deployment Practices (SDP) on both their Azure VMs and containerized workloads. This functionality enables cloud-native developers to innovate faster, and at the same time, operators to increase the resiliency and security of their popular Linux workloads. We’re excited to integrate cloud scale/aware management and update services with Ubuntu’s new repo snapshot service.“

## Conclusion

Cloud administrators for larger Ubuntu estates will often need to test security updates and roll these gradually through their production fleet. The continuously changing Ubuntu archive made it difficult to ensure that the updated packages that are tested in staging match those that are rolled out to each production instance. Canonical’s new snapshot service, coupled with Azure’s integration, lets cloud administrators test and deploy a consistent set of updates, all through familiar Azure interfaces. We look forward to seeing all of the new and exciting ways that our users and partners leverage the new snapshot service to push the boundaries of innovation while maintaining the highest standards of dependability and security for our users.

**Update**: See the new landing page and documentation for the snapshot service [here](https://snapshot.ubuntu.com/)!
