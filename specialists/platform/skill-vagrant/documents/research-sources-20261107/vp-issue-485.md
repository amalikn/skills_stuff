<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels/issues/485
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: 200 via GitHub API (`gh issue view --json`)

---

# #485 Parallels Desktop Enterprise edition is not a supported version

State: CLOSED; opened 2025-02-24T10:33:18Z; closed 2025-02-24T13:34:00Z

## Body

After installing some updates this weekend, I find I cannot launch my existing vagrant-parallels virtual macine:

```
# robmee01@YFKPW136N2:~/work/dbf/DBF  (main *$|u+5) 10:28:07
# vagrant up
The provider 'parallels' that was requested to back the machine
'default' is reporting that it isn't usable on this system. The
reason is shown below:

Vagrant has detected that you have an edition of Parallels Desktop for Mac
installed that is not supported. Vagrant Parallels provider is compatible
only with Pro and Business editions of Parallels Desktop. Other editions
do not have command line functionality and can not be used with Vagrant.

Please upgrade your installation: https://parallels.com/desktop
```

This is suprising, as it was working on Friday and my license is still valid:

```
# robmee01@YFKPW136N2:~/work/dbf/DBF  (main *$|u+5) 10:28:14
# prlsrvctl info --license --json
{
        "status": "ACTIVE",
        "serial": "W3WSRH-******-******-******-KF9GKH",
        "expiration": "04\/05\/2026 09:16:59",
        "main_period_ends_at": "03\/06\/2026 09:16:59",
        "grace_period_ends_at": "04\/05\/2026 09:16:59",
        "cpu_total": 32,
        "max_memory": 131072,
        "edition": "enterprise",
        "is_volume": "yes",
        "deferred_activation": "disabled",
        "uuid": "c7934f05a3384cee9a5904c09db8be27"
}
```

Version info:

```
# robmee01@YFKPW136N2:~/work/dbf/DBF  (main *$|u+5) 10:28:52
# vagrant --version
Vagrant 2.4.1


# robmee01@YFKPW136N2:~/work/dbf/DBF  (main *$|u+5) 10:34:07
# vagrant plugin list
vagrant-parallels (2.4.2, global)
  - Version Constraint: > 0


# robmee01@YFKPW136N2:~/work/dbf/DBF  (main *$|u+5) 10:30:59
# prlsrvctl info
ID: {8ce251f5-ee77-4991-9d33-9a532fa44ddc}
Hostname: 127.0.0.1
OS: macOS 15.3.1(24D70)
Version: Desktop 20.2.1-55876
Build flags: external
Started as service: on
VM home: /Users/robmee01/Parallels
Memory limit: auto
Minimal security level: low
Manage settings for new users: allow
CEP mechanism: off
Verbose log: off
Log rotation: on
External device auto connect: host
Web portal domain: parallels.com
Web portal domain auto mode: on
Allow attach screenshots: on
Custom password protection: off
Preferences are locked: off
Disable deleting report archive: off
Add serial port output to report: off
License: state='valid' key='W3WSRH-******-******-******-KF9GKH' restricted='false'
Hardware Id: {b15a8054-6b89-50ce-a462-272c3b14e977}
Signed In: no
Hardware info:
     hdd  APPLE SSD AP1024Z Media (disk0)          '/dev/disk0'
hdd-part  iBootSystemContainer                     '/dev/disk0s1'
hdd-part  Container                                '/dev/disk0s2'
hdd-part  RecoveryOSContainer                      '/dev/disk0s3'
     hdd  AppleAPFSMedia (disk3)                   '/dev/disk3'
hdd-part  Macintosh HD                             '/dev/disk3s1'
hdd-part  Preboot                                  '/dev/disk3s2'
hdd-part  Recovery                                 '/dev/disk3s3'
hdd-part  Update                                   '/dev/disk3s4'
hdd-part  Data                                     '/dev/disk3s5'
hdd-part  VM                                       '/dev/disk3s6'
     net  Wi-Fi                                    'en0'
     usb  Apple Watch Magnetic Charging Cable      '120000|05ac|1392|full|--|DLC80950D4CH1Y8AA'
     usb  MSI Gaming Controller                    '130000|1462|3fa4|full|--|A02019010700'
  serial  /dev/cu.debug-console                    '/dev/cu.debug-console'
  serial  /dev/cu.WoojerStrapEdge                  '/dev/cu.WoojerStrapEdge'
  serial  /dev/cu.Bluetooth-Incoming-Port          '/dev/cu.Bluetooth-Incoming-Port'
```

Is there a way to override this check, as I am fairly certain my version of Parallels Desktop supports all the CLI features needed by vagrant-parallels?

## Comment by sai-kumar-peddireddy at 2025-02-24T12:06:42Z

@meermanr working on this..

## Comment by meermanr at 2025-02-24T14:04:37Z

Thank you @sai-kumar-peddireddy !

Are you also able to update the docs at https://parallels.github.io/vagrant-parallels/docs/installation/ which currently read:

> Only Pro and Business editions of Parallels Desktop for Mac can be used with this Vagrant provider

There are also multiple mentions of "Pro" and "Business" in this code base that should probably be extended too.

I've been able to build and install v2.4.3 locally, but installing via `vagrant install vagrant-parallels` still installs the older verison, v2.4.2. 

## Comment by sai-kumar-peddireddy at 2025-02-25T08:47:04Z

> Thank you [@sai-kumar-peddireddy](https://github.com/sai-kumar-peddireddy) !
> 
> Are you also able to update the docs at https://parallels.github.io/vagrant-parallels/docs/installation/ which currently read:
> 
> > Only Pro and Business editions of Parallels Desktop for Mac can be used with this Vagrant provider
> 
> There are also multiple mentions of "Pro" and "Business" in this code base that should probably be extended too.
> 
> I've been able to build and install v2.4.3 locally, but installing via `vagrant install vagrant-parallels` still installs the older verison, v2.4.2.

You are welcome! Thanks for mentioning it.  will update docs and release it officially.
