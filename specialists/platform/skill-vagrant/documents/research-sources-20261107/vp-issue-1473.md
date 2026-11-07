<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/chef/bento/issues/1473
**Retrieved**: 2026-11-07 15:55 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #1473 Network and SSH problems using bento/ubuntu-20.04-arm64 and bento/ubuntu-22.04-arm64 with Vagrant 

State: CLOSED; opened 2023-02-13T17:34:22Z; closed 2023-07-07T14:34:27Z

## Body

# Version
bento/ubuntu-20.04-arm64 v202301.20.0

## Environment
Vagrant 2.3.4

## Scenario
Installing multiple vm's and randomly failing with login into vm with the vagrant ssh key at the vm creating stage, eventually it will time out with vagrant up. 

As stated, it happens randomly, so when a login is succesful into a vm, it happens a lot that the internal networking remains working (172.16.0.0/24), but the internet connection is working for about a minute, then unreachable for 5 minutes or more, every time at a different stage in my Vagrantfile. I use multiple shell provisioners. 

This all happens with the 202301.20.0 version. When using the 202112.19.0 version it all works fine, every time.

## Steps to Reproduce
You need to setup multiple vm's and use a couple of shell provisioners and download data. In my case there are helm charts and apt packages.

## Expected Result
With 202301.20.0 the same result as using 202112.19.0

## Actual Result
Tried it 11 times, it fails all the time with 202301.20.0, tested it 4 times with 202112.19.0, 4 times succesful. I also tried it with bento/ubuntu-22.04-arm64, but the same login problems rise. I was unable to get to the shell provisioners part at my 2 tests with bento/ubuntu-22.04-arm64.


## Comment by sford at 2023-02-17T14:44:26Z

This feels similar to #1421. There is a bug where `/etc/machine-id` isn't unique, which can impact DHCP and cause network problems. Fix #1471 has been merged but boxes haven't been updated yet on vagrant cloud.

## Comment by Evantage-WS at 2023-02-17T19:45:55Z

@sford, thanks for your info, I will test this next week. Enjoy the weekend

## Comment by Evantage-WS at 2023-02-19T12:10:45Z

Hello @sford, it is indeed the same. Does anybody knows when the images are going to be updated? Thanks!

## Comment by Stromweld at 2023-02-19T15:52:12Z

Beginning of march I plan to update the images. Hoping to keep a quarterly cadence. With the new hcl rewrite and dedicated builders for testing I’m currently working on getting the builds stable and working. Most x86_64 builds are working for virtualbox, parallels, and VMware, but aarch64, hyperv, and qemu machines still have a bit of tweaking needed to get builds working. 

## Comment by Stromweld at 2023-02-19T15:56:09Z

With that, any testing and fixes you may find, if you can submit PR’s for them that’ll be greatly appreciated. 

## Comment by Evantage-WS at 2023-02-19T18:18:44Z

Hi, thanks for the reply. When I find something I will certainty look at it. 

## Comment by Stromweld at 2023-03-05T04:46:55Z

Can someone test one of these images to verify it fixes the issues you guys are seeing? If so then I can work on getting them officially published. https://github.com/chef/bento/actions/runs/4328485365#artifacts

## Comment by Evantage-WS at 2023-03-05T14:11:04Z

Sure, but I need some help how to test the aarch64 Ubuntu 22.10, how do I specify this image in the Vagrant file?

## Comment by Stromweld at 2023-03-05T14:59:17Z

If you download the image you want to test then you can use the vagrant box add command and give it a name like test/ubuntu-version and point to the downloaded file. Then in your vagrant file you’d set the image to the name you gave it. 

## Comment by Evantage-WS at 2023-03-06T07:19:41Z

Hi,

I have done it, it is picking up the new box, but I do get an error, when changing some SSH parameters, FYI, this is working in 20.04:

BTW, this is a config with only 1 vm in it.

