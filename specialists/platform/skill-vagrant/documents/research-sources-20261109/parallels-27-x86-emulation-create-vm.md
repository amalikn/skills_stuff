<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://docs.parallels.com/landing/pdfm-ug/parallels-desktop-for-mac-27-users-guide/advanced-topics/working-with-virtual-machines/importing-and-running-x86_64-intel-virtual-machines-on-apple-silicon-macs/creating-a-new-x86_64-intel-virtual-machine-on-an-apple-silicon-mac
**Retrieved**: 2026-11-09 11:27 AEDT
**HTTP status**: 200 via all-scraper `md` (defuddle); the Parallels Desktop 26 URL redirected to the 27 guide

---


**Source:** [https://docs.parallels.com/landing/pdfm-ug/parallels-desktop-for-mac-27-users-guide/advanced-topics/working-with-virtual-machines/importing-and-running-x86_64-intel-virtual-machines-on-apple-silicon-macs/creating-a-new-x86_64-intel-virtual-machine-on-an-apple-silicon-mac](https://docs.parallels.com/landing/pdfm-ug/parallels-desktop-for-mac-27-users-guide/advanced-topics/working-with-virtual-machines/importing-and-running-x86_64-intel-virtual-machines-on-apple-silicon-macs/creating-a-new-x86_64-intel-virtual-machine-on-an-apple-silicon-mac)

---

For the complete documentation index, see llms.txt. This page is also available as Markdown.

Although it is not recommended, you can technically create an x86\_64 virtual machine directly on your Apple Silicon Mac without the use of an Intel Mac.

**Warning**: Creating a new x86\_64 virtual machine directly on an Apple Silicon Mac will take A LOT of time. Depending on the size of the image file, expect the process to take anything between 30 minutes (Windows 10 21H2 or Windows Server) and a couple of hours (Fedora 40).

**Note**: Only Windows 10 and Windows Server 2022 x86\_64 distributives are supported for direct installation on Apple Silicon Macs using Parallels emulation. Starting from version 20.4.0, creating new Windows 10 22H2 and Windows Server 2019 machines is also supported. If you encounter any issues, refer to the Troubleshooting section of this KB article.

Installing Linux distros may present many challenges, including, but not limited to, Parallels Tools for Linux failing to install on newly created Linux virtual machines. We will continue to update the KB article linked above with more details as we test more distros.

Follow these steps:

1. Download an x86\_64 ISO image of a compatible operating system. A Windows 10 ISO can be found here.
2. Launch the macOS Terminal and execute the following commands: > *prlctl create <vm\_name> -d \<distro> --cpu-type x86* *\> prlctl set <vm\_name> --device-set cdrom0 --image <x86\_iso\_path> --connect* *\> prlctl start <vm\_name>* ***Note****: For a full list of possible options for \<distro> variable, run the following command in Terminal and pick the one matching your operating system:*
	\> *prlctl create <vm\_name>-d -list* *For Windows 10, the value of \<distro> is* `*win-10*`*.*

3. Follow on-screen instructions to proceed with the installation of the operating system.

For the latest compatibility updates and troubleshooting information, refer to this KB article.
