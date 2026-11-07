<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://documentation.ubuntu.com/server/how-to/software/snapshot-service/
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://documentation.ubuntu.com/server/how-to/software/snapshot-service/:
---
description: Use the Ubuntu snapshot service to install historical package versions, ensure reproducible deployments, and manage structured update workflows.
title: How to use the Ubuntu snapshot service
image: https://assets.ubuntu.com/v1/cc828679-docs_illustration.svg
---

[Skip to content](#furo-main-content)

[Ubuntu Server documentation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/)

- [Tutorial](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/)
  - [Basic installation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/basic-installation/)
  - [Welcome to the terminal](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/welcome-to-the-terminal/)
  - [The command line in depth](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/cli-in-depth/)
  - [Managing your software](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/managing-software/)
  - [Attach your Ubuntu Pro subscription](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/tutorial/attach-your-ubuntu-pro-subscription/)
- [How-to guides](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/)
  - [Server installation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/)
    - [amd64 netboot install](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/how-to-netboot-the-server-installer-on-amd64/)
    - [arm64 netboot install](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/netboot-the-server-installer-via-uefi-pxe-on-arm-aarch64-arm64-and-x86-64-amd64/)
    - [Choose between the arm64 and arm64+largemem installer options](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/choosing-between-the-arm64-and-arm64-largemem-installer-options/)
    - [ppc64el netboot install](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/netboot-the-live-server-installer-on-ibm-power-ppc64el-with-petitboot/)
    - [Virtual CD-ROM and Petitboot install on ppc64el](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/how-to-start-a-live-server-installation-on-ibm-power-ppc64el-with-a-virtual-cd-rom-and-petitboot/)
    - [s390x install via z/VM](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/interactive-live-server-installation-on-ibm-z-vm-s390x/)
    - [Non-interactive IBM z/VM autoinstall (s390x)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/non-interactive-ibm-z-vm-autoinstall-s390x/)
    - [s390x install via LPAR](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/interactive-live-server-installation-on-ibm-z-lpar-s390x/)
    - [Non-interactive IBM Z LPAR autoinstall (s390x)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/installation/non-interactive-ibm-z-lpar-autoinstall-s390x/)
  - [Security](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/)
    - [User management](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/user-management/)
    - [Firewalls](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/firewalls/)
    - [AppArmor](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/apparmor/)
    - [Console security](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/console-security/)
    - [TPM-backed LUKS decryption with Clevis](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/tpm-backed-luks-decryption-with-clevis/)
    - [Kerberos](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/)
      - [Install a Kerberos server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/install-a-kerberos-server/)
      - [Configure service principals](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/configure-service-principals/)
      - [Kerberos encryption types](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/kerberos-encryption-types/)
      - [Set up secondary KDC](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/set-up-secondary-kdc/)
      - [Basic workstation authentication](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/basic-workstation-authentication/)
      - [Kerberos with OpenLDAP backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/kerberos/kerberos-with-openldap-backend/)
    - [Network user authentication with SSSD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/sssd/)
      - [SSSD with Active Directory](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/sssd/with-active-directory/)
      - [SSSD with LDAP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/sssd/with-ldap/)
      - [SSSD with LDAP and Kerberos](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/sssd/with-ldap-and-kerberos/)
      - [Troubleshooting SSSD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/sssd/troubleshooting/)
    - [Smart cards](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/smart-card-authentication/)
      - [Smart card authentication](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/smart-card-authentication/)
      - [Smart card authentication with SSH](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/smart-card-authentication-with-ssh/)
    - [OpenSSH](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/openssh-server/)
      - [2FA with TOTP/HOTP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/two-factor-authentication-with-totp-or-hotp/)
      - [2FA with U2F/FIDO](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/two-factor-authentication-with-u2f-or-fido/)
      - [GSSAPI/Kerberos authentication](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/openssh-gssapi/)
    - [Obtain TLS certificates](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/obtain-tls-certificates/)
    - [Install a root CA certificate](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/install-a-root-ca-certificate-in-the-trust-store/)
    - [OpenVPN](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/security/install-openvpn/)
    - [WireGuard VPN](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/)
      - [Peer-to-site](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/peer-to-site/)
        - [Peer-to-site (on router)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/peer-to-site-on-router/)
        - [Peer-to-site (inside device)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/on-an-internal-system/)
      - [Site-to-site](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/site-to-site/)
      - [Default gateway](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/vpn-as-the-default-gateway/)
      - [Common tasks](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/common-tasks/)
      - [Security tips](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/security-tips/)
      - [Troubleshooting](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/wireguard-vpn/troubleshooting/)
  - [Networking](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/)
    - [Host files with an FTP server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/ftp/)
    - [Set up a name server (DNS)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-dns/)
    - [Set up DNS Security Extensions (DNSSEC)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-dnssec/)
    - [DNSSEC Troubleshooting](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/dnssec-troubleshooting/)
    - [Use Open vSwitch with DPDK](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/dpdk-with-open-vswitch/)
    - [Install DOCA-OFED](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-doca-ofed/)
    - [Install DHCP isc-kea](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-isc-kea/)
    - [Install DHCP isc-dhcp-server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-isc-dhcp-server/)
    - [Time sync with chrony](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/chrony-client/)
    - [Time sync with timedatectl and timesyncd](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/timedatectl-and-timesyncd/)
    - [Serving time with chrony](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/serve-ntp-with-chrony/)
    - [Network File System (NFS) sharing](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/install-nfs/)
    - [Samba](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/)
      - [Set up a Samba AD Domain Controller](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/provision-samba-ad-controller/)
      - [Join an Active Directory domain](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/member-server-in-an-ad-domain/)
      - [Set up a file server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/file-server/)
      - [Set up a print server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/print-server/)
      - [Share access controls](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/share-access-controls/)
      - [Create AppArmor profile](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/apparmor-profile/)
      - [Mount CIFS shares permanently](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/mount-cifs-shares-permanently/)
      - [NT4 domain controller](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/nt4-domain-controller-legacy/)
      - [OpenLDAP backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/samba/openldap-backend-legacy/)
    - [Active Directory integration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/active-directory/)
      - [Prepare to join a domain](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/active-directory/join-a-domain-with-winbind-preparation/)
      - [Join a simple domain with the rid backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/active-directory/join-a-simple-domain-with-the-rid-backend/)
      - [Join a forest with the rid backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/active-directory/join-a-forest-with-the-rid-backend/)
      - [Join a forest with the autorid backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/active-directory/join-a-forest-with-the-autorid-backend/)
    - [Traffic shaping with tc and CAKE](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/traffic-shaping-tc-cake/)
    - [Set up a CUPS print server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/networking/cups-print-server/)
  - [Managing software](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/)
    - [Package management](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/package-management/)
    - [Automatic updates](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/automatic-updates/)
    - [Upgrade your release](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/upgrade-your-release/)
    - Snapshot service
    - [Reporting bugs](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/report-a-bug/)
  - [Data and storage](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/data-and-storage/)
    - [OpenLDAP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/)
      - [Install OpenLDAP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/install-openldap/)
      - [Set up access control](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/access-control/)
      - [OpenLDAP with replication](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/replication/)
      - [User and group management](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/users-and-groups/)
      - [OpenLDAP and TLS](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/ldap-and-tls/)
      - [Backup and restore](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/backup-and-restore/)
      - [Introduction to passthrough authentication](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/ldap-saslauthd-authentication-intro/)
      - [Passthrough authentication with Kerberos](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/ldap-saslauthd-kerberos/)
      - [Set up an LDAP client](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/openldap/ldap-client/)
    - [Databases](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/databases/)
      - [MySQL](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/databases/install-mysql/)
      - [PostgreSQL](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/databases/install-postgresql/)
    - [Storage](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/storage/)
      - [Manage logical volumes](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/storage/manage-logical-volumes/)
      - [iSCSI](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/storage/iscsi-initiator-or-client/)
    - [Backups and version control](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/)
      - [Install Bacula](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/install-bacula/)
      - [Install rsnapshot](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/install-rsnapshot/)
      - [Backup with shell scripts](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/back-up-using-shell-scripts/)
      - [etckeeper](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/install-etckeeper/)
      - [Install gitolite](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/backups/install-gitolite/)
  - [Mail services](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/mail-services/)
    - [Install Postfix](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/mail-services/install-postfix/)
    - [Install Exim4](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/mail-services/install-exim4/)
    - [Install Dovecot](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/mail-services/install-dovecot/)
  - [Web services](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/)
    - [Install a Squid server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/install-a-squid-server/)
    - [Install Apache2](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/install-apache2/)
    - [Apache2 settings](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/configure-apache2-settings/)
    - [Apache2 modules](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/use-apache2-modules/)
    - [Install nginx](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/install-nginx/)
    - [nginx settings](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/configure-nginx/)
    - [nginx modules](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/use-nginx-modules/)
    - [Install PHP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/install-php/)
    - [Install Ruby on Rails](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/web-services/install-ruby-on-rails/)
  - [Graphics](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/graphics/)
    - [Install NVIDIA drivers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/graphics/install-nvidia-drivers/)
    - [vGPU with QEMU/KVM](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/graphics/gpu-virtualization-with-qemu-kvm/)
  - [Virtualisation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/)
    - [LXD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/lxd/)
    - [Multipass](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/multipass/)
    - [UVtool](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/cloud-image-vms-with-uvtool/)
    - [QEMU](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/qemu/)
    - [AMD SEV](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/sev-snp/)
    - [Intel TDX](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/intel-tdx/)
    - [Hardware enablement virtualization stack](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/virt-hwe/)
    - [Libvirt and virsh](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/libvirt/)
    - [virt-manager](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/virtual-machine-manager/)
    - [Nested virtualization](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/enable-nested-virtualisation/)
    - [Ubuntu on Hyper-V](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/ubuntu-on-hyper-v/)
  - [Containers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/containers/)
    - [LXD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/virtualisation/lxd/)
    - [Docker for sysadmins](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/containers/docker-for-system-admins/)
    - [How to run rocks on your server](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/containers/run-rocks-on-your-server/)
    - [Skopeo for sysadmins](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/containers/skopeo/)
  - [High availability](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/high-availability/)
    - [Distributed Replicated Block Device (DRBD)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/high-availability/install-drbd/)
  - [Observability](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/)
    - [Set up your LMA stack](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/set-up-your-lma-stack/)
    - [Install Logwatch](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/install-logwatch/)
    - [Install Munin](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/install-munin/)
    - [Install Nagios Core 4](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/install-nagios/)
    - [Use Nagios with Munin](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/observability/use-nagios-with-munin/)
  - [Debugging](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/debugging/)
    - [About debuginfod](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/debugging/about-debuginfod/)
    - [Debug symbol packages](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/debugging/debug-symbol-packages/)
    - [Kernel crash dump](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/software/kernel-crash-dump/)
    - [eBPF](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/how-to/debugging/ebpf/)
- [Reference](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/)
  - [Glossary](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/glossary/)
  - [Command-line cheat sheet](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/cli-cheatsheet/)
  - [System requirements](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/installation/system-requirements/)
  - [High availability](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/high-availability/)
    - [Migrate from crmsh to pcs](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/high-availability/migrate-from-crmsh-to-pcs/)
  - [Other tools](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/other-tools/)
    - [terminal-multiplexers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/other-tools/terminal-multiplexers/)
    - [pam\_motd](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/other-tools/pam-motd/)
    - [sudo-rs](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/reference/other-tools/sudo-rs/)
- [Explanation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/)
  - [Security](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/security/)
    - [Introduction to security](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/security/)
    - [Security suggestions](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/security/security_suggestions/)
    - [Introduction to Kerberos](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/kerberos/)
    - [Introduction to network user authentication with SSSD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/sssd/)
    - [DNSSEC](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/dnssec/dnssec/)
    - [Cryptography](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/cryptography/)
      - [Introduction to cryptographic libraries](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/crypto-libraries/)
      - [OpenSSL](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/openssl/)
      - [GnuTLS](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/gnutls/)
      - [Network Security Services (NSS)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/network-security-services-nss/)
      - [Java cryptography configuration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/java-cryptography-configuration/)
      - [BIND 9 DNSSEC cryptography selection](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/bind-9-dnssec-cryptography-selection/)
      - [OpenSSH crypto configuration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/openssh-crypto-configuration/)
      - [Troubleshooting TLS/SSL](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/crypto/troubleshooting-tls-ssl/)
    - [Certificates](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/security/certificates/)
    - [Introduction to WireGuard VPN](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/wireguard-vpn/)
    - [OpenVPN clients](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/security/openvpn-client-implementations/)
  - [Networking](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/)
    - [Introduction to networking](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/networking/)
    - [Networking key concepts](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/networking-key-concepts/)
    - [About Netplan](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/about-netplan/)
    - [Configuring networks](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/configuring-networks/)
    - [The DPDK library](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/about-dpdk/)
    - [About DHCP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/about-dhcp/)
    - [Time synchronisation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/networking/about-time-synchronisation/)
    - [Introduction to Samba](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/samba/)
    - [Active Directory integration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/)
      - [Introduction to Active Directory integration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/AD-integration/)
      - [Choosing an integration method](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/choosing-an-integration-method/)
      - [Security identifiers (SIDs)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/security-identifiers-sids/)
      - [Identity Mapping (idmap) backends](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/identity-mapping-idmap-backends/)
      - [The rid idmap backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/the-rid-idmap-backend/)
      - [The autorid idmap backend](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/active-directory/the-autorid-idmap-backend/)
  - [Managing software](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/)
    - [Third party repository usage](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/third-party-repository-usage/)
    - [Changing package files](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/changing-package-files/)
    - [Configuration managers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/config-managers/)
    - [About apt upgrade and phased updates](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/about-apt-upgrade-and-phased-updates/)
    - [Advance testing of updates in best practice server deployments](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/software/advance-testing-of-updates-in-best-practice-server-deployments/)
  - [Data and storage](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/data-and-storage/)
    - [Introduction to OpenLDAP](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/openldap/)
    - [Introduction to databases](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/databases/)
    - [Storage](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/storage/)
      - [About LVM](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/storage/about-lvm/)
    - [Multipath](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/multipath/)
      - [Introduction to device mapper multipathing (“multipath”)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/multipath/)
      - [Configuration options and overview](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/multipath/configuring-multipath/)
      - [Configuration examples](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/multipath/multipath-configuration-examples/)
      - [Common tasks and procedures](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/multipath/common-multipath-tasks-and-procedures/)
  - [Web services](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/web-services/)
    - [Introduction to web services](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/web-servers/)
    - [About web servers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/web-services/about-web-servers/)
    - [About Squid proxy servers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/web-services/about-squid-proxy-servers/)
  - [Virtualisation and containers](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/)
    - [Introduction to virtualization](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/virtualisation/)
    - [VM tools overview](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/vm-tools-in-the-ubuntu-space/)
    - [QEMU microvm](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/qemu-microvm/)
    - [QEMU/libvirt live migration](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/live-migration/)
    - [QEMU machine types](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/qemu-machine-types/)
    - [Container tools overview](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/container-tools-in-the-ubuntu-space/)
    - [About rock images](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/about-rock-images/)
    - [Docker storage, networking, and logging](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/docker-storage-networking-and-logging/)
    - [About OpenStack](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/virtualisation/about-openstack/)
  - [Clouds](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/clouds/)
    - [About cloud-init](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/cloud-init/)
    - [Cloud images](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/clouds/find-cloud-images/)
  - [High Availability](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/high-availability/)
    - [Introduction to HA](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/intro-to/high-availability/)
    - [Pacemaker resource agents](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/high-availability/pacemaker-resource-agents/)
    - [Pacemaker fence agents](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/high-availability/pacemaker-fence-agents/)
  - [Performance](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/)
    - [Profile-Guided Optimization](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-pgo/)
    - [hwloc](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-tune-hwloc/)
    - [CPU Power (states)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-p-states/)
    - [cpupower (tool)](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-tune-cpupower/)
    - [TuneD](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-tune-tuned/)
    - [CPU affinity and NUMA](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/explanation/performance/perf-tune-affinity-numa/)

- [Contributing](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/)
  - [Contribute to this documentation](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/)
  - [Types of contributions](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/contrib-types/)
  - [Local development](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/local-development/)
  - [Guidance for writing](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/writing-guidance/)
  - [AI tools in this project](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/ai-tools-in-this-project/)
  - [Getting help](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/get-help/)
  - [Our contributors](https://canonical-ubuntu-server-documentation.readthedocs-hosted.com/contributing/contributors/)

Back to top

[Contribute to this page](https://github.com/canonical/ubuntu-server-documentation/edit/main/docs/how-to/software/snapshot-service.md "Contribute to this page")

# How to use the Ubuntu snapshot service ¶

The Ubuntu snapshot service allows you to access old packages in the Ubuntu archive based on past dates. Some of the use cases for this service include:

- Installing a superseded version of a package as it existed at a particular date and time, which is useful to troubleshoot bugs or regressions, or to allow reproducibility.
- Setting upgrades to known states, which can be useful to ensure homogeneity for a fleet of Ubuntu installations and to ensure predictability upon package upgrades (including unattended upgrades).
- Support a structured update workflow by validating snapshots in different environments or by rolling out package upgrades in stages for a large set of machines.

Here we show how to set up and use the snapshot service.

## Prerequisites ¶

Snapshots are supported in Ubuntu 23.10 onward and on updated installations of Ubuntu 20.04 LTS (starting from `apt` 2.0.10) and Ubuntu 22.04 LTS (starting from `apt` 2.4.11).

In Ubuntu 24.04 LTS and later, `apt` will automatically detect whether a repository supports snapshots. Therefore, there is no need for additional configuration before you can start using the Ubuntu snapshot service. For Ubuntu versions lower than 24.04, you need to set a `snapshot` option in the relevant entries of the `/etc/apt/sources.list` file. For instance:

If you have the following contents in the `/etc/apt/sources.list` file:

```
deb http://archive.ubuntu.com/ubuntu jammy main universe restricted multiverse
deb http://archive.ubuntu.com/ubuntu jammy-updates main universe restricted multiverse
deb http://archive.ubuntu.com/ubuntu jammy-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse

```

you can enable the snapshot service for [all components in all pockets](https://documentation.ubuntu.com/project/how-ubuntu-is-made/concepts/package-archive/#pockets) by changing it to

```
deb [snapshot=yes] http://archive.ubuntu.com/ubuntu jammy main universe restricted multiverse
deb [snapshot=yes] http://archive.ubuntu.com/ubuntu jammy-updates main universe restricted multiverse
deb [snapshot=yes] http://archive.ubuntu.com/ubuntu jammy-backports main restricted universe multiverse
deb [snapshot=yes] http://security.ubuntu.com/ubuntu jammy-security main restricted universe multiverse

```

Without the setup shown above, `apt` will simply ignore snapshot related command line options in Ubuntu releases lower than 24.04.

The following table describes whether the snapshot service can be used with each supported Ubuntu release, and whether or not it is necessary to configure the `snapshot` option in your sources configuration.

| Ubuntu Release | Supports Snapshot Service? | Need to configure sources? |
| --- | --- | --- |
| Next Ubuntu releases | Yes | No |
| Ubuntu 24.04 LTS | Yes | No |
| Ubuntu 22.04 LTS | Yes (with `apt` >= `2.4.11`) | Yes |
| Ubuntu 20.04 LTS | Yes (with `apt` >= `2.0.10`) | Yes |

## Quick start ¶

You can start using the snapshot service right away by passing the `--snapshot` option to `apt` followed by a timestamp in the format shown below.

`$`

`sudo apt install hello --update --snapshot 20240301T030400Z`

The `--snapshot` option and the the timestamp format are discussed with more details in the next sections.

## Using the snapshot service ¶

There are several options when it comes to setting up Ubuntu snapshot services. Here we present the most relevant, supported ones.

Below, we refer to the snapshot ID as `$SNAPSHOT_ID`. This is a UTC date and time formatted as `YYYYMMDDTHHMMSSZ`, e.g., `20240430T214500Z`, which refers to the snapshot that represents the state of the Ubuntu archive on April 30th, 2024, at 21:45:00 UTC.

Currently, the Ubuntu snapshot service provides snapshots for any date and time **after 1 March 2023**.

### The `--snapshot` CLI option ¶

The snapshot service can be used through the `--snapshot` (or `-S`) CLI option for `apt`, which receives a snapshot ID argument.

`$`

`sudo apt update --snapshot $SNAPSHOT_ID`

`$`

`sudo apt install $PACKAGE_NAME --snapshot $SNAPSHOT_ID`

You can also use the short, atomic version to merge the two actions above in a single command, which will download the package information from the repository, then download and install the package:

`$`

`sudo apt install $PACKAGE_NAME --update --snapshot $SNAPSHOT_ID`

or using the short version of the snapshot option:

`$`

`sudo apt install $PACKAGE_NAME --update -S $SNAPSHOT_ID`

For instance, if you want to install Docker as it was released when Ubuntu 24.04 LTS first came out, you could try a snapshot from May 2025:

`$`

`sudo apt update --snapshot 20240501T120000Z`

Note that you will need to keep using the snapshot option to let `apt` operate over the snapshot repositories. For example, if you want to check what versions of Docker are available with the snapshot:

`$`

`apt policy docker.io --snapshot 20240501T120000Z`

```
docker.io:
  Installed: (none)
  Candidate: 24.0.7-0ubuntu4
  Version table:
     24.0.7-0ubuntu4 500
        500 https://snapshot.ubuntu.com/ubuntu/20240501T120000Z noble/universe amd64 Packages

```

If you forget to use the snapshot option, `apt` will operate over the regular archive:

`$`

`apt policy docker.io`

```
docker.io:
  Installed: (none)
  Candidate: 28.2.2-0ubuntu1~24.04.1
  Version table:
     28.2.2-0ubuntu1~24.04.1 500
        500 http://archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages
     27.5.1-0ubuntu3~24.04.2 500
        500 http://security.ubuntu.com/ubuntu noble-security/universe amd64 Packages
     24.0.7-0ubuntu4 500
        500 http://archive.ubuntu.com/ubuntu noble/universe amd64 Packages

```

Then, you can install Docker from that snapshot:

`$`

`sudo apt install docker.io --snapshot 20240501T120000Z`

```
...

```

`$`

`docker --version`

```
Docker version 24.0.7, build 24.0.7-0ubuntu4

```

Now, let’s say you checked the [Docker package publishing history in Launchpad](https://launchpad.net/ubuntu/+source/docker.io-app/+publishinghistory) and (for some reason) decided you want to install version `26.1.3-0ubuntu1~24.04.1`, which, as inferred from the publishing history, superseded `docker.io` `24.0.7-0ubuntu4.1` in `noble-updates` on `2024-11-25`. Then, `24.0.7-0ubuntu4.1` was removed from the `-updates` pocket on `2024-11-26`.

You could then use `20241126T230000Z` as the snapshot ID to get the target package (`26.1.3-0ubuntu1~24.04.1`):

`$`

`sudo apt install docker.io --update --snapshot 20241126T230000Z`

```
...

```

`$`

`docker --version`

```
Docker version 26.1.3, build 26.1.3-0ubuntu1~24.04.1

```

Note

Note that, at the time of writing, the version of [docker.io](http://docker.io) in the `noble-security` pocket is `27.5.1-0ubuntu3~24.04.2`, i.e., the version used in the example above may be affected by known vulnerabilities. When using the snapshot service, do make sure to check the latest version available in your Ubuntu release’s `-security` pocket to make sure you are not installing a vulnerable package.

### Configuring the snapshot service for specific repositories ¶

In your `apt` repositories configuration files, it is possible to specify snapshots to be used for each specific repository. In the deb822 format, add a `Snapshot` option to the relevant stanza in your `.sources` file:

```
Snapshot: $SNAPSHOT_ID

```

If you are using the one-line format in `/etc/apt/sources.list` (Ubuntu 22.04 LTS and earlier), replace the `yes` value with the snapshot ID:

```
deb [snapshot=$SNAPSHOT_ID] http://archive.ubuntu.com/ubuntu ...

```

Let’s say you want to pin a specific snapshot for all the pockets in your Ubuntu 24.04 LTS server. Then, you add the `Snapshot` options to `/etc/apt/sources.list.d/ubuntu.sources`:

```
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble noble-updates noble-backports
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: 20250530T223000Z

Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: noble-security
Components: main universe restricted multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: 20250530T223000Z

```

Afterwards, you can run the following commands to install the Docker version present in that snapshot:

`$`

`sudo apt install --update docker.io`

to install the Docker version present in that snapshot.

`$`

`docker --version`

```
Docker version 27.5.1, build 27.5.1-0ubuntu3~24.04.1

```

Note that, when you configure a repository to use a snapshot using the method described above, `apt` will always ignore the `--snapshot` option:

`$`

`sudo apt install --update docker.io --snapshot 20251013T2300Z`

```
...
Hit:5 https://snapshot.ubuntu.com/ubuntu/20250530T223000Z noble InRelease
Hit:6 https://snapshot.ubuntu.com/ubuntu/20250530T223000Z noble-updates InRelease
Hit:7 https://snapshot.ubuntu.com/ubuntu/20250530T223000Z noble-backports InRelease
Hit:8 https://snapshot.ubuntu.com/ubuntu/20250530T223000Z noble-security InRelease
...
docker.io is already the newest version (27.5.1-0ubuntu3~24.04.1).
0 upgraded, 0 newly installed, 0 to remove and 3 not upgraded.

```

As you can see from the logs above, `apt` is still using the snapshot configured in `/etc/apt/sources.list.d/ubuntu.sources`, ignoring the `--snapshot` CLI option.

### Configuring the snapshot service globally ¶

As an alternative to configuring a specific snapshot for each individual repository, as described in the previous section, you can configure a snapshot globally for all repositories that have snapshots enabled.

Warning

If you are following these examples until here, make sure to revert the changes to the sources configuration file made in the previous section.

Let’s configure `apt` to default to a specific snapshot by setting the `APT::Snapshot` option:

`$`

`echo 'APT::Snapshot "20250801T111111Z";' | sudo tee /etc/apt/apt.conf.d/50snapshot`

The system will now default to fetching packages from the configured snapshot:

`$`

`sudo apt install docker.io --update`

```
...

```

`$`

`docker --version`

```
Docker version 27.5.1, build 27.5.1-0ubuntu3~24.04.2

```

Note that, in contrast to repositories with snapshots configured in the sources file as shown in the previous section, configuring a snapshot globally will not make `apt` ignore the `--snapshot` CLI option:

`$`

`sudo apt install docker.io --update --snapshot 20251013T120000Z`

`$`

`docker --version`

```
Docker version 28.2.2, build 28.2.2-0ubuntu1~24.04.1

```

You can revert the global configuration by removing the file which added it:

`$`

`sudo rm /etc/apt/apt.conf.d/50snapshot`

## Further reading ¶

- [The Ubuntu snapshot service official page and documentation](https://snapshot.ubuntu.com/)
- [Securing multiple Ubuntu instances while maximising uptime](https://ubuntu.com/blog/securing-multiple-ubuntu-instances-while-maximising-uptime)
- [Integrating the Ubuntu Snapshot Service into systems management and update tools](https://ubuntu.com/blog/integrating-the-ubuntu-snapshot-service-into-systems-management-and-update-tools)

Contents

- How to use the Ubuntu snapshot service
  - [Prerequisites](#prerequisites)
  - [Quick start](#quick-start)
  - [Using the snapshot service](#using-the-snapshot-service)
    - [The `--snapshot` CLI option](#the-snapshot-cli-option)
    - [Configuring the snapshot service for specific repositories](#configuring-the-snapshot-service-for-specific-repositories)
    - [Configuring the snapshot service globally](#configuring-the-snapshot-service-globally)
  - [Further reading](#further-reading)

Related links

- [Ubuntu Summit 26.10  
   Register now, online Nov 12-13](https://discourse.ubuntu.com/c/ubuntu-summit)
