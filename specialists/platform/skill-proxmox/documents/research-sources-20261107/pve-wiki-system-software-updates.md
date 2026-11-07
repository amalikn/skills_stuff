Contents of https://pve.proxmox.com/wiki/System_Software_Updates:
# System Software Updates

Proxmox provides updates on a regular basis for all repositories. To install
updates use the web-based GUI or the following CLI commands:

```
# apt update
# apt full-upgrade
```

|  |  |
| --- | --- |
| Warning | As Proxmox VE uses a rolling release model on top of Debian, performing an apt upgrade may result in a partially upgraded or broken package state. This is because apt full-upgrade can also remove existing packages to satisfy dependencies if needed, while apt upgrade cannot. |

For occasionally upgrading Ceph to its succeeding major release, see
[Ceph Repositories](/wiki/Package_Repositories#sysadmin_package_repositories_ceph).

|  |  |
| --- | --- |
| Note | The APT package management system is very flexible and provides many features, see man apt, or [[Hertzog13]](/wiki/Bibliography#Hertzog13) for additional information. |

|  |  |
| --- | --- |
| Tip | Regular updates are essential to get the latest patches and security related fixes. Major system upgrades are announced in the [Proxmox VE Community Forum](https://forum.proxmox.com/). |
