<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://www.freedesktop.org/software/systemd/man/latest/networkd.conf.html
**Retrieved**: 2026-11-07 15:55 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://www.freedesktop.org/software/systemd/man/latest/networkd.conf.html:
# networkd.conf

## Name

networkd.conf, networkd.conf.d — Global Network configuration files

## Synopsis

|  |
| --- |
| `/etc/systemd/networkd.conf` |
| `/run/systemd/networkd.conf` |
| `/usr/local/lib/systemd/networkd.conf` |
| `/usr/lib/systemd/networkd.conf` |
| `/etc/systemd/networkd.conf.d/*.conf` |
| `/run/systemd/networkd.conf.d/*.conf` |
| `/usr/local/lib/systemd/networkd.conf.d/*.conf` |
| `/usr/lib/systemd/networkd.conf.d/*.conf` |

## Description[¶](#Description "Permalink to this headline")

These configuration files control global network parameters.

## Configuration Directories and Precedence[¶](#Configuration%20Directories%20and%20Precedence "Permalink to this headline")

The default configuration is set during compilation, so configuration is only needed when it is
necessary to deviate from those defaults. The main configuration file is loaded from one of the
listed directories in order of priority, only the first file found is used:
`/etc/systemd/`,
`/run/systemd/`,
`/usr/local/lib/systemd/` [[1]](#ftn.usr-local-footnote),
`/usr/lib/systemd/`.
The vendor version of the file contains commented out entries showing the defaults as a guide to the
administrator. Local overrides can also be created by creating drop-ins, as described below. The main
configuration file can also be edited for this purpose (or a copy in `/etc/` if it is
shipped under `/usr/`), however using drop-ins for local configuration is recommended
over modifications to the main configuration file.

In addition to the main configuration file, drop-in configuration snippets are read from
`/usr/lib/systemd/*.conf.d/`, `/usr/local/lib/systemd/*.conf.d/`,
and `/etc/systemd/*.conf.d/`. Those drop-ins have higher precedence and override the
main configuration file. Files in the `*.conf.d/` configuration subdirectories are
sorted by their filename in lexicographic order, regardless of in which of the subdirectories they
reside. When multiple files specify the same option, for options which accept just a single value, the
entry in the file sorted last takes precedence, and for options which accept a list of values, entries
are collected as they occur in the sorted files.

When packages need to customize the configuration, they can install drop-ins under
`/usr/`. Files in `/etc/` are reserved for the local administrator,
who may use this logic to override the configuration files installed by vendor packages. Drop-ins have to
be used to override package drop-ins, since the main configuration file has lower precedence. It is
recommended to prefix all filenames in those subdirectories with a two-digit number and a dash, to
simplify the ordering. This also defines a concept of drop-in priorities to allow OS vendors to ship
drop-ins within a specific range lower than the range used by users. This should lower the risk of
package drop-ins overriding accidentally drop-ins defined by users. It is recommended to use the range
10-40 for drop-ins in `/usr/` and the range 60-90 for drop-ins in
`/etc/` and `/run/`, to make sure that local and transient drop-ins
take priority over drop-ins shipped by the OS vendor.

To disable a configuration file supplied by the vendor, the recommended way is to place a symlink
to `/dev/null` in the configuration directory in `/etc/`, with the
same filename as the vendor configuration file.

## [Network] Section Options[¶](#%5BNetwork%5D%20Section%20Options "Permalink to this headline")

The following options are available in the [Network] section:

`SpeedMeter=`[¶](#SpeedMeter= "Permalink to this term")
:   Takes a boolean. If set to yes, then **systemd-networkd**
    measures the traffic of each interface, and
    **networkctl status *`INTERFACE`*** shows the measured speed.
    Defaults to no.

    Added in version 244.

`SpeedMeterIntervalSec=`[¶](#SpeedMeterIntervalSec= "Permalink to this term")
:   Specifies the time interval to calculate the traffic speed of each interface.
    If `SpeedMeter=no`, the value is ignored. Defaults to 10sec.

    Added in version 244.

`ManageForeignRoutingPolicyRules=`[¶](#ManageForeignRoutingPolicyRules= "Permalink to this term")
:   A boolean. When true, **systemd-networkd** will remove rules
    that are not configured in .network files (except for rules with protocol
    "`kernel`"). When false, it will not remove any foreign rules, keeping them even
    if they are not configured in a .network file. Defaults to yes.

    Added in version 249.

`ManageForeignRoutes=`[¶](#ManageForeignRoutes= "Permalink to this term")
:   A boolean. When true, **systemd-networkd** will remove routes
    that are not configured in .network files (except for routes with protocol
    "`kernel`", "`dhcp`" when `KeepConfiguration=`
    is true or "`dhcp`", and "`static`" when
    `KeepConfiguration=` is true or "`static`"). When false, it will
    not remove any foreign routes, keeping them even if they are not configured in a .network file.
    Defaults to yes.

    Added in version 246.

`ManageForeignNextHops=`[¶](#ManageForeignNextHops= "Permalink to this term")
:   A boolean. When true, **systemd-networkd** will remove nexthops
    that are not configured in .network files (except for routes with protocol
    "`kernel`"). When false, it will
    not remove any foreign nexthops, keeping them even if they are not configured in a .network file.
    Defaults to yes.

    Added in version 256.

`RouteTable=`[¶](#RouteTable= "Permalink to this term")
:   Defines the route table name. Takes a whitespace-separated list of the pairs of
    route table name and number. The route table name and number in each pair are separated with a
    colon, i.e., "`name:number`".
    The route table name must not be "`default`", "`main`", or
    "`local`", as these route table names are predefined with route table number 253,
    254, and 255, respectively. The route table number must be an integer in the range 1…4294967295,
    except for predefined numbers 253, 254, and 255. This setting can be specified multiple times.
    If an empty string is specified, then the list specified earlier are cleared. Defaults to unset.

    Added in version 248.

`IPv4Forwarding=`[¶](#IPv4Forwarding= "Permalink to this term")
:   Configures IPv4 packet forwarding for the system. Takes a boolean value. This controls the
    `net.ipv4.conf.default.forwarding` and
    `net.ipv4.conf.all.forwarding` sysctl options. See
    [IP Sysctl](https://docs.kernel.org/networking/ip-sysctl.html)
    for more details about the sysctl options. Defaults to unset and the sysctl options will not be
    changed.

    If an interface is configured with a .network file that enables `IPMasquerade=`
    for IPv4 (that is, "`ipv4`" or "`both`"), this setting is implied
    unless explicitly specified. See `IPMasquerade=` in
    [systemd.network(5)](systemd.network.html#)
    for more details.

    Added in version 256.

`IPv6Forwarding=`[¶](#IPv6Forwarding= "Permalink to this term")
:   Configures IPv6 packet forwarding for the system. Takes a boolean value. This controls the
    `net.ipv6.conf.default.forwarding` and
    `net.ipv6.conf.all.forwarding` sysctl options. See
    [IP Sysctl](https://docs.kernel.org/networking/ip-sysctl.html)
    for more details about the sysctl options. Defaults to unset and the sysctl options will not be
    changed.

    If an interface is configured with a .network file that enables `IPMasquerade=`
    for IPv6 (that is, "`ipv6`" or "`both`"), this setting is implied
    unless explicitly specified. See `IPMasquerade=` in
    [systemd.network(5)](systemd.network.html#)
    for more details.

    Added in version 256.

`IPv6PrivacyExtensions=`[¶](#IPv6PrivacyExtensions= "Permalink to this term")
:   Specifies the default value for per-network `IPv6PrivacyExtensions=`.
    Takes a boolean or the special values "`prefer-public`" and
    "`kernel`". See for details in
    [systemd.network(5)](systemd.network.html#).
    Defaults to "`no`".

    Added in version 254.

`UseDomains=`[¶](#UseDomains= "Permalink to this term")
:   Specifies the network- and protocol-independent default value for the same settings in
    [IPv6AcceptRA], [DHCPv4], and [DHCPv6] sections below. Takes a boolean, or the special value
    `route`. See the same setting in
    [systemd.network(5)](systemd.network.html#).
    Defaults to "`no`".

    Added in version 256.

## [IPv6AcceptRA] Section Options[¶](#%5BIPv6AcceptRA%5D%20Section%20Options "Permalink to this headline")

This section configures the default setting of the Neighbor Discovery. The following options are
available in the [IPv6AcceptRA] section:

`UseDomains=`[¶](#UseDomains=1 "Permalink to this term")
:   Specifies the network-independent default value for the same setting in the [IPv6AcceptRA]
    section in
    [systemd.network(5)](systemd.network.html#).
    Takes a boolean, or the special value `route`. When unspecified, the value specified
    in the [Network] section in
    [networkd.conf(5)](networkd.conf.html#),
    which defaults to "`no`", will be used.

    Added in version 256.

## [IPv6AddressLabel] Section Options[¶](#%5BIPv6AddressLabel%5D%20Section%20Options "Permalink to this headline")

An [IPv6AddressLabel] section accepts the following keys. Specify multiple [IPv6AddressLabel]
sections to configure multiple address labels. IPv6 address labels are used for address selection.
See [RFC 3484](https://tools.ietf.org/html/rfc3484). Precedence is managed by
userspace, and only the label itself is stored in the kernel.

`Label=`[¶](#Label= "Permalink to this term")
:   The label for the prefix, an unsigned integer in the range 0…4294967294. 0xffffffff is
    reserved. This setting is mandatory.

    Added in version 257.

`Prefix=`[¶](#Prefix= "Permalink to this term")
:   IPv6 prefix is an address with a prefix length, separated by a slash
    "`/`" character. This setting is mandatory.

    Added in version 257.

## [DHCPv4] Section Options[¶](#%5BDHCPv4%5D%20Section%20Options "Permalink to this headline")

This section configures the default configurations of DHCPv4 client. If the DHCPv4 client is
enabled on an interface, then the configurations below will be used by default unless explicitly
specified in the corresponding `.network` file. See also
[systemd.network(5)](systemd.network.html#).

The following options are understood:

`ClientIdentifier=`[¶](#ClientIdentifier= "Permalink to this term")
:   Specifies the default DHCPv4 client identifier to be used. Takes one of `mac`
    or `duid`. If set to `mac`, the MAC address of each link will be used.
    If set to `duid`, an RFC4361-compliant Client ID, which is the combination of IAID
    and DUID, is used. IAID can be configured by `IAID=` in each matching
    `.network` file. DUID can be configured by `DUIDType=` and
    `DUIDRawData=`. Defaults to `duid`.

    Added in version 258.

`DUIDType=`[¶](#DUIDType= "Permalink to this term")
:   Specifies how the DUID should be generated. See
    [RFC 3315](https://tools.ietf.org/html/rfc3315#section-9)
    for a description of all the options.

    This takes an integer in the range 0…65535, or one of the following string values:

    `vendor`[¶](#vendor "Permalink to this term")
    :   If "`DUIDType=vendor`", then the DUID value will be generated using
        "`43793`" as the vendor identifier (systemd) and hashed contents of
        [machine-id(5)](machine-id.html#).
        This is the default if `DUIDType=` is not specified.

        Added in version 230.

    `uuid`[¶](#uuid "Permalink to this term")
    :   If "`DUIDType=uuid`", and `DUIDRawData=` is not set,
        then the product UUID is used as a DUID value. If a system does not have valid product UUID, then
        an application-specific
        [machine-id(5)](machine-id.html#)
        is used as a DUID value. About the application-specific machine ID, see
        [sd\_id128\_get\_machine\_app\_specific(3)](sd_id128_get_machine_app_specific.html#).

        Added in version 230.

    `link-layer-time[:TIME]`, `link-layer`[¶](#link-layer-time%5B:TIME%5D "Permalink to this term")
    :   If "`link-layer-time`" or "`link-layer`" is specified,
        then the MAC address of the interface is used as a DUID value. The value "`link-layer-time`"
        can take additional time value after a colon, e.g. "`link-layer-time:2018-01-23 12:34:56 UTC`".
        The default time value is "`2000-01-01 00:00:00 UTC`".

        Added in version 240.

    In all cases, `DUIDRawData=` can be used to override the
    actual DUID value that is used.

    Added in version 230.

`DUIDRawData=`[¶](#DUIDRawData= "Permalink to this term")
:   Specifies the DHCP DUID value as a single newline-terminated, hexadecimal string, with each
    byte separated by "`:`". The DUID that is sent is composed of the DUID type specified by
    `DUIDType=` and the value configured here.

    The DUID value specified here overrides the DUID that
    [systemd-networkd.service(8)](systemd-networkd.service.html#)
    generates from the machine ID. To configure DUID per-network, see
    [systemd.network(5)](systemd.network.html#).
    The configured DHCP DUID should conform to the specification in
    [RFC 3315](http://tools.ietf.org/html/rfc3315#section-9),
    [RFC 6355](http://tools.ietf.org/html/rfc6355). To configure IAID, see
    [systemd.network(5)](systemd.network.html#).

    **Example 1. A `DUIDType=vendor` with a custom value**

    ```
    DUIDType=vendor
    DUIDRawData=00:00:ab:11:f9:2a:c2:77:29:f9:5c:00
    ```

    This specifies a 14 byte DUID, with the type DUID-EN ("`00:02`"), enterprise number
    43793 ("`00:00:ab:11`"), and identifier value "`f9:2a:c2:77:29:f9:5c:00`".

    Added in version 230.

`UseDomains=`[¶](#UseDomains=2 "Permalink to this term")
:   Same as the one in the [IPv6AcceptRA] section, but applied for DHCPv4 protocol.

    Added in version 256.

## [DHCPv6] Section Options[¶](#%5BDHCPv6%5D%20Section%20Options "Permalink to this headline")

This section configures the default configurations of DHCPv6 client. If the DHCPv6 client is
enabled on an interface, then the configurations below will be used by default unless explicitly
specified in the corresponding `.network` file. See also
[systemd.network(5)](systemd.network.html#).

The following options are understood:

`DUIDType=`, `DUIDRawData=`[¶](#DUIDType=1 "Permalink to this term")
:   As in the [DHCPv4] section.

    Added in version 249.

`UseDomains=`[¶](#UseDomains=3 "Permalink to this term")
:   As in the [DHCPv4] section.

    Added in version 256.

## [DHCPRelay] Section Options[¶](#%5BDHCPRelay%5D%20Section%20Options "Permalink to this headline")

The [DHCPRelay] section contains host-wide settings for the DHCP relay agent.

`ServerAddress=`[¶](#ServerAddress= "Permalink to this term")
:   Specifies the IPv4 address of the upstream DHCP server. This is required for the host to act
    as a DHCP relay agent.

    Added in version 261.

`OverrideServerIdentifier=`[¶](#OverrideServerIdentifier= "Permalink to this term")
:   Takes a boolean value. When enabled, the Server Identifier Override sub-option and the Relay
    Agent Flags sub-option in the Relay Agent Information option will be appended to the DHCP message
    forwarded to the upstream DHCP server. Defaults to false.

    Added in version 261.

`RemoteId=`[¶](#RemoteId= "Permalink to this term")
:   Specifies the remote ID, which is typically used by DHCP servers to identify the DHCP relay
    agent. Takes a data type and data separated with a colon
    ("`type:value`"). The type
    takes one of "`uint8`", "`uint16`", "`uint32`",
    "`ipv4address`", "`ipv6address`", or "`string`".
    Special characters in the data string may be escaped using
    [C-style escapes](https://en.wikipedia.org/wiki/Escape_sequences_in_C#Table_of_escape_sequences).
    If unset, a UUID generated from the local machine ID will be used.

    Added in version 261.
:   Specifies an extra sub-option in the Relay Agent Information option, which is appended to
    DHCP messages forwarded to the upstream DHCP server. Takes a sub-option code, data type, and data
    separated with a colon
    ("`code:type:value`").
    The code is an integer in 1…254. See `RemoteId=` in the above for the acceptable
    type and data. This setting can be specified multiple times. When an empty string is specified,
    all previous assignments are cleared. Defaults to unset, and no extra sub-option will be appended.

    Added in version 261.

## [DHCPServer] Section Options[¶](#%5BDHCPServer%5D%20Section%20Options "Permalink to this headline")

This section configures the default setting of the DHCP server. The following options are available
in the [DHCPServer] section:

`PersistLeases=`[¶](#PersistLeases= "Permalink to this term")
:   Specifies the default value for per-network `PersistLeases=`.
    Takes a boolean or special value "`runtime`". See for details in
    [systemd.network(5)](systemd.network.html#).
    Defaults to "`yes`".

    Added in version 256.

---

[[1]](#usr-local-footnote) 💣💥🧨💥💥💣 Please note that those configuration files must be available at all times. If
`/usr/local/` is a separate partition, it may not be available during early boot,
and must not be used for configuration.
