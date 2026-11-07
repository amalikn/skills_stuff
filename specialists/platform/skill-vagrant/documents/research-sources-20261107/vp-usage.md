<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://parallels.github.io/vagrant-parallels/docs/usage.html
**Retrieved**: 2026-11-07 15:53 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: scrapling-http(ok))

---

<html><head><meta charset="utf-8"><title> Usage - Vagrant Parallels Provider Documentation</title><meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no"><link href="../stylesheets/bootstrap-83bc38f8.css" rel="stylesheet"><link href="../stylesheets/vagrant-parallels-4acb13e4.css" rel="stylesheet"><script src="../javascripts/jquery-7a374c2f.js"></script><script src="../javascripts/modernizr-d4b01192.js"></script><script src="../javascripts/bootstrap.min-94c68c6f.js"></script><script src="../javascripts/backstretch-3d1212ad.js"></script><script src="../javascripts/vagrant-parallels-919511ec.js"></script><link href="http://fonts.googleapis.com/css?family=Inconsolata" rel="stylesheet" type="text/css"></head><body>
		
		<div class="wrapper">

			

			<nav class="docs"><div class="container">
					
					<a href="./" class="vagrant-docs-logo">Vagrant Parallels Documentation</a>
					
					<ul class="pull-right"><li><a href="https://docs.vagrantup.com">Vagrant Docs</a></li>
						<li><a href="https://github.com/Parallels/vagrant-parallels">Github</a></li>
					</ul></div> 
			</nav><div class="page docs docs-home">
				<div class="container">
					<div class="sidebar span4">
						
						
						<aside class="sidebar-nav"><div class="toggle hidden-desktop">
								<div class="open-close open"></div>
								<a href="#">Contents</a>
							</div>

							<ul class="unstyled"><li><a href="./">Overview</a></li>
								<li><a href="installation/">Installation</a></li>


								<li class="current"><a href="usage.html">Usage</a></li>
								<li><a href="getting-started.html">Getting Started</a></li>
								<li><a href="share.html">Vagrant Share</a></li>
								<li><a href="boxes/">Boxes</a></li>


								<li><a href="sharedfolders.html">Shared Folders</a></li>
								<li><a href="configuration.html">Configuration</a></li>
								<li><a href="networking/">Networking</a></li>


								<li><a href="contacts.html">Contacts</a></li>
							</ul></aside></div> 

					<div class="page-contents span9">
						<div class="page-background"></div>

						
						<div class="row">
							<div class="span8 offset1">
								<h1>Usage</h1>

<p>The Parallels provider is used just like any other provider. Please read the
general <a href="https://www.vagrantup.com/docs/providers/basic_usage.html">basic usage</a>
page for providers.</p>

<p>When Parallels provider is installed it has a higher priority than any other
provider shipped with Vagrant. In most cases you will not have to specify the
provider name, just "vagrant up" will be enough:</p>

<ul><li>For Macs with Intel chip:</li>
</ul><div class="highlight"><pre class="highlight plaintext"><code>$ vagrant init bento/ubuntu-18.04
$ vagrant up
</code></pre></div>
<ul><li>For Macs with Apple M-series chip:</li>
</ul><div class="highlight"><pre class="highlight plaintext"><code>$ vagrant init bento/ubuntu-20.04-arm64
$ vagrant up
</code></pre></div>
<p>But if you have a multi-provider configuration and/or want to be sure that
exactly <code>parallels</code> provider will be used, then you can specify it explicitly:</p>
<div class="highlight"><pre class="highlight plaintext"><code>$ vagrant up --provider=parallels
</code></pre></div>
							</div> 
						</div> 
					</div> 
				</div> 
			</div> 

			
			<footer><div class="container">
					<div class="row">
						<ul class="unstyled logos"><a href="http://www.vagrantup.com/downloads.html">
								<li class="vagrant-logo-monochrome">
									<p>Vagrant</p>
								</li>
							</a>
							<a href="http://www.parallels.com/products/desktop/">
								<li class="pd-logo-monochrome">
									<p>Parallels Desktop</p>
								</li>
							</a>
						</ul></div> 

					<div class="row">
						<h6 class="legal">
							© 2025 Parallels International GmbH.
						</h6>
					</div> 
				</div> 
			</footer></div>

		
	</body></html>
