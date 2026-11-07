<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/527
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #527 New Release

State: CLOSED; opened 2026-10-14T16:20:52Z; closed 2026-10-28T14:53:29Z

## Body

It looks like quite a few PRs have been merged since the last tagged release (2.4.7) but no new release has been created.

https://github.com/Parallels/vagrant-parallels/compare/v2.4.7...master

I'm not sure at what point the 2.4.8 and 2.4.9 releases were created as they don't seem to have tags. I currently have 2.4.9 installed

```bash
$ vagrant plugin list
vagrant-parallels (2.4.9, global)
  - Version Constraint: > 0
```

and there are no updates available it seems:

```bash
$ vagrant plugin update vagrant-parallels
Updating plugins: vagrant-parallels. This may take a few minutes...
Building native extensions. This could take a while...
Fetching nokogiri-1.19.4-arm64-darwin.gem
Removing nokogiri
Successfully uninstalled nokogiri-1.19.4-arm64-darwin
All plugins are up to date.
```

I'm not sure if there's now a constraint between the plugin and vagrant itself - I currently have the latest installed (as of this writing)

```bash
$ vagrant --version
Vagrant 2.4.9
```

PR #525  is particularly key as it's causing us problems with our guest images which use `fusermount3`. Now that it's been merged, please can we get a timeline for a new release - it's frustrating that we can't take advantage of the change which has already gone into master.

## Comment by cjlapao at 2026-10-28T11:08:16Z

@ronanchilvers the github releases might not be up to date as they are mostly not used. The 2.4.9 was a merged of the latest tested commit by our QA and since then there has not been a lot of activity, just the FUSE work by the community, hence still under testing from our side. We do tend to join more than one PR for release and we will be releasing this when we are ready, should be somewhere this week


## Comment by cjlapao at 2026-10-28T14:53:29Z

@ronanchilvers we have release this today, we were unable to really test all scenarios but we do not see the pr as having anything that breaks, this is in 2.4.10


## Comment by ronanchilvers at 2026-10-28T15:19:07Z

That's great news! Thanks @cjlapao 🙏
