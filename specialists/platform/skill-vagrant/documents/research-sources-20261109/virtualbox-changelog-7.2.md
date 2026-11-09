<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://www.virtualbox.org/wiki/Changelog-7.2
**Retrieved**: 2026-11-09 11:33 AEDT
**HTTP status**: rc 0 via all-scraper `md`

---


**Source:** [https://www.virtualbox.org/wiki/Changelog-7.2](https://www.virtualbox.org/wiki/Changelog-7.2)

---

# Page Structure Map
```text
Changelog-7.2     – Oracle VirtualBox
└── Changelog for VirtualBox 7.2
```

---

## Changelog for VirtualBox 7.2

This page lists all changes of the VirtualBox 7.2 **releases**.  
All branches: 7.2 · 7.1 · 7.0 · 6.1 · 6.0 · 5.2 · 5.1 · 5.0 · 4.3 · 4.2 · 4.1 · 4.0

**VirtualBox 7.2.22** (released October 20 2026)  

This is a maintenance release with security-related fixes.  

**VirtualBox 7.2.20** (released September 22 2026)  

This is a maintenance release. The following items were fixed or added:

- Windows Host: Fixed regression causing VMs to fail with VERR\_SUP\_VP\_FOUND\_EXEC\_MEMORY (github:gh-870)

**VirtualBox 7.2.18** (released September 15 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed Windows 11 on ARM guests crashing with a blue screen after restoring from a saved state
- GUI: Fixed German and Traditional Chinese translations (github:gh-847, github:gh-809)
- Storage: Fixed data corruption in VDI differencing images after writing full blocks of zeroes and reopening the image (github:gh-850)
- Graphics: Fixed a VM process crash that could occur on Linux hosts with 3D acceleration enabled (github:gh-829)
- Shared Clipboard: Fixed the first character being removed from filenames when copying files located directly in a filesystem root
- Linux Host: Fixed builds across the RHEL 9.8 file-open API transition (github:gh-830)
- Linux Host: Fixed builds for AMD systems where FRED is not available (Intel KVM only, github:gh-784, github:gh-835)
- Linux Host: Fixed issues with Kernel 7.3 compilation
- Linux Host: Preserved the shared DKMS directory during uninstallation (github:gh-826)
- Linux Host and Guest: Added support for RHEL 10.3 kernel (github:gh-833)
- Linux Guest: Fixed builds for kernel 6.12.103 (github:gh-845)

**VirtualBox 7.2.16** (released August 18 2026)  

This is a maintenance release. The following items were fixed or added:

- GUI: Updated Catalan translations
- GUI: Fixed OVF import warning visibility
- GUI: Added graceful handling of inaccessible VMs
- Graphics: VMSVGA 3D performance improvements
- Video Recording: Fixed a hang when stopping recording after a large number of display updates
- Host: OpenSSL 4.0 build fixes (github:gh-794)
- Linux Host: Support for FRED (github:gh-784)
- Linux Host and Guest: Improvements in shared clipboard handling in Wayland
- Linux Guest: Fixed support for RHEL 9.8 kernels (github:gh-732, github:gh-771)

**VirtualBox 7.2.14** (released July 21 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Avoided querying/setting xcr0 for CPUs without xsave feature when using Windows Hyper-V as the virtualization engine
- Windows installer: Added support for detecting the Visual C++ runtime via the servicing infrastructure (github:gh-723)
- Windows Host: Fixed clipboard handling of Unicode formats (github:gh-677)
- Linux Host: Added initial support for kernel 7.2
- Linux Guest: Fixed support for updated RHEL 9.8 and 9.9 kernels
- UEFI: Fixed possible bug check and reboot of Windows 11 when updating Secure Boot DBX entries
- BIOS: Simplified build prerequisites, NASM 2.16 or later is now usable for everything (github:gh-520)

**VirtualBox 7.2.12** (released June 30 2026)  

This is a maintenance release. The following items were fixed or added:

- Windows Guest: Added DX11 performance improvements and fixes
- Linux Host: Fixed kernel panic (github:gh-711, github:gh-712)
- Linux Host and Guest: Fixed various NASM build issues (github:gh-520)

**VirtualBox 7.2.10** (released June 16 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when CentOS 10 VM was not booting due to the message "Fatal glibc error: CPU does not support x86-64-v3" (github:gh-642)
- Devices/EFI: Fixed booting issue when ARM VM had less than 1024 MiB of RAM assigned (github:gh-679)
- USB: Fixed issue when it was not possible to attach USB device to headless VM on Apple Silicon/macOS 26.4.1 (github:gh-631)
- Storage: Fixed issue when VIRTIO-SCSI device was not recognized as SSD device by guest system (github:gh-634)
- Network: Fixed issue in E1000 emulation code which triggered debug log creation (github:gh-645)
- Network: Fixed issue in E1000 emulation code which prevented OS/2 guest from booting (github:gh-683)
- Linux Host: Fixed issue when VMs could not be started due to kernel oops (github:gh-639)
- Linux Host and Guest: Fixed issue when kernel modules were failing to build with openSUSE 16.0 kernel
- Linux Host and Guest: Added initial support for kernel 7.1
- Linux Host and Guest: Added extra fixes for RHEL 9.8 kernel (github:gh-676)
- Linux Host and Guest: Added possibility to build source code using NASM instead of YASM as the assembler (github:gh-520)
- Linux Guest Additions: Added initial support for Extended Data Control Protocol for clipboard sharing with Plasma on Wayland guests (github:gh-33)
- Linux Guest Additions: Added extra fixes for preventing vboxvideo kernel module build with kernel version 7.0 and newer (github:gh-655)
- OS/2 Guest Additions: Fixed issue when Shared Folders automount and clipboard sharing stopped working (github:gh-551)

**VirtualBox 7.2.8** (released April 21 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue which caused a Guru Meditation with VERR\_IEM\_IPE\_4 if the guest was trying to execute the wrong hypercall instruction but injected a UD exception instead (github:gh-616)
- NAT Network: Fixed issue when internal DNS server could not be reached
- Graphics: Fixed issue when mouse cursor did not change shape by context in Ubuntu 25.10 / Wayland (github:gh-464)
- Main: Fixed crash on FreeBSD 16.0 shutdown with multiple devices attached to LSI Logic SAS controller (github:gh-538)
- IPRT: Merged Github pull request 503 (fix: infinite loop in vsscanf whitespace processing). github-merge-author: lachlanharrisdev
- Unattended: General improvements
- Linux Host: Added initial support for kernels 6.19 and 7.0 (github:gh-467, github:gh-623)
- Linux Host: Added support for guest time accounting (github:gh-2)
- Linux Host and Guest: Introduced additional fixes for RHEL 10.1 and 10.2 kernels (github:gh-455)
- Linux Host and Guest: Added support for UEK9 kernel on Oracle Linux 9
- Linux Host and Guest: Added improvements to make 'rcvboxdrv/rcvboxadd setup' and installation process faster
- Linux Guest Additions: Deprecated vboxvideo kernel module for kernels 7.0 and newer; please consider using VMSVGA graphics or vboxvideo module which comes with Linux kernel or provided by your Linux distribution if guest running kernel 7.0+; vboxvideo will still be available for older kernels
- Linux Guest Additions: Fixed issue when clipboard sharing was not possible in combination of Wayland guest and Windows host (github:gh-33)
- Linux Guest Additions: Fixed issue when last character was not pasted into Windows host clipboard when copying from Wayland guest (bug:22339)
- Windows Guest: Fixed issue when Windows 11 guest experienced BSOD - DRIVER\_OVERRAN\_STACK\_BUFFER (github:gh-590)
- UEFI: Fixed errors with secure boot certificate updates and Windows 11 guests (github:gh-133)
- DMI: Fixed issue when 0.0 value was provided for the BIOS release and BIOS firmware version numbers so Windows did not populate the registry keys under HKLM\\HARDWARE\\System\\BIOS which some components rely on (bug:21943)

**VirtualBox 7.2.6** (released January 20 2026)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when VM process was crashing during RHEL5 guest boot
- VMM: Fixed issue when VMX nested-guest VM-entry was checking the wrong VM-execution control bit in the virtual VMCS (github:gh-313)
- VMM: Fixed issue when VM was crashing on start after recent Windows update (KB5066793) (github:gh-360)
- VMM: Fixed issue when guest process was crashing inside Windows guest on AMD system (github:gh-400)
- VMM: Fixed issue when VM process was crashing on Windows host (github:gh-426, github:gh-407, github:gh-404, github:gh-369, github:gh-238, github:gh-207, github:gh-187, github:gh-178)
- VMM: Fixed Guru Meditation issue on VM start on Windows host (github:gh-346)
- VMM: Fixed issue when VM was failing to shut down on Windows 11 ARM host (github:gh-416)
- VMM: Fixed issue when booting Red Hat 6.1 i386 was failing on AMD Zen4 Windows 11 Pro host (github:gh-466)
- GUI: Added fixes for full-screen support in multi-monitor case (github:gh-197, github:gh-243)
- GUI: Fixed issue when downloading update files was failing (github:gh-327, github:gh-372)
- GUI: Fixed issue when list of VMs was not properly displayed in Resource Manager tab (github:gh-364)
- GUI: Fixed issue when with switching between light/dark modes on macOS host (github:gh-457)
- GUI: Fixed issue when storage controller type list was displayed incorrectly (github:gh-413)
- DevACPI: Fixed issue with file path key names for Dsdt/Ssdt (github:gh-381)
- DevACPI: Added change to make OemTabId configurable using AcpiOemTabId option (github:gh-383)
- NAT: Fixed issue with high CPU usage when VM was using NAT (github:gh-356)
- RDP: The VRDP server was moved to the open source base package
- SmartCard: The USB smartcard emulation was moved to the open source base package
- VM encryption: The disk and VM encryption feature was moved to the open source base package
- VBoxManage: Fixed issue when VBoxManage was not displaying interface name for FreeBSD guests (github:gh-403)
- VBoxManage: Fixed issue when VM could not be started from command line in some circumstances (github:gh-418)
- Main: Improved filename check for drag-and-drop operations (github:gh-68)
- Linux Host: Fixed issue when vboxautostart-service did not start corresponding VMs on system boot (github:gh-309)
- Linux Host: Fixed issue when VM was not able to start if host was running realtime kernel configuration (github:gh-332)
- Guest Additions: Fixed installation on Windows XP 64-bit guests (github:gh-142)
- Guest Additions: Fixed issue when guest process was crashing due to low memory in the system (github:gh-410)
- Linux Guest Additions: Fixed build issue for kernels 2.5.52 and older
- Linux Guest Additions: Fixed issue when VBoxService was not started due to abandoned pid file
- Linux Guest Additions: Fixed issue when user session services were not started on old Linux distributions
- Linux Guest Additions: Fixed check if kernel modules were loaded for old Linux distributions
- Linux Guest Additions: Fixed issue when Guest Additions processes were left running on system reboot or shutdown (github:gh-311)
- Linux Guest Additions: Added additional fixes for RHEL 9.8, 10.1 and 10.2 kernels
- Linux Guest Additions: Added initial support for kernel 6.19 (github:gh-467)
- BIOS: Fixed issue with booting VM using IPXE (github:gh-417)

**VirtualBox 7.2.4** (released October 21 2025)  

This is a maintenance release. The following items were fixed or added:

- GUI: Fixed VirtualBox VM Manager crash when host was resuming from sleep (github:gh-121, github:gh-170)
- GUI: Updated native language support for Traditional Chinese, Greek, Swedish, Hungarian and Indonesian translations
- NAT: Fixed issue when multiple port forwarding rules affected NAT functionality (github:gh-232)
- Linux host and guest: Introduced initial support for kernel 6.18
- Linux Guest Additions: Introduced additional fixes for RHEL 9.6 and 9.7 kernels (github:gh-12)
- Windows Guest Additions: Introduced additional fixes for issue when installation was failing in Windows XP SP2 guest (github:gh-142)

**VirtualBox 7.2.2** (released September 10 2025)  

This is a maintenance release. The following items were fixed or added:

- VMM: Fixed issue when VM was not able to start on Windows Arm host (issue github:gh-8)
- GUI: Fixed VBox Manager crash when some VM has a lot of snapshots (issue github:gh-119)
- GUI: Fixed issue when error notifications could not be displayed on snapshot deletion (issue github:gh-75)
- GUI: Fixed VBox Manager crash while attempting to show error notifications too early (issues github:gh-135 and github:gh-171)
- GUI: Fixed VBox Manager crash while removing all VMs from VM list
- GUI: Fixed VBox Manager freeze on Linux hosts at startup or while attempting to add a VM (issues github:gh-70 and github:gh-168)
- GUI: Fixed VBox Manager layout bug with too strict size constraints (issue github:gh-87)
- GUI: Updated VBox VM network status-bar indicator tooltip (IP address) on guest additions change (issue github:gh-179)
- GUI: Added possibility for Windows 11 host to use legacy light/dark themes from Windows 10 (issues github:gh-137 and github:gh-151)
- GUI: Forcing xdgdesktopportal platform theme on Linux when org.freedesktop.portal.Desktop DBus service is available (issues github:gh-138 and github:gh-150)
- Network (NAT, DNS): Fixed potential issue where a nameserver in the 127/8 network could have been passed to the guest (issue github:gh-136)
- Network: Added a new experimental type of e1000 adapter (82583V). It requires the ICH9 chipset, since MSIs are not supported by PIIX3
- USB: Fixed passing through USB devices exposed over USB/IP (issue github:gh-192)
- USB Webcam: The virtual USB webcam is now part of the open source base package
- Arm host: Improved high CPU usage for idling VMs (issue github:gh-34)
- Linux host: Use KVM APIs on kernel 6.16.0 and newer for acquiring/releasing VT-x (issue github:gh-81, github:gh-139 and github:gh-141)
- macOS host: Fixed internal networking, including NAT networks on macOS (7.2.0 regression; issue github:gh-140)
- macOS host: Fixed VM crash on Arm host on VM start (issue github:gh-101)
- Linux Guest Additions: Fixed issue when VBoxClient was reporting it's unable to load shared libraries on start (issue github:gh-165)
- Windows Guest Additions: Fixed issue when installation was failing on Windows XP SP2 64-bit (issue github:gh-142)
- EFI: Fixed TPM device not working with certain guests (issue github:gh-143)

**VirtualBox 7.2.0** (released August 14 2025)  

This is a major update. The following new features were added:

- GUI: Moved global and VM tools from hamburger menus to global tools taskbar (vertically on the left) and the VM tools tabs (horizontally above the right hand panel) to make them easier to reach
- Windows/Arm host: Arm virtualization of VMs added, in the unified Windows installer package
- Arm host: Virtualization of Windows 11/Arm VMs
- Linux host: Video decoding acceleration when 3D is enabled
- Windows/Arm guest: Guest additions for new OS type Windows 11/Arm
- macOS Arm host: Experimental 3D acceleration support using DXMT, removing the previous non working solution using DXVK on top of MoltenVK. 3D acceleration is not supported on macOS hosts using Intel CPUs anymore.
- Storage: The NVMe storage controller emulation is now part of the open source base package

In addition, the following items were fixed or added:

- Arm VMs: Note that the saved state of Arm VMs from VirtualBox 7.1 is incompatible with VirtualBox 7.2, so please shut down such VMs in saved state before upgrading to 7.2 (snapshots with associated saved state created with 7.1 will no longer work with 7.2)
- VMM: Improved x86\_64 and Arm CPU feature reporting when using Windows Hyper-V as the virtualization engine
- VMM: Added xsave/xrestor instruction handling when using Windows/x86\_64 Hyper-V as the virtualization engine, offering the x86\_64-v3 instruction set extensions (including AVX and AVX2) on recent CPUs
- VMM: Fixed issue when X86\_64-v3 features were not passed to the guest (github:gh-36)
- VMM/HM: Fixed Nested Virtualization feature on Intel CPUs
- GUI: Fixed a bug in clone VM wizard which made impossible to include snapshots in clone result (github:gh-59)
- GUI: Polished Preferences and Settings pages, NLS fixing
- GUI: Improved handling of keyboard LEDs in the Soft Keyboard
- GUI: Added checkbox for making a Shared Folder global to all VMs
- GUI: Removed IO-APIC from Arm VM settings
- Graphics: Avoid assertion when guest tries to use VMSVGA 3D functions when the feature is disabled
- Audio: Fixed crash in rare circumstances (github:gh-72)
- NAT: Multiple fixes and improvements, for example better DNS server handling, saving of the VM settings and generating a boot file name which stays within the length limit
- NAT Network: Use the (almost) same code as for NAT, unifying behavior and features
- NAT: Fixed possible crash in rare circumstances when no nameservers could be detected in the host system
- Storage: Fixed corruption of VMDK images when resizing
- Video Recording: Fixed frame synchronization, a small memory leak and other bugs
- TPM: Fixed save state load failures
- Arm VMs: ACPI now available
- API/Unattended: Added explicit unattended installation support for Oracle Linux 10
- API and VBoxManage: Added functionality to define global Shared Folders for all VMs
- API: Fixed issue when OVF/OVA import resulted in a broken VM on Arm (bug #22370)
- API: Fixed issue when exporting a VM which had an inaccessible disk resulted in crash
- VBoxManage: Document currently unavailable NAT options
- Linux host and guest: Initial support for kernel version 6.16
- Linux/Solaris host: Fixed swapped scan code for Pause and Num Lock keys in the table used when relying on Xkb for translation
- Windows host: Removed release assertion causing crash of VBoxUsbMon driver if unloading fails
- Arm host: vboxwebsrv is now included in the packages
- Linux host and guest: Introduced initial support for kernel 6.17
- Linux guest: Fixed handling of (long optional) vboxvideo kernel module in init script
- Linux guest: Fixed start failure of VBoxClient with kernel from the 2.6 series or older
- Windows/Arm guest: Added WDDM Graphics driver, with 2D and 3D mode
- Windows/Arm guest: Added Shared Folder feature
- Windows Host: Added improvements in Windows drivers installation
- Linux Guest Additions: Fixed issue when autorun installer was not automatically starting on Additions ISO image insert for Oracle Linux 10 and RHEL 10 guests
- BIOS: Fixed keyboard translation, added and updated several entries and do not report keypresses when scan code and ASCII code are both zero
- BIOS: Fixed error reporting fo single sided floppy disks
- UEFI: Added workaround for Grub bug causing guest OS crashes
- UEFI: Fixed macOS kernel logging over serial port (github:gh-82)
- 3rd Party Tools: Eliminated build time dependency on libIDL and IASL

Last modified 15 months ago Last modified on 08/14/2025 03:33:54 PM

**Note:** See TracWiki for help on using the wiki.
