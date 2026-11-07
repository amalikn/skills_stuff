<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/483
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #483 prl_fs filesystem not found with latest parallels version (20.2.0)

State: CLOSED; opened 2025-01-27T22:58:25Z; closed 2025-02-26T07:08:41Z

## Body

Vagrant version 2.4.3. vagrant-parallels version 2.4.2. Mac M3 Pro.

```
==> default: Mounting shared folders...
    default: /.../vm/hosted => /vagrant
Vagrant was unable to mount Parallels Desktop shared folders. This is usually
because the filesystem "prl_fs" is not available. This filesystem is
made available via the Parallels Tools and kernel module.
Please verify that these guest tools are properly installed in the
guest. This is not a bug in Vagrant and is usually caused by a faulty
Vagrant box. For context, the command attempted was:

mount -t prl_fs -o uid=1000,gid=1000,_netdev vagrant /vagrant

The error output from the command was:

mount: /vagrant: unknown filesystem type 'prl_fs'.
```

I don't specify the file system type in the Vagrantfile:
```
# -*- mode: ruby -*-
# vi: set ft=ruby :

BOX = "hosted"
NAME = "hosted"
MEMORY = 12288
CPUS = 2

Vagrant.require_version ">= 2.4.1"

Vagrant.configure(2) do |config|

  # To register a box file with vagrant, run:
  # vagrant add box dev dev-parallels-desktop-arm64.box

  config.vm.box = BOX
  config.vm.hostname = NAME

  config.ssh.forward_agent = true

  config.vm.synced_folder "~/git", "/host/home/git"

  config.vm.provider :parallels do |vm, override|
    vm.name = NAME
    vm.linked_clone = false
    vm.memory = MEMORY
    vm.cpus = CPUS
    vm.customize ["set", :id, "--on-window-close", "keep-running"]
    vm.customize ["set", :id, "--startup-view", "headless"]
    # vm.update_guest_tools = true
  end

  config.vm.provider :virtualbox do |vm, override|
    vm.name = NAME
    vm.linked_clone = false
    vm.memory = MEMORY
    vm.cpus = CPUS
    vm.customize ["modifyvm", :id, "--vram", 256]
    vm.gui = false
  end

end
```

## Comment by BodoHuber at 2025-01-28T18:07:57Z

Same problem here with me using Parallels Version 20.2.0 (55872) on Mac OS 15.2 running on ARM Mx silicon trying to `vagrant up` my Ubuntu 22.0.4 ARM64 VM.  I get the same error telling that the filesystem 'prl_fs' is not found when vagrant tries to run the `mount` command.  

**After fixing** the installation package of the parallels-tools (the prl-tools-lin-arm.iso) of that Parallels version has a missing closing " in the file dkms.conf as part of the packed prl_mod.tar.gz) **the installation runs without errors**.  **Without that fix the installation of parallels-tools fails in my setup**.  See here for instructions to manually re-install the parallels-tools: [https://kb.parallels.com/en/129740](https://kb.parallels.com/en/129740)

If I manually start my existing Ubuntu 22.04.4 ARM64VM which I updated to the new version of Parallels and where I re-installed the parallels-tools after the missing " fix, I can see all my shares mounted to `/media/psf/...` and they work.  After checking some mounting status (`less /etc/mtab` and `ps ax | grep prl_fsd`) I see that those shares are mounted using a FUSE filesystem.  'prl_fs' is not listed in the available filesystems shown with `cat /proc/filesystems`.  

So, did Parallels switch to FUSE filesystem on Linux recently?  Is the vagrant-parallels mount command line using `-t prl_fs` deprecated then?  

I am just guessing here, I have no access to a previous version of Parallels.  But maybe someone can take advantage of this findings, maybe it is boring known stuff...  

## Comment by mpdude at 2025-01-29T17:50:10Z

To fix the Tools installation, attach the CD-ROM with Parallels Tools to the VM. Then:

