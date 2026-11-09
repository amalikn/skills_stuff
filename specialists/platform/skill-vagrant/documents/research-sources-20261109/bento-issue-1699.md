<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/chef/bento/issues/1699
**Retrieved**: 2026-11-09 11:25 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #1699 [RFC] Host bento boxes on GitLab Generic Package Registry + GitLab Pages after HCP Vagrant EOL

State: OPEN; opened 2026-09-08T04:38:20Z; closed open

## Body

### Background

HashiCorp has announced that **HCP Vagrant (Vagrant Cloud) is being deprecated**:

- **2026-10-01** — new boxes can no longer be created in HCP Vagrant
- **2026-12-31** — end of operations; all deployments will be decommissioned

Source: https://developer.hashicorp.com/vagrant/vagrant-cloud/boxes/catalog

Without an alternative, the `bento` org on Vagrant Cloud becomes read-only on 2026-10-01, and every box it publishes disappears on 2026-12-31. I would like to propose moving bento's hosting to GitLab, using only public static resources:

1. **Box binary files** → GitLab Generic Package Registry (gitlab.com, free for public projects)
2. **Box metadata catalog** (the JSON document consumed by `vagrant box add https://.../metadata.json`) → GitLab Pages

### Why GitHub alone is not sufficient

| Constraint | GitHub |
|---|---|
| Release asset max file size | **2 GiB** |
| Release total size / bandwidth | unlimited |
| Pages site size | 1 GB |
| Pages bandwidth | 100 GB / month (soft limit) |

Ref: https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases#storage-and-bandwidth-quotas

### Why GitLab works

From https://docs.gitlab.com/user/gitlab_com/ (the GitLab for SaaS docs):

- **Generic package registry** — maximum file size **5 GB** per package, which covers every current and foreseeable bento box.
- **Generic packages support unauthenticated download** at `GET /projects/:id/packages/generic/:package_name/:package_version/:file_name` — exactly the shape the `url` field of a Vagrant metadata catalog needs, i.e., no auth required for end users.
- **GitLab Pages** — site size limit 1 GB, which is more than enough for a metadata catalog for hundreds of box/provider/arch combinations.
- No documented total storage or bandwidth quota for generic packages or Pages on gitlab.com; both are served via GitLab's CDN.

So both the box binaries and the metadata catalog can live on GitLab in a single free public project.

## Comment by drbenzin at 2026-10-06T11:12:49Z

One more option to weigh against static metadata.json: Vagrant 2.4 resolves `bento/ubuntu-24.04` against whatever `VAGRANT_SERVER_URL` points to, and the same URL works as `config.vm.box_url` without the env var, so box names, versions and `vagrant box update` keep working.

I've built a small registry that serves that API from a Cloudflare R2 bucket (no egress fees, multi-GB boxes uploaded in parts) and a migrator that copies every version, provider and architecture from HCP and checks the checksums. Tested with Vagrant 2.4.9. Notes: https://factodus.com/boxharbor/

Happy to run the migration of the bento org for free if that helps the decision.


## Comment by rmoriz at 2026-10-06T22:44:52Z

Maybe Cloudflare or another CDN with a S3 clone can step in and sponsor the hosting? I'm not sure if GitLab is willing to provide unlimited traffic for such larges files in the future.

