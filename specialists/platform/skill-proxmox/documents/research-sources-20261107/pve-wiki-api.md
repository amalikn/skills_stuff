Contents of https://pve.proxmox.com/wiki/Proxmox_VE_API:
# Proxmox VE API

## Introduction

Proxmox VE uses a REST like API. The concept is described in [1] (Resource Oriented Architecture - ROA).

We choose JSON as primary data format, and the whole API is formally defined using JSON Schema [2].

You can explore the API documentation at <http://pve.proxmox.com/pve-docs/api-viewer/index.html>

## JSON and JSON Schema

The API use JSON as data format, because it is simple and parse-able by any
web browser.

Additionally, we use JSON Schema [2] to formally describe our API. So
we can automatically generate the whole API Documentation, and we can
verify all parameters and return values.

An great side effect was that we are able to use JSON Schema to
produce command line argument parsers automatically. In fact, the REST
API and the command line tools use the same code. A small utility called 'pvesh'
exposes the whole REST API on the command line.

So here is a summary of the advantage:

* easy, human-readable data format (native web browser format)
* automatic parameter verification (we can also verify return values)
* automatic generation of API documentation
* easy way to create command line tools (use the same API)

## API Stability & Breakage

Proxmox VE tries to stay API compatible in a major release.
For example, an API call that worked with 6.0 should also work with 6.4 but has no guarantee to do so with 7.0.

A breaking change is defined as:

* Removing an API endpoint entirely
* Moving an API endpoint to a new path. Normally we add the new one already and move the legacy option on the next major version bump.
* Removing parameters from an API endpoint
* Changing the return type from a non-null type to another type

The following examples are **not** considered as breaking change:

* Changing an endpoint's return type from `null` to anything else is **not** considered as breaking change
* Adding new parameters
* Adding new properties to returned objects
* Changing the type of an object's property to property string (nested object flattened into comma-separated list of key=value pairs) with the original property as default key
* Slight semantic changes, as this is often a requirement for a bug fix, albeit we either try
  + to guard those under opt-in parameters
  + to mirror the Linux Kernel "never break user-space" principle. I.e., we break it as long as deemed small enough and useful, but we are open for addressing complaints by actual users and find a solution, or switch the behavior back to the previous one.
* Adding new API endpoints

## API URL

The API uses the HTTPS protocol and the server listens to port 8006. So the base URL for that API is

```
https://your.server:8006/api2/json/
```

Parameters can be passed using standard HTTP techniques:

* via the URL
* using `x-www-form-urlencoded` content-type for PUT and POST request.

It is possible to specify the return format in the URL. Above example uses `JSON`, but you can use any of the following values:

* `json`: JSON
* `extjs`: JSON, but result nested inside an object, with `data` object, variant compatible with ExtJS forms
* `html`: HTML formatted text - sometimes useful for debugging
* `text`: plain text - sometimes useful for debugging

Please contact use on the development mailing list if you need other data formats.

## Authentication

Proxmox VE uses a ticket or token based authentication, all request to the API need to include a ticket inside a Cookie (header) or sending an API token through the Authorization header.

**NOTE**: The following examples use the cURL tool in an unsafe way because they pass authentication HTTP headers through the command line. Since the command line can be read by other users, this method is not secure on untrusted systems.
We recommend placing the entire header in a file accessible only by your user. For example, place it in your home directory. Then, use the `-H @/path/to/secure/file.headers` option to pass this to cURL.

### Ticket Cookie

A ticket is a signed random text value with the user and creation time included. Tickets are signed by the cluster-wide authentication key that is rotated once per day.

Additionally, any write (POST/PUT/DELETE) request must include a CSRF prevention token inside the HTTP header. The following examples use the `curl` command line tool.

#### Example: Get a New Ticket and the CSRF Prevention Token

Request - warning, command line parameters are visible to the whole system, avoid running below on untrusted hosts:

`curl -k -d 'username=root@pam' --data-urlencode 'password=xxxxxxxxx' https://10.0.0.1:8006/api2/json/access/ticket`

Safer variant with the password in a file only readable for the user):

