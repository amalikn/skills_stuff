<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://github.com/Parallels/vagrant-parallels
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://github.com/Parallels/vagrant-parallels:
# GitHub - Parallels/vagrant-parallels: Vagrant Parallels Provider

[![Gem Version](https://camo.githubusercontent.com/9cb1b200ecddaa9e6dd0f1d57df31311017686ab6cc1c8e9dc634e110341d6bf/68747470733a2f2f62616467652e667572792e696f2f72622f76616772616e742d706172616c6c656c732e737667)](https://badge.fury.io/rb/vagrant-parallels)
[![Build Status](https://camo.githubusercontent.com/f2e1820424c88500b2a7e44d418036f822d74901fa3f9ee6d75778e1faa193f8/68747470733a2f2f7472617669732d63692e6f72672f506172616c6c656c732f76616772616e742d706172616c6c656c732e7376673f6272616e63683d6d6173746572)](https://travis-ci.org/Parallels/vagrant-parallels)
[![Code Climate](https://camo.githubusercontent.com/d5aa6afcd9ce321c898f1c419ecf27825fbf29d979ec61762951ac84a7902045/68747470733a2f2f636f6465636c696d6174652e636f6d2f6769746875622f506172616c6c656c732f76616772616e742d706172616c6c656c732e737667)](https://codeclimate.com/github/Parallels/vagrant-parallels)

*Vagrant Parallels Provider* is a plugin for [Vagrant](https://www.vagrantup.com/),
allowing to manage [Parallels Desktop](https://www.parallels.com/products/desktop/)
virtual machines on macOS hosts.

## Requirements

* [Vagrant v1.9.7](https://www.vagrantup.com/) or higher
* [Parallels Desktop 11 for Mac](https://www.parallels.com/products/desktop/) or higher

*Note:* Only **Pro**, **Business** and **Enterprise** editions of **Parallels Desktop for Mac**
are compatible with this Vagrant provider.
Standard edition doesn't have a full command line functionality and can not be used
with Vagrant.

## Features

The Parallels provider supports all basic Vagrant features, including Shared Folders,
Private and Public Networking, Forwarded ports and Vagrant Share.

If you're just getting started with Vagrant, it is highly recommended that you
read the official [Vagrant documentation](https://docs.vagrantup.com/v2/) first.

## Installation

Make sure that you have [Parallels Desktop for Mac](https://www.parallels.com/products/desktop/)
and [Vagrant](https://www.vagrantup.com/downloads.html) properly installed. We recommend
that you use the latest versions of these products.

Additionally, you'll need the command line software development tools provided as a part of Xcode
to be able to build the plugin on your machine. To install these, run this command:

```
xcode-select --install
```

You can then install the Parallels provider plugin for Vagrant. Run this command to install it:

```
vagrant plugin install vagrant-parallels
```

## Provider Documentation

More information about the Parallels provider is available in
[Vagrant Parallels Documentation](https://parallels.github.io/vagrant-parallels/docs/)

We recommend you to start from these pages:

* [Usage](https://parallels.github.io/vagrant-parallels/docs/usage.html)
* [Getting Started](https://parallels.github.io/vagrant-parallels/docs/getting-started.html)
* [Boxes](https://parallels.github.io/vagrant-parallels/docs/boxes/index.html)

## Getting Help

If you have an issue with the Parallels provider or discover a bug,
please report it on the [Issue Tracker](https://github.com/Parallels/vagrant-parallels/issues).

## License and Authors

* Author: Youssef Shahin [yshahin@gmail.com](mailto:yshahin@gmail.com)
* Author: Mikhail Zholobov [legal90@gmail.com](mailto:legal90@gmail.com)
* Copyright 2013-2023, Parallels International GmbH.

Vagrant Parallels Provider is open-sourced software licensed under the [MIT license](https://opensource.org/licenses/MIT).