```
    cluster1-single-node-cluster: -------------------------------------------------------------------------------------------------------------
    cluster1-single-node-cluster: ====  base.sh: START: stop and disable firewall
    cluster1-single-node-cluster: Synchronizing state of ufw.service with SysV service script with /lib/systemd/systemd-sysv-install.
    cluster1-single-node-cluster: Executing: /lib/systemd/systemd-sysv-install disable ufw
    cluster1-single-node-cluster: Removed "/etc/systemd/system/multi-user.target.wants/ufw.service".
    cluster1-single-node-cluster: ====  base.sh: END  : stop and disable firewall
    cluster1-single-node-cluster: ====  base.sh: START: copy SSH public key to root
    cluster1-single-node-cluster: ====  base.sh: END  : copy SSH public key to root
    cluster1-single-node-cluster: ====  base.sh: START: change SSH PasswordAuthentication
    cluster1-single-node-cluster: Failed to reload sshd.service: Unit sshd.service not found.
The SSH command responded with a non-zero exit status. Vagrant
assumes that this means the command failed. The output for this command
should be in the log above. Please read the output to determine what
went wrong.
```

Maybe something changed in Ubuntu regarding SSH or something corrupt? https://codetryout.com/failed-to-restart-sshd-service-unit-sshd-service-not-found/

## Comment by Evantage-WS at 2023-03-06T07:58:52Z

Hi, testing with 22.10, 4 vm's, gives problems:

This is with 20.04, working:
```
==> management-loadbalancer1: Registering VM image from the base box 'bento/ubuntu-20.04-arm64'...
==> management-loadbalancer1: Creating new virtual machine as a linked clone of the box image...
==> management-loadbalancer1: Unregistering the box VM image...
==> management-loadbalancer1: Setting the default configuration for VM...
==> management-loadbalancer1: Checking if box 'bento/ubuntu-20.04-arm64' version '202301.20.0' is up to date...
==> management-loadbalancer1: Setting the name of the VM: management-loadbalancer1
==> management-loadbalancer1: Preparing network interfaces based on configuration...
    management-loadbalancer1: Adapter 0: shared
    management-loadbalancer1: Adapter 1: hostonly
==> management-loadbalancer1: Clearing any previously set network interfaces...
==> management-loadbalancer1: Running 'pre-boot' VM customizations...
==> management-loadbalancer1: Booting VM...
==> management-loadbalancer1: Waiting for machine to boot. This may take a few minutes...
    management-loadbalancer1: SSH address: :22
    management-loadbalancer1: SSH username: vagrant
    management-loadbalancer1: SSH auth method: private key
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: 
    management-loadbalancer1: Vagrant insecure key detected. Vagrant will automatically replace
    management-loadbalancer1: this with a newly generated keypair for better security.
    management-loadbalancer1: 
    management-loadbalancer1: Inserting generated public key within guest...
    management-loadbalancer1: Removing insecure key from the guest if it's present...
    management-loadbalancer1: Key inserted! Disconnecting and reconnecting using new SSH key...
==> management-loadbalancer1: Machine booted and ready!
==> management-loadbalancer1: Checking for Parallels Tools installed on the VM...
```

This is with 22.10, I only changed the box in the config, failing:
```
==> management-loadbalancer1: Registering VM image from the base box 'test/ubuntu-2210'...
==> management-loadbalancer1: Creating new virtual machine as a linked clone of the box image...
==> management-loadbalancer1: Unregistering the box VM image...
==> management-loadbalancer1: Setting the default configuration for VM...
==> management-loadbalancer1: Setting the name of the VM: management-loadbalancer1
==> management-loadbalancer1: Preparing network interfaces based on configuration...
    management-loadbalancer1: Adapter 0: shared
    management-loadbalancer1: Adapter 1: hostonly
==> management-loadbalancer1: Clearing any previously set network interfaces...
==> management-loadbalancer1: Running 'pre-boot' VM customizations...
==> management-loadbalancer1: Booting VM...
==> management-loadbalancer1: Waiting for machine to boot. This may take a few minutes...
    management-loadbalancer1: SSH address: :22
    management-loadbalancer1: SSH username: vagrant
    management-loadbalancer1: SSH auth method: private key
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
```

