<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://raw.githubusercontent.com/hashicorp/vagrant/main/CHANGELOG.md
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: scrapling(transient))

---

Content type text/plain; charset=utf-8 cannot be simplified to markdown, but here is the raw content:
Contents of https://raw.githubusercontent.com/hashicorp/vagrant/main/CHANGELOG.md:
## 2.4.10.dev (UNRELEASED)

FEATURES:

- provider/virtualbox: Add support for LSI Logic SAS storage controller [GH-13692]

IMPROVEMENTS:

- provisioner/ansible: Add support for dynamically selecting ansible-playbook inventory argument option based on ansible-core version [GH-13740]
- docs: Add deprecation notice for documentation under website directory [GH-13746]
- docs: Fix typos and lingustic issues in various places [GH-13731]

BUG FIXES:

- core: Fix issue with missing translations when running vagrant login [GH-13747]
- provider/hyperv: Preserve primary disk when resizing disks [GH-13748]

## 2.4.9 (August 21, 2025)

FEATURES:

- provider/virtualbox: Add support for VirtualBox 7.2 [GH-13709]

IMPROVEMENTS:

- docs: Update the node version for the docs site [GH-13713]
- docs: Remove outdated link for Vagrant Cloud [GH-13710]

BUG FIXES:

- provisioner/ansible: Fix OS version detection, when installing Ansible on RHEL-like operating systems [GH-13701]

## 2.4.8 (August 05, 2025)

IMPROVEMENTS:

- core: Improve error message when no matching provider is found for a box [GH-13693]
- core: Improve error message on box add failures [GH-13687]

BUG FIXES:

- core: Fix box add action when adding a box directly from a file [GH-13699]
- provider/hyperv: Fix XML configuration parsing logic, and add additional checks for minimum amount of memory and CPU [GH-13691]
- core: Fix guest network configuration when more than one network interface is present [GH-13686]

## 2.4.7 (June 17, 2025)

BUG FIXES:

- guests/linux: Fix /etc/fstab clean up behavior [GH-13681]
- provider/docker: Fix auto generated container names [GH-13678]
- provider/hyperv: Fix import for XML based configuration [GH-13674]

## 2.4.6 (May 21, 2025)

IMPROVEMENTS:

- core: Improve error messages on box add failures [GH-13660]
- core: Only generate and attach ISO for cloud-init on first boot [GH-13666]
- host/windows: Add basic oscdimg detection on Windows [GH-13668]
- provider/hyperv: Enable cloud-init support [GH-13671]
- provider/virtualbox: Allow link-local IPv6 addresses for hostonly [GH-12653]

BUG FIXES:

- command: Remove server mode checks [GH-13657]
- core: Prevent cloud-init from regenerating and attaching ISO [GH-13666]
- provider/hyperv: Extract machine ID if collection returned [GH-13669]
- provider/hyperv: Fix import failure due to lack of resources [GH-13670]
- provider/virtualbox: Fix VirtualBox private network setup [GH-13659]

## 2.4.5 (April 23, 2025)

FEATURES:

- communicator/none: Add experimental none communicator [GH-13651]

BUG FIXES:

- core/bundler: Handle multiple versions for system specifications [GH-13652]

## 2.4.4 (April 21, 2025)

IMPROVEMENTS:

- communicator/ssh: Update connect retry behavior, make configurable [GH-13628]
- core: Better behavior outside installers [GH-13636]
- guest/amazonlinux: Support networkd based configuration [GH-13626]
- guest/arch: Update networking for recent versions [GH-13640]
- guest/rhel: Fix networking setup in recent versions [GH-13625]
- host/darwin: Remove HFS from ISO creation [GH-13561]
- provider/hyperv: Add dvd disk support [GH-13642]
- provider/hyperv: Update primary disk detection [GH-13643]
- provider/virtualbox: Add VirtioSCSI storage controller support [GH-13587]
- util/powershell: Prefer using pwsh when available [GH-13648]

BUG FIXES:

- command/box: Fix architecture constraints in outdated/updated command [GH-13601]
- command/box: Fix architecture constraint on provider matches [GH-13647]
- communicators/winrm: Catch IO::Timeout when waiting for communicator [GH-13606]
- communicators/ssh: Catch IO::Timeout when waiting for communicator [GH-13606]
- guest/alpine: Fix DHCP assigned default route behavior [GH-13633]
- provider/docker: Handle variation in error text during image removal [GH-13564]
- provider/virtualbox: Use interface name for hostonly configuration [GH-13644]
- synced_folder/smb: Remove `nofail` mount option [GH-13645]

VAGRANT-GO:

- Removed with work archived to vagrant-go branch [GH-13622]

## 2.4.3 (November 12, 2024)

IMPROVEMENTS:

- command/cloud: Support HCP authentication [GH-13540]

BUG FIXES:

- core: Relax constraint on logger dependency [GH-13532]

## 2.4.2 (November 01, 2024)

FEATURES:

- provider/virtualbox: Add support for VirtualBox 7.1 [GH-13513]

IMPROVEMENTS:

- core: Always downcase type value when getting digest for checksum calculation [GH-13471]
- core: Activate all runtime dependencies at startup [GH-13526]
- guest/debian: Fix NFS install capability to prevent hang on install [GH-13411]
- kernel_v2/config: Add warning for IPv6 address ending with :1 [GH-13362]
- provider/docker: Properly match container ID when trailing output is present [GH-13475]
- provider/docker: Support build with containerd storage [GH-13343]
- provider/virtualbox: Allow paused state when booting vm [GH-13496]
- provider/virtualbox: Handling warnings in output when detecting version [GH-13394]
- synced_folder/nfs: Output mounting entry [GH-13383]
- synced_folder/smb: Adjust ordering in mount entry output [GH-13383]

BUG FIXES:

- command/cloud: Fix provider upload [GH-13467]
- host/bsd: Use nfsd update command instead of restart [GH-13490]
- kernel_v2/config: Fix IP address check [GH-13494] 
- provider/docker: Prevent error if network configuration data is missing [GH-13337, GH-13373]
- provider/docker: Fix docker-exec commands to pass kwargs correctly [GH-13488]
- provider/docker: Fix docker to not rebuild image if it already exists [GH-13489]
- provider/virtualbox: Prevent encoding errors within error translation [GH-13525]
- provider/hyperv: Fix configure disks capability [GH-13346]
- provisioner/ansible: Fix version detection [GH-13375]
- provisioner/ansible: Support double digit versions [GH-13493]
- provisioner/salt: Fix bootstrap script URLs [GH-13517]
- synced_folder/nfs: Fix upstart detection [GH-13409]

VAGRANT-GO:

## 2.4.1 (January 19, 2024)

FEATURES:

IMPROVEMENTS:

- communicator/ssh: Support ECDSA type keys for insecure key replacement [GH-13327]
- communicator/ssh: Inspect guest for supported key types [GH-13334]
- core: Update Ruby constraint to allow Ruby 3.3 [GH-13335]
- core/bundler: Force strict dependencies for default gems [GH-13336]
- provisioner/ansible: Support pip installation for RHEL >= 8 [GH-13326]
- util/keypair: Add support for ECDSA keys [GH-13327]

BUG FIXES:

