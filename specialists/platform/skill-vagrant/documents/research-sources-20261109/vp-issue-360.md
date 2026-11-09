<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/360
**Retrieved**: 2026-11-09 11:25 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #360 How to set/enlarge disk

State: OPEN; opened 2020-07-24T09:49:15Z; closed open

## Body

By default the disk size is 32gb.
How do I tell the vagrantfile to use a larger storage space?

## Comment by legal90 at 2020-11-20T19:25:32Z

Hi @matthew-gill 
Sorry for the late response. You asked a good question - apparently there is no a reliable way to change the disk size at this moment.

In fact, that could be done using this customization rule:
```ruby
  config.vm.provider "parallels" do |prl|
    prl.customize "post-import", ["set", :id, "--device-set", "hdd0", "--size", "40000"]
  end
```
But that will fail if in the past there was at least one linked clone created from this base box:
```
#<VagrantPlugins::Parallels::Errors::ExecutionError: There was an error while command execution. The command and stderr is shown below.

Command: ["/usr/local/bin/prlctl", "set", "a0963bf0-5333-42eb-b428-1764a6031a65", "--device-set", "hdd0", "--size", "40000"]

Stderr: Failed to resize: This virtual hard disk cannot be resized because it has one or more snapshots. To resize the disk, delete the snapshots and try again.
Failed to configure the virtual machine.
```

_Details_
This error message is saying about the one special snapshot of the base box disk which is used as a common "node" (starting point) for all potential linked clones created from this base box. And unfortunately we can't remove this snapshot,
because that will corrupt all existing linked clones.

@andreydanin, do you know if there is a way to increase the disk size of linked clone without affecting the source disk image?

## Comment by matthew-gill at 2020-11-20T21:27:00Z

@legal90  thanks for looking into this! For now we have a workaround where we manually Mount and partition a new disk, but it's not ideal!

## Comment by jamesmartin at 2021-08-24T06:26:07Z

👋 any movement on this? I'm trying to achieve the same thing.

## Comment by kgifford-hv at 2021-11-04T23:05:25Z

So, I understand the underlying difficulty in accomplishing this mentioned by @legal90.

That said, there are some of us where the danger, "...unfortunately we can't remove this snapshot, because that will corrupt all existing linked clones." is irrelevant.

The fact that I _used_ to have a version of my VM that used linked cloning is vestigial.

The reality is, I only need/use exactly 1 VM (at a time; I often `vagrant destroy` / `vagrant up` as necessary). This one VM references my one and only base box. I used to be okay with our company-wide Vagrantfile that used linked cloning.

However, a subset of us now need larger disks. We have a per-developer `Vagrantfile.local` that we can define to override general settings. I can almost use it to enlarge my disk by disabling linked cloning and using `prl.customize` to set a new/larger disk size. Only the snapshot (from prior instances of the VM that did use linked cloning of the base box, but have since all been nuked) gets in the way.

I'd love a way to have vagrant-parallels give me the option to explicitly request any/all such snapshots be nuked (`prlctl snapshot-delete ...`) regardless of the "danger". Perhaps force me to include some extra parameter that essentially says, "I understand the risk associated with deleting any such snapshots of the base box's disk, but my circumstances are such that I'm declaring it's okay".

I'd just work around this myself if there were a way for me, within the context of the `Vagrantfile`'s main block, to run `prlctl` commands (like `prl.customize`) but where I could get the output. I'd manually list and nuke any such snapshots prior to requesting the modified disk size.

## Comment by zarinfam at 2023-03-04T15:21:38Z

Do you know if there is any progress on this issue? I have this problem too.

## Comment by dogukancagatay at 2023-04-01T10:20:41Z

I tackled this problem when creating Vagrant boxes for the Parallels provider, and found [this solution](https://github.com/dogukancagatay/fedora-boxes-aarch64/blob/9eeb5f9b67155982db4be48fff6107dbf9c8da3a/templates/build.pkr.hcl#L69-L70).

You need those snapshots deleted, which is done with `prl_disk_tool merge` and `prl_disk_tool compact` commands.

```
prl_disk_tool merge --hdd vm.pvm/harddisk1.hdd
prl_disk_tool compact --hdd vm.pvm/harddisk1.hdd
```

## Comment by luiscantor at 2024-02-02T00:05:38Z

You'll need to execute this command first:

`vagrant plugin install vagrant-disksize`

and then add a line like this to your vagrantfile:
`config.disksize.size = '60GB'`

I was having the same problem and this was the solution for me.

## Comment by markush81 at 2024-02-02T16:05:19Z

> You'll need to execute this command first:
> 
> `vagrant plugin install vagrant-disksize`
> 
> and then add a line like this to your vagrantfile: `config.disksize.size = '60GB'`
> 
> I was having the same problem and this was the solution for me.

actually this plugin https://github.com/sprotheroe/vagrant-disksize, says

> The plugin only works with VirtualBox but it will issue an error message and then disable itself if you try to use it with another provider.

and this issue is for **Parallels** provider. So it can't and doesn't work.

## Comment by maxexcloo at 2024-05-17T04:40:22Z

Having this issue also, wondering if anyone found any fixes?

## Comment by mromero-convoso at 2024-08-22T22:45:37Z

Also having this issue. Any way to get a similar 'vagrant-disksize' plugin for Parallels provider types?

## Comment by savvn001 at 2026-01-12T14:52:23Z

Same issue, is there ANY way to set the disk size of the VM? I can't change it in Parallels desktop either, as the slider is completely missing. I'm stuck with a default 64GB disk image.

## Comment by mromero-convoso at 2026-08-05T17:10:07Z

*bump

## Comment by cjlapao at 2026-08-06T09:05:25Z

Those operations are not supported as it is not simply changing the disk size, the OS also matter, the disk can grow but the OS would not see it


## Comment by mromero-convoso at 2026-08-06T09:07:46Z

> Those operations are not supported as it is not simply changing the disk size, the OS also matter, the disk can grow but the OS would not see it
> 

An inline script can take care of extending the disk once it's resized - vagrant-disksize plugin for virtualbox doesn't resize the file system and requires you handle that part on your own

## Comment by cjlapao at 2026-08-07T05:39:50Z

as I stated those operations are not supported by the plugin nor de we have plans to add those in the near future, but if anyone wants to create the pr to implement that we would review the changes and if good merge them

