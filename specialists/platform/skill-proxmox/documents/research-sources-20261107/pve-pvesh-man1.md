Contents of https://pve.proxmox.com/pve-docs/pvesh.1.html:
# pvesh(1)

[↑](#)

## NAME

pvesh - Shell interface for the Proxmox VE API

## SYNOPSIS

**pvesh** <COMMAND> [ARGS] [OPTIONS]

**pvesh create** <api\_path> [OPTIONS] [FORMAT\_OPTIONS]

Call API POST on <api\_path>.

<api\_path>: <string>
:   API path.

--noproxy <boolean>
:   Disable automatic proxying.

**pvesh delete** <api\_path> [OPTIONS] [FORMAT\_OPTIONS]

Call API DELETE on <api\_path>.

<api\_path>: <string>
:   API path.

--noproxy <boolean>
:   Disable automatic proxying.

**pvesh get** <api\_path> [OPTIONS] [FORMAT\_OPTIONS]

Call API GET on <api\_path>.

<api\_path>: <string>
:   API path.

--noproxy <boolean>
:   Disable automatic proxying.

**pvesh help** [OPTIONS]

Get help about specified command.

--extra-args <array>
:   Shows help for a specific command

--verbose <boolean>
:   Verbose output format.

**pvesh ls** <api\_path> [OPTIONS] [FORMAT\_OPTIONS]

List child objects on <api\_path>.

<api\_path>: <string>
:   API path.

--noproxy <boolean>
:   Disable automatic proxying.

**pvesh set** <api\_path> [OPTIONS] [FORMAT\_OPTIONS]

Call API PUT on <api\_path>.

<api\_path>: <string>
:   API path.

--noproxy <boolean>
:   Disable automatic proxying.

**pvesh usage** <api\_path> [OPTIONS]

print API usage information for <api\_path>.

<api\_path>: <string>
:   API path.

--command <create | delete | get | set>
:   API command.

--returns <boolean>
:   Including schema for returned data.

--verbose <boolean>
:   Verbose output format.

## DESCRIPTION

The Proxmox VE management tool (pvesh) allows to directly invoke API
function, without using the REST/HTTPS server.

|  |  |
| --- | --- |
| Note | Only *root* is allowed to do that. |

## FORMAT\_OPTIONS

It is possible to specify the output format using the
--output-format parameter. The default format *text* uses ASCII-art
to draw nice borders around tables. It additionally transforms some
values into human-readable text, for example:

* Unix epoch is displayed as ISO 8601 date string.
* Durations are displayed as week/day/hour/minute/second count, i.e 1d 5h.
* Byte sizes value include units (B, KiB, MiB, GiB, TiB, PiB).
* Fractions are display as percentage, i.e. 1.0 is displayed as 100%.

You can also completely suppress output using option --quiet.

--human-readable <boolean> (*default =* 1)
:   Call output rendering functions to produce human readable text.

--noborder <boolean> (*default =* 0)
:   Do not draw borders (for *text* format).

--noheader <boolean> (*default =* 0)
:   Do not show column headers (for *text* format).

--output-format <json | json-pretty | text | yaml> (*default =* text)
:   Output format.

--quiet <boolean>
:   Suppress printing results.

## EXAMPLES

Get the list of nodes in my cluster

```
# pvesh get /nodes
```

Get a list of available options for the datacenter

```
# pvesh usage cluster/options -v
```

Set the HTMl5 NoVNC console as the default console for the datacenter

```
# pvesh set cluster/options -console html5
```

## Copyright and Disclaimer

Copyright © 2007-2022 Proxmox Server Solutions GmbH

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with this program. If not, see
<https://www.gnu.org/licenses/>