`curl -k -d 'username=root@pam' --data-urlencode "password@$HOME/.pve-pass-file" https://10.0.0.1:8006/api2/json/access/ticket`

Note that we're using `--data-urlencode` for the password parameter to ensure neither curl nor the API gets confused about special characters in the password.

Example Response

```
{ 
  "data": { 
    "CSRFPreventionToken":"4EEC61E2:lwk7od06fa1+DcPUwBTXCcndyAY",  
    "ticket":"PVE:root@pam:4EEC61E2::rsKoApxDTLYPn6H3NNT6iP2mv...", 
    "username":"root@pam"
  }
}
```

NOTE: Tickets have a limited lifetime of 2 hours.
But you can simply get a new ticket by passing the old ticket as password to the `/access/ticket` method before its lifetime expired.

#### Example: Use the New Ticket

You need to pass the returned ticket with a cookie to any further request:
`curl -k -b "PVEAuthCookie=PVE:root@pam:4EEC61E2::rsKoApxDTLYPn6H3NNT6iP2mv..." https://10.0.0.1:8006/api2/json/`

Response:

```
{
  "data": [
    { "subdir": "version" },
    { "subdir": "cluster" },
    { "subdir": "nodes" },
    { "subdir": "storage" },
    { "subdir": "access" },
    { "subdir": "pools" }
  ]
}
```

#### Example: Ticket & CSRF for PUT, POST, DELETE

Additionally, any write request (POST, PUT, DELETE) must include the `CSRFPreventionToken` header:

`curl -XDELETE -H "CSRFPreventionToken: 4EEC61E2:lwk7od06fa1+DcPUwBTXCcndyAY" ...`

### API Tokens

API tokens allow stateless access to most parts of the REST API by another system, software or API client. Tokens can be generated for individual users and can be given separate permissions and expiration dates to limit the scope and duration of the access. Should the API token get compromised it can be revoked without disabling the user itself.

To use an API token, set the HTTP `Authorization` header value to the form of `PVEAPIToken=USER@REALM!TOKENID=UUID` when making API requests, or refer to your API client documentation.

#### Example: Use API Token

`curl -H 'Authorization: PVEAPIToken=root@pam!monitoring=aaaaaaaaa-bbb-cccc-dddd-ef0123456789' https://10.0.0.1:8006/api2/json/`

Note: API tokens do not need CSRF values for POST, PUT or DELETE. Tokens are normally not used in a browser context, so the main attack vector of CSRF is not applicable in the first place.

## Step-by-step Example of Container Create Using the API

Assumptions:

* the node where we log in is called APINODE
* the node on which is the container will be created is called TARGETNODE
* the auth cookie will be placed in the file "cookie"
* the CSRF token will be placed in the file "csrftoken"

Note: for ease of use we use the `jq` package which parses and pretty prints JSON data

### Export Variables

```
export APINODE=pve4
export TARGETNODE=pve4
```

### 

```
curl --silent --insecure --data "username=root@pam&password=yourpassword" \
 https://$APINODE:8006/api2/json/access/ticket\
| jq --raw-output '.data.ticket' | sed 's/^/PVEAuthCookie=/' > cookie
```

### Save a CSRF Token Locally

```
curl --silent --insecure --data "username=root@pam&password=yourpassword" \
 https://$APINODE:8006/api2/json/access/ticket \
| jq --raw-output '.data.CSRFPreventionToken' | sed 's/^/CSRFPreventionToken:/' > csrftoken
```

### Test auth credentials

Let's display the target node status to test that the ticket creation worked:

```
curl  --insecure --cookie "$(<cookie)" https://$APINODE:8006/api2/json/nodes/$TARGETNODE/status | jq '.'
```

### Creates a LXC Container

Note: we need to encode the HTTP POST body when passing non-alphanumeric parameters

```
curl --silent --insecure  --cookie "$(<cookie)" --header "$(<csrftoken)" -X POST\
 --data-urlencode net0="name=myct0,bridge=vmbr0" \
 --data-urlencode ostemplate="local:vztmpl/debian-8.0-standard_8.0-1_amd64.tar.gz" \
 --data vmid=601\
 https://$APINODE:8006/api2/json/nodes/$TARGETNODE/lxc
```