```bash
$ sudo mount /dev/cdrom /mnt
$ cp -R /mnt prl-tools
$ cd prl-tools/kmods/
$ tar xzf prl_mod.tar.gz
$ patch
--- dkms.conf.orig	2025-01-29 16:28:49.324491015 +0000
+++ dkms.conf	2025-01-29 16:28:56.060555234 +0000
@@ -5,7 +5,7 @@
 # http://www.parallels.com


-MAKE="make -f Makefile.kmods KSRC=$kernel_source_dir KVER=$kernelver
+MAKE="make -f Makefile.kmods KSRC=$kernel_source_dir KVER=$kernelver"
 CLEAN="make -f Makefile.kmods clean"
 PACKAGE_NAME="parallels-tools"
 PACKAGE_VERSION="20.2.0.55872"
(press ctrl-D here)
$ tar czf prl_mod.tar.gz --exclude=prl_mod.tar.gz .
$ cd ..
$ sudo ./install
# To clean up:
$ cd ..
$ rm -rf prl-tools
```

But, as @BodoHuber outlined, that alone does not cut it since the `prl_fs` module is no longer there and filesystems seem to be mounted/shared in another way.

## Comment by mpdude at 2025-01-29T17:54:18Z

X-link https://forum.parallels.com/threads/filesystem-prl_fs-is-not-available-since-updating-to-20-2-0.366523/

## Comment by mpdude at 2025-01-29T18:54:16Z

For the time being, does anybody know where/how I can download PD version 20.1.3?

## Comment by BodoHuber at 2025-01-29T19:53:39Z

@mpdude thx for the command sequence above, that seems to do exactly what I did manually before.  

In the meantime I am sure that Parallels moved to fuse filesystem, but I don't know when this happened.  Unfortunately I can not figure out how to mount a share from commandline using fuse.prl_fsd.  If anybody knows how to do it, I am excited to learn about.  

