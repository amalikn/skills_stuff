<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/experimental
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/experimental:
# Vagrant Experimental Feature Flag \| Vagrant \| HashiCorp Developer

Some features that aren't ready for release can be enabled through this feature
flag. There are a couple of different ways of going about enabling these features.
It is also worth noting that Vagrant will not validate the existence of a feature
flag.

For example if you are on Linux or Mac, and you wish to enable every single experimental feature, you can set the flag
to "on" by setting it to `1`:

```
export VAGRANT_EXPERIMENTAL="1"
```

You can also enable some or many features if there are specific ones you would like,
but don't want every single feature enabled:

```
# Only enables feature_one
export VAGRANT_EXPERIMENTAL="feature_one"
```

```
# Enables both feature_one and feature_two
export VAGRANT_EXPERIMENTAL="feature_one,feature_two"
```

**Advanced topic!** This is an advanced topic for use only if
you want to use new Vagrant features. If you are just getting
started with Vagrant, you may safely skip this section.

This is a list of all the valid experimental features that Vagrant recognizes:

* [`none_communicator`](/vagrant/docs/experimental#none_communicator) - Allows Vagrant to manage remote machines without the ability to connect to them for configuration/provisioning.
