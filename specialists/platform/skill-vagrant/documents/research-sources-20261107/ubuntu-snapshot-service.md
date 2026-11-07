<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://snapshot.ubuntu.com/
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://snapshot.ubuntu.com/:
The Ubuntu snapshot service makes it possible to see and use the Ubuntu archive as it was at any specified date and time. Snapshots of the Ubuntu archive are available for any date and time after 1 March 2023. This means that you are able to enable the service on the repositories and use `apt` to query or install packages as they were at any recent date and time.

Common use cases of this service include:

* enabling reproducible deployments of a set of packages as at a particular date and time;
* determining when a change in behaviour occurred in the archive; and
* supporting a structured update workflow, for example where a snapshot is validated in  
  one environment before being released to other environments.

Snapshots are supported in Ubuntu 23.10 onwards, plus on updated installations of Ubuntu 20.04 LTS (`apt` 2.0.10) and Ubuntu 22.04 LTS (`apt` 2.4.11). We intend to ensure snapshots are available for dates up to at least 2 years in the past, which we may extend if there is demand.

## How to Use Snapshots on Ubuntu

### Enable snapshot service on configured repositories

#### For Ubuntu 24.04 and later

The `apt` included in Ubuntu 24.04 and later automatically detects when snapshots are supported for a repository (any repository with a Snapshots: directive in the Release file). This includes the official Ubuntu repositories, so snapshots for these will be enabled by default.

#### For Ubuntu 23.10 and earlier

On Ubuntu 23.10 and earlier, edit `/etc/apt/sources.list` to add `[snapshot=yes]` into the standard prefix, for example:

```
deb [snapshot=yes] http://archive.ubuntu.com/ubuntu/ jammy main restricted
deb [snapshot=yes] http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted
deb [snapshot=yes] http://security.ubuntu.com/ubuntu jammy-security main restricted
```

### Use a Snapshot ID with apt Commands

#### Snapshot ID format

The Snapshot ID will be the desired date and UTC time in the YYYYMMDDTHHMMSSZ format, for example 20230302T030400Z for 03:04 UTC on 2 March 2023.

#### Using a Snapshot ID with each apt command

Once snapshots are enabled for a repository, it is possible to pass a specific Snapshot ID to most `apt` or `apt-get` commands with `--snapshot [Snapshot ID]` or `-S [Snapshot ID]`, for example:

```
apt update --snapshot 20231102T030400Z
apt policy hello -S 20231102T030400Z
apt install hello --snapshot 20231102T030400Z
```

Note that the `apt update --snapshot [snapshot]` command needs to be run immediately before the other `apt` commands. These commands will also fail if the snapshot format is incorrect or the snapshot does not exist (for example, if you try to use a date before that Ubuntu release existed).

#### Using a specific snapshot for a repository for all apt commands

Enabling snapshots for the repository will allow you to specify a snapshot when using `apt`, as shown above. Alternatively, it is possible to set `apt` to use a particular snapshot for all `apt` commands for a repository, including `unattended-upgrades`. To do this, the specific Snapshot ID (e.g. 20230302T030400Z) can be used in the place of “yes” in the relevant source. If a specific snapshot is configured in this way then it will be used even if a different snapshot ID is given as part of an `apt` command.

For example, on Ubuntu 24.04 LTS onwards:

```
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble noble-updates
Components: main universe
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: 20240301T030400Z

## Ubuntu security updates. Aside from URIs and Suites,
## this should mirror your choices in the previous section.
Types: deb
URIs: http://security.ubuntu.com/ubuntu
Suites: noble-security
Components: main universe
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: 20240301T030400Z
```

Ubuntu 23.10 and earlier:

```
deb [snapshot=20230302T030400Z] http://archive.ubuntu.com/ubuntu/ jammy main restricted
deb [snapshot=20230302T030400Z] http://archive.ubuntu.com/ubuntu/ jammy-updates main restricted
deb [snapshot=20230302T030400Z] http://security.ubuntu.com/ubuntu jammy-security main restricted
```

#### Using a specific snapshot for all repositories that support snapshots

Alternatively, across all supported Ubuntu releases, a snapshot can be set for all repositories that have snapshots enabled on a system using an `apt.conf`a variable. First, ensure the [relevant repositories are enabled](#enable-snapshot-service), and then set `APT::Snapshot` to the relevant snapshot ID, for example:

```
echo 'APT::Snapshot "20240301T030400Z";' | sudo tee /etc/apt/apt.conf.d/50snapshot
```

As above, this snapshot will then be used for all `apt` commands, including `unattended-upgrades`. The system can then be updated to use a different snapshot by simply running the above command again with a different snapshot ID.

### Disable Snapshot Service for a repository

#### For Ubuntu 24.04 and later (Deb822 sources)

As mentioned above, on Ubuntu 24.04 and later, snapshots are enabled automatically for supported repositories. If you do **not** want archive snapshots to be enabled for a repository, edit the relevant sources file (e.g. `/etc/apt/sources.list.d/ubuntu.sources`) to add `Snapshot: no` to the relevant sources, for example:

```
Types: deb
URIs: http://archive.ubuntu.com/ubuntu
Suites: noble noble-updates
Components: main universe
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
Snapshot: no
```

#### For Ubuntu 23.10 and earlier

On Ubuntu 23.10 and earlier the included version of `apt` did not automatically detect snapshot support and so snapshots should not be enabled unless you have added `[snapshot=yes]` to the relevant source (as explained above).