This should return a JSON structure containing the task ID (UPID) of the creation task worker which looks like:

```
{
  "data": "UPID:pve4:00002F9D:000DC5EA:57500527:vzcreate:602:root@pam:"
}
```

Make sure you use an available vmid when creating a container.

## Using 'pvesh' to Access the API

As mentioned above, there is a command line tool called `pvesh` which exposes the whole REST API of a cluster when executed as root directly on a Proxmox VE node.
This is the Swiss Army knife for developers and system administrators.

The tool automatically proxies call to other cluster members using ssh.

### Examples

:   get current version

```
pvesh get /version
```

:   get all configured users

pvesh get /access/users

:   create a new user:

```
pvesh create /access/users --userid testuser@pve
```

:   delete that user:

```
pvesh delete /access/users/testuser@pve
```

:   create and then launch a new container:

```
pvesh create /nodes/{node}/lxc -vmid 100 -hostname test --storage local \
    --password "supersecret" \
    --ostemplate local:vztmpl/debian-9.0-standard_9.5-1_amd64.tar.gz \
    --memory 512 --swap 512
pvesh create /nodes/{node}/lxc/100/status/start
```

Where `{node}` must be replaced with the name of the node on which the container should be created.

## API Client Libraries

### Official Proxmox Maintained

perl
:   <https://git.proxmox.com/?p=pve-apiclient.git;a=summary>

Available in the Proxmox Repositories, via

```
apt-get install libpve-apiclient-perl
```

### Community Maintained

#### Python

:   <https://pypi.python.org/pypi/proxmoxer>

    :   used in the ansible proxmox and proxmox\_kvm modules
:   <https://github.com/remofritzsche/proxmox-utils> (Console Client)
:   <https://github.com/baseblack/Proxmoxia> (Wrapper)
:   <https://github.com/pcdummy/pmxc> (Console Client)

#### PowerShell

:   <https://github.com/Corsinvest/cv4pve-api-powershell>

#### Ruby

:   <https://github.com/nledez/proxmox>

#### NodeJS

:   <https://www.npmjs.com/package/proxmox>
:   <https://github.com/AmiCole/pvea>
:   <https://github.com/Corsinvest/cv4pve-api-javascript>

#### C#

:   <https://github.com/ionelanton/ProxmoxSharp>
:   <https://github.com/Corsinvest/cv4pve-api-dotnet>
:   <https://github.com/Corsinvest/cv4pve-cli>
:   <https://github.com/Corsinvest/cv4pve-botgram>
:   <https://github.com/Corsinvest/cv4pve-pepper>

#### PHP

:   <https://github.com/CpuID/pve2-api-php-client>
:   <https://github.com/ZzAntares/ProxmoxVE>
:   <https://github.com/aheahe/pve-cli-utils>
:   <https://github.com/Corsinvest/cv4pve-api-php>
:   <https://github.com/MrKampf/proxmoxVE>

#### Java

:   <https://github.com/Corsinvest/cv4pve-api-java>
:   <https://github.com/FreshPerf/PVE4J>

#### Perl

:   <http://search.cpan.org/~djzort/Net-Proxmox-VE-0.006/>

#### Go

:   <https://github.com/Telmate/proxmox-api-go>

    :   basis for the related Terraform provider, see Terraform section below
:   <https://github.com/luthermonson/go-proxmox>

    :   Inspired from Telmate package, but fully stand alone and some other improvements - see the projects' README file for details
:   <https://developer.hashicorp.com/packer/integrations/hashicorp/proxmox>

    :   Packer Plugin for Proxmox VE ([source](https://github.com/hashicorp/packer-plugin-proxmox))

#### Terraform

:   <https://github.com/Telmate/terraform-provider-proxmox>

    :   uses the Go API helper to provide Terraform integration

Please add any other clients here as they become available.

## References

[1] RESTful Web Services - Web services for the real world

By Leonard Richardson and Sam Ruby, Publisher: O'Reilly Media, Released: May 2007

[2] JSON Schema links: <http://json-schema.org/>