it times out

## Comment by Stromweld at 2023-03-06T08:30:31Z

Thanks. What do you get with testing 22.04? I know starting with 22.04 and rhel 9 based machines they finally removed the old ssh key algorithms based on sha1 and less than 2048 bits. Since that was the old default it requires users to generate new ssh keys for auth. I’m not sure if there are any other ssh changes that would be affecting the service.

## Comment by Stromweld at 2023-03-06T08:32:00Z

Your output for working 20.04 box is that based on new version from the PR build yet to be released or is that old version that is currently in vagrant cloud?

## Comment by Evantage-WS at 2023-03-06T09:58:18Z

> 

It is the one in Vagrant Cloud

## Comment by Evantage-WS at 2023-03-06T09:58:51Z

> Thanks. What do you get with testing 22.04? I know starting with 22.04 and rhel 9 based machines they finally removed the old ssh key algorithms based on sha1 and less than 2048 bits. Since that was the old default it requires users to generate new ssh keys for auth. I’m not sure if there are any other ssh changes that would be affecting the service.

I will test it with 22.04 today, give me a few hours

## Comment by Evantage-WS at 2023-03-06T11:18:53Z

With 22.04 same problem as with 22.10:

```
==> management-loadbalancer1: Registering VM image from the base box 'test/ubuntu-2204'...
==> management-loadbalancer1: Creating new virtual machine as a linked clone of the box image...
==> management-loadbalancer1: Unregistering the box VM image...
==> management-loadbalancer1: Setting the default configuration for VM...
==> management-loadbalancer1: Setting the name of the VM: management-loadbalancer1
==> management-loadbalancer1: Fixed port collision for 22 => 2222. Now on port 2200.
==> management-loadbalancer1: Preparing network interfaces based on configuration...
    management-loadbalancer1: Adapter 0: shared
    management-loadbalancer1: Adapter 1: hostonly
==> management-loadbalancer1: Clearing any previously set network interfaces...
==> management-loadbalancer1: Running 'pre-boot' VM customizations...
==> management-loadbalancer1: Booting VM...
==> management-loadbalancer1: Waiting for machine to boot. This may take a few minutes...
    management-loadbalancer1: SSH address: :22
    management-loadbalancer1: SSH username: vagrant
    management-loadbalancer1: SSH auth method: private key
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
```

## Comment by Stromweld at 2023-03-06T14:49:06Z

Can you try the 20.04 release in the linked build job? Want to rule out OS ssh changes or Bento build script changes.

## Comment by Evantage-WS at 2023-03-06T15:02:11Z

Hi, the 20.04 in the linked build job is working correctly

## Comment by Stromweld at 2023-03-06T15:15:07Z

ok thanks, since all versions are running the same scripts/setup that means it probably has to do with dropping of old ssh algorithms. Can you see if updating your keys or adding to the sshd_config for weak ciphers fixes your issue for you. This article explains it pretty well. https://askubuntu.com/questions/1409105/ubuntu-22-04-ssh-the-rsa-key-isnt-working-since-upgrading-from-20-04. 

Thanks again for all the help testing.

## Comment by sford at 2023-03-06T15:55:22Z

Hi @Stromweld, this is probably the wrong place to document since I am not using `arm64`, but with respect to testing recent bug fixes... I successfully tested `ubuntu-22.04-x86_64.virtualbox.box` from that github actions link. I didn't run into any problems with DHCP, networking, or duplicate IPs 🎉 

Some more details... I am using `vagrant-libvirt` so I installed `ubuntu-22.04-x86_64.virtualbox.box` and mutated it to `libvirt` provider.

Here are logs showing `bento/ubuntu-22.04` and all VMs having unique IP addresses:

