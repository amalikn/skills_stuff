Contents of https://pve.proxmox.com/wiki/Serial_Terminal:
## Why would I need a serial terminal / serial console?

Note: This applies to QEMU/KVM virtualization.

If you do a lot of work over SSH on your Proxmox VE server, you would maybe appreciate to connect to your running VMs
like:

```
qm status 101
status: running
```

```
qm terminal 101
starting serial terminal on interface serial0 (press control-O to exit)
Debian GNU/Linux 8 debian8 ttyS0
debian8 login:
```

Other use cases:

* you lost network access to the guest and VNC is either too slow for you or does not have the features you need (i.e. easy copy/paste between other terminals)
* your guest freezes or kernel panics, you want to debug it, but it is impossible to capture all messages on VNC screen
* your keyboard layout is borked on the guest
* you are familiar with `xm console <guest>` from Xen and you want to use a similar feature here

## Some background so you get the idea

When you start Unix/Linux on a PC, the default input device is the attached keyboard (PS/2 or USB), and the default output device is the available VGA /HDMI / Display port of the PC. This is called in Unix-speak the **default console**, or **system console**.
During boot, the kernel sends its boot messages, like device detection, to this default console, and at the end of the boot processes, fires a "login: " prompt on this console. (Actually it spawns multiple login prompts, you can switch between them with Ctrl-alt-F1, Ctrl-alt-F2, etc ... )

Now it is perfectly fine to send the boot messages and start a login prompt on something else. For instance the Linux Kernel has a **netconsole** feature, to send the boot messages over the network to another Linux computer. It is also possible to send a copy of the boot messages, and start a login prompt on the **serial port** of the PC. We get then what is called a **serial console**.
If you connect to this serial port any computing device with a **terminal emulation** program, it will be possible to work on the Linux PC as if you were using the PC locally in text mode. The requirements of the terminal emulation are quite low, so you could use HyperTerminal on a Windows PC, Minicom on Linux or even an [old Atari ST](https://www.tldp.org/LDP/LG/issue70/arndt.html) with the appropriate program.

### How does this apply to Proxmox VE ?

In Proxmox things work exactly the same, but with emulated devices. NoVNC/ VNC Applet connects to your VM keyboard and VM VGA display and displays the stuff you would expect from a real PC on a VGA display with a locally attached keyboard.
Now we can also configure our VM to have an emulated serial port, and instruct the OS, to send a copy of the boot messages / start a login prompt on the emulated serial port.
Once this is configured it will be possible to connect from the host (i.e. the server running PVE) using a **terminal emulation** program, which is handily builtin in the Proxmox Qemu Manager.

## Configuration on the host

##### Add a virtual serial port to the VM

This can be done in the Proxmox VE web GUI under Hardware -> Add -> Serial Port. As explained in the [qm documentation](https://pve.proxmox.com/pve-docs/qm.1.html), it is possible to add multiple serial ports to a VM.

Alternatively, it can also be set via the CLI by running:

```
qm set <VMID> -serial0 socket
```

Or edited directly in the VM configuration file:

```
# open  /etc/pve/qemu-server/<VMID>.conf and add the following parameter at the end of file
serial0: socket
```

## Configuration on the guest

### Configure guests that use systemd

As explained in [systemd for Administrators, Part XVI](https://0pointer.de/blog/projects/serial-console.html), setting up a serial terminal in a VM with systemd is easy - only the kernel parameters need to be set (see below).

### Configure guests that use other init systems

As detailed in <https://help.ubuntu.com/community/SerialConsoleHowto#Server_Setup> , check if you have the file **/etc/init/ttyS0.conf**. If not, create it:

```
   # ttyS0 - getty
   #
   # This service maintains a getty on ttyS0 from the point the system is
   # started until it is shut down again.
```

```
   start on stopped rc RUNLEVEL=[12345]
   stop on runlevel [!12345]
```

```
   respawn
   exec /sbin/getty -L 115200 ttyS0 vt102
```

then ask upstart to start terminal

```
   sudo start ttyS0
```

In case multiple serial ports are configured, use the appropriate port number(s) instead of (or in addition to) `ttyS0`. You might consider creating the ttyS1.conf file as well, just as a backup in case you have a crash with ttyS0.

### Reboot the VM, verify that the emulated serial port is there

```
dmesg | grep ttyS
[    0.457814] 00:0a: ttyS0 at I/O 0x3f8 (irq = 4) is a 16550A
```

For guests using systemd, no further configuration should be necessary. In case of special setups (for example, if more than one serial login prompt is needed or the kernel console should be redirected to a different terminal than the login prompt), it might be necessary to enable and start the service manually inside the VM, for each serial port:

```
systemctl enable serial-getty@ttyS0.service
systemctl start serial-getty@ttyS0.service
```

For init systems other than systemd, if ttyS0 is not there, type the following inside the VM:

```
sudo start ttyS0
```

### Instruct grub2 to send the boot messages on the VGA display and on the serial port

In `/etc/default/grub`, append the GRUB\_CMDLINE\_LINUX parameter to contain the following options in addition to the existing ones:

```
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0"
```

In case multiple serial ports are configured, use the appropriate port number(s) instead of (or in addition to) `ttyS0`.

Afterwards, run:

```
# Debian-based
update-grub
# RedHat-based
grub2-mkconfig --output=/boot/grub2/grub.cfg
```

and do a final reboot.

For more details on the available Linux kernel parameters, please check [Linux Serial Console](https://docs.kernel.org/admin-guide/serial-console.html).

## Connecting to the Serial Terminal

On the Host, just enter

```
 qm terminal <VMID>
```

and enter **enter** a second time you should get a login prompt

**Note:** if it seems this is not working, and if you have defined ttyS1, you can connect to itwith the command

```
 qm terminal <VMID> -iface serial1
```

Now if you reboot your system you should see that the kernel startup messages are send to both your serial terminal and noVNC display.

Additionally (quoting from a private email, edited for clarity):

```
Qemu also supports binding the emulated serial port to a telnet server.  Look for the -chardev parameter in the qemu-kvm manual page.  (With proxmox you would then use the "args:" parameter in vm.conf to specify extra args.)  This would allow you to telnet to your host on a specific port to get a serial console.  As with every telnet traffic remember that nothing is encrypted, so I wouldn't do this in a production setup.
```

## Troubleshooting

You can check that the virtual serial port is present, and properly bound to the unix socket that **qm terminal** uses with:

```
qm monitor <VMiD>
info chardev
```

which should contains a line starting with *serial0* like:

```
serial0: filename=disconnected:unix:/var/run/qemu-server/101.serial0,server
```

Remember the `qm terminal` uses Ctrl-O as shortcut, so saving a file from `nano` with Ctrl-O will log you out instead

## Going Further

It is also possible to have the grub2 and grub accessible from the serial port. See <https://help.ubuntu.com/community/Grub2#Booting_from_a_serial_console> for how to do this with Grub2.