Since you ask for 20.1.3 in particular: do you **know** that this version still uses 'prl_fs' filesystem?  Or is it a guess?  I am asking since the [version history](https://kb.parallels.com/en/130212) of Parallels mentions a move to high-level FUSE API with 20.0.0, so I wonder if any 20.x version will work with vagrant.  Even the forum link you mentioned above tells about downgrading to 19.  

## Comment by mpdude at 2025-01-29T20:17:52Z

You're right - it was just my unverified assumption that this happened in the latest minor release.

Unfortunately, I did not find any download sources for 20.1 or 20.0 versions. So, I will have to downgrade to v19 for the time being and hope that someone from Parallels will pick this up. I'd be glad to try workarounds or other if that helps.

## Comment by BodoHuber at 2025-01-29T20:33:19Z

Testing 20.1.3 right now found [here](https://parallels-desktop.sooftware.com/mac/download/401123).  Bitdefender did not find any issues, nor do I see any hint to fraud versions.  Anybody ever had problems with downloads from sooftware.com?  Sounds really suspicious, but I am carefully testing now.  

Good news is that 20.1.3 seems to have 'fuse.prl_fsd' AND 'prl_fs'...  Doing further tests now...

**PS: 20.1.3 works with vagrant because it still has 'prl_fs' !!!**

## Comment by mpdude at 2025-02-13T09:17:18Z

I have opened support ticket 5156867 with Parallels and hope that somebody from their company will help us here :-)

## Comment by bineesh-n at 2025-02-13T09:49:20Z

Hi Guys, sorry for the delay, we are checking this internally. 

## Comment by cjlapao at 2025-02-13T09:55:57Z

You can find the official download link here [Version 20.1.3-55743](https://download.parallels.com/desktop/v20/20.1.3-55743/ParallelsDesktop-20.1.3-55743.dmg)

## Comment by mpdude at 2025-02-17T15:27:07Z

@bineesh-n Do you have insight into your support tickets and could you check `[Parallels #5156867]`?

Do you really need me to send screenshots and a technical report for that? If now, maybe you could add an internal note that progress for this case does not depend upon that?

## Comment by BodoHuber at 2025-02-18T14:01:49Z

@bineesh-n From my perspective a vagrant-parallels specialist would need to replace the mounting and unmounting commands, the allowed share options and in addition the mtab-line which needs to be more fuse.prl_fsd aware.  With fuse.prl_fsd the commands look different than the mount and unmount commands we are used to.  

To mount a share vagrant-parallels would need to run something like `sudo prl_fsd -ofsname=_mtab-name_,gid=1000,uid=1000,subtype=prl_fsd _mountingpoint_`.  In my tests a `nonempty` option was required because the vagrant share was already mounted when a second mount happened.  But I do not know the vagrant-parallels plugin nor the whole vagrant project in detail to judge if this is a acceptable situation or if some unmount should happen before a second mount.  

To unmount a share vagrant-parallels would need to run something like `sudo fusermount -u _moutingpoint_`

## Comment by sai-kumar-peddireddy at 2025-02-20T11:03:10Z

@saml-caprx I tried to reproduce this issue 

it's not reproduced with Version Parallels **20.2.0 (55872) and 20.2.1 (55876)**
**Vagrant 2.4.3**
**Apple M2 Max**

### config I tested with 

```
# -*- mode: ruby -*-
# vi: set ft=ruby :

BOX = "bento/ubuntu-22.04"
NAME = "hosted"
MEMORY = 12288
CPUS = 2

Vagrant.require_version ">= 2.4.1"

Vagrant.configure(2) do |config|

  # To register a box file with vagrant, run:
  # vagrant add box dev dev-parallels-desktop-arm64.box

  config.vm.box = BOX
  # config.vm.box_version = "20250118.01"
  config.vm.hostname = NAME

  config.ssh.forward_agent = true

  config.vm.synced_folder "~/go", "/host/home/go"

  config.vm.provider :parallels do |vm, override|
    vm.name = NAME
    vm.linked_clone = false
    vm.memory = MEMORY
    vm.cpus = CPUS
    vm.customize ["set", :id, "--on-window-close", "keep-running"]
    vm.customize ["set", :id, "--startup-view", "headless"]
    # vm.update_guest_tools = true
  end

  config.vm.provider :virtualbox do |vm, override|
    vm.name = NAME
    vm.linked_clone = false
    vm.memory = MEMORY
    vm.cpus = CPUS
    vm.customize ["modifyvm", :id, "--vram", 256]
    vm.gui = false
  end

end
```

### Vagrant logs

Bringing machine 'default' up with 'parallels' provider...
==> default: Registering VM image from the base box 'bento/ubuntu-22.04'...
==> default: Creating new virtual machine as a full clone of the box image...
==> default: Unregistering the box VM image...
==> default: Setting the default configuration for VM...
==> default: Checking if box 'bento/ubuntu-22.04' version '202407.22.0' is up to date...
==> default: Setting the name of the VM: hosted
==> default: Preparing network interfaces based on configuration...
    default: Adapter 0: shared
==> default: Clearing any previously set network interfaces...
==> default: Running 'pre-boot' VM customizations...
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 10.211.55.140:22
    default: SSH username: vagrant
    default: SSH auth method: private key
    default: Warning: Connection refused. Retrying...
    default: 
    default: Vagrant insecure key detected. Vagrant will automatically replace
    default: this with a newly generated keypair for better security.
    default: 
    default: Inserting generated public key within guest...
    default: Removing insecure key from the guest if it's present...
    default: Key inserted! Disconnecting and reconnecting using new SSH key...
==> default: Machine booted and ready!
==> default: Checking for Parallels Tools installed on the VM...
==> default: Parallels Tools installed on this VM are outdated! In most cases
==> default: this is fine but in rare cases it can cause things such as shared
==> default: folders to not work properly. If you see shared folder errors,
==> default: please update Parallels Tools within the virtual machine and
==> default: reload your VM.
==> default: Setting hostname...
==> default: Mounting shared folders...
    default: /Users/Qa/Office/Repos/vagrant-test => /vagrant
    default: /Users/Qa/go => /host/home/go

### mount command log in the guest machine 

sysfs on /sys type sysfs (rw,nosuid,nodev,noexec,relatime)
proc on /proc type proc (rw,nosuid,nodev,noexec,relatime)
udev on /dev type devtmpfs (rw,nosuid,relatime,size=6041316k,nr_inodes=1510329,mode=755,inode64)
devpts on /dev/pts type devpts (rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000)
tmpfs on /run type tmpfs (rw,nosuid,nodev,noexec,relatime,size=1222728k,mode=755,inode64)
efivarfs on /sys/firmware/efi/efivars type efivarfs (rw,nosuid,nodev,noexec,relatime)
/dev/mapper/ubuntu--vg-ubuntu--lv on / type ext4 (rw,relatime)
securityfs on /sys/kernel/security type securityfs (rw,nosuid,nodev,noexec,relatime)
tmpfs on /dev/shm type tmpfs (rw,nosuid,nodev,inode64)
tmpfs on /run/lock type tmpfs (rw,nosuid,nodev,noexec,relatime,size=5120k,inode64)
cgroup2 on /sys/fs/cgroup type cgroup2 (rw,nosuid,nodev,noexec,relatime,nsdelegate,memory_recursiveprot)
pstore on /sys/fs/pstore type pstore (rw,nosuid,nodev,noexec,relatime)
bpf on /sys/fs/bpf type bpf (rw,nosuid,nodev,noexec,relatime,mode=700)
systemd-1 on /proc/sys/fs/binfmt_misc type autofs (rw,relatime,fd=29,pgrp=1,timeout=0,minproto=5,maxproto=5,direct,pipe_ino=18469)
mqueue on /dev/mqueue type mqueue (rw,nosuid,nodev,noexec,relatime)
hugetlbfs on /dev/hugepages type hugetlbfs (rw,relatime,pagesize=2M)
tracefs on /sys/kernel/tracing type tracefs (rw,nosuid,nodev,noexec,relatime)
debugfs on /sys/kernel/debug type debugfs (rw,nosuid,nodev,noexec,relatime)
fusectl on /sys/fs/fuse/connections type fusectl (rw,nosuid,nodev,noexec,relatime)
configfs on /sys/kernel/config type configfs (rw,nosuid,nodev,noexec,relatime)
none on /run/credentials/systemd-sysusers.service type ramfs (ro,nosuid,nodev,noexec,relatime,mode=700)
/var/lib/snapd/snaps/lxd_27038.snap on /snap/lxd/27038 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
/var/lib/snapd/snaps/core20_2186.snap on /snap/core20/2186 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
/var/lib/snapd/snaps/snapd_20674.snap on /snap/snapd/20674 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
/dev/sda2 on /boot type ext4 (rw,relatime)
/dev/sda1 on /boot/efi type vfat (rw,relatime,fmask=0022,dmask=0022,codepage=437,iocharset=iso8859-1,shortname=mixed,errors=remount-ro)
binfmt_misc on /proc/sys/fs/binfmt_misc type binfmt_misc (rw,nosuid,nodev,noexec,relatime)
tmpfs on /run/snapd/ns type tmpfs (rw,nosuid,nodev,noexec,relatime,size=1222728k,mode=755,inode64)
**host_home_go on /media/psf/host_home_go type prl_fs (rw,nosuid,nodev,noatime,sync,ttl=250,share)
vagrant on /media/psf/vagrant type prl_fs (rw,nosuid,nodev,noatime,sync,ttl=250,share)
vagrant on /vagrant type prl_fs (rw,relatime,sync,ttl=250,uid=1000,gid=1000,_netdev)
host_home_go on /host/home/go type prl_fs (rw,relatime,sync,ttl=250,uid=1000,gid=1000,_netdev)**
/var/lib/snapd/snaps/snapd_23546.snap on /snap/snapd/23546 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
/var/lib/snapd/snaps/core20_2499.snap on /snap/core20/2499 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
/var/lib/snapd/snaps/lxd_31335.snap on /snap/lxd/31335 type squashfs (ro,nodev,relatime,errors=continue,x-gdu.hide)
nsfs on /run/snapd/ns/lxd.mnt type nsfs (rw)
tmpfs on /run/user/1000 type tmpfs (rw,nosuid,nodev,relatime,size=1222728k,nr_inodes=305682,mode=700,uid=1000,gid=1000,inode64)







## Comment by bjoernhaeuser at 2025-02-20T11:05:24Z

You also need to install the latest parallels tools, only they do not provide the required `prl_fs`:

> ==> default: Checking for Parallels Tools installed on the VM...
==> default: Parallels Tools installed on this VM are outdated! In most cases
==> default: this is fine but in rare cases it can cause things such as shared
==> default: folders to not work properly. If you see shared folder errors,
==> default: please update Parallels Tools within the virtual machine and
==> default: reload your VM.


If you build the VM with the latest tools, the mounting does not work anymore. 

## Comment by sai-kumar-peddireddy at 2025-02-20T11:17:37Z

> You also need to install the latest parallels tools, only they do not provide the required `prl_fs`:
> 
> > ==> default: Checking for Parallels Tools installed on the VM...
> > ==> default: Parallels Tools installed on this VM are outdated! In most cases
> > ==> default: this is fine but in rare cases it can cause things such as shared
> > ==> default: folders to not work properly. If you see shared folder errors,
> > ==> default: please update Parallels Tools within the virtual machine and
> > ==> default: reload your VM.
> 
> If you build the VM with the latest tools, the mounting does not work anymore.

checking that 

## Comment by sai-kumar-peddireddy at 2025-02-20T13:38:53Z

@bjoernhaeuser I was able to reproduce this issue and soon, will give a fix

## Comment by amigrave at 2025-02-25T15:20:53Z

@sai-kumar-peddireddy could you provide some insight about why prl_fs was removed, and if it will be reintroduced ?

AFAIK using fuse won't work with some kernel's IO lowe level features (eg: nginx not being able to use sendfile). I've bought Parallels desktop because virtualbox broke this as well in the past and prl_fs allowed me to use such fstab options:

    XXX    /home/ubuntu/XXX    prl_fs    uid=YYYY,gid=ZZZZ,sync,nosuid,nodev,noatime,host_inodes    0 2

Also it seems that some users already have other issues as well:
https://forum.parallels.com/threads/parallels-20-hardlinks-not-supported-in-shared-folders.365235/

## Comment by WardF at 2025-02-25T16:01:45Z

My ability to test across versions is narrow, but within my own set of homebrew Vagrant boxes (and a handful I've downloaded and tested), the change I've posted in #487 appears to work. I won't be surprised at all if it can be further refined, but this is proving to be a pretty serious roadblock for my day-to-day workflow, and I suspect it may be for others as well.  

## Comment by amigrave at 2025-02-25T16:17:41Z

> this is proving to be a pretty serious roadblock for my day-to-day workflow, and I suspect it may be for others as well.

Indeed, I'm not even using vagrant and I'm impacted as well.
`prl_fs` is a requirement for my in-vm developpements, so I had to revert back to Parallel Desktop version 20.1.3

## Comment by WardF at 2025-02-25T17:48:03Z

> > this is proving to be a pretty serious roadblock for my day-to-day workflow, and I suspect it may be for others as well.
> 
> Indeed, I'm not even using vagrant and I'm impacted as well. `prl_fs` is a requirement for my in-vm developpements, so I had to revert back to Parallel Desktop version 20.1.3

I'll be curious if the decision to drop `prl_fs` was intentional or if it was an oversight; I'm an open-source system library dev and I've certainly made off the cuff decisions that I've had to backtrack on after realizing I hadn't considered a part of the bigger picture. This feels like the sort of thing that will have bigger repercussions for devs using Parallels than expected.  I don't know if Parallels has a beta release program, but that would hopefully have caught this sort of thing if there were customer-developer involvement.  But as is always the case, I'm too busy figuring things out to go looking for answers XD.

## Comment by sai-kumar-peddireddy at 2025-02-25T18:47:18Z

> [@sai-kumar-peddireddy](https://github.com/sai-kumar-peddireddy) could you provide some insight about why prl_fs was removed, and if it will be reintroduced ?
> 
> AFAIK using fuse won't work with some kernel's IO lowe level features (eg: nginx not being able to use sendfile). I've bought Parallels desktop because virtualbox broke this as well in the past and prl_fs allowed me to use such fstab options:
> 
> ```
> XXX    /home/ubuntu/XXX    prl_fs    uid=YYYY,gid=ZZZZ,sync,nosuid,nodev,noatime,host_inodes    0 2
> ```
> 
> Also it seems that some users already have other issues as well: https://forum.parallels.com/threads/parallels-20-hardlinks-not-supported-in-shared-folders.365235/
@amigrave I don't know the exact reason for the removal of `prl_fs` and introducing `prl_fsd`  will update here If know any info I will post it here




## Comment by sai-kumar-peddireddy at 2025-02-25T18:55:26Z

> > > this is proving to be a pretty serious roadblock for my day-to-day workflow, and I suspect it may be for others as well.
> > 
> > 
> > Indeed, I'm not even using vagrant and I'm impacted as well. `prl_fs` is a requirement for my in-vm developpements, so I had to revert back to Parallel Desktop version 20.1.3
> 
> I'll be curious if the decision to drop `prl_fs` was intentional or if it was an oversight; I'm an open-source system library dev and I've certainly made off the cuff decisions that I've had to backtrack on after realizing I hadn't considered a part of the bigger picture. This feels like the sort of thing that will have bigger repercussions for devs using Parallels than expected. I don't know if Parallels has a beta release program, but that would hopefully have caught this sort of thing if there were customer-developer involvement. But as is always the case, I'm too busy figuring things out to go looking for answers XD.

@WardF sorry for the inconvenience caused, thanks for using our product for such a long time..

I proposed a plan to auto/manual test part of the release for Parallels desktop with Packer, vagrant ..any other open-source tools dependent on Parallels desktop.

I will definitely inform your feedback to internal teams.

## Comment by amigrave at 2025-02-26T07:21:31Z

Hi @cjlapao 

Could you let this issue opened so we can get a clear answer about the fate of prl_fs in Parallels ?

## Comment by cjlapao at 2025-02-26T07:27:34Z

@amigrave I'm not sure this is the right forum to discuss the future of the prl_fs. That decision is in the hands of the Parallels Team, and any concerns should be addressed to them. This discussion is focused on the Vagrant Plugin. In this case, we have created a solution for the issue. As mentioned, we are also incorporating internal testing for any changes we make to the main product, ensuring that our open-source projects and plugins are not adversely affected.

If you have concerns about the future of the prl_fs, you can raise them either by contacting support or by posting them in the Parallels Forum.

make sense?

## Comment by BodoHuber at 2025-02-26T09:51:31Z

@cjlapao Since you closed the issue, I wonder about the unmount command?  I see a modification when mounting, but no modification for unmounting.  Also the mount options are not rejected as invalid options in case of using fuse.  Is that code considered to be complete?  

## Comment by cjlapao at 2025-02-26T09:56:24Z

@BodoHuber Yes, the bug was specific to the mount, not the unmount. If there is an issue with the unmount command, a new bug needs to be raised, and we (the community) will take a look. We are internally testing this and if we find more issue they will be addressed but in terms of management a bug is considered to be closed when it addresses the concern it was raised upon. Please open a bug for the unmount if you have an issue with it and we will have a look



## Comment by BodoHuber at 2025-02-26T10:32:15Z

@cjlapao thanks for clarification.  I will raise on demand.  

## Comment by mpdude at 2025-03-06T11:44:55Z

I am currently on Parallels 20.1.3 (55743) and using the version 2.4.4 of this plugin with the fix from #487.

At boot, Vagrant fails with the following error message:

```
Vagrant was unable to mount Parallels Desktop shared folders. This is usually
because the filesystem "prl_fs" is not available. This filesystem is
made available via the Parallels Tools and kernel module.
Please verify that these guest tools are properly installed in the
guest. This is not a bug in Vagrant and is usually caused by a faulty
Vagrant box. For context, the command attempted was:

            if [ -f /usr/bin/prl_fsd ]; then
              prl_fsd /var/www -o nosuid,nodev,noatime,big_writes,fsname=var_www,subtype=prl_fsd --share --sf=var_www
            else
              mount -t prl_fs -o share,noatime,host_inodes,uid=1000,gid=1000,_netdev var_www /var/www
            fi


The error output from the command was:

fuse: mountpoint is not empty
fuse: if you are sure this is safe, use the 'nonempty' mount option
```

When I SSH into the box, I find that this directory (`/var/www`) is still mounted with the `prl_fs` filesystem. When I unmount it, the `/var/www` mount point is indeed an empty directory.

So, my conclusion is that there is still something going on that mounts the filesystem with `prl_fs` _before_ `prl_fsd` is attempted. I have run `vagrant` with debug logging but was unable to find something related.

Any clues?

## Comment by fpatz at 2025-03-06T12:52:35Z

@mpdude 2.4.4 with Parallels 20.2.1 (55876) looks just fine for me with several flavors of Linux systems, so I'd say the issue is fixed. Yours looks more like either a setup problem with that particular VM or with the PD patch level you're using (yours is a bit older than mine).

## Comment by mpdude at 2025-03-06T12:58:32Z

Yes, currently looks as if there was a dangling (exited but not removed) Docker container. Upon system boot and start of the Docker daemon, that led to files being created in the mountpoint directory before Vagrant attempted to mount the `prl_fsd` folders.
