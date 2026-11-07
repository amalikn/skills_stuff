Contents of https://pve.proxmox.com/wiki/Storage:_Proxmox_Backup_Server:
# Storage: Proxmox Backup Server

[![screenshot/storage-pbs-encryption-with-key.png](/pve-docs/images/screenshot/storage-pbs-encryption-with-key.png)](/pve-docs/images/screenshot/storage-pbs-encryption-with-key.png)

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
