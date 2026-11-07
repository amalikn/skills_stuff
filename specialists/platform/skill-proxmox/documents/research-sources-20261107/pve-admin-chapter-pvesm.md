Contents of https://pve.proxmox.com/pve-docs/chapter-pvesm.html:
# Proxmox VE Storage

[↑](#)

The Proxmox VE storage model is very flexible. Virtual machine images
can either be stored on one or several local storages, or on shared
storage like NFS or iSCSI (NAS, SAN). There are no limits, and you may
configure as many storage pools as you like. You can use all
storage technologies available for Debian Linux.

One major benefit of storing VMs on shared storage is the ability to
live-migrate running machines without any downtime, as all nodes in
the cluster have direct access to VM disk images. There is no need to
copy VM image data, so live migration is very fast in that case.

The storage library (package libpve-storage-perl) uses a flexible
plugin system to provide a common interface to all storage types. This
can be easily adopted to include further storage types in the future.

## Storage Types

There are basically two different classes of storage types:

File level storage
:   File level based storage technologies allow access to a fully featured (POSIX)
    file system. They are in general more flexible than any Block level storage
    (see below), and allow you to store content of any type. ZFS is probably the
    most advanced system, and it has full support for snapshots and clones.

Block level storage
:   Allows to store large *raw* images. It is usually not possible to store
    other files (ISO, backups, ..) on such storage types. Most modern
    block level storage implementations support snapshots and clones.
    Ceph RADOS is a distributed systems, replicating storage data to different
    nodes that can be accessed as RBD (RADOS Block Device).

Table 1. Available storage types







| Description | Plugin type | Level | Shared | Snapshots | Stable |
| --- | --- | --- | --- | --- | --- |
| ZFS (local) | zfspool | both1 | no | yes | yes |
| Directory | dir | file | no | yes2 | yes |
| BTRFS | btrfs | file | no | yes | TP5 |
| NFS | nfs | file | yes | yes2 | yes |
| CIFS | cifs | file | yes | yes2 | yes |
| Proxmox Backup | pbs | both | yes | n/a | yes |
| CephFS | cephfs | file | yes | yes | yes |
| LVM | lvm | block | no3 | yes4 | yes |
| LVM-thin | lvmthin | block | no | yes | yes |
| iSCSI/kernel | iscsi | block | yes3 | yes4 | yes |
| iSCSI/libiscsi | iscsidirect | block | yes3 | yes4 | yes |
| FC/SAS | native6 | block | yes3 | yes4 | yes |
| Ceph/RBD | rbd | block | yes | yes | yes |
| ZFS over iSCSI | zfs | block | yes | yes | yes |

1: Disk images for VMs are stored in ZFS volume (zvol) datasets, which provide
block device functionality.

2: On file based storages, snapshots are possible with the *qcow2* format,
either using the internal snapshot function, or snapshots as volume chains4.
Creating and deleting internal *qcow2* snapshots will block a running VM and
is not an efficient operation. The performance is particularly bad with network
storages like NFS. On some setups and for large disks (multiple hundred GiB or
TiB sized), these operations may take several minutes, or in extreme cases, even
hours. If your setup is affected, create and remove snapshots while the VM is
shut down, expecting a long task duration.

3: With iSCSI, FibreChannel (FC), or SAS block storage as shared storage in a
cluster, LVM is used to split the LUN into virtual disks. The
[Multipath Guide](https://pve.proxmox.com/wiki/Multipath) explains how to
configure it in a cluster, including multipathing which is usually a
requirement in these scenarios.

4: Since Proxmox VE 9, snapshots as a volume chain have been available for VMs.
These snapshots use separate volumes for the snapshot data and layer them. For
more details, see the description for snapshot-as-volume-chain in the
[LVM configuration](/pve-docs/chapter-pvesm.html#pvesm_lvm_config) section.

5 Technology preview with best-effort support.

6 Fibre Channel (FC) and SAS block storage is handled directly by the host
without a dedicated storage plugin.

### Thin Provisioning

A number of storages, and the QEMU image format qcow2, support *thin
provisioning*. With thin provisioning activated, only the blocks that
the guest system actually use will be written to the storage.

Say for instance you create a VM with a 32GB hard disk, and after
installing the guest system OS, the root file system of the VM contains
3 GB of data. In that case only 3GB are written to the storage, even
if the guest VM sees a 32GB hard drive. In this way thin provisioning
allows you to create disk images which are larger than the currently
available storage blocks. You can create large disk images for your
VMs, and when the need arises, add more disks to your storage without
resizing the VMs' file systems.

All storage types which have the “Snapshots” feature also support thin
provisioning.

|  |  |
| --- | --- |
| Caution | If a storage runs full, all guests using volumes on that storage receive IO errors. This can cause file system inconsistencies and may corrupt your data. So it is advisable to avoid over-provisioning of your storage resources, or carefully observe free space to avoid such conditions. |

## Storage Configuration

All Proxmox VE related storage configuration is stored within a single text
file at /etc/pve/storage.cfg. As this file is within /etc/pve/, it
gets automatically distributed to all cluster nodes. So all nodes
share the same storage configuration.

Sharing storage configuration makes perfect sense for shared storage,
because the same “shared” storage is accessible from all nodes. But it is
also useful for local storage types. In this case such local storage
is available on all nodes, but it is physically different and can have
totally different content.

### Storage Pools

Each storage pool has a <type>, and is uniquely identified by its
<STORAGE\_ID>. A pool configuration looks like this:

```
<type>: <STORAGE_ID>
        <property> <value>
        <property> <value>
        <property>
        ...
```

The <type>: <STORAGE\_ID> line starts the pool definition, which is then
followed by a list of properties. Most properties require a value. Some have
reasonable defaults, in which case you can omit the value.

To be more specific, take a look at the default storage configuration
after installation. It contains one special local storage pool named
local, which refers to the directory /var/lib/vz and is always
available. The Proxmox VE installer creates additional storage entries
depending on the storage type chosen at installation time.

Default storage configuration (/etc/pve/storage.cfg)

```
dir: local
        path /var/lib/vz
        content iso,vztmpl,backup

# default image store on LVM based installation
lvmthin: local-lvm
        thinpool data
        vgname pve
        content rootdir,images

# default image store on ZFS based installation
zfspool: local-zfs
        pool rpool/data
        sparse
        content images,rootdir
```

|  |  |
| --- | --- |
| Caution | It is problematic to have multiple storage configurations pointing to the exact same underlying storage. Such an *aliased* storage configuration can lead to two different volume IDs (*volid*) pointing to the exact same disk image. Proxmox VE expects that the images' volume IDs point to, are unique. Choosing different content types for *aliased* storage configurations can be fine, but is not recommended. |

### Common Storage Properties

A few storage properties are common among different storage types.

nodes
:   List of cluster node names where this storage is
    usable/accessible. One can use this property to restrict storage
    access to a limited set of nodes.

content
:   A storage can support several content types, for example virtual disk
    images, cdrom iso images, container templates or container root
    directories. Not all storage types support all content types. One can set
    this property to select what this storage is used for.

    images
    :   QEMU/KVM VM images.

    rootdir
    :   Allow to store container data.

    vztmpl
    :   Container templates.

    backup
    :   Backup files (vzdump).

    iso
    :   ISO images

    snippets
    :   Snippet files, for example guest hook scripts

    import
    :   OVAs and VM disk images that can be imported from this storage

shared
:   Indicate that this is a single storage with the same contents on all nodes (or
    all listed in the *nodes* option). It will not make the contents of a local
    storage automatically accessible to other nodes, it just marks an already shared
    storage as such!

disable
:   You can use this flag to disable the storage completely.

prune-backups
:   Retention options for backups. For details, see
    [Backup Retention](/pve-docs/chapter-vzdump.html#vzdump_retention).

format
:   Default image format (raw|qcow2|vmdk)

preallocation
:   Preallocation mode (off|metadata|falloc|full) for raw and qcow2 images on
    file-based storages. The default is metadata, which is treated like off for
    raw images. When using network storages in combination with large qcow2
    images, using off can help to avoid timeouts.

|  |  |
| --- | --- |
| Warning | It is not advisable to use the same storage pool on different Proxmox VE clusters. Some storage operation need exclusive access to the storage, so proper locking is required. While this is implemented within a cluster, it does not work between different clusters. |

## Volumes

We use a special notation to address storage data. When you allocate
data from a storage pool, it returns such a volume identifier. A volume
is identified by the <STORAGE\_ID>, followed by a storage type
dependent volume name, separated by colon. A valid <VOLUME\_ID> looks
like:

```
local:230/example-image.raw
```

```
local:iso/debian-501-amd64-netinst.iso
```

```
local:vztmpl/debian-5.0-joomla_1.5.9-1_i386.tar.gz
```

```
iscsi-storage:0.0.2.scsi-14f504e46494c4500494b5042546d2d646744372d31616d61
```

To get the file system path for a <VOLUME\_ID> use:

```
pvesm path <VOLUME_ID>
```

### Volume Ownership

There exists an ownership relation for image type volumes. Each such
volume is owned by a VM or Container. For example volume
local:230/example-image.raw is owned by VM 230. Most storage
backends encodes this ownership information into the volume name.

When you remove a VM or Container, the system also removes all
associated volumes which are owned by that VM or Container.

## Using the Command-line Interface

It is recommended to familiarize yourself with the concept behind storage
pools and volume identifiers, but in real life, you are not forced to do any
of those low level operations on the command line. Normally,
allocation and removal of volumes is done by the VM and Container
management tools.

Nevertheless, there is a command-line tool called pvesm (“Proxmox VE
Storage Manager”), which is able to perform common storage management
tasks.

### Examples

Add storage pools

```
pvesm add <TYPE> <STORAGE_ID> <OPTIONS>
pvesm add dir <STORAGE_ID> --path <PATH>
pvesm add nfs <STORAGE_ID> --path <PATH> --server <SERVER> --export <EXPORT>
pvesm add lvm <STORAGE_ID> --vgname <VGNAME>
pvesm add iscsi <STORAGE_ID> --portal <HOST[:PORT]> --target <TARGET>
```

Disable storage pools

```
pvesm set <STORAGE_ID> --disable 1
```

Enable storage pools

```
pvesm set <STORAGE_ID> --disable 0
```

Change/set storage options

```
pvesm set <STORAGE_ID> <OPTIONS>
pvesm set <STORAGE_ID> --shared 1
pvesm set local --format qcow2
pvesm set <STORAGE_ID> --content iso
```

Remove storage pools. This does not delete any data, and does not
disconnect or unmount anything. It just removes the storage
configuration.

```
pvesm remove <STORAGE_ID>
```

Allocate volumes

```
pvesm alloc <STORAGE_ID> <VMID> <name> <size> [--format <raw|qcow2>]
```

Allocate a 4G volume in local storage. The name is auto-generated if
you pass an empty string as <name>

```
pvesm alloc local <VMID> '' 4G
```

Free volumes

```
pvesm free <VOLUME_ID>
```

|  |  |
| --- | --- |
| Warning | This really destroys all volume data. |

List storage status

```
pvesm status
```

List storage contents

```
pvesm list <STORAGE_ID> [--vmid <VMID>]
```

List volumes allocated by VMID

```
pvesm list <STORAGE_ID> --vmid <VMID>
```

List iso images

```
pvesm list <STORAGE_ID> --content iso
```

List container templates

```
pvesm list <STORAGE_ID> --content vztmpl
```

Show file system path for a volume

```
pvesm path <VOLUME_ID>
```

Exporting the volume local:103/vm-103-disk-0.qcow2 to the file target.
This is mostly used internally with pvesm import.
The stream format qcow2+size is different to the qcow2 format.
Consequently, the exported file cannot simply be attached to a VM.
This also holds for the other formats.

```
pvesm export local:103/vm-103-disk-0.qcow2 qcow2+size target --with-snapshots 1
```

## Directory Backend

Storage pool type: dir

Proxmox VE can use local directories or locally mounted shares for
storage. A directory is a file level storage, so you can store any
content type like virtual disk images, containers, templates, ISO images
or backup files.

|  |  |
| --- | --- |
| Note | You can mount additional storages via standard linux /etc/fstab, and then define a directory storage for that mount point. This way you can use any file system supported by Linux. |

This backend assumes that the underlying directory is POSIX
compatible, but nothing else. This implies that you cannot create
snapshots at the storage level. But there exists a workaround for VM
images using the qcow2 file format, because that format supports
snapshots internally.

|  |  |
| --- | --- |
| Tip | Some storage types do not support O\_DIRECT, so you can’t use cache mode none with such storages. Simply use cache mode writeback instead. |

We use a predefined directory layout to store different content types
into different sub-directories. This layout is used by all file level
storage backends.

Table 2. Directory layout



| Content type | Subdir |
| --- | --- |
| VM images | images/<VMID>/ |
| ISO images | template/iso/ |
| Container templates | template/cache/ |
| Backup files | dump/ |
| Snippets | snippets/ |
| Import | import/ |

### Configuration

This backend supports all common storage properties, and adds two
additional properties. The path property is used to specify the
directory. This needs to be an absolute file system path.

The optional content-dirs property allows for the default layout
to be changed. It consists of a comma-separated list of identifiers
in the following format:

```
vtype=path
```

Where vtype is one of the allowed content types for the storage, and
path is a path relative to the mountpoint of the storage.

Configuration Example (/etc/pve/storage.cfg)

```
dir: backup
        path /mnt/backup
        content backup
        prune-backups keep-last=7
        max-protected-backups 3
        content-dirs backup=custom/backup/dir
```

The above configuration defines a storage pool called backup. That pool can be
used to store up to 7 regular backups (keep-last=7) and 3 protected backups
per VM. The real path for the backup files is /mnt/backup/custom/backup/dir/....

### File naming conventions

This backend uses a well defined naming scheme for VM images:

```
vm-<VMID>-<NAME>.<FORMAT>
```

<VMID>
:   This specifies the owner VM.

<NAME>
:   This can be an arbitrary name (ascii) without white space. The
    backend uses disk-[N] as default, where [N] is replaced by an
    integer to make the name unique.

<FORMAT>
:   Specifies the image format (raw|qcow2|vmdk).

When you create a VM template, all VM images are renamed to indicate
that they are now read-only, and can be used as a base image for clones:

```
base-<VMID>-<NAME>.<FORMAT>
```

|  |  |
| --- | --- |
| Note | Such base images are used to generate cloned images. So it is important that those files are read-only, and never get modified. The backend changes the access mode to 0444, and sets the immutable flag (chattr +i) if the storage supports that. |

### Storage Features

As mentioned above, most file systems do not support snapshots out
of the box. To workaround that problem, this backend is able to use
qcow2 internal snapshot capabilities.

Same applies to clones. The backend uses the qcow2 base image
feature to create clones.

Table 3. Storage features for backend dir






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir vztmpl iso backup snippets | raw qcow2 vmdk subvol | no | qcow2 | qcow2 |

### Examples

Please use the following command to allocate a 4GB image on storage local:

```
# pvesm alloc local 100 vm-100-disk10.raw 4G
Formatting '/var/lib/vz/images/100/vm-100-disk10.raw', fmt=raw size=4294967296
successfully created 'local:100/vm-100-disk10.raw'
```

|  |  |
| --- | --- |
| Note | The image name must conform to above naming conventions. |

The real file system path is shown with:

```
# pvesm path local:100/vm-100-disk10.raw
/var/lib/vz/images/100/vm-100-disk10.raw
```

And you can remove the image with:

```
# pvesm free local:100/vm-100-disk10.raw
```

## NFS Backend

Storage pool type: nfs

The NFS backend is based on the directory backend, so it shares most
properties. The directory layout and the file naming conventions are
the same. The main advantage is that you can directly configure the
NFS server properties, so the backend can mount the share
automatically. There is no need to modify /etc/fstab. The backend
can also test if the server is online, and provides a method to query
the server for exported shares.

### Configuration

The backend supports all common storage properties, except the shared
flag, which is always set. Additionally, the following properties are
used to configure the NFS server:

server
:   Server IP or DNS name. To avoid DNS lookup delays, it is usually
    preferable to use an IP address instead of a DNS name - unless you
    have a very reliable DNS server, or list the server in the local
    /etc/hosts file.

export
:   NFS export path (as listed by pvesm nfsscan).

You can also set NFS mount options:

path
:   The local mount point (defaults to /mnt/pve/<STORAGE\_ID>/).

content-dirs
:   Overrides for the default directory layout. Optional.

options
:   NFS mount options (see man nfs).

Configuration Example (/etc/pve/storage.cfg)

```
nfs: iso-templates
        path /mnt/pve/iso-templates
        server 10.0.0.10
        export /space/iso-templates
        options vers=3,soft
        content iso,vztmpl
```

|  |  |
| --- | --- |
| Tip | After an NFS request times out, NFS request are retried indefinitely by default. This can lead to unexpected hangs on the client side. For read-only content, it is worth to consider the NFS soft option, which limits the number of retries to three. |

### Storage Features

NFS does not support snapshots, but the backend uses qcow2 features
to implement snapshots and cloning.

Table 4. Storage features for backend nfs






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir vztmpl iso backup snippets | raw qcow2 vmdk | yes | qcow2 | qcow2 |

### Examples

You can get a list of exported NFS shares with:

```
# pvesm scan nfs <server>
```

## CIFS Backend

Storage pool type: cifs

The CIFS backend extends the directory backend, so that no manual
setup of a CIFS mount is needed. Such a storage can be added directly
through the Proxmox VE API or the web UI, with all our backend advantages,
like server heartbeat check or comfortable selection of exported
shares.

### Configuration

The backend supports all common storage properties, except the shared
flag, which is always set. Additionally, the following CIFS special
properties are available:

server
:   Server IP or DNS name. Required.

|  |  |
| --- | --- |
| Tip | To avoid DNS lookup delays, it is usually preferable to use an IP address instead of a DNS name - unless you have a very reliable DNS server, or list the server in the local /etc/hosts file. |

share
:   CIFS share to use (get available ones with pvesm scan cifs <address> or the
    web UI). Required.

username
:   The username for the CIFS storage. Optional, defaults to ‘guest’.

password
:   The user password. Optional.
    It will be saved in a file only readable by root
    (/etc/pve/priv/storage/<STORAGE-ID>.pw).

domain
:   Sets the user domain (workgroup) for this storage. Optional.

smbversion
:   SMB protocol version. Optional, when set to default or when unset, negotiates
    the highest SMB2+ version supported by both the client and server. SMB1 is not
    supported due to security issues.

path
:   The local mount point. Optional, defaults to /mnt/pve/<STORAGE\_ID>/.

content-dirs
:   Overrides for the default directory layout. Optional.

options
:   Additional CIFS mount options (see man mount.cifs). Some options are set
    automatically and shouldn’t be set here. Proxmox VE will always set the option
    soft. Depending on the configuration, these options are set automatically:
    username, credentials, guest, domain, vers.

subdir
:   The subdirectory of the share to mount. Optional, defaults to the root directory
    of the share.

Configuration Example (/etc/pve/storage.cfg)

```
cifs: backup
        path /mnt/pve/backup
        server 10.0.0.11
        share VMData
        content backup
        options noserverino,echo_interval=30
        username anna
        smbversion 3
        subdir /data
```

### Storage Features

CIFS does not support snapshots on a storage level. But you may use
qcow2 backing files if you still want to have snapshots and cloning
features available.

Table 5. Storage features for backend cifs






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir vztmpl iso backup snippets | raw qcow2 vmdk | yes | qcow2 | qcow2 |

### Examples

You can get a list of exported CIFS shares with:

```
# pvesm scan cifs <server> [--username <username>] [--password]
```

Then you can add one of these shares as a storage to the whole Proxmox VE cluster
with:

```
# pvesm add cifs <storagename> --server <server> --share <share> [--username <username>] [--password]
```

## Proxmox Backup Server

Storage pool type: pbs

This backend allows direct integration of a
[Proxmox
Backup Server](https://www.proxmox.com/en/products/proxmox-backup-server/overview) into Proxmox VE like any other storage.

A Proxmox Backup storage can be added directly through the Proxmox VE API, CLI or
the web interface.

### Configuration

The backend supports all common storage properties, except the shared flag,
which is always set. Additionally, the following special properties to Proxmox
Backup Server are available:

server
:   Server IP or DNS name. Required.

port
:   Use this port instead of the default one, i.e. 8007. Optional.

username
:   The username for the Proxmox Backup Server storage. Required.

|  |  |
| --- | --- |
| Tip | Do not forget to add the realm to the username. For example, root@pam or archiver@pbs. |

password
:   The user password. The value will be saved in a file under
    /etc/pve/priv/storage/<STORAGE-ID>.pw with access restricted to the root
    user. Required.

datastore
:   The ID of the Proxmox Backup Server datastore to use. Required.

fingerprint
:   The fingerprint of the Proxmox Backup Server API TLS certificate. You can get
    it in the Servers Dashboard or using the proxmox-backup-manager cert info
    command. Required for self-signed certificates or any other one where the host
    does not trusts the servers CA.

encryption-key
:   A key to encrypt the backup data from the client side. Currently only
    non-password protected (no key derive function (kdf)) are supported. Will be
    saved in a file under /etc/pve/priv/storage/<STORAGE-ID>.enc with access
    restricted to the root user. Use the magic value autogen to automatically
    generate a new one using proxmox-backup-client key create --kdf none <path>.
    Optional.

master-pubkey
:   A public RSA key used to encrypt the backup encryption key as part of the
    backup task. Will be saved in a file under
    /etc/pve/priv/storage/<STORAGE-ID>.master.pem with access restricted to the
    root user.
    The encrypted copy of the backup encryption key will be appended to each backup
    and stored on the Proxmox Backup Server instance for recovery purposes.
    Optional, requires encryption-key.

Configuration Example (/etc/pve/storage.cfg)

```
pbs: backup
        datastore main
        server enya.proxmox.com
        content backup
        fingerprint 09:54:ef:..snip..:88:af:47:fe:4c:3b:cf:8b:26:88:0b:4e:3c:b2
        prune-backups keep-all=1
        username archiver@pbs
        encryption-key a9:ee:c8:02:13:..snip..:2d:53:2c:98
        master-pubkey 1
```

### Storage Features

Proxmox Backup Server only supports backups, they can be block-level or
file-level based. Proxmox VE uses block-level for virtual machines and file-level for
container.

Table 6. Storage features for backend pbs






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| backup | n/a | yes | n/a | n/a |

### Encryption

[![screenshot/storage-pbs-encryption-with-key.png](images/screenshot/storage-pbs-encryption-with-key.png)](images/screenshot/storage-pbs-encryption-with-key.png)

Optionally, you can configure client-side encryption with AES-256 in GCM mode.
Encryption can be configured either via the web interface, or on the CLI with
the encryption-key option (see above). The key will be saved in the file
/etc/pve/priv/storage/<STORAGE-ID>.enc, which is only accessible by the root
user.

|  |  |
| --- | --- |
| Warning | Without their key, backups will be inaccessible. Thus, you should keep keys ordered and in a place that is separate from the contents being backed up. It can happen, for example, that you back up an entire system, using a key on that system. If the system then becomes inaccessible for any reason and needs to be restored, this will not be possible as the encryption key will be lost along with the broken system. |

It is recommended that you keep your key safe, but easily accessible, in
order for quick disaster recovery. For this reason, the best place to store it
is in your password manager, where it is immediately recoverable. As a backup to
this, you should also save the key to a USB flash drive and store that in a secure
place. This way, it is detached from any system, but is still easy to recover
from, in case of emergency. Finally, in preparation for the worst case scenario,
you should also consider keeping a paper copy of your key locked away in a safe
place. The paperkey subcommand can be used to create a QR encoded version of
your key. The following command sends the output of the paperkey command to
a text file, for easy printing.

```
# proxmox-backup-client key paperkey /etc/pve/priv/storage/<STORAGE-ID>.enc --output-format text > qrkey.txt
```

Additionally, it is possible to use a single RSA master key pair for key
recovery purposes: configure all clients doing encrypted backups to use a
single public master key, and all subsequent encrypted backups will contain a
RSA-encrypted copy of the used AES encryption key. The corresponding private
master key allows recovering the AES key and decrypting the backup even if the
client system is no longer available.

|  |  |
| --- | --- |
| Warning | The same safe-keeping rules apply to the master key pair as to the regular encryption keys. Without a copy of the private key recovery is not possible! The paperkey command supports generating paper copies of private master keys for storage in a safe, physical location. |

Because the encryption is managed on the client side, you can use the same
datastore on the server for unencrypted backups and encrypted backups, even
if they are encrypted with different keys. However, deduplication between
backups with different keys is not possible, so it is often better to create
separate datastores.

|  |  |
| --- | --- |
| Note | Do not use encryption if there is no benefit from it, for example, when you are running the server locally in a trusted network. It is always easier to recover from unencrypted backups. |

### Example: Add Storage over CLI

You can get a list of available Proxmox Backup Server datastores with:

```
# pvesm scan pbs <server> <username> [--password <string>] [--fingerprint <string>]
```

Then you can add one of these datastores as a storage to the whole Proxmox VE
cluster with:

```
# pvesm add pbs <id> --server <server> --datastore <datastore> --username <username> --fingerprint 00:B4:... --password
```

## Local ZFS Pool Backend

Storage pool type: zfspool

This backend allows you to access local ZFS pools (or ZFS file systems
inside such pools).

### Configuration

The backend supports the common storage properties content, nodes,
disable, and the following ZFS specific properties:

pool
:   Select the ZFS pool/filesystem. All allocations are done within that
    pool.

blocksize
:   Set ZFS blocksize parameter.

sparse
:   Use ZFS thin-provisioning. A sparse volume is a volume whose
    reservation is not equal to the volume size.

mountpoint
:   The mount point of the ZFS pool/filesystem. Changing this does not
    affect the mountpoint property of the dataset seen by zfs.
    Defaults to /<pool>.

Configuration Example (/etc/pve/storage.cfg)

```
zfspool: vmdata
        pool tank/vmdata
        content rootdir,images
        sparse
```

### File naming conventions

The backend uses the following naming scheme for VM images:

```
vm-<VMID>-<NAME>      // normal VM images
base-<VMID>-<NAME>    // template VM image (read-only)
subvol-<VMID>-<NAME>  // subvolumes (ZFS filesystem for containers)
```

<VMID>
:   This specifies the owner VM.

<NAME>
:   This can be an arbitrary name (ascii) without white space. The
    backend uses disk[N] as default, where [N] is replaced by an
    integer to make the name unique.

### Storage Features

ZFS is probably the most advanced storage type regarding snapshot and
cloning. The backend uses ZFS datasets for both VM images (format
raw) and container data (format subvol). ZFS properties are
inherited from the parent dataset, so you can simply set defaults
on the parent dataset.

Table 7. Storage features for backend zfs






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir | raw subvol | no | yes | yes |

### Encryption

ZFS supports encryption of dataset hierarchies. Each encrypted dataset, is
either an encryption\_root, storing the properties for encryption itself or
descendant of its encryption\_root - see the zfs-load-key(8) manpage for
details.

Sending and receiving encrypted datasets is subject to constraints as some
encryption parameters (initialization vectors for the symmetric ciphers) need
to be either transferred with the data, breaking inheriting the encryption
properties on the receiving side, or need to be recreated on target, requiring
the data to be sent unencrypted - see the zfs-recv(8) manpage for details.

For migration and storage replication of encrypted datasets in Proxmox VE, the
data is sent without the encryption properties, and the state of encryption
is determined by the target.

If you want to send and receive encrypted ZFS datasets, you need to ensure that
all involved storages on all nodes are encrypted.

### Examples

It is recommended to create an extra ZFS file system to store your VM images:

```
# zfs create tank/vmdata
```

To enable compression on that newly allocated file system:

```
# zfs set compression=on tank/vmdata
```

You can get a list of available ZFS filesystems with:

```
# pvesm scan zfs
```

## LVM Backend

Storage pool type: lvm

LVM is a lightweight software layer that sits on top of hard disks and
partitions. It can be used to divide available disk space into smaller logical
volumes.

Another use case is placing LVM on top of a large iSCSI LUN (Logical Unit
Number) or a SAN (Storage Area Network) connected via Fibre Channel.
This allows you to easily manage the space on the iSCSI LUN, which would
otherwise be impossible because the iSCSI specification does not define a
management interface for space allocation.

### Configuration

The LVM backend supports the common storage properties content, nodes,
disable, and the following LVM specific properties:

vgname
:   LVM volume group name. This must point to an existing volume group.

base
:   Base volume. This volume is automatically activated before accessing
    the storage. This is mostly useful when the LVM volume group resides
    on a remote iSCSI server.

saferemove
:   Called "Wipe Removed Volumes" in the web UI. Zero-out data when removing LVs.
    When removing a volume, this makes sure that all data gets erased and cannot be
    accessed by other LVs created later (which happen to be assigned the same
    physical extents). This is a costly operation, but may be required as a security
    measure in certain environments.

    Storage devices that support the "write zeroes" operation will use blkdiscard
    to zero blocks. Otherwise, a fallback to cstream is performed.

saferemove-stepsize
:   Wipe step size in MiB (blkdiscard -p parameter value), capped to the maximum
    step size supported by the underlying storage. Up to 32 MiB (maximum) by
    default.

saferemove\_throughput
:   Wipe throughput (cstream -t parameter value), up to 10 MiB/s by default.

snapshot-as-volume-chain
:   Set this flag to enable snapshot support for virtual machines on LVM with a
    volume backing chain.
    With this setting, taking a snapshot persists the current state under the
    snapshot’s name and starts a new volume backed by the snapshot.

    A volume based on a snapshot references its parent snapshot volume as its
    backing volume and records only the differences to that backing volume.
    Snapshot volumes are currently thick-provisioned LVM logical volumes.

    This design avoids issues with native LVM snapshots, such as significant
    input/output (I/O) penalties and unexpected, dangerous behavior when running out
    of pre-allocated space.

    Snapshots as volume chains provide vendor-agnostic support for snapshots on any
    storage system that supports block storage. This includes iSCSI and Fibre
    Channel-attached SANs.

    Note that, although this feature relies on qcow2, it only uses qcow2’s ability
    to layer multiple volumes in a backing chain, not qcow2’s snapshot
    functionality.
    The snapshot functionality is managed by the PVE storage system.

    Enabling or disabling this flag only affects newly created virtual disk volumes.

    For efficient support of snapshot-as-volume-chain, the backing storage must
    support thin-provisioning and discard. Each snapshot will appear to use the
    full volume size on the PVE side, but the actual space usage on the underlying
    storage will be smaller if those requirements are met.

|  |  |
| --- | --- |
| Warning | Snapshots as volume chains are currently a **technology preview** in Proxmox VE. |

Configuration Example (/etc/pve/storage.cfg)

```
lvm: myspace
        vgname myspace
        content rootdir,images
```

### File naming conventions

The backend use basically the same naming conventions as the ZFS pool
backend.

```
vm-<VMID>-<NAME>      // normal VM images
```

### Storage Features

LVM is a typical block storage system.
Unfortunately, regular LVM snapshots are inefficient because they interfere with
all write operations within the entire volume group while the snapshot is
active, which causes significant I/O degradation.
This is why LVM does not support linked clones, and why Proxmox VE added support for
snapshots as volume chains. This feature manages the snapshot volume through the
storage plugin and uses qcow2 to layer separate volumes as a backing chain. This
creates a single disk state that is exposed to the guest.

A benefit of LVM is that it can be used with shared storage.
For example, an iSCSI LUN. The backend implements proper cluster-wide locking if
the storage is marked as shared in the configuration.

|  |  |
| --- | --- |
| Tip | You can use the LVM-thin backend for non-shared local storage. It supports snapshots and linked clones. |

Table 8. Storage features for backend lvm







| Content types | Image formats | Shared | Snapshots | Full Clones | Linked Clones |
| --- | --- | --- | --- | --- | --- |
| images rootdir | raw, qcow21 | possible | yes1 | yes | no |

1: Since Proxmox VE 9, snapshots as a volume chain have been available for VMs, for
details see the [LVM configuration](/pve-docs/chapter-pvesm.html#pvesm_lvm_config) section.

### Examples

You can get a list of available LVM volume groups with:

```
# pvesm scan lvm
```

## LVM thin Backend

Storage pool type: lvmthin

LVM normally allocates blocks when you create a volume. LVM thin pools
instead allocates blocks when they are written. This behaviour is
called thin-provisioning, because volumes can be much larger than
physically available space.

You can use the normal LVM command-line tools to manage and create LVM
thin pools (see man lvmthin for details). Assuming you already have
a LVM volume group called pve, the following commands create a new
LVM thin pool (size 100G) called data:

```
lvcreate -L 100G -n data pve
lvconvert --type thin-pool pve/data
```

### Configuration

The LVM thin backend supports the common storage properties content, nodes,
disable, and the following LVM specific properties:

vgname
:   LVM volume group name. This must point to an existing volume group.

thinpool
:   The name of the LVM thin pool.

Configuration Example (/etc/pve/storage.cfg)

```
lvmthin: local-lvm
        thinpool data
        vgname pve
        content rootdir,images
```

### File naming conventions

The backend use basically the same naming conventions as the ZFS pool
backend.

```
vm-<VMID>-<NAME>      // normal VM images
```

### Storage Features

LVM thin is a block storage, but fully supports snapshots and clones
efficiently. New volumes are automatically initialized with zero.

It must be mentioned that LVM thin pools cannot be shared across
multiple nodes, so you can only use them as local storage.

Table 9. Storage features for backend lvmthin






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir | raw | no | yes | yes |

### Examples

You can get a list of available LVM thin pools on the volume group pve with:

```
# pvesm scan lvmthin pve
```

## Open-iSCSI initiator

Storage pool type: iscsi

iSCSI is a widely employed technology used to connect to storage
servers. Almost all storage vendors support iSCSI. There are also open
source iSCSI target solutions available,
e.g. [OpenMediaVault](https://www.openmediavault.org/), which is based on
Debian.

To use this backend, you need to install the
[Open-iSCSI](https://www.open-iscsi.com/) (open-iscsi) package. This is a
standard Debian package, but it is not installed by default to save
resources.

```
# apt-get install open-iscsi
```

Low-level iscsi management task can be done using the iscsiadm tool.

### Configuration

The backend supports the common storage properties content, nodes,
disable, and the following iSCSI specific properties:

portal
:   iSCSI portal (IP or DNS name with optional port).

target
:   iSCSI target.

Configuration Example (/etc/pve/storage.cfg)

```
iscsi: mynas
     portal 10.10.10.1
     target iqn.2006-01.openfiler.com:tsn.dcb5aaaddd
     content none
```

|  |  |
| --- | --- |
| Tip | If you want to use LVM on top of iSCSI, it make sense to set content none. That way it is not possible to create VMs using iSCSI LUNs directly. |

### File naming conventions

The iSCSI protocol does not define an interface to allocate or delete
data. Instead, that needs to be done on the target side and is vendor
specific. The target simply exports them as numbered LUNs. So Proxmox VE
iSCSI volume names just encodes some information about the LUN as seen
by the linux kernel.

### Storage Features

iSCSI is a block level type storage, and provides no management
interface. So it is usually best to export one big LUN, and setup LVM
on top of that LUN. You can then use the LVM plugin to manage the
storage on that iSCSI LUN.

Table 10. Storage features for backend iscsi






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images none | raw | yes | no | no |

### Examples

You can scan a remote iSCSI portal and get a list of possible targets with:

```
pvesm scan iscsi <HOST[:PORT]>
```

## User Mode iSCSI Backend

Storage pool type: iscsidirect

This backend provides basically the same functionality as the Open-iSCSI backed,
but uses a user-level library to implement it. You need to install the
libiscsi-bin package in order to use this backend.

It should be noted that there are no kernel drivers involved, so this
can be viewed as performance optimization. But this comes with the
drawback that you cannot use LVM on top of such iSCSI LUN. So you need
to manage all space allocations at the storage server side.

### Configuration

The user mode iSCSI backend uses the same configuration options as the
Open-iSCSI backed.

Configuration Example (/etc/pve/storage.cfg)

```
iscsidirect: faststore
     portal 10.10.10.1
     target iqn.2006-01.openfiler.com:tsn.dcb5aaaddd
```

### Storage Features

|  |  |
| --- | --- |
| Note | This backend works with VMs only. Containers cannot use this driver. |

Table 11. Storage features for backend iscsidirect






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images | raw | yes | no | no |

## Ceph RADOS Block Devices (RBD)

Storage pool type: rbd

[Ceph](https://ceph.com/) is a distributed object store and file system
designed to provide excellent performance, reliability and
scalability. RADOS block devices implement a feature rich block level
storage, and you get the following advantages:

* thin provisioning
* resizable volumes
* distributed and redundant (striped over multiple OSDs)
* full snapshot and clone capabilities
* self healing
* no single point of failure
* scalable to the exabyte level
* kernel and user space implementation available

|  |  |
| --- | --- |
| Note | For smaller deployments, it is also possible to run Ceph services directly on your Proxmox VE nodes. Recent hardware has plenty of CPU power and RAM, so running storage services and VMs on same node is possible. |

### Configuration

This backend supports the common storage properties nodes,
disable, content, and the following rbd specific properties:

monhost
:   List of monitor daemon IPs. Optional, only needed if Ceph is not running on the
    Proxmox VE cluster. With monhost set, Proxmox VE treats the cluster as external and
    keeps a separate key copy for this storage, even if the monitors belong to the
    Ceph cluster of this Proxmox VE cluster.

pool
:   Ceph pool name.

username
:   Ceph client ID. Optional, defaults to admin. Use only the ID without the
    client. prefix.

krbd
:   Enforce access to rados block devices through the krbd kernel module. Optional.

|  |  |
| --- | --- |
| Note | Containers will use krbd independent of the option value. |

Configuration Example for an external Ceph cluster (/etc/pve/storage.cfg)

```
rbd: ceph-external
        monhost 10.1.1.20 10.1.1.21 10.1.1.22
        pool ceph-external
        content images
        username pve-rbd
```

|  |  |
| --- | --- |
| Tip | You can use the rbd utility to do low-level management tasks. |

### Authentication

|  |  |
| --- | --- |
| Note | If Ceph is installed locally on the Proxmox VE cluster, the following is done automatically when adding the storage. |

If you use cephx authentication, which is enabled by default, provide a
keyring from the external Ceph cluster. Obtain or create a dedicated identity
with only the capabilities required for this storage, as described in
Ceph User Management.  
[[Ceph User Management](https://docs.ceph.com/en/tentacle/rados/operations/user-management/)]  
The example below uses client.pve-rbd; do not copy client.admin to a storage
client.

Copy the keyring to one Proxmox VE node:

```
# scp <external-ceph-server>:/etc/ceph/ceph.client.pve-rbd.keyring /root/rbd.keyring
```

Then pass that file and the identity without its client. prefix to pvesm:

```
# pvesm add rbd <name> --monhost "10.1.1.20 10.1.1.21 10.1.1.22" \
    --pool ceph-external --content images --username pve-rbd \
    --keyring /root/rbd.keyring
```

After pvesm succeeds, remove /root/rbd.keyring because it contains the key
in plain text.

When configuring an external RBD storage via the GUI, you can copy and paste
the keyring into the appropriate field.

The keyring will be stored at

```
# /etc/pve/priv/ceph/<STORAGE_ID>.keyring
```

If the external cluster rotates this identity, replace the stored keyring before
refreshing its consumers. The local cephx migration helper never rotates keys
of external clusters.

### Ceph client configuration (optional)

Connecting to an external Ceph storage doesn’t always allow setting
client-specific options in the config DB on the external cluster. You can add a
ceph.conf beside the Ceph keyring to change the Ceph client configuration for
the storage.

The ceph.conf needs to have the same name as the storage.

```
# /etc/pve/priv/ceph/<STORAGE_ID>.conf
```

|  |  |
| --- | --- |
| Note | Do not change these settings lightly. Proxmox VE is merging the <STORAGE\_ID>.conf with the storage configuration. |

### Storage Features

The rbd backend is a block level storage, and implements full
snapshot and clone functionality.

Table 12. Storage features for backend rbd






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images rootdir | raw | yes | yes | yes |

## Ceph Filesystem (CephFS)

Storage pool type: cephfs

CephFS implements a POSIX-compliant filesystem, using a [Ceph](https://ceph.com/)
storage cluster to store its data. As CephFS builds upon Ceph, it shares most of
its properties. This includes redundancy, scalability, self-healing, and high
availability.

|  |  |
| --- | --- |
| Tip | Proxmox VE can [manage Ceph setups](/pve-docs/chapter-pveceph.html#chapter_pveceph), which makes configuring a CephFS storage easier. As modern hardware offers a lot of processing power and RAM, running storage services and VMs on same node is possible without a significant performance impact. |

To use the CephFS storage plugin, you must replace the stock Debian Ceph client,
by adding our [Ceph repository](/pve-docs/chapter-sysadmin.html#sysadmin_package_repositories_ceph).
Once added, run apt update, followed by apt dist-upgrade, in order to get
the newest packages.

|  |  |
| --- | --- |
| Warning | Please ensure that there are no other Ceph repositories configured. Otherwise the installation will fail or there will be mixed package versions on the node, leading to unexpected behavior. |

### Configuration

This backend supports the common storage properties nodes,
disable, content, as well as the following cephfs specific properties:

fs-name
:   Name of the Ceph FS.

monhost
:   List of monitor daemon addresses. Optional, only needed if Ceph is not running
    on the Proxmox VE cluster. With monhost set, Proxmox VE treats the cluster as external
    and keeps a separate key copy for this storage, even if the monitors belong to
    the Ceph cluster of this Proxmox VE cluster.

path
:   The local mount point. Optional, defaults to /mnt/pve/<STORAGE\_ID>/.

username
:   Ceph client ID. Optional, defaults to admin. Use only the ID without the
    client. prefix.

subdir
:   CephFS subdirectory to mount. Optional, defaults to /.

fuse
:   Access CephFS through FUSE, instead of the kernel client. Optional, defaults
    to 0.

Configuration example for an external Ceph cluster (/etc/pve/storage.cfg)

```
cephfs: cephfs-external
        monhost 10.1.1.20 10.1.1.21 10.1.1.22
        path /mnt/pve/cephfs-external
        content backup
        username pve-cephfs
        fs-name cephfs
```

|  |  |
| --- | --- |
| Note | Don’t forget to set up the client’s secret key file, if cephx was not disabled. |

### Authentication

|  |  |
| --- | --- |
| Note | If Ceph is installed locally on the Proxmox VE cluster, the following is done automatically when adding the storage. |

If you use cephx authentication, which is enabled by default, provide the
secret of a dedicated identity with only the capabilities required for this
storage. Obtain or create the identity as described in
Ceph User Management.  
[[cephusermgmt]](#_footnote_cephusermgmt)  
The example below uses client.pve-cephfs; do not use client.admin for a
storage client.

Export the bare key through SSH to one Proxmox VE node:

```
# ssh root@<external-ceph-server> \
    'ceph auth get-key client.pve-cephfs' > /root/cephfs.secret
```

Then pass that file and the identity without its client. prefix to pvesm:

```
# pvesm add cephfs <name> --monhost "10.1.1.20 10.1.1.21 10.1.1.22" \
    --fs-name cephfs --content backup --username pve-cephfs \
    --keyring /root/cephfs.secret
```

After pvesm succeeds, remove /root/cephfs.secret because it contains the key
in plain text.

When configuring an external CephFS storage in the web interface, paste the
secret into the appropriate field. CephFS uses the bare key, not the RBD keyring
format with a [client.<USER>] section. Proxmox VE stores the secret at
/etc/pve/priv/ceph/<STORAGE\_ID>.secret.

If the external cluster rotates this identity, replace the stored secret before
remounting the storage. The local cephx migration helper never rotates keys of
external clusters.

### Storage Features

The cephfs backend is a POSIX-compliant filesystem, on top of a Ceph cluster.

Table 13. Storage features for backend cephfs






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| vztmpl iso backup snippets | none | yes | yes[1] | no |

[1] While no known bugs exist, snapshots are not yet guaranteed to be stable,
as they lack sufficient testing.

## BTRFS Backend

Storage pool type: btrfs

On the surface, this storage type is very similar to the directory storage type,
so see the directory backend section for a general overview.

The main difference is that with this storage type raw formatted disks will be
placed in a subvolume, in order to allow taking snapshots and supporting offline
storage migration with snapshots being preserved.

|  |  |
| --- | --- |
| Note | BTRFS will honor the O\_DIRECT flag when opening files, meaning VMs should not use cache mode none, otherwise there will be checksum errors. |

### Configuration

This backend is configured similarly to the directory storage. Note that when
adding a directory as a BTRFS storage, which is not itself also the mount point,
it is highly recommended to specify the actual mount point via the
is\_mountpoint option.

For example, if a BTRFS file system is mounted at /mnt/data2 and its
pve-storage/ subdirectory (which may be a snapshot, which is recommended)
should be added as a storage pool called data2, you can use the following
entry:

```
btrfs: data2
        path /mnt/data2/pve-storage
        content rootdir,images
        is_mountpoint /mnt/data2
```

### Snapshots

When taking a snapshot of a subvolume or raw file, the snapshot will be
created as a read-only subvolume with the same path followed by an @ and the
snapshot’s name.

## ZFS over ISCSI Backend

Storage pool type: zfs

This backend accesses a remote machine having a ZFS pool as storage and an iSCSI
target implementation via ssh. For each guest disk it creates a ZVOL and,
exports it as iSCSI LUN. This LUN is used by Proxmox VE for the guest disk.

The following iSCSI target implementations are supported:

* LIO (Linux)
* IET (Linux)
* ISTGT (FreeBSD)
* Comstar (Solaris)

|  |  |
| --- | --- |
| Note | This plugin needs a ZFS capable remote storage appliance, you cannot use it to create a ZFS Pool on a regular Storage Appliance/SAN |

### Configuration

In order to use the ZFS over iSCSI plugin you need to configure the remote
machine (target) to accept ssh connections from the Proxmox VE node. Proxmox VE connects to the target for creating the ZVOLs and exporting them via iSCSI.
Authentication is done through a ssh-key (without password protection) stored in
/etc/pve/priv/zfs/<target\_ip>\_id\_rsa

The following steps create a ssh-key and distribute it to the storage machine
with IP 192.0.2.1:

```
mkdir /etc/pve/priv/zfs
ssh-keygen -f /etc/pve/priv/zfs/192.0.2.1_id_rsa
ssh-copy-id -i /etc/pve/priv/zfs/192.0.2.1_id_rsa.pub root@192.0.2.1
ssh -i /etc/pve/priv/zfs/192.0.2.1_id_rsa root@192.0.2.1
```

The backend supports the common storage properties content, nodes,
disable, and the following ZFS over ISCSI specific properties:

pool
:   The ZFS pool/filesystem on the iSCSI target. All allocations are done within that
    pool.

portal
:   iSCSI portal (IP or DNS name with optional port).

target
:   iSCSI target.

iscsiprovider
:   The iSCSI target implementation used on the remote machine

comstar\_tg
:   target group for comstar views.

comstar\_hg
:   host group for comstar views.

lio\_tpg
:   target portal group for Linux LIO targets

nowritecache
:   disable write caching on the target

blocksize
:   Set ZFS blocksize parameter.

sparse
:   Use ZFS thin-provisioning. A sparse volume is a volume whose
    reservation is not equal to the volume size.

Configuration Examples (/etc/pve/storage.cfg)

```
zfs: lio
   blocksize 4k
   iscsiprovider LIO
   pool tank
   portal 192.0.2.111
   target iqn.2003-01.org.linux-iscsi.lio.x8664:sn.xxxxxxxxxxxx
   content images
   lio_tpg tpg1
   sparse 1

zfs: solaris
   blocksize 4k
   target iqn.2010-08.org.illumos:02:xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx:tank1
   pool tank
   iscsiprovider comstar
   portal 192.0.2.112
   content images

zfs: freebsd
   blocksize 4k
   target iqn.2007-09.jp.ne.peach.istgt:tank1
   pool tank
   iscsiprovider istgt
   portal 192.0.2.113
   content images

zfs: iet
   blocksize 4k
   target iqn.2001-04.com.example:tank1
   pool tank
   iscsiprovider iet
   portal 192.0.2.114
   content images
```

### Storage Features

The ZFS over iSCSI plugin provides a shared storage, which is capable of
snapshots. You need to make sure that the ZFS appliance does not become a single
point of failure in your deployment.

Table 14. Storage features for backend iscsi






| Content types | Image formats | Shared | Snapshots | Clones |
| --- | --- | --- | --- | --- |
| images | raw | yes | yes | no |