- command/plugin: Fix plugin extension installation on Windows [GH-13328]
- communicator/ssh: Fix private key writing on Windows [GH-13329]
- core: Fix Vagrant SSL helper detection on macOS [GH-13277]
- core: Fix box collection sorting [GH-#13320]
- util/platform: Fix architecture mapping for Windows [GH-13278]

VAGRANT-GO:

## 2.4.0 (October 16, 2023)

FEATURES:

- core: Add architecture support [GH-13239]

IMPROVEMENTS:

- communicator/ssh: Add key type detection on insecure key replacement [GH-13219] 
- core: Extract box files as sparse files [GH-13252]
- keys: Add ed25519 insecure private key [GH-13219]
- util/downloader: Perform best effort revocation checks on Windows [GH-13214]
- util/keypair: Add support for generating ed25519 key pairs [GH-13219]

BUG FIXES:

- core: Fix extension installation path [GH-13215]
- provider/virtualbox: Fix ipv6 static network configuration [GH-13241]

VAGRANT-GO:

- Add basic support for HCL based config [GH-13257]

## 2.3.7 (June 15, 2023)

IMPROVEMENTS:

- command/ssh: Enable deprecated key types and algorithms [GH-13179]
- core: Update user error message on failed extension installs [GH-13207]
- core: Support loading legacy providers in OpenSSL 3 [GH-13178]
- provisioner/salt: Verify bootstrap-salt download [GH-13166]

BUG FIXES:

- communicator/ssh: Remove keyboard-interactive auth method [GH-13194]
- provisioner/salt: Fix usage on Windows guests [GH-13086]

VAGRANT-GO:

- Update data layer implementation [GH-12904]
- Update dependencies [GH-13201]

## 2.3.6 (May 19, 2023)

BUG FIXES:

- command/serve: Isolate proto constants to file for auto-loading [GH-13165]
- core/util: Unlock file prior to deletion [GH-13159]
- provider/docker: Attempt using docker command for bridge ip [GH-13153]
- provider/virtualbox: Update preferred locale values for driver [GH-13160]

## 2.3.5 (May 15, 2023)

BUG FIXES:

- communicator/ssh: Use netssh builtin keep alive functionality [GH-13069]
- communicator/ssh: Update connection settings when using a password to connect ssh [GH-13052]
- core:  Add a file mutex when downloading box files [GH-13057]
- guest/arch: Support differentiating between Artix and Arch Linux [GH-13055]
- host/windows: Get state of Windows feature "Microsoft-Hyper-V-Hypervisor" [GH-11933]
- provider/docker: Ignore inactive docker containers when assigning ports [GH-13146]
- provider/docker: Sync folders before preparing nfs settings [GH-13149]
- provider/virtualbox: De-duplicate machine port forward info [GH-13056]
- provider/virtualbox:  Remove check for hyperv being enabled when verifying virtualbox is usable on windows [GH-13090]
- provider/virtualbox: Validate LANG value when possible [GH-13150]
- provider/hyperv: Check for hyper-v feature "EnhancedSessionTransportType" [GH-12280]
- provisioner/ansible: Fix installing Ansible provisioner with version and pip [GH-13054]
- synced_folders/rsync: allow rsync-auto to also ignore relative paths [GH-13066]

NOTE: Vagrant installer packages were updated to Ruby 3

## 2.3.4 (December 9, 2022)

IMPROVEMENTS:

- host/darwin: Isolate loading incompatible libraries to support EOL platforms [GH-13022]
- provider/virtualbox: Detect network type when not provided [GH-13024]

BUG FIXES:

- host/windows: Add fix for Powershell 7.3.0 [GH-13006]
- provider/virtualbox: Adjust hostnet DHCP configuration, ignore invalid devices [GH-13004]
- provisioner/ansible: Fix install package names on older debian (and derivatives) versions [GH-13017]

## 2.3.3 (November 15, 2022) 

IMPROVEMENTS:

- core: Bump net-ssh dependency to 7.0 and remove patches [GH-12979]
- synced_folders/rsync: Include ssh `extra_args` value [GH-12973]

BUG FIXES:

- command/serve: Force root level namespace for Google constant [GH-12989]
- guest/solaris: Fix insecure key authorized keys removal [GH-12740]
- provider/virtualbox: Fix `:private_network` support for VirtualBox 7 on macOS [GH-12983]
- provider/virtualbox: Prevent localization of command output [GH-12994]
- provisioner/ansible: Update setup packages in debian capability [GH-12832]

## 2.3.2 (October 18, 2022)

FEATURES:

- provider/virtualbox: Add support for VirtualBox 7.0 [GH-12947]

## 2.3.1 (September 29, 2022)

IMPROVEMENTS:

- core: Raise error if required metadata.json box fields are not present [GH-12895]
- core: Provider helpful error when box version format is invalid [GH-12911]

BUG FIXES:

- Fix flakiness when bringing up a machine that forwards ssh [GH-12909]
- communicator/ssh: Fix `private_key_path` behavior when `keys_only` is disabled [GH-12885]
- synced_folder/nfs: Update exports file creation [GH-12910]
- util/downloader: Fix user agent [GH-12925]

VAGRANT-GO:

- Support secret interactive input [GH-12876]
- Support terminal coloring [GH-12888]
- Validate if requested provider is usable and append/prepend information to errors [GH-12898]
- Raise error if required metadata.json box fields are not present [GH-12919]

## 2.3.0 (August 5, 2022)

FEATURES:

- core: Introduce vagrant-go [GH-12819]

IMPROVEMENTS:

- core: Set rsa-sha2 in kex algorithm set to enable in key exchange [GH-12584]
- core/bundler: Improve Gem spec selection when resolving [GH-12567]
- push/heroku: Display output from push [GH-12646]

BUG FIXES:

- host/darwin: Fix `NameError` for version capability [GH-12581]
- push/ftp:  Fix `VAGRANT_CWD` handling [GH-12645]
- guests/redhat: Fix NFS shares on Rocky 9 guests [GH-12813]

## 2.2.19 (November 5, 2021)

IMPROVEMENTS:

- guest/suse: Add fallback shutdown for versions without systemd [GH-12489]
- provider/virtualbox: Validate VirtualBox hostonly network range [GH-12564]

BUG FIXES

- guest/atomic: Update detection to prevent matching on non-atomic guests [GH-12575]
- guest/coreos: Fix configure network capability [GH-12575]
- guest/windows: Fix directory creation with rsync [GH-11880]
- host/windows: Properly handle spaces in path to SSH key [GH-12398]
- provisioner/chef: Update install checks [GH-12555]

## 2.2.18 (July 27, 2021)

BUG FIXES:

- core: Fix of plugin manager kwargs [GH-12452]
- providers/docker: Pass in docker command opts as a map [GH-12449]
- providers/hyperv: Fix network address detection [GH-12472]

## 2.2.17 (July 7, 2021)

FEATURES:

- guest/rocky: Add guest support for Rocky Linux [GH-12440]

IMPROVEMENTS:

- command/package: Add --info flag to package command [GH-12304]
- guest/debian: Retry network setup on debain [GH-12421]
- guest/suse: Use systemctl poweroff in the background instead of shutdown [GH-12439]
- guest/windows: Get powershell path in %WINDIR%/System32 [GH-12436]
- host/windows: Check Domain and Application Directory contexts for credentials when validating SMB creds [GH-12428]
- providers/hyper-v: Fix IP detection when multiple devices are attached [GH-12232]
- provisioner/ansible: Detects new versions of ansible-4.0.0+ [GH-12391]
- provisioner/ansible: Strip whitespace from ansible version [GH-12420]
- provisioner/salt: Always use upstream Salt bootstrap script on Windows [GH-12127]
- provisioner/salt: Use more conservative TLS settings to work on older .NET versions [GH-12413]
- provisioner/shell: Buffer output to display full lines [GH-12437]
- vagrant: Updates to support Ruby 3.0 [GH-12427]

BUG FIXES:

- command/cloud: Fix authentication middleware to prevent breaking local paths [GH-12419]
- communicator/ssh: Fix net-ssh patches for RSA signatures [GH-12415]
- core: Add box directly with authed urls [GH-12278]

## 2.2.16 (April 29, 2021)

IMPROVEMENTS:

- guest/linux: Detect in process shutdown in reboot capability [GH-12302]
- util/powershell: Support `pwsh` executable in new versions of powershell [GH-12335]

BUG FIXES:

- communicator/ssh: Properly handle authentication with RSA keys [GH-12298]
- guest/fedora: Import guest detection module [GH-12275]
- guest/linux: Fix SMB folder mount name capability call [GH-12281]
- provider/docker: Properly handle updated buildkit build output [GH-12300]

## 2.2.15 (March 30, 2021)

IMPROVEMENTS:

- command/cloud: Remove access token URL parameter by default [GH-12234]
- command/cloud: Add VAGRANT_SERVER_ACCESS_TOKEN_BY_URL to revert access token behavior [GH-12252]
- core: Bump vagrant_cloud dependency to 3.0.3 [GH-12200]
- core: Bump listen gem version and remove ruby_dep [GH-12148]
- core: Bump vagrant_cloud dependency to 3.0.4 [GH-12242]
- core/bundler: Update resolution handling when outside of installer and bundler [GH-12225]
- core/plugin: Provide friendlier error messages on install fail when possible [GH-12225]
- guest/openwrt: Add support for OpenWrt guests [GH-11791]
- guest/freebsd: FreeBSD updated ansible to py37-ansible [GH-12201]
- provider/virtualbox: Get default dhcp ip from a matching host ip [GH-12211]
- util/downloader: Prevent redirect notification for default store [GH-12235]

BUG FIXES:

- command/cloud: Automatically disable direct uploads when file is too large [GH-12250]
- core: Make shell script for loop shell agnostic [GH-12205]
- core: Raise error if downloading box metadata fails [GH-12189]
- core: Apply download options to metadata requests [GH-12177]
- core: Don't try to find "" by prefix in the machine index [GH-12188]
- core: Don't count not created machines as declined when destroying [GH-12186]
- core: Bump bcrypt_pbkdf version [GH-12216]
- core: Remove all space from checksums [GH-12168]
- core/bundler: Do not include default gems as pinned constraints [GH-12253]
- core/synced_folders: Extract os friendly mount name for vbox shared folders [GH-12184]
- guest/alpine: Check if interface exists before shutting it down [GH-12181]
- guest/nixos: Fix network config for recent NixOS releases [GH-12152]
- guest/fedora: Detect fedora using os-releases id [GH-12230]

## 2.2.14 (November 20, 2020)

IMPROVEMENTS:

- host/windows: Update filesystem type matching on WSL2 [GH-12056]
- provisioner/salt: Modernize Salt bootstrap script [GH-12135]

BUG FIXES:

- core: Track raw actions as they are applied to prevent multiple insertions [GH-12037]
- core/bundler: Update solution file resolution to support prerelease matching [GH-12054]
- guest/darwin: Mount vmware synced folders for big sur guests [GH-12053]

## 2.2.13 (November 06, 2020)

BUG FIXES:

- core/bundler: Adjust request sets properly with non-development prerelease [GH-12025]

## 2.2.12 (November 06, 2020)

BUG FIXES:

- core/bundler: Automatically enable prerelease dependency resolution [GH-12023]

NOTE: This is a fix release to resolve an immediate issue with Vagrant
      plugin functionality

## 2.2.11 (November 05, 2020)

IMPROVEMENTS:

- command/cap: Add ability to specify target [GH-11965]
- command/cloud: Add --force flag to `version release` command [GH-11912]
- command/cloud: Updates to utilize the 3.0 version of vagrant_cloud [GH-11916]
- core: Switch from unmaintained gem erubis to erubi [GH-11893]
- core: Download Vagrant boxes using auth headers [GH-11835]
- core: Remove dependency on mime gem [GH-11857]
- core: Handle Errno::EALREADY exceptions on port check [GH-12008]
- core: Fix missing hook/trigger insertion into action stack [GH-12014]
- guest/linux: Make max reboot wait duration configurable [GH-12011]
- guest/windows: Make max reboot wait duration configurable [GH-12011]
- providers/virtualbox: Fix availability check of provider [GH-11936]
- tests: Add integration tests for Docker provider [GH-11907]

BUG FIXES:

- core/synced_folders: Don't persist synced folders to fstab if guest is not reachable [GH-11900]
- core: Don't try to recover machine without a uuid [GH-11863]
- config/disks: Transform provider specific config to common form [GH-11939]
- config/vm: Override synced-folder `:nfs` option [GH-11988]
- contrib/zsh: Remove newline from beginning of completion script [GH-11963]
- guests/arch: Install smbclient when setting up arch smb [GH-11923]
- guest/linux: Check for /etc/fstab before trying to modify [GH-11897]
- guest/linux: Create an /etc/fstab if does not exist [GH-11909]
- guest/linux: Persist SMB mounts [GH-11846]
- guest/debian: Set hostname in /etc/hosts as first step to changing hostname [GH-11885]
- guest/rhel: Check for existence of network files before trying to update them [GH-11877]
- guest/suse: Don't use hostnamectl to set hostname if not available on system [GH-11996]
- tests: Remove rsync dependency from tests [GH-11889]

## 2.2.10 (August 24, 2020)

FEATURES:

- hyperv/disks: Add ability to manage virtual disks for guests [GH-11541]

IMPROVEMENTS:

- core: Allow provisioners to be run when a communicator is not available [GH-11579]
- core: Add `autocomplete` command that allows for install of bash or zsh autocomplete scripts [GH-11523]
- core: Update to childprocess gem to 4.0.0 [GH-11717]
- core: Add action to wait for cloud-init to finish running [GH-11773]
- core: Update to net-ssh to 6.0 and net-sftp to 3.0 [GH-11621]
- core: Optimize port in use check for faster validation [GH-11810]
- core: Support for Ruby 2.7 [GH-11814]
- core: Add synced folder capabilities for mount options and default fstab modification behavior [GH-11797]
- guest/arch: Use systemd-networkd to configure networking for guests [GH-11400]
- guest/haiku: Rsync install for rsync synced folders [GH-11614]
- guest/solaris11: Add guest capability shell_expand_guest_path [GH-11759]
- host/darwin: Add ability to build ISO [GH-11694]
- hosts/linux: Add ability to build ISO [GH-11750]
- hosts/windows: Add ability to build ISO [GH-11750]
- providers/hyperv: Add support for SecureBootTemplate setting on import [GH-11756]
- providers/hyperv: Add support for EnhancedSessionTransportType [GH-11014]
- virtualbox/disks: Add ability to manage virtual dvds for guests [GH-11613]

BUG FIXES:

- core: Ensure MapCommandOptions class is required [GH-11629]
- core: Fix `:all` special value on triggers [GH-11688]
- core: Ensure network addresses have a valid netmask [GH-11679]
- core: Recover local machine metadata in global index [GH-11656]
- core: Print CLI help message is ambiguous option provided [GH-11746]
- core: Update how `/etc/hosts` gets updated for darwin, freebsd and openbsd [GH-11719]
- core: Capture `[3J` escape sequence [GH-11807]
- core: Treat empty box value as invalid [GH-11618]
- core: Allow forwarding ports to unknown addresses [GH-11810]
- core: Scrub credentials as whole words [GH-11837]
- commands/destroy: Add gracefull option to switch beween gracefully or forcefully shutting down a vm [GH-11628]
- communicator/ssh: Raise an error for a nil exit status [GH-11721]
- communicator/winrm: Check for nil return from querying for forwarded ports [GH-11831]
- config/vm: Add option `allow_hosts_modification` to allow/disable Vagrant editing the guests `/etc/hosts` file [GH-11565]
- config/vm: Add config option `hostname` to `config.vm.network` [GH-11566]
- config/vm: Don't ignore NFS synced folders on Windows hosts [GH-11631]
- host: Use regular port check for loopback addresses [GH-11654]
- host: Allow windows and linux hosts to detach from rdp process [GH-11732]
- host/windows: Properly register SMB password validation capability [GH-11795]
- guests: Allow setting of hostname according to `hostname` option for multiple guests [GH-11704]
- guest/alpine: Allow setting of hostname according to `hostname` option [GH-11718]
- guest/esxi: Be more permissive with permissions of ssh directory [GH-11587]
- guest/linux: Add virtual box shared folders to guest fstab [GH-11570]
- guest/suse: Allow setting of hostname according to `hostname` option [GH-11567]
- providers/docker: Ensure new containers don't grab existing bound ports [GH-11602]
- providers/hyperv: Fix check for secure boot [GH-11809]
- providers/virtualbox: Fix inability to create disk with same name across multiple guests [GH-11767]
- provisioners/docker: Allow to specify docker image version using the `run` option [GH-11806]
- provisioners/file: Allow creating empty folders [GH-11805]
- provisioners/shell: Ensure Windows shell provisioner gets the correct file extension [GH-11644]
- util/powershell: Use correct powershell executable for privileged commands [GH-11787]

## 2.2.9 (May 07, 2020)

BUG FIXES:

- core/bundler: Properly handle plugin install with available specification [GH-11592]
- provisioners/docker: Fix CentOS docker install and start service capabilities [GH-11581]
- provisioners/podman: Seperate RHEL install from CentOS install [GH-11584]

## 2.2.8 (May 04, 2020)

FEATURES:

- virtualbox/disks: Add ability to manage virtual disks for guests [GH-11349]

IMPROVEMENTS:

- bin/vagrant: Automatically include global options within commands [GH-11473]
- bin/vagrant: Suppress Ruby warnings when not running pre-release version [GH-11446]
- communicator/ssh: Add support for configuring SSH connect timeout [GH-11533]
- core: Update childprocess gem [GH-11487]
- core: Add cli option `--no-tty` [GH-11414]
- core: Overhaul call stack modifications implementation for hooks and triggers [GH-11455]
- core/bundler: Cache plugin solution sets to speed up startup times [GH-11363]
- config/vm: Add`box_download_options` config to specify extra download options for a box [GH-11560]
- guest/alpine: Add ansible provisioner guest support [GH-11411]
- guest/linux: Update systemd? check to use sudo [GH-11398]
- guest/linux: Use systemd if available to halt and reboot system [GH-11407]
- guests/linux: Mount smb folders with `mfsymlinks` option by default [GH-11503]
- guest/redhat: Add support for SMB [GH-11463]
- guest/windows: Rescue all regular exceptions during reboot wait [GH-11428]
- providers/docker: Support catching container name when using podman [GH-11356]
- provisioners/docker: Support Centos8 [GH-11462]
- provisioners/podman: Add Podman as a provisioner [GH-11472]
- provisioners/salt: Allow specifying python_version [GH-11436]

BUG FIXES:

- communicators/winssh: Fix issues with Windows SSH communicator [GH-11430]
- core/bundler: Activate vagrant specification when not active [GH-11445]
- core/bundler: Properly resolve sets when Vagrant is in prerelease [GH-11571]
- core/downloader: Always set `-q` flag as first option [GH-11366]
- core/hooks: Update dynamic action hook implementation to prevent looping [GH-11427]
- core/synced_folders: Validate type option if set [GH-11359]
- guests/debian: Choose netplan renderer based on network configuration and installed tools [GH-11498]
- host/darwin: Quote directories in /etc/exports [GH-11441]
- host/linux: Ensure `/etc/exports` does not contain duplicate records [GH-10591]
- host/windows: Check all interfaces for port conflict when host_ip: "0.0.0.0" [GH-11454]
- providers/docker: Fix issue where Vagrant fails to remove image if it is in use [GH-11355]
- providers/docker: Fix issue with getting correct docker image id from build output [GH-11461]
- providers/hyperv: Prevent error when identity reference cannot be translated [GH-11425]
- provider/hyperv: Use service id for manipulating vm integration services [GH-11499]
- providers/virtualbox: Parse `list dhcpservers` output on VirtualBox 6.1 [GH-11404]
- providers/virtualbox: Raise an error if guest IP ends in .1 [GH-11500]
- provisioners/shell: Ensure windows shell provisioners always get an extension [GH-11517]
- util/io: Fix encoding conversion errors [GH-11571]

## 2.2.7 (January 27, 2020)

IMPROVEMENTS:

- guest/opensuse: Check for basename hostname prior to setting hostname [GH-11170]
- host/linux: Check for modinfo in /sbin if it's not on PATH [GH-11178]
- core: Show guest name in hostname error message [GH-11175]
- provisioners/shell: Linux guests now support `reboot` option [GH-11194]
- darwin/nfs: Put each NFS export on its own line [GH-11216]
- contrib/bash: Add more completion flags to up command [GH-11223]
- provider/virtualbox: Add VirtualBox provider support for version 6.1.x [GH-11250]
- box/outdated: Allow to force check for box updates and ignore cached check [GH-11231]
- guest/alpine: Update apk cache when installing rsync [GH-11220]
- provider/virtualbox: Improve error message when machine folder is inaccessible [GH-11239]
- provisioner/ansible_local: Add pip install method for arch guests [GH-11265]
- communicators/winssh: Use Windows shell for `vagrant ssh -c` [GH-11258]

BUG FIXES:

- command/snapshot/save: Fix regression that prevented snapshot of all guests in environment [GH-11152]
- core: Update UI to properly retain newlines when adding prefix [GH-11126]
- core: Check if box update is available locally [GH-11188]
- core: Ensure Vagrant::Errors are loaded in file_checksum util [GH-11183]
- cloud/publish: Improve argument handling for missing arguments to command [GH-11184]
- core: Get latest version for current provider during outdated check [GH-11192]
- linux/nfs: avoid adding extra newlines to /etc/exports [GH-11201]
- guest/darwin: Fix VMware synced folders on APFS [GH-11267]
- guest/redhat: Ensure `nfs-server` is restarted when installing nfs client [GH-11212]
- core: Do not validate checksums if options are empty string [GH-11211]
- provider/docker: Enhance docker build method to match against buildkit output [GH-11205]
- provisioner/ansible_local: Don't prompt for input when installing Ansible on Ubuntu and Debian [GH-11191]
- provisioner/ansible_local: Ensure all guest caps accept all passed in arguments [GH-11265]
- host/windows: Fix regression that prevented port collisions from being detected [GH-11244]
- core/provisioner: Set top level provisioner name if set in a provisioner config [GH-11295]

## 2.2.6 (October 14, 2019)

FEATURES:

- core/provisioners: Introduce new Provisioner options: before and after [GH-11043]
- guest/alpine: Integrate the vagrant-alpine plugin into Vagrant core [GH-10975]

IMPROVEMENTS:

- command/box/prune: Allow prompt skip while preserving actively in use boxes [GH-10908]
- command/cloud: Support providing checksum information with boxes [GH-11101]
- dev: Fixed Vagrantfile for Vagrant development [GH-11012]
- guest/alt: Improve handling for using network tools when setting hostname [GH-11000]
- guest/suse: Add ipv6 network config templates for SUSE based distributions [GH-11013]
- guest/windows: Retry on connection timeout errors for the reboot capability [GH-11093]
- host/bsd: Use host resolve path capability to modify local paths if required [GH-11108]
- host/darwin: Add host resolve path capability to provide real paths for firmlinks [GH-11108]
- provisioners/chef: Update pkg install flags for chef on FreeBSD guests [GH-11075]
- provider/hyperv: Improve error message when VMMS is not running [GH-10978]
- provider/virtualbox: Raise additional errors for incomplete virtualbox installation on usable check [GH-10938]
- util/filechecksum: Add support for more checksum types [GH-11101]

BUG FIXES:

- command/rsync-auto: Fix path watcher bug so that all subdirectories are synced when changed [GH-11089]
- command/snapshot/save: Ensure VM id is passed to list snapshots for hyper-v provider [GH-11097]
- core: Ensure proper paths are shown in config loading exceptions [GH-11056]
- guest/suse: Use hostnamectl instead of hostname to set the hostname under SUSE [GH-11100]
- provider/docker: Fix default provider validation if password is used [GH-11053]
- provider/docker: Fix Docker providers usable? check [GH-11068]
- provisioner/ansible_local: Ensure pip_install_cmd is finalized to emptry string [GH-11098]
- provisioner/file: Ensure relative path for file provisioner source is relative to guest machines cwd [GH-11099]
- provider/docker: Ensure docker build_args option is properly set in docker compose config yaml [GH-11106]
- guest/suse: Update nfs & service daemon names for suse based hosts and guests [GH-11076]
- provider/docker: Determine ip address prefix workaround for docker public networks [GH-11111]
- provider/docker: Only return interfaces where addr is not nil for networks [GH-11116]

## 2.2.5 (June 19, 2019)

FEATURES:

- providers/docker: Private and Public networking support [GH-10702]

IMPROVEMENTS:

- command/global-status: Provide machine-readable information [GH-10506]
- command/snapshot: Separate snapshot names for guests when listing snapshots [GH-10828]
- command/box/update: Ignore missing metadata files when updating all boxes [GH-10829]
- core: Use consistent settings when unpacking boxes as root [GH-10707]
- core: Write metadata.json file when packaging box [GH-10706]
- core: Remove whitespace from id file on load [GH-10727]
- core/bundler: Support resolution when installed within system [GH-10894]
- guest/coreos:  Update network configuration and hostname setting [GH-10752]
- guest/freebsd: Add proper VirtualBox share folders support for FreeBSD guests [GH-10717]
- guest/freebsd: Add unmount share folder for  VirtualBox guests [GH-10761]
- guest/freebsd: Simplify network interface listing when configuring networks [GH-10763]
- providers/docker: Add usable? check to docker provider [GH-10890]
- synced_folder/smb: Remove configuration information from synced folder data [GH-10811]

BUG FIXES:

- command/box/update: Ensure the right version is picked when updating specific boxes [GH-10810]
- command/cloud: Properly set variable from CLI argument parsing for `username` field [GH-10726]
- command/rsync_auto: Use relative paths to machines folder path for file path Listener [GH-10902]
- communicator/ssh: Remove net/sftp loading to prevent loading errors [GH-10745]
- contrib/bash: Search for running_vm_list only in `machines` folder [GH-10841]
- core/bundler: Properly parse multiple constants when installing plugins [GH-10896]
- core/environment: Support plugin configuration within box Vagrantfiles [GH-10889]
- core/triggers: Fix typo in UI output [GH-10748]
- core/triggers: Properly exit with abort option [GH-10824]
- core/triggers: Ensure guest names are string when filtering trigger configs [GH-10854]
- core/triggers: Abort after all running processes have completed when parallel is enabled [GH-10891]
- guest/void: Fix NFS capability detection [GH-10713]
- guest/bsd: Properly set BSD options order for /etc/exports [GH-10909]
- host/windows: Fix rubygems error when host has directory named `c` [GH-10803]
- provider/virtualbox: Ensure non-existent machines do not attempt to list snapshots [GH-10784]
- provider/docker: Properly set docker-compose config file with volume names [GH-10820]
- provisioner/ansible: Fix pip installer hardcoded curl get_pip.py piped to python [GH-10625]
- provisioner/chef: Update chef install check for guests [GH-10917]
- synced_folders/rsync: Remove rsync__excludes from command if array is empty [GH-10901]

## 2.2.4 (February 27, 2019)

FEATURES:

- core/triggers: Introduce new option `:type` for actions, hooks, and commands [GH-10615]

IMPROVEMENTS:

- communicator/ssh: Update `#upload` behavior to work properly with new sshd path checks [GH-10698]
- communicator/winrm: Update `#upload` behavior to match ssh communicator upload behavior [GH-10698]
- guest/windows: Add reboot output to guest capability [GH-10638]
- provisioner/file: Refactor path modification rules and allow communicator to handle details [GH-10698]

BUG FIXES:

- core: Fix format finalization of plugins in Vagrantfile [GH-10664]
- core: Fix SIGINT behavior and prevent backtrace [GH-10666]
- core: Change remaining box_client_cert refs to box_download_client_cert [GH-10622]
- core: Move over AddAuthentication middleware and hooks  out of deprecated class [GH-10686]
- guest/debian: Properly set DHCP for systemd-networkd ips [GH-10586]
- guest/solaris11: Create interface if required before configuration [GH-10595]
- installers/appimage: Use ld path with appimage libs on suffix [GH-10647]
- providers/docker: Expand paths when comparing synced folders on reload [GH-10645]
- providers/virtualbox: Fix import paths on Windows with VirtualBox 6 [GH-10629]
- synced_folders/rsync: Properly clean up tmp folder created during rsync [GH-10690]

## 2.2.3 (January 9, 2019)

FEATURES:

- host/void: Add host support for void linux [GH-10012]

IMPROVEMENTS:

- command/rsync-auto: Prevent crash on post-rsync command failure [GH-10515]
- command/snapshot: Raise error for bad subcommand [GH-10470]
- command/package: Ensure temp dir for package command is cleaned up [GH-10479]
- command/powershell: Support running elevated commands [GH-10528]
- communicator/ssh: Add `config` and `remote_user` options [GH-10496]
- core: Display version update on stderr instead of stdout [GH-10482]
- core: Add experimental feature flag [GH-10485]
- core: Show box version during box outdated check [GH-10573]
- guest/windows: Modify elevated username only on username failure [GH-10488]
- host/windows: Prevent SMB setup commands from becoming too long [GH-10489]
- host/windows: Automatically answer yes when pruning SMB shares [GH-10524]
- provisioners/file: Show source and destination locations with file provisioner [GH-10570]
- provisioners/salt: Validate that `install_type` is set if `version` is specified [GH-10474]
- provisioners/salt: Update default install version [GH-10537]
- provisioners/shell: Add `reboot` option for rebooting supported guest [GH-10532]
- synced_folders/rsync: Support using rsync `--chown` option [GH-10529]
- util/guest_inspection: Validate hostnamectl command works when detected [GH-10512]
- util/platform: Use wslpath command for customized root on WSL [GH-10574]

BUG FIXES:

- command/cloud publish: Ensure box file exists before path expanding [GH-10468]
- command/cloud publish: Catch InvalidVersion errors from vagrant_cloud client [GH-10513]
- command/snapshot: Retain consistent provisioning behavior across all commands [GH-10490]
- command/validate: Bypass install checks for validating configs with the `--ignore-provider` flag [GH-10467]
- communicator/ssh: Fix garbage output detection [GH-10571]
- guest/alt: Fix network configuration errors [GH-10527]
- guest/coreos: Fix grep command for network interface of CoreOS guest [GH-10554]
- guest/freebsd: Fix defaultrouter rcvar in static network template [GH-10469]
- guest/redhat: Fix network configuration errors [GH-10527]
- providers/virtualbox: Adjust version requirement for NIC warning [GH-10486]
- util/powershell: Use correct Base64 encoding for encoded commands [GH-10487]

## 2.2.2 (November 27, 2018)

BUG FIXES:

- providers/virtualbox: Update default_nic_type implementation and add warning [GH-10450]

## 2.2.1 (November 15, 2018)

FEATURES:

- core/plugins: Add reset! method to communicator [GH-10399]
- providers/virtualbox: Add support for VirtualBox 6.0 [GH-10379]

IMPROVEMENTS:

- command/validate: Allow validation of config while ignoring provider [GH-10351]
- communicators/ssh: Prevent overly verbose output waiting for connection [GH-10321]
- communicators/ssh: Support ed25519 keys [GH-10365]
- communicators/ssh: Add reset! implementation [GH-10399]
- communicators/winrm: Add reset! implementation [GH-10399]
- core: Limit number of automatic box update checks [GH-10359]
- host/windows: Remove PATH check in WSL detection [GH-10313]
- providers/hyperv: Disable automatic checkpoints before deletion [GH-10406]
- providers/virtualbox: Add `automount` flag if specified with synced_folder [GH-10326]
- providers/virtualbox: Refactor host only network settings [GH-7699]
- providers/virtualbox: Support setting default NIC type for network adapters [GH-10383]
- providers/virtualbox: Update ssh_port helper to handle multiple matches [GH-10409]
- provisioners/shell: Add :reset option to allow communicator reset [GH-10399]
- synced_folders/smb: Allow for 'default' smb_username in prompt if set [GH-10319]
- util/network_ip: Simplify `network_address` helper [GH-7693]
- util/platform: Prevent hard failure during hyper-v enabled check [GH-10332]

BUG FIXES:

- command/login: Only show deprecation warning when command is invoked [GH-10374]
- core: Fallback to Vagrantfile defined box information [GH-10368]
- core/bundler: Update source ordering to properly resolve with new RubyGems [GH-10364]
- core/triggers: Only split inline script if host is non-Windows [GH-10405]
- communicator/winrm: Prepend computer name to username when running elevated commands [GH-10387]
- guest/debian: Fix halting issue when setting hostname by restarting networking on guest [GH-10301, GH-10330]
- guest/linux: Fix vagrant user access to docker after install [GH-10399]
- guest/windows: Add reboot capability to fix hostname race condition [GH-10347]
- guest/windows: Allow for reading key paths with spaces [GH-10389]
- host/windows: Fix powershell to properly handle paths with spaces [GH-10390]
- providers/docker: Deterministic host VM synced folder location for Docker VM [GH-10311]
- providers/hyperv: Fix network vlan configuration script [GH-10366]
- providers/hyperv: Properly output error message on failed guest import [GH-10404]
- providers/hyperv: Fix typo in network configuration detection script [GH-10410]

## 2.2.0 (October 16, 2018)

FEATURES:

- command/cloud: Introduce `vagrant cloud` subcommand to Vagrant [GH-10148]
- command/upload: Add command for uploading files to guest [GH-10263]
- command/winrm: Add command for executing guest commands via WinRM [GH-10263]
- command/winrm-config: Add command for providing WinRM configuration [GH-10263]

IMPROVEMENTS:

- core: Ensure file paths are identical when checking for cwd [GH-10220]
- core: Add config option `ignore_box_vagrantfile` for ignoring vagrantfile inside box [GH-10242]
- core/triggers: Add abort option to core triggers [GH-10232]
- core/triggers: Introduce `ruby` option for trigger [GH-10267]
- contrib/bash: Add completion for snapshot names for vagrant snapshot restore|delete [GH-9054]
- providers/docker: Build docker from git repo [GH-10221]
- providers/hyperv: Update Hyper-V admin check and allow override via ENV variable [GH-10275]
- providers/virtualbox: Allow base_mac to be optional [GH-10255]
- provisioners/salt: bootstrap-salt.sh: use -s with curl [GH-9432]
- provisioners/salt: remove leading space with bootstrap_options [GH-9431]

BUG FIXES:

- core/environment: Provide rgloader for local plugin installations [GH-10279]
- contrib/sudoers/osx: Fix missing comma and add remove export alias [GH-10235]
- guest/redhat: Update restart logic in redhat change_host_name cap [GH-10223]
- guest/windows: Allow special characters in SMB password field [GH-10219]
- providers/hyperv: Only use AutomaticCheckpointsEnabled when available [GH-10264]
- providers/hyperv: Only use CheckpointType when available [GH-10265]
- provisioners/ansible: Fix remote directory creation [GH-10259, GH-10258]
- provisioners/puppet: Properly set env variables for puppet provisioner on windows [GH-10218]
- provisioners/salt: Properly set salt pillar variables for windows guests [GH-10215]
- synced_folders/rsync: Ensure unique tmp dirs for ControlPath with rsync [GH-10291]

## 2.1.5 (September 12, 2018)

IMPROVEMENTS:

- core: Add `Vagrant.version?` helper method [GH-10191]
- core: Scrub sensitive values from logger output [GH-10200]
- core: Prevent multiple evaluations of Vagrantfile [GH-10199]
- command/init: Support VAGRANT_DEFAULT_TEMPLATE env var [GH-10171]
- command/powershell: Improve doc help string and fix winrm locales error [GH-10189]
- contrib/bash: autocomplete running VM names for destroy subcommand [GH-10168]
- guest/debian: Use `sudo` to determine if systemd is in use for hardened systems [GH-10198]
- guest/openbsd: Add IPv6 network template for OpenBSD machines [GH-8912]
- provisioners/salt: Allow non-windows hosts to pass along version [GH-10194]

BUG FIXES:

- core: Fix Vagrant.has_plugin? behavior before plugins are initialized [GH-10165]
- core: Check verify_host_key for falsey or :never values when generating ssh config [GH-10182]
- guest/linux: Filter out empty strings and loopback interfaces when constructing list of network interfaces [GH-10092]
- provider/hyper-v: Check for automatic checkpoint support before configuring [GH-10181]

## 2.1.4 (August 30, 2018)

BUG FIXES:

- core: Fix local plugin installation prompt answer parsing [GH-10154]
- core: Reset internal environment after plugin loading [GH-10155]
- host/windows: Fix SMB list parsing when extra fields are included [GH-10156]
- provisioners/ansible_local: Fix umask setting permission bug [GH-10140]

## 2.1.3 (August 29, 2018)

FEATURES:

- core: Support for project specific plugins [GH-10037]

IMPROVEMENTS:

- command/reload: Add `--force` flag to reload command [GH-10123]
- communicator/winrm: Display warning if vagrant-winrm plugin is detected [GH-10076]
- contrib/bash: Replace -VAGRANTSLASH- with literal slash in completion [GH-9987]
- core: Show installed version of Vagrant when displaying version check [GH-9968]
- core: Retain information of original box backing active guest [GH-10083]
- core: Only write box info if provider supports box objects [GH-10126]
- core: Update net-ssh dependency constraint to ~> 5.0.0 [GH-10066]
- core/triggers: Catch and allow for non-standard exit codes with triggers `run` options [GH-10005]
- core/triggers: Allow for spaces in `path` for trigger run option [GH-10118]
- guest/debian: Isolate network interface configuration to individual files for systemd [GH-9889]
- guest/redhat: Use libnfs-utils package if available [GH-9878]
- provider/docker: Support Docker volume consistency for synced folders [GH-9811]
- provider/hyperv: Disable synced folders on non-DrvFs file systems by default [GH-10001]
- util/downloader: Support custom suffix on user agent string [GH-9966]
- util/downloader: Prevent false positive matches on Location header [GH-10041]
- util/subprocess: Force system library paths for executables external to AppImage [GH-10078]

BUG FIXES:

- core: Disable Vagrantfile loading with plugin commands [GH-10030]
- core: Ensure the SecureRandom library is loaded for the trigger class [GH-10063]
- core/triggers: Allow trigger run args option to be a single string [GH-10116]
- util/powershell: Properly `join` commands from passed in array [GH-10115]
- guest/solaris: Add back guest detection check for Solaris derived guests [GH-10081]
- guest/windows: Be more explicit when invoking cmd.exe with mount_volume script [GH-9976]
- host/linux: Fix sudo usage in NFS capability when modifying exports file [GH-10084]
- host/windows: Remove localization dependency from SMB list generation [GH-10043]
- provider/docker: Convert windows paths for volume mounts on docker driver [GH-10100]
- provider/hyperv: Fix checkpoint configuration and properly disable automatic checkpoints by default [GH-9999]
- provider/hyperv: Remove localization dependency from access check [GH-10000]
- provider/hyperv: Enable ExposeVirtualizationExtensions only when available [GH-10079]
- provider/virtualbox: Skip link-local when fixing IPv6 route [GH-9639, GH-10077]
- push/ftp: Custom error when attempting to push too many files [GH-9952]
- util/downloader: Prevent errors when Location header contains relative path [GH-10017]
- util/guest_inspection: Prevent nmcli check from hanging when pty is enabled [GH-9926]
- util/platform: Always force string type conversion on path [GH-9998]

## 2.1.2 (June 26, 2018)

IMPROVEMENTS:

- commands/suspend: Introduce flag for suspending all machines [GH-9829]
- commands/global-status: Improve message about removing stale entries [GH-9856]
- provider/hyperv: Attempt to determine import failure cause [GH-9936]
- provider/hyperv: Update implementation. Include support for modifications on reload [GH-9872]
- provider/hyperv: Validate maxmemory configuration setting [GH-9932]
- provider/hyperv: Enable provider within WSL [GH-9943]
- provider/hyperv: Add Hyper-V accessibility check on data directory path [GH-9944]
- provisioners/ansible_local: Improve installation from PPA on Ubuntu guests.
    The compatibility is maintained only for active long-term support (LTS) versions,
    i.e. Ubuntu 12.04 (Precise Pangolin) is no longer supported. [GH-9879]

BUG FIXES:

- communicator/ssh: Update ssh private key file permission handling on Windows [GH-9923, GH-9900]
- core: Display plugin commands in help [GH-9808]
- core: Ensure guestpath or name is set with synced_folder option and dont set guestpath if not provided [GH-9692]
- guest/debian: Fix netplan generation when using DHCP [GH-9855]
- guest/debain: Update priority of network configuration file when using networkd [GH-9867]
- guest/ubuntu: Update netplan config generation to detect NetworkManager [GH-9824]
- guest/ubuntu: Fix failing Ansible installation from PPA on Bionic Beaver (18.04 LTS) [GH-9796]
- host/windows: Prevent processing of last SMB line when using net share [GH-9917]
- provisioner/chef: Prevent node_name set on configuration with chef_apply [GH-9916]
- provisioner/salt: Remove usage of masterless? config attribute [GH-9833]

## 2.1.1 (May 7, 2018)

IMPROVEMENTS:

- guest/linux: Support builtin vboxsf module for shared folders [GH-9800]
- host/windows: Update SMB capability to work without Get-SmbShare cmdlet [GH-9785]

BUG FIXES:

- core/triggers: Initialize internal trigger object for machine before initializing provider [GH-9784]
- core/triggers: Ensure internal trigger fire does not get called if plugin installed [GH-9799]
- provider/hyperv: Call import script with switchid instead of switchname [GH-9781]

## 2.1.0 (May 3, 2018)

FEATURES:

- core: Integrate vagrant-triggers plugin functionality into core Vagrant [GH-9713]

IMPROVEMENTS:

- core: Improve messaging around not finding requested provider [GH-9735]
- core: Disable exception reports by default [GH-9738]
- core: Continue on if vagrant fails to parse metadata box for update [GH-9760]
- hosts/linux: Support RDP capability within WSL [GH-9758]
- hosts/windows: Add SMB default mount options capability and set default version to 2.0 [GH-9734]
- provider/hyperv: Include neighbor check for MAC on guest IP detection [GH-9737]
- provider/virtualbox: Do not require VirtualBox availability within WSL [GH-9759]
- provisioner/chef_zero: Support arrays for data_bags_path [GH-9669]
- util/downloader: Don't raise error if response is HTTP 416 [GH-9729]
- util/platform: Update Hyper-V enabled check [GH-9746]

BUG FIXES:

- communicators/ssh: Log error and proceed on Windows private key permissions [GH-9769]
- middleware/authentication: Prevent URL modification when no changes are required [GH-9730]
- middleware/authentication: Ignore URLs which cannot be parsed [GH-9739]
- provider/hyperv: Reference switches by ID instead of name [GH-9747]
- provider/docker: Use Util::SafeExec if docker-exec is run with `-t` option [GH-9761]
- provisioner/chef: Trim drive letter from path on Windows [GH-9766]
- provisioner/puppet: Properly finalize structured_facts config option [GH-9720]
- util/platform: Fix original WSL to Windows path for "root" directory [GH-9696]

## 2.0.4 (April 20, 2018)

FEATURES:

- core: Vagrant aliases [GH-9504]

IMPROVEMENTS:

- communicators/ssh: Update file permissions when generating new key pairs [GH-9676]
- core: Make resolv-replace usage opt-in instead of opt-out [GH-9644]
- core: Suppress error messages from checkpoint runs [GH-9645]
- guests/coreos: Identify operating systems closely related to CoreOS [GH-9600]
- guests/debian: Adjust network configuration file prefix to 50- [GH-9646]
- guests/photon: Less specific string grep to fix PhotonOS 2.0 detection [GH-9528]
- guests/windows: Fix slow timeout when updating windows hostname [GH-9578]
- hosts/windows: Make powershell version detection timeout configurable [GH-9506]
- providers/virtualbox: Improve network collision error message [GH-9685]
- provisioner/chef_solo: Improve Windows drive letter removal hack for remote paths[GH-9490]
- provisioner/chef_zero: File path expand all chef_zero config path options [GH-9690]
- provisioner/puppet: Puppet structured facts toyaml on provisioner [GH-9670]
- provisioner/salt: Add master_json_config & minion_json_config options [GH-9420]
- util/platform: Warn on ArgumentError exceptions from encoding [GH-9506]

BUG FIXES:

- commands/package: Fix uninitialized constant error [GH-9654]
- communicators/winrm: Fix command filter to properly parse commands [GH-9673]
- hosts/windows: Properly respect the VAGRANT_PREFER_SYSTEM_BIN environment variable [GH-9503]
- hosts/windows: Fix virtualbox shared folders path for windows guests [GH-8099]
- guests/freebsd: Fix typo in command that manages configuring networks [GH-9705]
- util/checkpoint_client: Respect VAGRANT_CHECKPOINT_DISABLE environment variable [GH-9659]
- util/platform: Use `--version` instead of `version` for WSL validation [GH-9674]

## 2.0.3 (March 15, 2018)

IMPROVEMENTS:

  - guests/solaris: More explicit Solaris 11 and inherit SmartOS from Solaris [GH-9398]
  - hosts/windows: Add support for latest WSL release [GH-9525, GH-9300]
  - plugins/login: Update middleware to re-map hosts and warn on custom server [GH-9499]
  - providers/hyper-v: Exit if Hyper-V is enabled and VirtualBox provider is used [GH-9456]
  - provisioners/salt: Change to a temporary directory before downloading script files [GH-9351]
  - sycned_folders/nfs: Default udp to false when using version 4 [GH-8828]
  - util/downloader: Notify on host redirect [GH-9344]

BUG FIXES:

  - core: Use provider override when specifying box_version [GH-9502]
  - guests/debian: Renew DHCP lease on hostname change [GH-9405]
  - guests/debian: Point hostname to 127.0.1.1 in /etc/hosts [GH-9404]
  - guests/debian: Update systemd? check for guest inspection [GH-9459]
  - guests/debian: Use ip route in dhcp template [GH-8730]
  - guests/gentoo: Disable if/netplugd when setting up a static ip on a gentoo guest using openrc [GH-9261]
  - guests/openbsd: Atomically apply new hostname.if(5) [GH-9265]
  - hosts/windows: Fix halt problem when determining powershell version on old powershells [GH-9470]
  - hosts/windows: Convert to windows path if on WSL during vbox export [GH-9518]
  - providers/virtualbox: Fix hostonly matching not respecting :name argument [GH-9302]
  - util/credential_scrubber: Ignore empty strings [GH-9472, GH-9462]

## 2.0.2 (January 29, 2018)

FEATURES:

  - core: Provide mechanism for removing sensitive data from output [GH-9276]
  - core: Relax Ruby constraints to include 2.5 [GH-9363]
  - core: Hide sensitive values in output [GH-9369]
  - command/init: Support custom Vagrantfile templates [GH-9202]
  - guests: Add support for the Haiku operating system [GH-7805, GH-9245]
  - synced_folders/smb: Add support for macOS hosts [GH-9294]
  - vagrant-spec: Update vagrant-spec to include Windows platforms and updated linux boxes [GH-9183]

IMPROVEMENTS:

  - config/ssh: Deprecate :paranoid in favor of :verify_host_key [GH-9341]
  - core: Add optional timestamp prefix on log output [GH-9269]
  - core: Print more helpful error message for NameEror exceptions in Vagrantfiles [GH-9252]
  - core: Update checkpoint implementation to announce updates and support notifications [GH-9380]
  - core: Use Ruby's Resolv by default [GH-9394]
  - docs: Include virtualbox 5.2.x as supported in docs [GH-9237]
  - docs: Improve how to pipe debug log on powershell [GH-9330]
  - guests/amazon: Improve guest detection [GH-9307]
  - guests/debian: Update guest configure networks [GH-9338]
  - guests/dragonflybsd: Base guest on FreeBSD to inherit more functionality [GH-9205]
  - guests/linux: Improve NFS service name detection and interactions [GH-9274]
  - guests/linux: Support mount option overrides for SMB mounts [GH-9366]
  - guests/linux: Use `ip` for reading guest address if available [GH-9315]
  - guests/solaris: Improve guest detection for alternatives [GH-9295]
  - hosts/windows: Check credentials during SMB prepare [GH-9365]
  - providers/hyper-v: Ensure Hyper-V cmdlets are fully qualified [GH-8863]
  - middleware/authentication: Add app.vagrantup.com to allowed hosts [GH-9145]
  - provisioners/shell: Support hiding environment variable values in output [GH-9367]
  - providers/virtualbox: Add a clean error message for invalid IP addresses [GH-9275]
  - providers/virtualbox: Introduce flag for SharedFoldersEnableSymlinksCreate setting [GH-9354]
  - providers/virtualbox: Provide warning for SharedFoldersEnableSymlinksCreate setting [GH-9389]
  - provisioners/salt: Fixes timeout issue in salt bootstrapping for windows [GH-8992]
  - synced_folders/smb: Update Windows implementation [GH-9294]
  - util/ssh: Attempt to locate local ssh client before attempting installer provided [GH-9400]

BUG FIXES:

  - commands/box: Show all box providers with `update outdated --global` [GH-9347]
  - commands/destroy: Exit 0 if vagrant destroy finds no running vms [GH-9251]
  - commands/package: Fix --output path with specified folder [GH-9131]
  - guests/suse: Do not use full name when setting hostname [GH-9212]
  - providers/hyper-v: Fix enable virtualization extensions on import [GH-9255]
  - provisioners/ansible(both): Fix broken 'ask_sudo_pass' option [GH-9173]

## 2.0.1 (November 2, 2017)

FEATURES:

  - core: Introduce Ruby 2.4 to Vagrant [GH-9102]
  - providers/virtualbox: Virtualbox 5.2 support [GH-8955]

IMPROVEMENTS:

  - command/destroy: Introduce parallel destroy for certain providers [GH-9127]
  - communicators/winrm: Include APIPA check within ready check [GH-8997]
  - core: Clear POSIXLY_CORRECT when using optparse [GH-8685]
  - docs: Add auto_start_action and auto_stop_action to docs. [GH-9029]
  - docs: Fix typo in box format doc [GH-9100]
  - provisioners/chef: Handle chef provisioner reboot request [GH-8874]
  - providers/salt: Support Windows Salt Minions greater than 2016.x.x [GH-8926]
  - provisioners/salt: Add wget to bootstrap_salt options when fetching installer file [GH-9112]
  - provisioners/shell: Use ui.detail for displaying output [GH-8983]
  - util/downloader: Use CURL_CA_BUNDLE environment variable [GH-9135]

BUG FIXES:

  - communicators/ssh: Retry on Errno::EPIPE exceptions [GH-9065]
  - core: Rescue more exceptions when checking if port is open [GH-8517]
  - guests/solaris11: Inherit from Solaris guest and keep solaris11 specific methods [GH-9034]
  - guests/windows: Split out cygwin path helper for msys2/cygwin paths and ensure cygpath exists [GH-8972]
  - guests/windows: Specify expected shell when executing on guest (fixes einssh communicator usage) [GH-9012]
  - guests/windows: Include WinSSH Communicator when using insert_public_key [GH-9105]
  - hosts/windows: Check for vagrant.exe when validating versions within WSL [GH-9107, GH-8962]
  - providers/docker: Isolate windows check within executor to handle running through VM [GH-8921]
  - providers/hyper-v: Properly invoke Auto stop action [GH-9000]
  - provisioners/puppet: Fix winssh communicator support in puppet provisioner [GH-9014]
  - virtualbox/synced_folders: Allow synced folders to contain spaces in the guest path [GH-8995]

## 2.0.0 (September 7, 2017)

IMPROVEMENTS:

  - commands/login: Add support for two-factor authentication [GH-8935]
  - commands/ssh-config: Properly display windows path if invoked from msys2 or
      cygwin [GH-8915]
  - guests/alt: Add support for ALT Linux [GH-8746]
  - guests/kali: Fix file permissions on guest plugin ruby files [GH-8950]
  - hosts/linux: Provide common systemd detection for services interaction, fix NFS
      host interactions [GH-8938]
  - providers/salt: Remove duplicate stdout, stderr output from salt [GH-8767]
  - providers/salt: Introduce salt_call_args and salt_args option for salt provisioner
      [GH-8927]
  - providers/virtualbox: Improving resilience of some VirtualBox commands [GH-8951]
  - provisioners/ansible(both): Add the compatibility_mode option, with auto-detection
      enabled by default [GH-8913, GH-6570]
  - provisioners/ansible: Add the version option to the host-based provisioner
      [GH-8913, GH-8914]
  - provisioners/ansible(both): Add the become and become_user options with deprecation
      of sudo and sudo_user options [GH-8913, GH-6570]
  - provisioners/ansible: Add the ask_become_pass option with deprecation of the
      ask_sudo_pass option [GH-8913, GH-6570]

BUG FIXES:

  - guests/shell_expand_guest_path : Properly expand guest paths that include relative
      path alias [GH-8918]
  - hosts/linux: Remove duplicate export folders before writing /etc/exports [GH-8945]
  - provisioners/ansible(both): Add single quotes to the inventory host variables, only
      when necessary [GH-8597]
  - provisioners/ansible(both): Add the "all:vars" section to the inventory when defined
      in `groups` option [GH-7730]
  - provisioners/ansible_local: Extra variables are no longer truncated when a dollar ($)
      character is present [GH-7735]
  - provisioners/file: Align file provisioner functionality on all platforms [GH-8939]
  - util/ssh: Properly quote key path for IdentityFile option to allow for spaces [GH-8924]

BREAKING CHANGES:

  - Both Ansible provisioners are now capable of automatically setting the compatibility_mode that
      best fits with the Ansible version in use. You may encounter some compatibility issues when
      upgrading. If you were using Ansible 2.x and referring to the _ssh-prefixed variables present
      in the generated inventory (e.g. `ansible_ssh_host`). In this case, you can fix your Vagrant
      setup by setting compatibility_mode = "1.8", or by migrating to the new variable names (e.g.
      ansible_host).

## 1.9.8 (August 23, 2017)

IMPROVEMENTS:

  - bash: Add box prune to contrib bash completion [GH-8806]
  - commands/login: Ask for description of Vagrant Cloud token [GH-8876]
  - commands/validate: Improve functionality of the validate command [GH-8889]n
  - core: Updated Vagrants rspec gem to 3.5.0 [GH-8850]
  - core: Validate powershell availability and version before use [GH-8839]
  - core: Introduce extra_args setting for ssh configs [GH-8895]
  - docs: Align contrib/sudoers file for ubuntu linux with docs [GH-8842]
  - provider/hyperv: Prefer IPv4 guest address [GH-8831, GH-8759]
  - provisioners/chef: Add config option omnibus_url for chef provisioners [GH-8682]
  - provisioners/chef: Improve exception handling around missing folder paths [GH-8775]

BUG FIXES:

  - box/update: Add force flag for box upgrade command [GH-8871]
  - commands/rsync-auto: Ensure relative dirs are still rsync'd if defined [GH-8781]
  - commands/up: Disable install providers when using global id on vagrant up [GH-8910]
  - communicators/winssh: Fix public key insertion to retain ACL [GH-8790]
  - core: Update util/ssh to use `-o` for identity files [GH-8786]
  - guests/freebsd: Fix regex for listing network devices on some FreeBSD boxes. [GH-8760]
  - hosts/windows: Prevent control characters in version check for WSL [GH-8902, GH-8901]
  - providers/docker: Split String type links into Array when using compose [GH-8837, GH-8821]
  - providers/docker: Expand relative volume paths correctly [GH-8838, GH-8822]
  - providers/docker: Error when compose option enabled with force_host_vm [GH-8911]
  - provisioners/ansible: Update to use `-o` for identity files [GH-8786]
  - provisioners/file: Ensure remote folder exists prior to scp file or folder [GH-8880]
  - provisioners/salt: Fix error case when github is unreachable for installer [GH-8864]
  - provisioners/shell: Allow frozen string scripts [GH-8875]
  - provisioners/puppet: Remove `--manifestdir` flag from puppet apply in provisioner [GH-8797]
  - synced_folders/rsync: Correctly format IPv6 host [GH-8840, GH-8809]

## 1.9.7 (July 7, 2017)

FEATURES:

  - core: Add support for preferred providers [GH-8558]

IMPROVEMENTS:

  - guests/bsd: Invoke `tee` with explicit path [GH-8740]
  - guests/smartos: Guest updates for host name and nfs capabilities [GH-8695]
  - guests/windows: Add public key capabilities for WinSSH communicator [GH-8761]
  - hosts/windows: Log command exec encoding failures and use original string on failure [GH-8820]
  - providers/virtualbox: Filter machine IPs when preparing NFS settings [GH-8819]

BUG FIXES:

  - communicators/winssh: Make script upload directory configurable [GH-8761]
  - core: Update cygwin detection to prevent PATH related errors [GH-8749, GH-6788]
  - core: Fix URI parsing of box names to prevent errors [GH-8762, GH-8758]
  - provider/docker: Only rsync-auto current working dir with docker provider [GH-8756]

## 1.9.6 (June 28, 2017)

IMPROVEMENTS:

  - commands/snapshot: Enforce unique snapshot names and introduce `--force` flag [GH-7810]
  - commands/ssh: Introduce tty flag for `vagrant ssh -c` [GH-6827]
  - core: Warn about vagrant CWD changes for a machine [GH-3921]
  - core: Allow Compression and DSAAuthentication ssh flags to be configurable [GH-8693]
  - core/box: Warn if user sets box as url [GH-7118]
  - core/bundler: Enforce stict constraints on vendored libraries [GH-8692]
  - guests/kali: Add support for guest [GH-8553]
  - guests/smartos: Update halt capability and add public key insert and remove capabilities [GH-8618]
  - provisioners/ansible: Fix SSH keys only behavior to be consistent with Vagrant [GH-8467]
  - providers/docker: Add post install provisioner for docker setup [GH-8722]
  - snapshot/delete: Improve error message when given snapshot doesn't exist [GH-8653]
  - snapshot/list: Raise exception if provider does not support snapshots [GH-8619]
  - snapshot/restore: Improve error message when given snapshot doesn't exist [GH-8653]
  - snapshot/save: Raise exception if provider does not support snapshots [GH-8619]

BUG FIXES:

  - communicators/ssh: Move `none` cipher to end of default cipher list in Net::SSH [GH-8661]
  - core: Add unique identifier to provisioner objects [GH-8680]
  - core: Stop config loader from loading dupe config if home and project dir are equal [GH-8707]
  - core/bundler: Impose constraints on update and allow system plugins to properly update [GH-8729]
  - guests/linux: Strip whitespace from GID [GH-8666, GH-8664]
  - guests/solaris: Do not use UNC style path for shared folders from windows hosts [GH-7723]
  - guests/windows: Fix directory creation when using rsync for synced folders [GH-8588]
  - hosts/windows: Force common encoding when running system commands [GH-8725]
  - providers/docker: Fix check for docker-compose [GH-8659, GH-8660]
  - providers/docker: Fix SSH under docker provider [GH-8706]
  - providers/hyperv: Fix box import [GH-8678, GH-8677]
  - provisioners/ansible_local: Catch pip_args in FreeBSD's and SUSE's ansible_install [GH-8676]
  - provisioners/salt: Fix minion ID configuration [GH-7865, GH-7454]
  - snapshot/restore: Exit 1 if vm has not been created when command is invoked [GH-8653]

## 1.9.5 (May 15, 2017)

FEATURES:

  - hosts/windows: Support running within WSL [GH-8570, GH-8582]

IMPROVEMENTS:

  - communicators/ssh: Retry on aborted connections [GH-8526, GH-8520]
  - communicators/winssh: Enabling shared folders and networking setup [GH-8567]
  - core: Remove nokogiri dependency and constraint [GH-8571]
  - guests: Do not modify existing /etc/hosts content [GH-8506, GH-7794]
  - guests/redhat: Update network configuration capability to properly handle NM [GH-8531]
  - hosts/windows: Check for elevated shell for Hyper-V [GH-8548, GH-8510]
  - hosts/windows: Fix invalid share names on Windows guests from Windows hosts [GH-8433]
  - providers: Return errors from docker/hyperv on ssh when not available [GH-8565, GH-8508]
  - providers/docker: Add support for driving provider with docker-compose [GH-8576]

BUG FIXES:

  - guests/debian: Fix use_dhcp_assigned_default_route [GH-8577, GH-8575]
  - provisioners/shell: Fix Windows batch file provisioning [GH-8539, GH-8535]
  - providers/docker: Fall back to old style for SSH info lookup [GH-8566, GH-8552]
  - providers/hyperv: Fix import script [GH-8529]
  - providers/hyperv: Use string comparison for conditional checks in import scripts [GH-8568, GH-8444]

## 1.9.4 (April 24, 2017)

FEATURES:

  - command/validate: Add Vagrantfile validation command [GH-8264, GH-8151]
  - communicators/winssh: Add WinSSH communicator for Win32-OpenSSH [GH-8485]
  - provider/hyperv: Support integration services configuration [GH-8379, GH-8378]

IMPROVEMENTS:

  - core: Update internal dependencies [GH-8329, GH-8456]
  - core/bundler: Warn when plugin require fails instead of generating hard failure [GH-8400, GH-8392]
  - core/bundler: Error when configured plugin sources are unavailable [GH-8442]
  - guests/elementary: Add support for new guest "Elementary OS" [GH-8472]
  - guests/esxi: Add public_key capability [GH-8310]
  - guests/freebsd: Add chef_install and chef_installed? capabilities [GH-8443]
  - guests/gentoo: Add support for systemd in network configuration [GH-8407, GH-8406]
  - guests/windows: Support mounting synced folders via SSH on windows [GH-7425, GH-6220]
  - hosts/windows: Improve user permission detection [GH-7797]
  - provider/docker: Improve IP and port detection [GH-7840, GH-7651]
  - provider/docker: Do not force docker host VM on Darwin or Windows [GH-8437, GH-7895]
  - provisioners/ansible_local: Add `pip_args` option to define additional parameters when installing Ansible via pip [GH-8170, GH-8405]
  - provisioners/ansible_local: Add `:pip_args_only` install mode to allow full custom pip installations [GH-8405]
  - provisioners/salt: Update minion version installed to 2016.11.3 [GH-8448]

BUG FIXES:

  - command/box: Remove extraneous sort from box list prior to display [GH-8422]
  - command/box: Properly handle local paths with spaces for box add [GH-8503, GH-6825]
  - command/up: Prevent other provider installation when explicitly defined [GH-8393, GH-8389]
  - communicators/ssh: Do not yield empty output data [GH-8495, GH-8259]
  - core: Provide fallback and retry when 0.0.0.0 is unavailable during port check [GH-8399, GH-8395]
  - core: Support port checker methods that do not expect inclusion of host_ip [GH-8497, GH-8423]
  - core/bundler: Check if source is local path and prevent addition to remote sources [GH-8401]
  - core/ui: Prevent deadlock detection errors [GH-8414, GH-8125]
  - guests/debian: Remove hardcoded device name in interface template [GH-8336, GH-7960]
  - guests/linux: Fix SMB mount capability [GH-8410, GH-8404]
  - hosts/windows: Fix issues with Windows encoding [GH-8385, GH-8380, GH-8212, GH-8207, GH-7516]
  - hosts/windows: Fix UNC path generation when UNC path is provided [GH-8504]
  - provisioners/salt: Allow Salt version to match 2 digit month [GH-8428]
  - provisioners/shell: Properly handle remote paths on Windows that include spaces [GH-8498, GH-7234]

## 1.9.3 (March 21, 2017)

IMPROVEMENTS:

  - command/plugin: Remove requirement for paths with no spaces [GH-7967]
  - core: Support host_ip for forwarded ports [GH-7035, GH-8350]
  - core: Include disk space hint in box install failure message [GH-8089]
  - core/bundler: Allow vagrant constraint matching in prerelease mode [GH-8341]
  - provisioner/docker: Include /bin/docker as valid path [GH-8390]
  - provider/hyperv: Support enabling Hyper-V nested virtualization [GH-8325, GH-7738]

BUG FIXES:

  - communicator/winrm: Prevent inaccurate WinRM address [GH-7983, GH-8073]
  - contrib/bash: Handle path spaces in bash completion [GH-8337]
  - core: Fix box sorting on find and list [GH-7956, GH-8334]
  - core/bundler: Force path as preferred source on install [GH-8327]
  - core/provision: Update "never" behavior to match documentation [GH-8366, GH-8016]
  - plugins/push: Isolate deprecation to Atlas strategy only
  - plugins/synced_folders: Give UID/GID precedence if found within mount options
      [GH-8122, GH-8064, GH-7859]

## 1.9.2 (February 27, 2017)

FEATURES:

  - providers/hyperv: Support packaging of Hyper-V boxes [GH-7867]
  - util/command_deprecation: Add utility module for command deprecation [GH-8300]
  - util/subprocess: Add #stop and #running? methods [GH-8270]

IMPROVEMENTS:

  - commands/expunge: Display default value on prompt and validate input [GH-8192, GH-8171]
  - communicator/winrm: Refactor WinRM communicator to use latest WinRM
      gems and V2 API [GH-8102]
  - core: Scrub URL credentials from output when adding boxes [GH-8194, GH-8117]
  - providers/hyperv: Prefer VMCX over XML configuration when VMCX is supported [GH-8119]

BUG FIXES:

  - command/init: Include box version when using minimal option [GH-8283, GH-8282]
  - command/package: Fix SecureRandom constant error [GH-8159]
  - communicator/ssh: Remove any STDERR output prior to command execution [GH-8291, GH-8288]
  - core/bundler: Prevent pristine warning messages [GH-8191, GH-8190, GH-8147]
  - core/bundler: Fix local installations of pre-release plugins [GH-8252, GH-8253]
  - core/bundler: Prefer user defined source when installing plugins [GH-8273, GH-8210]
  - core/environment: Prevent persisting original environment variable if name is empty
      [GH-8198, GH-8126]
  - core/environment: Fix gems_path location [GH-8248]
  - core/environment: Properly expand dotfile path [GH-8196, GH-8108]
  - guests/arch: Fix configuring multiple network interfaces [GH-8165]
  - guests/linux: Fix guest detection for names with spaces [GH-8092]
  - guests/redhat: Fix network interface configuration [GH-8148]

DEPRECATIONS:

  - command/push: Disable push command [GH-8300]

## 1.9.1 (December 7, 2016)

IMPROVEMENTS:

  - core: Disable Vagrantfile loading when running plugin commands [GH-8066]
  - guests/redhat: Detect and restart NetworkManager service if in use [GH-8052, GH-7994]

BUG FIXES:

  - core: Detect load failures within install solution sets and retry [GH-8068]
  - core: Prevent interactive shell on plugin uninstall [GH-8086, GH-8087]
  - core: Remove bundler usage from Util::Env [GH-8090, GH-8094]
  - guests/linux: Prevent stderr output on init version check for synced folders [GH-8051]

## 1.9.0 (November 28, 2016)

FEATURES:

  - commands/box: Add `prune` subcommand for removing outdated boxes [GH-7978]
  - core: Remove Bundler integration for handling internal plugins [GH-7793, GH-8000, GH-8011, GH-8031]
  - providers/hyperv: Add support for Hyper-V binary configuration format
      [GH-7854, GH-7706, GH-6102]
  - provisioners/shell: Support MD5/SHA1 checksum validation of remote scripts [GH-7985, GH-6323]

IMPROVEMENTS:

  - commands/plugin: Retain name sorted output when listing plugins [GH-8028]
  - communicator/ssh: Support custom environment variable export template
      [GH-7976, GH-6747]
  - provisioners/ansible(both): Add `config_file` option to point the location of an
      `ansible.cfg` file via ANSIBLE_CONFIG environment variable [GH-7195, GH-7918]
  - synced_folders: Support custom naming and disable auto-mount [GH-7980, GH-6836]

BUG FIXES:

  - guests/linux: Do not match interfaces with special characters when sorting [GH-7989, GH-7988]
  - provisioner/salt: Fix Hash construction for constant [GH-7986, GH-7981]

## 1.8.7 (November 4, 2016)

IMPROVEMENTS:

  - guests/linux: Place ethernet devices at start of network devices list [GH-7848]
  - guests/linux: Provide more consistent guest detection [GH-7887, GH-7827]
  - guests/openbsd: Validate guest rsync installation success [GH-7929, GH-7898]
  - guests/redhat: Include Virtuozzo Linux 7 within flavor identification [GH-7818]
  - guests/windows: Allow vagrant to start Windows Nano without provisioning [GH-7831]
  - provisioners/ansible_local: Change the Ansible binary detection mechanism [GH-7536]
  - provisioners/ansible(both): Add the `playbook_command` option [GH-7881]
  - provisioners/puppet: Support custom environment variables [GH-7931, GH-7252, GH-2270]
  - util/safe_exec: Use subprocess for safe_exec on Windows [GH-7802]
  - util/subprocess: Allow closing STDIN [GH-7778]

BUG FIXES:

  - communicators/winrm: Prevent connection leakage [GH-7712]
  - core: Prevent duplicate provider priorities [GH-7756]
  - core: Allow Numeric type for box version [GH-7874, GH-6960]
  - core: Provide friendly error when user environment is too large [GH-7889, GH-7857]
  - guests: Remove `set -e` usage for better shell compatibility [GH-7921, GH-7739]
  - guests/linux: Fix incorrectly configured private network [GH-7844, GH-7848]
  - guests/linux: Properly order network interfaces
      [GH-7866, GH-7876, GH-7858, GH-7876]
  - guests/linux: Only emit upstart event if initctl is available [GH-7813]
  - guests/netbsd: Fix rsync installation [GH-7922, GH-7901]
  - guests/photon: Fix networking setup [GH-7808, GH-7873]
  - guests/redhat: Properly configure network and restart service [GH-7751]
  - guests/redhat: Prevent NetworkManager from managing devices on initial start [GH-7926]
  - hosts/linux: Fix race condition in writing /etc/exports file for NFS configuration
      [GH-7947, GH-7938] - Thanks to Aron Griffis (@agriffis) for identifying this issue
  - plugins/rsync: Escape exclude paths [GH-7928, GH-7910]
  - providers/docker: Remove --interactive flag when pty is true [GH-7688]
  - provisioners/ansible_local: Use enquoted path for file/directory existence checks
  - provisioners/salt: Synchronize configuration defaults with documentation [GH-7907, GH-6624]
  - pushes/atlas: Fix atlas push on Windows platform [GH-6938, GH-7802]

## 1.8.6 (September 27, 2016)

IMPROVEMENTS:

  - Add detection for DragonFly BSD [GH-7701]
  - Implement auto_start and auto_stop actions for Hyper-V [GH-7647]
  - communicators/ssh: Remove any content prepended to STDOUT [GH-7676, GH-7613]

BUG FIXES:

  - commands/package: Provide machine data directory for base box package
      [GH-5070, GH-7725]
  - core: Fix windows path formatting [GH-6598]
  - core: Fixes for ssh-agent interactions [GH-7703, GH-7621, GH-7398]
  - core: Support VAGRANT_DOTFILE_PATH relative to the Vagrantfile [GH-7623]
  - guests: Prevent ssh disconnect errors on halt command [GH-7675]
  - guests/bsd: Remove Darwin matching [GH-7701]
  - guests/linux: Fix SSH key permissions [GH-7610, GH-7611]
  - guests/linux: Always sort discovered network interfaces [GH-7705, GH-7668]
  - guests/linux: Fixes for user and group ID lookups for virtualbox shared folders
      [GH-7616, GH-7662, GH-7720]
  - guests/openbsd: Add custom halt capability [GH-7701]
  - guests/ubuntu: Fix detection on older guests [GH-7632, GH-7524, GH-7625]
  - hosts/arch: Detect NFS server by service name on arch [GH-7630, GH-7629]
  - hosts/darwin: Fix generated RDP configuration file [GH-7698]
  - provisioners/ansible: Add support for `ssh.proxy_command` setting [GH-7752]
  - synced_folders/nfs: Display warning when configured for NFSv4 and UDP [GH-7740]
  - synced_folders/rsync: Properly ignore excluded files within synced directory
      from `chown` command. [GH-5256, GH-7726]

## 1.8.5 (July 18, 2016)

FEATURES:

  - core: Provide a way to globally disable box update checks with the
      environment variable `VAGRANT_BOX_UPDATE_CHECK_DISABLE`. Setting this
      to any non-empty value will instruct Vagrant to not look for box updates
      when running `vagrant up`. Setting this environment variable has no
      effect on the `vagrant box` commands.

IMPROVEMENTS:

  - guests/arch: Support installing synced folder clients [GH-7519]
  - guests/darwin: Allow ipv6 static networks [GH-7491]
  - providers/virtualbox: Add support for 5.1 [GH-7574]

BUG FIXES:

  - core: Bump listen gem and Ruby version to improve rsync performance
      [GH-7453, GH-7441]
  - core: Check process stdout when detecting if a hyperv admin
      [GH-7465, GH-7467]
  - core: Ensure removal of temporary directory when box download fails
      [GH-7496, GH-7499]
  - core: Fix regression for installing plugins from path [GH-7505, GH-7493]
  - core: Skip checking conflicts on disabled ports [GH-7587]
  - core: Idempotent write-out for state file [GH-7550]
  - core/guests: Create common BSD guest for shared logic
  - core/guests: Ignore empty output from `/sbin/ip`
      [GH-7539, GH-7537, GH-7533, GH-7605]
  - synced_folders/nfs: Shellescape rsync paths
      [GH-7540, GH-7605]
  - synced_folders/nfs: Ensure retries take place [GH-6360, GH-7605]
  - synced_folders/rsync: Shellescape rsync paths
      [GH-7580, GH-6690, GH-7579, GH-7605]
  - synced_folders/rsync: Translate Windows paths
      [GH-7012, GH-6702, GH-6568, GH-7046]
  - guests/bsd: Consolidate core logic for mounting NFS folders
      [GH-7480, GH-7474, GH-7466]
  - guests/bsd: Consolidate core logic for public key management [GH-7481]
  - guests/bsd: Consolidate core logic for halting [GH-7484]
  - guests/centos: Use `ip` instead of `ifconfig` to detect network interfaces
      [GH-7460]
  - guests/debian: Ensure newline when inserting public key [GH-7456]
  - guests/linux: Ensure NFS retries during mounting [GH-7492]
  - guests/redhat: Use `/sbin/ip` to list and configure networks for
      compatability with older versions of CentOS [GH-7482]
  - guests/redhat: Ensure newline when inserting public key [GH-7598, GH-7605]
  - guests/ubuntu: Use /etc/os-release to detect [GH-7524]
  - guests/ubuntu: Use short hostname [GH-7488, GH-7605]
  - providers/hyperv: Fix version check and catch statement [GH-7447, GH-7487]

## 1.8.4 (June 13, 2016)

BUG FIXES:

  - core: Fix bundler plugin issue and version constraint [GH-7418, GH-7415]
  - providers/virtualbox: Use 8 network interfaces (due to Windows limitation)
      [GH-7417, GH-7419]
  - provisioners/ansible(both): Honor "galaxy_roles_path" option when running
      ansible-playbook [GH-7269, GH-7420]
  - provisioners/ansible_local: Add quotes around "ansible-galaxy" arguments
      [GH-7420]

IMPROVEMENTS:

  - guests/redhat: Add CloudLinux detection [GH-7428, GH-7427]

## 1.8.3 (June 10, 2016)

BREAKING CHANGES:

  - The `winrm` communicator now shares the same upload behavior as the `ssh`
      communicator. This change should have no impact to most vagrant operations
      but may break behavior when uploading directories to an existing
      destination target. The `file` provisioner should be the only builtin
      provisioner affected by this change. When uploading a directory and the
      destination directory exists on the endpoint, the source base directory
      will be created below the destination directory on the endpoint and the
      source directory contents will be unzipped to that location. Prior to this
      release, the contents of the source directory would be unzipped to an
      existing destination directory without creating the source base directory.
      This new behavior is more consistent with SCP and other well known shell copy commands.
  - The Chef provisioner's `channel` default value has changed from "current" to
      "stable". The "current" channel includes nightly releases and should be
      opt-in only. Note that users wishing to download the Chef Development Kit
      will need to opt into the "current" channel until Chef Software promotes
      into the "stable" channel.
  - The Arch Linux host capability for NFS removed support for rc.d in favor or
      systemd which has been present since 2012. Please see GH-7181 for more
      information.

FEATURES:

  - provider/docker: Allow non-linux users to opt-out of the host VM to run
      Docker containers by setting `config.force_host_vm = false` in the
      Vagrantfile. This is especially useful for customers who wish to use
      the beta builds for Mac and Windows, dlite, or a custom provider.
      [GH-7277, GH-7298, 8c11b53]
  - provider/docker: New command: `docker-exec` allows attaching to an
      already-running container.
      [GH-7377, GH-6566, GH-5193, GH-4904, GH-4057, GH-4179, GH-4903]

IMPROVEMENTS:

  - core/downloader: increase box resume download limit to 24h
      [GH-7352, GH-7272]
  - core/package: run validations prior to packaging [GH-7353, GH-7351]
  - core/action: make `start` ("vagrant up") run provisioners [GH-4467, GH-4421]
  - commands/all: Make it clear that machine IDs can be specified
      [GH-7356, GH-7228]
  - commands/init: Add support for specifying the box version [GH-7363, GH-5004]
  - commands/login: Print a warning with both the environment variable and
      local login token are present [GH-7206, GH-7219]
  - communicators/winrm: Upgrade to latest WinRM gems [GH-6922]
  - provisioners/ansible_local: Allow to install Ansible from pip,
      with version selection capability [GH-6654, GH-7167]
  - provisioners/ansible_local: Use `provisioning_path` as working directory
      for `ansible-galaxy` execution
  - provisioners/ansible(both provisioners): Add basic config
      validators/converters on `raw_arguments` and `raw_ssh_args` options
      [GH-7103]
  - provisioners/chef: Add the ability to install on SUSE [GH-6806]
  - provisioners/chef: Support legacy solo mode [GH-7327]
  - provisioners/docker: Restart container if newer image is available
      [GH-7358, GH-6620]
  - hosts/arch: Remove sysvinit and assume systemd [GH-7181]
  - hosts/linux: Do not use a pager with systemctl commands [GH-7270]
  - hosts/darwin: Add `extra_args` support for RDP [GH-5523, GH-6602]
  - hosts/windows: Use SafeExec to capture history in Powershell [GH-6749]
  - guests/amazon: Add detection [GH-7395, GH-7254]
  - guests/freebsd: Add quotes around hostname [GH-6867]
  - guests/fedora: Add support for ipv6 static networks [GH-7275, GH-7276]
  - guests/tinycore: Add support for shared folders [GH-6977, GH-6968]
  - guests/trisquel: Add initial support [GH-6842, GH-6843]
  - guests/windows: Add support for automatic login (no password prompting)
      [GH-5670]
  - core: Add `--no-delete` and provisioning flags to snapshot restore/pop
      [GH-6879]
  - providers/docker: Allow TCP and UDP ports on the same number [GH-7365,
      GH-5527]
  - providers/hyperv: Add support for differencing disk [GH-7090]
  - providers/hyperv: Add support for snapshots [GH-7110]
  - providers/hyperv: Reinstate compatibility with PS 4 [GH-7108]
  - providers/virtualbox: Add linked clone support for Virtualbox 1.4 [GH-7050]
  - synced_folders/nfs: Read static and dynamic IPs [GH-7290, GH-7289]

BUG FIXES:

  - core: Bump nokogiri version to fix windows bug [GH-6766, GH-6848]
  - core: Revert a change made to the output of the identify file [GH-6962,
      GH-6929, GH-6589]
  - core: Fix login command behind a proxy [GH-6898, GH-6899]
  - core: Fix support for regular expressions on multi-machine `up`
      [GH-6908, GH-6909]
  - core: Allow boxes to use pre-release versions [GH-6892, GH-6893]
  - core: Rescue `Errno:ENOTCONN` waiting for port to be open [GH-7182, GH-7184]
  - core: Properly authenticate metadata box URLs [GH-6776, GH-7158]
  - core: Do not run provisioners if already run on resume [GH-7059, GH-6787]
  - core: Implement better tracking of tempfiles and tmpdirs to identify file
      leaks [GH-7355]
  - core: Allow SSH forwarding on Windows [GH-7287, GH-7202]
  - core: Allow customizing `keys_only` SSH option [GH-7360, GH-4275]
  - core: Allow customizing `paranoid` SSH option [GH-7360, GH-4275]
  - command/box_update: Do not update the same box twice [GH-6042, GH-7379]
  - command/init: Remove unnecessary `sudo` from generated Vagrantfile
      [GH-7369, GH-7295]
  - docs & core: Be consistent about the "2" in the Vagrantfile version
      [GH-6961, GH-6963]
  - guests/all: Refactor guest capabilities to run in a single command -
      **please see GH-7393 for the complete list of changes!**
  - guests/arch: Restart network after configuration [GH-7120, GH-7119]
  - guests/debian: Do not return an error if ifdown fails [GH-7159,
      GH-7155, GH-6871]
  - guests/freebsd: Use `pkg` to install rsync [GH-6760]
  - guests/freebsd: Use `netif` to configure networks [GH-5852, GH-7093]
  - guests/coreos: Detect all interface names [GH-6608, GH-6610]
  - providers/hyperv: Only specify Hyper-V if the parameter is support
      [GH-7101, GH-7098]
  - providers/virtualbox: Set maximum network adapters to 36 [GH-7293, GH-7286]
  - providers/virtualbox: Do not fail when master VM from linked clone is
      missing [GH-7126, GH-6742]
  - providers/virtualbox: Use scoped overrides in preparing NFS
      [GH-7387, GH-7386]
  - provisioners/ansible: Fix a race condition in the concurrent generations of
      the ansible inventory file, while running `vagrant up --parallel`
      [GH-6526, GH-7190]
  - provisioners/ansible_local: Don't quote the Ansible arguments defined in the
      `raw_arguments` option [GH-7103]
  - provisioners/ansible_local: Format json `extra_vars` with double quotes
      [GH-6726, GH-7103]
  - provisioners/ansible_local: Fix errors in absolute paths to playbook or
      galaxy resources when running on a Windows host [GH-6740, GH-6757]
  - provisioners/ansible_local: Change the way to verify `ansible-galaxy`
      presence, to avoid a non-zero status code with Ansible 2.0 [GH-6793]
  - provisioners/ansible(both provisioners): The Ansible configuration files
      detection is only executed by the `provision` action [GH-6763, GH-6984]
  - provisioners/chef: Do not use double sudo when installing
      [GGH-6805, GH-6804]
  - provisioners/chef: Change the default channel to "stable" (previously it
      was "current") [GH-7001, GH-6979]
  - provisioners/chef: Default node_name to hostname if present
      [GH-7063, GH-7153]
  - provisioners/docker: Fix -no-trunc command option [GH-7085]
  - provisioners/docker: Allow provisioning when container name is specified
      [GH-7074, GH-7086]
  - provisioners/puppet: Use `where.exe` to locate puppet binary
      [GH-6912, GH-6876]
  - provisioners/salt: Move masterless config to apply to all platforms
      [GH-7207, Gh-6924, GH-6915]
  - pushes/ftp: Create parent directories when uploading [GH-7154, GH-6316]
  - synced_folders/smb: Do not interpolate configuration file [GH-6906]

## 1.8.1 (December 21, 2015)

BUG FIXES:

  - core: Don't create ".bundle" directory in pwd [GH-6717]
  - core: Fix exception on installing VirtualBox [GH-6713]
  - core: Do not convert standalone drive letters such as "D:" to
      UNC paths [GH-6598]
  - core: Fix a crash in parsing the config in some cases with network
      configurations [GH-6730]
  - core: Clean up temporarily files created by bundler
    [GH-7354, GH-6301, GH-3469, GH-6231]
  - commands/up: Smarter logic about what provider to install, avoiding
      situations where VirtualBox was installed over the correct provider [GH-6731]
  - guests/debian: Fix Docker install [GH-6722]
  - provisioners/chef: convert chef version to a string before comparing for
    the command builder [GH-6709, GH-6711]
  - provisioners/shell: convert env var values to strings [GH-6714]

## 1.8.0 (December 21, 2015)

FEATURES:

  - **New Command: `vagrant powershell`**: For machines that support it,
    this will open a PowerShell prompt.
  - **New Command: `vagrant port`**: For machines that support it, this will
    display the list of forwarded ports from the guest to the host.
  - **Linked Clones**: VirtualBox and VMware providers now support
    linked clones for very fast (millisecond) imports on up. [GH-4484]
  - **Snapshots**: The `vagrant snapshot` command can be used to checkpoint
    and restore point-in-time snapshots.
  - **IPv6 Private Networks**: Private networking now supports IPv6. This
    only works with VirtualBox and VMware at this point. [GH-6342]
  - New provisioner: `ansible_local` to execute Ansible from the guest
    machine. [GH-2103]

BREAKING CHANGES:

  - The `ansible` provisioner now can override the effective ansible remote user
    (i.e. `ansible_ssh_user` setting) to always correspond to the vagrant ssh
    username. This change is enabled by default, but we expect this to affect
    only a tiny number of people as it corresponds to the common usage.
    If you however use multiple remote usernames in your Ansible plays, tasks,
    or custom inventories, you can simply set the option `force_remote_user` to
    false to make Vagrant behave the same as before.
  - provisioners/salt: the "config_dir" option has been removed. It has no
      effect in Vagrant 1.8. [GH-6073]

IMPROVEMENTS:

  - core: allow removal of all box versions with `--all` flag [GH-3462]
  - core: prune entries from global status on non-existent cwd [GH-6535]
  - core: networking: allow specifying a DHCP IP [GH-6325]
  - core: run provisioner cleanup tasks before powering off the VM [GH-6553]
  - core: only run provisioner cleanup tasks if they're implemented [GH-6603]
      This improves UX, but wasn't a bug before.
  - command/plugin: Add `--plugin-clean-sources` flag to reset plugin install
      sources, primarily for corp firewalls. [GH-4738]
  - command/rsync-auto: SSH connection is cached for faster sync times [GH-6399]
  - command/up: provisioners are run on suspend resume [GH-5815]
  - communicators/ssh: allow specifying host environment variables to forward
    to guests [GH-4132, GH-6562]
  - communicators/winrm: Configurable execution time limit [GH-6213]
  - providers/virtualbox: cache version lookup, which caused significant
      slowdown on some Windows hosts [GH-6552]
  - providers/virtualbox: add `public_address` capability for virtualbox
    [GH-6583, GH-5978]
  - provisioners/chef: perform cleanup tasks on the guest instead of the host
  - provisioners/chef: automatically generate a node_name if one was not given
    [GH-6555]
  - provisioners/chef: install Chef automatically on Windows [GH-6557]
  - provisioners/chef: allow the user to specify the Chef product (such as
    the Chef Development Kit) [GH-6557]
  - provisioners/chef: allow data_bags_path to be an array [GH-5988, GH-6561]
  - provisioners/shell: Support interactive mode for elevated PowerShell
      scripts [GH-6185]
  - provisioners/shell: add `env` option [GH-6588, GH-6516]
  - provisioners/ansible+ansible_local: add support for ansible-galaxy [GH-2718]
  - provisioners/ansible+ansible_local: add support for group and host variables
      in the generated inventory [GH-6619]
  - provisioners/ansible+ansible_local: add support for alphanumeric patterns
      for groups in the generated inventory [GH-3539]
  - provisioners/ansible: add support for WinRM settings [GH-5086]
  - provisioners/ansible: add new `force_remote_user` option to control whether
    `ansible_ssh_user` parameter should be applied or not [GH-6348]
  - provisioners/ansible: show a warning when running from a Windows Host [GH-5292]
  - pushes/local-exec: add support for specifying script args [GH-6661, GH-6660]
  - guests/slackware: add support for networking [GH-6514]

BUG FIXES:

  - core: Ctrl-C weirdness fixed where it would exit parent process
      before Vagrant finished cleaning up [GH-6085]
  - core: DHCP network configurations don't warn on IP addresses ending
      in ".1" [GH-6150]
  - core: only append `access_token` when it does not exist in the URL
    [GH-6395, GH-6534]
  - core: use the correct private key when packaging a box [GH-6406]
  - core: fix crash when using invalid box checksum type [GH-6327]
  - core: don't check for metadata if the download URL is not HTTP [GH-6540]
  - core: don't make custom dotfile path if there is no Vagrantfile [GH-6542]
  - core: more robust check for admin privs on Windows [GH-5616]
  - core: properly detect when HTTP server doesn't support byte ranges and
      retry from scratch [GH-4479]
  - core: line numbers show properly in Vagrantfile syntax errors
      on Windows [GH-6445]
  - core: catch errors setting env vars on Windows [GH-6017]
  - core: remove cached synced folders when they're removed from the
      Vagrantfile [GH-6567]
  - core: use case-insensitive comparison for box checksum validations
    [GH-6648, GH-6650]
  - commands/box: add command with `~` paths on Windows works [GH-5747]
  - commands/box: the update command supports CA settings [GH-4473]
  - commands/box: removing all versions and providers of a box will properly
      clean all directories in `~/.vagrant.d/boxes` [GH-3570]
  - commands/box: outdated global won't halt on metadata download failure [GH-6453]
  - commands/login: respect environment variables in `vagrant login` command
    [GH-6590, GH-6422]
  - commands/package: when re-packaging a packaged box, preserve the
      generated SSH key [GH-5780]
  - commands/plugin: retry plugin install automatically a few times to
      avoid network issues [GH-6097]
  - commands/rdp: prefer `xfreerdp` if it is available on Linux [GH-6475]
  - commands/up: the `--provision-with` flag works with provisioner names [GH-5981]
  - communicator/ssh: fix potential crash case with PTY [GH-6225]
  - communicator/ssh: escape IdentityFile path [GH-6428, GH-6589]
  - communicator/winrm: respect `boot_timeout` setting [GH-6229]
  - communicator/winrm: execute scheduled tasks immediately on Windows XP
      since elevation isn't required [GH-6195]
  - communicator/winrm: Decouple default port forwarding rules for "winrm" and
      "winrm-ssl" [GH-6581]
  - communicator/winrm: Hide progress bars from PowerShell v5 [GH-6309]
  - guests/arch: enable network device after setting it up [GH-5737]
  - guests/darwin: advanced networking works with more NICs [GH-6386]
  - guests/debian: graceful shutdown works properly with newer releases [GH-5986]
  - guests/fedora: Preserve `localhost` entry when changing hostname [GH-6203]
  - guests/fedora: Use dnf if it is available [GH-6288]
  - guests/linux: when replacing a public SSH key, use POSIX-compliant
      sed flags [GH-6565]
  - guests/suse: DHCP network interfaces properly configured [GH-6502]
  - hosts/slackware: Better detection of NFS [GH-6367]
  - providers/hyper-v: support generation 2 VMs [GH-6372]
  - providers/hyper-v: support VMs with more than one NIC [GH-4346]
  - providers/hyper-v: check if user is in the Hyper-V admin group if
      they're not a Windows admin [GH-6662]
  - providers/virtualbox: ignore "Unknown" status bridge interfaces [GH-6061]
  - providers/virtualbox: only fix ipv6 interfaces that are in use
      [GH-6586, GH-6552]
  - provisioners/ansible: use quotes for the `ansible_ssh_private_key_file`
    value in the generated inventory [GH-6209]
  - provisioners/ansible: use quotes when passing the private key files via
      OpenSSH `-i` command line arguments [GH-6671]
  - provisioners/ansible: don't show the `ansible-playbook` command when verbose
    option is an empty string
  - provisioners/chef: fix `nodes_path` for Chef Zero [GH-6025, GH-6049]
  - provisioners/chef: do not error when the `node_name` is unset
    [GH-6005, GH-6064, GH-6541]
  - provisioners/chef: only force the formatter on Chef 11 or higher
    [GH-6278, GH-6556]
  - provisioners/chef: require `nodes_path` to be set for Chef Zero
    [GH-6110, GH-6559]
  - provisioners/puppet: apply provisioner uses correct default manifests
    with environments. [GH-5987]
  - provisioners/puppet: remove broken backticks [GH-6404]
  - provisioners/puppet: find Puppet binary properly on Windows [GH-6259]
  - provisioners/puppet-server: works with Puppet Collection 1 [GH-6389]
  - provisioners/salt: call correct executables on Windows [GH-5999]
  - provisioners/salt: log level and colorize works for masterless [GH-6474]
  - push/local-exec: use subprocess on windows when fork does not exist
    [GH-5307, GH-6563]
  - push/heroku: use current branch [GH-6554]
  - synced\_folders/rsync: on Windows, replace all paths with Cygwin
      paths since all rsync implementations require this [GH-6160]
  - synced\_folders/smb: use credentials files to allow for more characters
      in password [GH-4230]

PLUGIN AUTHOR CHANGES:

  - installer: Upgrade to Ruby 2.2.3

## 1.7.4 (July 17, 2015)

BUG FIXES:

  - communicators/winrm: catch timeout errors [GH-5971]
  - communicators/ssh: use the same SSH args for `vagrant ssh` with and without
    a command [GH-4986, GH-5928]
  - guests/fedora: networks can be configured without nmcli [GH-5931]
  - guests/fedora: biosdevname can return 4 or 127 [GH-6139]
  - guests/redhat: systemd detection should happen on guest [GH-5948]
  - guests/ubuntu: setting hostname fixed in 12.04 [GH-5937]
  - hosts/linux: NFS can be configured without `$TMP` set on the host [GH-5954]
  - hosts/linux: NFS will sudo copying back to `/etc/exports` [GH-5957]
  - providers/docker: Add `pull` setting, default to false [GH-5932]
  - providers/virtualbox: remove UNC path conversion on Windows since it
      caused mounting regressions [GH-5933]
  - provisioners/puppet: Windows Puppet 4 paths work correctly [GH-5967]
  - provisioners/puppet: Fix config merging errors [GH-5958]
  - provisioners/salt: fix "dummy config" error on bootstrap [GH-5936]

## 1.7.3 (July 10, 2015)

FEATURES:

  - **New guest: `atomic`* - Project Atomic is supported as a guest
  - providers/virtualbox: add support for 5.0 [GH-5647]

IMPROVEMENTS:

  - core: add password authentication to rdp_info hash [GH-4726]
  - core: improve error message when packaging fails [GH-5399]
  - core: improve message when adding a box from a file path [GH-5395]
  - core: add support for network gateways [GH-5721]
  - core: allow redirecting stdout and stderr in the UI [GH-5433]
  - core: update version of winrm-fs to 0.2.0 [GH-5738]
  - core: add option to enabled trusted http(s) redirects [GH-4422]
  - core: capture additional information such as line numbers during
    Vagrantfile loading [GH-4711, GH-5769]
  - core: add .color? to UI objects to see if they support color [GH-5771]
  - core: ignore hidden directories when searching for boxes [GH-5748, GH-5785]
  - core: use `config.ssh.sudo_command` to customize the sudo command
      format [GH-5573]
  - core: add `Vagrant.original_env` for Vagrant and plugins to restore or
      inspect the original environment when Vagrant is being run from the
      installer [GH-5910]
  - guests/darwin: support inserting generated key [GH-5204]
  - guests/darwin: support mounting SMB shares [GH-5750]

<error>Content truncated. Call the fetch tool with a start_index of 100000 to get more content.</error>
