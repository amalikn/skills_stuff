<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/providers/virtualbox/common-issues
**Retrieved**: 2026-11-09 11:32 AEDT
**HTTP status**: rc 0 via all-scraper `md`

---


**Author:** HashiCorp

**Date:** 2025-11-20

**Source:** [https://developer.hashicorp.com/vagrant/docs/providers/virtualbox/common-issues](https://developer.hashicorp.com/vagrant/docs/providers/virtualbox/common-issues)

---

# Page Structure Map
```text
Common Issues - VirtualBox Provider | Vagrant
├── Hanging on Windows
└── DNS Not Working
```

---

This page lists some common issues people run into with Vagrant and VirtualBox as well as solutions for those issues.

## Hanging on Windows

If Vagrant commands are hanging on Windows because they're communicating to VirtualBox, this may be caused by a permissions issue with VirtualBox. This is easy to fix. Starting VirtualBox as a normal user or as an administrator will prevent you from using it in the opposite way. Please keep in mind that when Vagrant interacts with VirtualBox, it will interact with it with the same access level as the console running Vagrant.

To fix this issue, completely shut down all VirtualBox machines and GUIs. Wait a few seconds. Then, launch VirtualBox only with the access level you wish to use.

## DNS Not Working

If DNS is not working within your VM, then you may need to enable a DNS proxy (built-in to VirtualBox). Please see the StackOverflow answers here for a guide on how to do that.

Edit this page on GitHub
