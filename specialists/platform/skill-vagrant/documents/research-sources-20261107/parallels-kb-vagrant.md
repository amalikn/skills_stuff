<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://kb.parallels.com/en/122843
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://kb.parallels.com/en/122843:
# KB Parallels: How to use Vagrant with Parallels Desktop

This article only briefly explains how to set up Vagrant to work with Parallels Desktop. For more information and documentation, please visit [Parallels + Vagrant website](http://parallels.github.io/vagrant-parallels/docs/).

---

**Note**: Vagrant plugin is available in Parallels Desktop Pro and Business Editions only.

---

Starting with Parallels Desktop 18.3.0, you can create a macOS virtual machine box with Vagrant and Parallels Desktop. Full instructions are available here: [KB 129720](https://kb.parallels.com/en/129720).

First, make sure that you have [Parallels Desktop for Mac Pro or Business Edition](https://kb.parallels.com/123279) and [Vagrant](https://www.vagrantup.com/downloads.html) properly installed.

After installing Vagrant, install and update **Parallels plugin** for **Vagrant**.

1. Start **Terminal** and execute:

   ```
   vagrant plugin install vagrant-parallels
   ```

   **NOTE:** the command above will download and install the latest version of **Parallels plugin** for **Vagrant**. If you believe your current version of plugin needs to be updated, please use the following command:

   ```
   vagrant plugin update vagrant-parallels
   ```

   **NOTE:** You may receive an error message stating that **json** is not installed, or that Xcode EULA is not agreed. Proceed with instructions written in the error message.
2. Now create a directory where you would like to store Vagrant boxes:

   ```
   mkdir new_vagrant_project
   cd new_vagrant_project
   ```
3. Now initialize Vagrant environment (we recommend using boxes prepared by the Bento community project) :

   If you are using an **Intel Mac**:

   ```
   vagrant init bento/ubuntu-22.10
   ```

   If you are using an **M-series Mac**:

   ```
   vagrant init bento/ubuntu-22.04-arm64
   ```
4. Create and run a virtual machine:

   ```
   vagrant up
   ```

The Parallels provider has a higher priority than any other provider built into Vagrant. Parallels provider will be used by default for your Vagrant virtual machines.

If you are using multiple Vagrant providers simultaneously and want to run your virtual machine with another provider, please read the general [basic usage](http://docs.vagrantup.com/v2/providers/basic_usage.html) page for providers.

In order to **set up a new project**, please check [Getting Started page](http://parallels.github.io/vagrant-parallels/docs/getting-started.html).

For **configuration**, please check [this webpage](http://parallels.github.io/vagrant-parallels/docs/configuration.html).

Use [this page](http://parallels.github.io/vagrant-parallels/docs/networking/index.html) for **networking**.