```
==> vm3:  -- Base box:          bento/ubuntu-22.04
==> vm2:  -- Base box:          bento/ubuntu-22.04
==> vm1:  -- Base box:          bento/ubuntu-22.04
==> vm6:  -- Base box:          bento/ubuntu-22.04
==> vm5:  -- Base box:          bento/ubuntu-22.04
==> vm7:  -- Base box:          bento/ubuntu-22.04
==> vm4:  -- Base box:          bento/ubuntu-22.04

vm1: SSH address: 192.168.121.121:22
vm2: SSH address: 192.168.121.11:22
vm6: SSH address: 192.168.121.126:22
vm5: SSH address: 192.168.121.190:22
vm7: SSH address: 192.168.121.210:22
vm4: SSH address: 192.168.121.140:22
vm3: SSH address: 192.168.121.69:22
``` 

I also ran our test suite on these VMs. We configure them with Puppet (sorry chef!) and run our tests. Everything passed and didn't run into any problems.

Thanks @Stromweld !


## Comment by Evantage-WS at 2023-03-06T16:54:35Z

> ok thanks, since all versions are running the same scripts/setup that means it probably has to do with dropping of old ssh algorithms. Can you see if updating your keys or adding to the sshd_config for weak ciphers fixes your issue for you. This article explains it pretty well. https://askubuntu.com/questions/1409105/ubuntu-22-04-ssh-the-rsa-key-isnt-working-since-upgrading-from-20-04.
> 
> Thanks again for all the help testing.

Hi, it is logging in with the Vagrant user, so I guess it is using an self generated keypair. For my own keypair, I have exactly done as written in your link, but that is for my own user.

Log:
```
==> management-loadbalancer1: Registering VM image from the base box 'test/ubuntu-2210'...
==> management-loadbalancer1: Creating new virtual machine as a linked clone of the box image...
==> management-loadbalancer1: Unregistering the box VM image...
==> management-loadbalancer1: Setting the default configuration for VM...
==> management-loadbalancer1: Setting the name of the VM: management-loadbalancer1
==> management-loadbalancer1: Fixed port collision for 22 => 2222. Now on port 2200.
==> management-loadbalancer1: Preparing network interfaces based on configuration...
    management-loadbalancer1: Adapter 0: shared
    management-loadbalancer1: Adapter 1: hostonly
==> management-loadbalancer1: Clearing any previously set network interfaces...
==> management-loadbalancer1: Running 'pre-boot' VM customizations...
==> management-loadbalancer1: Booting VM...
==> management-loadbalancer1: Waiting for machine to boot. This may take a few minutes...
    management-loadbalancer1: SSH address: :22
    management-loadbalancer1: SSH username: vagrant
    management-loadbalancer1: SSH auth method: private key
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
```

## Comment by Stromweld at 2023-03-06T18:34:28Z

@sford Thanks for letting me know. Glad to hear that's fixed.

@Evantage-WS Thanks for all the testing. I'll try to dig into it some more and see if I can figure out the issue/fix. 

## Comment by Evantage-WS at 2023-03-07T07:19:16Z

Great, thanks

## Comment by Evantage-WS at 2023-03-20T16:45:41Z

Hi @Stromweld, I do see a new release, is the problem I reported fixed so I can test it?

## Comment by Stromweld at 2023-03-20T17:26:21Z

There hasn't been a new release of the Vagrant Ubuntu boxes for Arm architecture yet. I'm hoping to get those built by the end of this week.

## Comment by Evantage-WS at 2023-03-21T08:14:12Z

Ok, thanks. 

## Comment by Stromweld at 2023-05-05T18:45:34Z

I don't have a working ubuntu-20.04-arm64 box yet, but there is the 22.04-arm box with the fixes mentioned above. Does this fit the need and does this box also fix the dhcp issue https://app.vagrantup.com/bento/boxes/ubuntu-22.04-arm64?

## Comment by Evantage-WS at 2023-05-08T14:11:29Z

