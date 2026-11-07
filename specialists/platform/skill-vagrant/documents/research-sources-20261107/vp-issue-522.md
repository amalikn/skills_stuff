<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/522
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #522 AppArmor blocking `prl_fsd`/`fusermount3` calls by default in Ubuntu 26.04

State: OPEN; opened 2026-06-08T08:51:55Z; closed -

## Body

I recently updates Paralles to version 26.3.3 (57507) and started a new Ubuntu 26.04 box for the first time. Upon boot, mounting the `prl_fsd` filesystem fails.

I built the box myself based on the "Bento" project and I can tell for sure that Parallels Tools are installed in the most recent version.

```
$ vagrant up
Bringing machine 'default' up with 'parallels' provider...
==> default: Registering VM image from the base box 'webfactory-de/ubuntu-26.04'...
==> default: Creating new virtual machine as a linked clone of the box image...
==> default: Unregistering the box VM image...
==> default: Setting the default configuration for VM...
==> default: Setting the name of the VM: wf-development-vm-2604
==> default: Preparing network interfaces based on configuration...
    default: Adapter 0: shared
    default: Adapter 1: hostonly
==> default: Clearing any previously set network interfaces...
==> default: Forwarding ports...
    default: 22 => 2227
==> default: Running 'pre-boot' VM customizations...
==> default: Booting VM...
==> default: Waiting for machine to boot. This may take a few minutes...
    default: SSH address: 10.211.55.94:22
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
vagrant-dns: trying to stop process with pid 24072 sending TERM and waiting 20s ...
vagrant-dns: process with pid 24072 successfully stopped.
vagrant-dns: process with pid 27326 started.
==> default: Restarted DNS Service
==> default: Setting hostname...
==> default: Configuring and enabling network interfaces...
==> default: Mounting shared folders...
    default: /Volumes/Projekte => /var/www
Vagrant was unable to mount Parallels Desktop shared folders. This is usually
because the filesystem "prl_fs" is not available OR you are passing
unsupported mount options to prl_fsd daemon for supported options please refer
to the prl_fsd --help in VM.
"prl_fs"/"prl_fsd" are available via the Parallels Tools and kernel module.
Please verify that these guest tools are properly installed in the
guest. This is not a bug in Vagrant and is usually caused by a faulty
Vagrant box. For context, the command attempted was:

            if [ -f /usr/bin/prl_fsd ]; then
              prl_fsd /var/www -o nonempty,noatime,nodev,nosuid,big_writes,fsname=var_www,subtype=prl_fsd --share --sf=var_www
            else
              mount -t prl_fs -o share,nonempty,noatime,nodev,nosuid,uid=1000,gid=1000,_netdev var_www /var/www
            fi


The error output from the command was:

fusermount: mount failed: Permission denied
```

It's a bit hard to tell where this might come from. The same Vagrantfile previously worked on an Ubuntu 24.04 box. 

What would be helpful for troubleshooting?

Running `sudo prl_fsd /var/www -o nonempty,noatime,nodev,nosuid,big_writes,fsname=var_www,subtype=prl_fsd --share --sf=var_www` from inside the box gives the same error.

## Comment by mpdude at 2026-06-08T09:57:25Z

The problem is that in Ubuntu 26.04 by default blocks `fusermount3` calls, which (I haven't figured out the details) happen behind the scenes when `prl_fsd` is used.

So, how to solve this in a generic way from within this plugin?

@cjlapao Would it help if I open a Parallels support ticket for this one? After all, this plugin is an official solution, right?

## Comment by mpdude at 2026-06-08T10:43:57Z

Related: https://forum.parallels.com/threads/ubuntu-25-04.367139/

## Comment by cjlapao at 2026-06-10T08:02:44Z

@mpdude 

> The problem is that in Ubuntu 26.04 by default blocks `fusermount3` calls, which (I haven't figured out the details) happen behind the scenes when `prl_fsd` is used.
> 
> So, how to solve this in a generic way from within this plugin?
> 
> [@cjlapao](https://github.com/cjlapao) Would it help if I open a Parallels support ticket for this one? After all, this plugin is an official solution, right?

Yes this is the official plugin but we are different teams and this is not a bug on the plugin but rather a issue with PD itself, so while we can have a look at the work you did as a workaround this as been flag internally for them to fix as there will be problems with other plugins we have and other services, we cannot simply do a workaround on all of them and maintain it. As you correctly stated this seems to be a regression or just something we need to implement. I see the pr and while we probably will merge it we are still understanding how long would PD team take to address the issue on the source. If that is a fast fix from their side we prefer not to merge it, if not we will merge your pr and release the fix, give us until this Friday to get a bit more clarification

## Comment by cjlapao at 2026-06-12T14:02:39Z

@mpdude We decided to merge your code as it will potentially take a bit of time for PD to catch up I am releasing this today. let me know if this fixes it and then we will close this

## Comment by mpdude at 2026-09-15T13:37:50Z

I am not sure if #523 resolved this issue here; upgrading to Ubuntu 26.04 was an experiment which I had to abandon for the time being, so I have no way of checking right now.
