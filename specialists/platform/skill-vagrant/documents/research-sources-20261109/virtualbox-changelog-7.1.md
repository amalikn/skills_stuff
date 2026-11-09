<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://www.virtualbox.org/wiki/Changelog-7.1
**Retrieved**: 2026-11-09 11:33 AEDT
**HTTP status**: rc 0 via all-scraper `md`

---


**Source:** [https://www.virtualbox.org/wiki/Changelog-7.1](https://www.virtualbox.org/wiki/Changelog-7.1)

---

# Page Structure Map
```text
Changelog-7.1     – Oracle VirtualBox
└── Changelog for VirtualBox 7.1
```

---

## Changelog for VirtualBox 7.1

This page lists all changes of the VirtualBox 7.1 **releases**.  
All branches: 7.2 · 7.1 · 7.0 · 6.1 · 6.0 · 5.2 · 5.1 · 5.0 · 4.3 · 4.2 · 4.1 · 4.0

**VirtualBox 7.1.x is no longer supported!**

**VirtualBox 7.1.18** (released April 21 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue which caused a Guru Meditation with VERR\_IEM\_IPE\_4 if the guest was trying to execute the wrong hypercall instruction but injected a UD exception instead (github:gh-616)
- NAT Network: Fixed issue when internal DNS server could not be reached
- Main: Fixed crash on FreeBSD 16.0 shutdown with multiple devices attached to LSI Logic SAS controller (github:gh-538)
- IPRT: Merged Github pull request 503 (fix: infinite loop in vsscanf whitespace processing). github-merge-author: lachlanharrisdev
- Linux Host: Added initial support for kernels 6.19 and 7.0 (github:gh-467, github:gh-623)
- Linux Host: Added support for guest time accounting (github:gh-2)
- Linux Host and Guest: Introduced additional fixes for RHEL 10.1 and 10.2 kernels (github:gh-455)
- Linux Host and Guest: Added support for UEK9 kernel on Oracle Linux 9
- Linux Host and Guest: Added improvements to make 'rcvboxdrv/rcvboxadd setup' and installation process faster
- Linux Guest Additions: Deprecated vboxvideo kernel module for kernels 7.0 and newer; please consider using VMSVGA graphics or vboxvideo module which comes with Linux kernel or provided by your Linux distribution if guest running kernel 7.0+; vboxvideo will still be available for older kernels
- Linux Guest Additions: Fixed issue when last character was not pasted into Windows host clipboard when copying from Wayland guest (bug:22339)
- UEFI: Fixed errors with secure boot certificate updates and Windows 11 guests (github:gh-133)

**VirtualBox 7.1.16** (released January 20 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when VM process was crashing during RHEL5 guest boot
- VMM: Fixed issue when VMX nested-guest VM-entry was checking the wrong VM-execution control bit in the virtual VMCS (github:gh-313)
- VMM: Fixed issue when VM was crashing on start after recent Windows update (KB5066793) (github:gh-360)
- VMM: Fixed issue when guest process was crashing inside Windows guest on AMD system (github:gh-400)
- VMM: Fixed issue when VM process was crashing on Windows host (github:gh-426, github:gh-407, github:gh-404, github:gh-369, github:gh-238, github:gh-207, github:gh-187, github:gh-178)
- GUI: Fixed issue when downloading update files was failing (github:gh-327, github:gh-372)
- Main: Improved filename check for drag-and-drop operations (github:gh-68)
- VBoxManage: Fixed issue when VM could not be started from command line in some circumstances (github:gh-418)
- Linux Host: Fixed issue when vboxautostart-service did not start corresponding VMs on system boot (github:gh-309)
- Guest Additions: Fixed issue when guest process was crashing due to low memory in the system (github:gh-410)
- Linux Guest Additions: Fixed build issue for kernels 2.5.52 and older
- Linux Guest Additions: Fixed issue when VBoxService was not started due to abandoned pid file
- Linux Guest Additions: Fixed issue when user session services were not started on old Linux distributions
- Linux Guest Additions: Fixed check if kernel modules were loaded for old Linux distributions
- Linux Guest Additions: Fixed issue when Guest Additions processes were left running on system reboot or shutdown (github:gh-311)
- Linux Guest Additions: Added additional fixes for RHEL 9.8, 10.1 and 10.2 kernels
- Linux Guest Additions: Added initial support for kernel 6.19 (github:gh-467)
- BIOS: Fixed issue with booting VM using IPXE (github:gh-417)

**VirtualBox 7.1.14** (released October 21 2025)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed running VirtualBox on Windows with Hyper-V enabled and older Intel CPUs (github:gh-85)
- GUI: Updated native language support for Polish, Greek, Swedish, Portuguese, Turkish and Italian translations
- GUI: Updated VBox VM network status-bar indicator tooltip (IP address) on guest additions change (github:gh-179)
- Audio: Fixed a crash on Windows hosts when a host device has been changed and failed to reset (github:gh-72)
- VBoxManage: Fixed issue when two or more parallel "import" commands were failing (github:gh-80)
- Main: Added support for including the NVRAM file when exporting and importing EFI-based VMs (bug #22370, github:gh-62)
- Main: Improved Vorbis check when building VirtualBox from source code (github:gh-94)
- Main: Fixed issue when some snapshots could not be deleted (github:gh-75)
- Main: Fixed issue when it was not possible to run more than 61 VMs in parallel (github:gh-111)
- Linux Guest and Host: Fixed issue when kernel modules could not be compiled once kernel was configured with CONFIG\_OBJTOOL\_WERROR=y option (github:gh-28, github:gh-93, github:gh-116)
- Linux Guest and Host: Introduced initial support for kernels 6.17 and 6.18
- Linux Guest Additions: Introduced additional fixes for RHEL 9.6 and 9.7 kernels (github:gh-12)
- Linux Guest Additions: Added autorun support for Oracle Linux 10 and RHEL 10
- OS/2 Guest Additions: Fixed issue when some files could not be copied from guest to host (github:gh-98)
- Windows Guest Additions: Fixed issue when Guest Additions could not be installed on Windows XP guest (github:gh-115)

**VirtualBox 7.1.12** (released July 15 2025)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when running a nested VM caused Guru Meditation for outer VM
- NAT: Fixed issue when VMs with long names were unable to start (github:gh-16)
- Linux host: Fixed possible kernel panic when using bridged networking with a network interface handled by the ixgbe driver on newer kernels
- Windows Host: Fixed issue resulting in BSOD upon closing VirtualBox GUI after host package uninstall (github:gh-38)
- Windows Host: General improvements in drivers installation
- Windows Host: Implement support for exposing AVX/AVX2 to the guest when Hyper-V is used (github:gh-36)
- Recording: Fixed issue when Windows Guest Machine was unable to start when recording was enabled in Display Settings (bug #22363)
- Linux Host and Guest: Added additional fixes to support kernel 6.16
- Linux Guest Additions: Fixed issue when 'rcvboxadd status-kernel' was reporting incorrect status when guest was running kernel 3.10 series and older
- Linux Guest Additions: Fixed issue when VBoxClient was unable to start if guest was running kernel 2.6 series and older
- Linux Guest Additions: Fixed issue which caused a warning in system log due to incorrect udev rule

**VirtualBox 7.1.10** (released June 03 2025)  

This is a maintenance release. The following items were fixed or added:

- VBoxManage: Fixed a crash when running 'guestcontrol run' on Windows hosts (bug #22175)
- Audio: Fixed device switching on Windows hosts (bug #22267)
- Windows host installer: Fixed multiple installation entries in the 'Add or remove programs' dialog and upgrade issues
- Linux host: Fixed issue which caused VM Selector process crash due to missing libdl.so and libpthread.so libraries (bug #22193)
- Linux host: Removed libIDL as a build time dependency when building VirtualBox from source code (bug #21169)
- Linux guest and host: Added initial support for kernel 6.15 (bug #22420)
- Linux guest: Added initial support for kernel 6.16-RC0
- Linux guest and host: Fixed issue with building modules for UEK8 kernel on Oracle Linux 9 distribution
- RDP: Fixed issue when it was not possible to paste clipboard buffer into a guest over RDP remote session

**VirtualBox 7.1.8** (released April 15 2025)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when VM clock went backwards in rare circumstances (bug #22334)
- GUI: Fixed issue when accelerated cursor image was not displayed correctly (bug #22096)
- DevVirtioSCSI: Fixed issue with restoring saved state
- Graphics: Fixed issue when assertion was triggered on restoring VM state if VMSVGA graphics adapter was used without 3D acceleration (bug #21955)
- Main: Fixed issue when VBoxSVC was crashing on saving machine config through VirtualBox web service (bug #22259)
- Main: Fixed issue when wireless network adapters could not be discovered on modern Linux distributions (bug #22362)
- Main: Fixed issue when deleting running VM snapshot was leaving the.sav file on disk (bug #21345)
- NAT: Fixed connectivity loss on Windows host (bug #22364)
- VBoxManage: Updated User Manual to correct the 'VBoxManage modifyvm' invocation for configuring a VM to use host-only networking (bug #22158)
- VBoxManage: Fixed issue when it was not possible to set disk bandwidth with 'VBoxManage bandwidthctl' command (bug #22328)
- Windows installer: Automatically load the support driver after a successful installation (bug #22292)
- Linux Host Installer: Fixed issue which sometimes resulted in installation failure due to incorrect check whether previous VirtualBox installation is running or not
- Linux Guest Additions: Fixed issue when VBoxClient could crash in XWayland guest (bug #22345)
- Linux Guest Additions: Fixed issue which resulted in cursor image corruption when VM was using VBoxVGA graphics adapter
- Linux Guest Additions: Fixed issue when installation could fail on the system which does not have X11 libraries installed
- Linux Guest Additions: Added initial support for kernel 6.14
- Linux Guest Additions: Introduced initial support for RHEL 9.7 kernel
- Linux Guest Additions: Introduced additional fixes for RHEL 9.4 kernel, (bug #22277)
- Linux Guest Additions: Improved 'rcvboxadd status-kernel' check
- Windows installer: Various bugfixes for the new installation code
- Windows installer: Implemented a new fatal error dialog with the ability to open the installer log file directly
- Windows Guest Additions: Fixed mouse driver installation on Vista guests
- Windows Guest Additions: Fixed uninstallation integrity issues (bug #22290)
- Windows Guest Additions: Fixed driver installation error ERROR\_AUTHENTICODE\_TRUST\_NOT\_ESTABLISHED (bug #22300)
- Windows Guest Additions: Fixed 100% CPU usage of VBoxTray which happened under certain circumstances (bug #22123)
- Windows Guest Additions: Now also ships the VBoxAudioTest binary for performing guest audio testing / diagnosis
- Windows Guest Additions: For older Windows versions (Windows 2000 to Windows 7) install alternative Shared Folder driver which avoids some compatibility glitches of the usual driver

**VirtualBox 7.1.6** (released January 21 2025)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when Windows 11 24H2 guest was experiencing BSOD in rare conditions
- GUI: Improved representation of disabled preferences contents (mask+font) when it is shown with certain Linux themes
- GUI: Fixed issue when seamless mode was not properly enabled or disabled in appropriate time according to GA status events
- GUI: Fixed rare crash on macOS hosts on application exit
- GUI: Fixed small 7.1.4 regression in preferences windows when filter editor was not in focus
- GUI: Introduced improvements in Advanced properties/settings dialog area
- GUI: Restored missing functionality to change bridged adapter at VM startup if current one wasn't found
- GUI: Fixed issue when Show action duplicates were created on macOS host in attempt to switch between running and powered off VMs
- GUI: Fixed regression when 3D acceleration check-box was not available for certain guest OS and graphical controller types
- GUI: Restored lost Help button for preferences windows on macOS
- GUI: Restored lost Help button shortcuts for certain windows
- GUI: Fixed issue when error message was shown when VM was starting in full-screen mode
- VirtioNet: Fixed issue with re-negotiation of features after reset
- Graphics: Fixed issue with Linux guest screen flickering when guest was using VMSVGA graphics adapter
- VBoxManage: Added the ability to export and import VMs which contain an NVMe storage controller
- VBoxManage: Fixed issue when it was not possible to set graphics controller to "QemuRamFB" using modifyvm command (bug #22232)
- Main: Fixed issue when specifying custom proxy server in GUI settings had no effect
- Network: Added changes which replaced NAT engines with libslirp
- Guest OSes: Added OS type for Windows Server 2025
- Linux guest and host: Added more fixes for UBSAN related warnings (bug #21877)
- Linux guest and host: Added initial support for RHEL 9.6 kernel
- Windows guests and host: Re-implemented driver installation
- Solaris host: Removed the VirtualBox GUI shared objects libqgtk2styleVBox.so and libqgtk2VBox.so from the Solaris installation packages as they depend on GTK2 which is EOL and no longer supported
- Linux Guest Additions: Introduced initial support for kernel 6.13
- Linux Guest Additions: vboxvideo: Added improvement for kernel 6.4 support and fixed issue when graphics could be frozen when using VBoxVGA adapter
- Linux Guest Additions: Introduced additional fixes for kernel 6.12 in vboxvideo

**VirtualBox 7.1.4** (released October 15 2024)  

This is a maintenance release. The following items were fixed or added:

- GUI: Added latest NLS update for Turkish, Indonesian and Italian languages
- VMSVGA: Improved flickering, black screen and other screen update issues with recent Linux kernels (bug #21955)
- NAT: Fixed issue with restoring 7.0.X saved state
- VBoxManage: Fixed breakage of "list vms" and "showvminfo" for inaccessible VMs
- Windows host: Fixed system DLL size checking which failed with Windows 11 24H2 and recent Insider Preview builds (bug #22162)
- Linux Guest Additions: Introduce initial support for kernel 6.12 (NOTE: In kernel 6.12, KVM initializes virtualization on module loading by default. This prevents VirtualBox VMs from starting. In order to avoid this, either add "kvm.enable\_virt\_at\_load=0" parameter into kernel command line or unload corresponding kvm\_XXX module)
- Linux/Arm Guest Additions: Added possibility to automatically upgrade Guest Additions via Devices menu
- EFI: Added missing LsiLogic MPT SCSI driver again to fix booting from devices attached to this device if the EFI firmware is used (7.1.0 regression)
- EFI: Restored broken network boot support (7.1.0 regression)

**VirtualBox 7.1.2** (released September 26 2024)  

This is a maintenance release. The following items were fixed or added:

- GUI: Added multiple window layout and translation related fixes
- GUI: Fixed an issue that meant VMs created using Unattended Install were not removed cleanly
- GUI: Added an option to change the remote display security method
- GUI: Removed the BETA label from the macOS/Arm UI
- NAT: Fixed slow performance on Windows host (bugs #22164 and #22180)
- NAT: Fixed DHCP problems with certain guests when domain is empty
- 3D: Fixed enabling 3D acceleration in the VM settings
- 3D: Fixed black screen with Windows VMs
- 3D: Fixed rendering issues caused by incorrect view handling
- 3D: Added possibility to enable 3D acceleration function for Arm platform VMs
- GCM: Fixed problem with loading saved state created by 7.0.x
- API: Fixed an issue with incorrect handling of NVRAM state with legacy BIOS and its removal on VM deletion
- API: Fixed UEFI Secure Boot state querying when the VM was never started
- Guest Additions: Fixed error message on automatic upgrading
- SDK: Fixed building code using the XPCOM bindings (bug #22174)

**VirtualBox 7.1.0** (released September 09 2024)  

This is a major update. The following new features were added:

- GUI: Modernized look and feel, offering a selection between Basic and Experienced user level with reduced or full UI functionality
- OCI Integration: Performance dashboard now shows resource usage for cloud VMs
- OCI Integration: Clone compute instances
- OCI Integration: Reset compute instances
- Oracle VirtualBox Extension Pack: Update to the PUEL license, removing the evaluation option. For evaluation use of the Extension Pack, please download it from the Oracle Software Delivery Cloud
- VRDE: If user does not set up TLS with custom certificates, enable it with self-signed certificate, including issuing a new one before the old one expires
- NAT: New engine with IPv6 support
- macOS/Arm host: Arm virtualization for Linux and BSD VMs
- Linux host and guest: Added Wayland support for Clipboard sharing (bug )
- Shared Clipboard: Added initial support for transferring files on Linux and Windows hosts / guests. This requires the 7.1 Guest Additions to be installed. See User Guide for known limitations
- Screen Recording: Significant performance improvements for the encoding pipeline, resulting in less CPU usage while recording is active. This requires 7.1 Guest Additions to be installed on Windows guests

In addition, the following items were fixed or added:

- VMM: Fixed EFLAGS.TF handling for CPUID instructions when Hyper-V is being used (bug #17961)
- virtio-net: Follow up fixes for FreeBSD 12.3 and pfSense 2.6.0 (bug #21201)
- EFI: Ability to add new Microsoft DB/KEX certificates to newly created VMs
- Oracle Extension Pack: Fixed shipping the cryptographic support module for full VM encryption
- GUI: Improved overall accessibility
- GUI: Update the version of Qt used
- Unattended Installation: Added support for subiquity- / cloud-init-based installers; this enables installing more modern Linux-based guest OSes in Unattended mode
- Unattended Installation: Added support for specifying separate passwords for the user and admin / root accounts
- VBoxManage: Added ability to show and (re-)attach to a (video) recording progress of a VM
- VBoxManage: Added the ability to query the guest's mount points via a new "mount" Guest Control sub command. Requires at least 7.1 Guest Additions
- Python: Our API bindings for Python 2.x is now marked as being deprecated and will be removed in a future version. Please upgrade your code to use Python 3
- VBoxShell: Lots of smaller and bigger bugfixes + Python 3.x compatibility

Last modified 7 months ago Last modified on 04/22/2026 10:02:55 AM

**Note:** See TracWiki for help on using the wiki.