Hi @Stromweld, just a quick test, unfortunally the same problem:

```
==> management-loadbalancer1: Box 'bento/ubuntu-22.04-arm64' could not be found. Attempting to find and install...
    management-loadbalancer1: Box Provider: parallels
    management-loadbalancer1: Box Version: 202304.27.0
==> management-loadbalancer1: Loading metadata for box 'bento/ubuntu-22.04-arm64'
    management-loadbalancer1: URL: https://vagrantcloud.com/bento/ubuntu-22.04-arm64
==> management-loadbalancer1: Adding box 'bento/ubuntu-22.04-arm64' (v202304.27.0) for provider: parallels
    management-loadbalancer1: Downloading: https://vagrantcloud.com/bento/boxes/ubuntu-22.04-arm64/versions/202304.27.0/providers/parallels.box
==> management-loadbalancer1: Successfully added box 'bento/ubuntu-22.04-arm64' (v202304.27.0) for 'parallels'!
==> management-loadbalancer1: Registering VM image from the base box 'bento/ubuntu-22.04-arm64'...
==> management-loadbalancer1: Creating new virtual machine as a linked clone of the box image...
==> management-loadbalancer1: Unregistering the box VM image...
==> management-loadbalancer1: Setting the default configuration for VM...
==> management-loadbalancer1: Checking if box 'bento/ubuntu-22.04-arm64' version '202304.27.0' is up to date...
==> management-loadbalancer1: Setting the name of the VM: management-loadbalancer1
==> management-loadbalancer1: Preparing network interfaces based on configuration...
    management-loadbalancer1: Adapter 0: shared
    management-loadbalancer1: Adapter 1: hostonly
==> management-loadbalancer1: Clearing any previously set network interfaces...
==> management-loadbalancer1: Running 'pre-boot' VM customizations...
==> management-loadbalancer1: Booting VM...
==> management-loadbalancer1: Waiting for machine to boot. This may take a few minutes...
    management-loadbalancer1: SSH address: :22
    management-loadbalancer1: SSH username: vagrant
    management-loadbalancer1: SSH auth method: private key
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
    management-loadbalancer1: Warning: Connection refused. Retrying...
```

## Comment by Stromweld at 2023-06-29T20:13:27Z

I believe this is actually a vagrant issue and should be fixed in the latest version of vagrant with the ssh key algorithm fix https://github.com/hashicorp/vagrant/blob/v2.3.7/CHANGELOG.md

I also just released new builds of 20.04-arm64 and 22.04-arm64. Can you confirm this is working for you now?

## Comment by Evantage-WS at 2023-06-30T08:37:38Z

Hi @Stromweld,

Thanks, I have upgraded Vagrant and updated my sources to use the newly created box, but when using it I do get an EFI_RNG_PROTOCOL unavailable error. When using the 20.04 image, it is working fine, so it think it is something in the newly created image
![image](https://github.com/chef/bento/assets/59507751/c13c82b6-027f-4763-8fbf-2a14f8a8161d)


## Comment by Stromweld at 2023-07-07T14:34:27Z

Both boxes are working for me. Please check that your vagrant files are the same. 
![image](https://github.com/chef/bento/assets/3476391/5720f4a5-5a7c-4f93-9034-4e22d7477634)
Here's my test-kitchen vagrant file:
```
Vagrant.configure("2") do |c|
  c.berkshelf.enabled = false if Vagrant.has_plugin?("vagrant-berkshelf")
  c.vm.box = "bento/ubuntu-22.04-arm64"
  c.vm.hostname = "default-ubuntu-2204.vagrantup.com"
  c.vm.synced_folder ".", "/vagrant", disabled: true
  c.vm.synced_folder "$HOME/.kitchen/cache", "/tmp/omnibus/cache", create: true
  c.vm.provider :parallels do |p|
  end
end
```

Closing this issue. Please feel free to open a new issue or reopen this issue if problems are found with boxes or code.
