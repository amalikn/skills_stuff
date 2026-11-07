<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072:
# Is it possible to use Vagrant with the trial version of Parallels for Mac?

**URL:** <https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072>\
**Category:** Vagrant\
**Created:** [September 18, 2024, 3:39pm UTC](https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072 "2024-09-18T15:39:35Z")\
**Posts on this page:** 2\
**Page:** 1

<div class="post-metadata">

**Author:** ![wmoon](https://sea2.discourse-cdn.com/hashicorp/user_avatar/discuss.hashicorp.com/wmoon/32/43055_2.png) [@wmoon](https://discuss.hashicorp.com/u/wmoon)\
**Post date:** [September 18, 2024, 3:39pm UTC](https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072/1 "2024-09-18T15:39:35Z")

</div>

I’m trying to use the latest Vagrant(v2.4.1) on my Mac with a trial version of Parallels, but get this message:

> $ vagrant up --provider=parallels  
> The provider ‘parallels’ that was requested to back the machine  
> ‘default’ is reporting that it isn’t usable on this system. The  
> reason is shown below:
> 
> Vagrant has detected that you have an edition of Parallels Desktop for Mac  
> installed that is not supported. Vagrant Parallels provider is compatible  
> only with Pro and Business editions of Parallels Desktop. Other editions  
> do not have command line functionality and can not be used with Vagrant.
> 
> Please upgrade your installation: [Run Windows on Mac with a virtual machine | Parallels Desktop](https://parallels.com/desktop)

I installed the Parallels plugin with:

> vagrant plugin install vagrant-parallels

which came from this guide: [KB Parallels: How to use Vagrant with Parallels Desktop](https://kb.parallels.com/122843/)

When I asked the Parallels support team about this, they responded with:

> Please note that Parallels Desktop trial version has all the same features as Parallels Desktop For Mac Pro version.

But I’m guessing that’s not the problem here. I think the problem has to do with how the the trial version of Parallels is identifying itself to whatever Vagrant is checking. Has anyone dealt with this and gotten the trial version of Parallels working with Vagrant?

---

<div class="post-metadata">

**Author:** ![wmoon](https://sea2.discourse-cdn.com/hashicorp/user_avatar/discuss.hashicorp.com/wmoon/32/43055_2.png) [@wmoon](https://discuss.hashicorp.com/u/wmoon)\
**Post date:** [September 19, 2024, 4:17pm UTC](https://discuss.hashicorp.com/t/is-it-possible-to-use-vagrant-with-the-trial-version-of-parallels-for-mac/70072/2 "2024-09-19T16:17:49Z")

</div>

Never mind, things are working now. The solution was that I needed to activate my free trial of Parallels. On the current version v20.0.1(55659), you won’t see an option to sign in(activate) with your Parallels account until you try adding a VM through the UI. After I added a Debian VM, I was able to get my unrelated Vagrant VM working.

