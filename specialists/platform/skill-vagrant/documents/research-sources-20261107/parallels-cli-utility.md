<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://docs.parallels.com/landing/parallels-desktop-developers-guide/command-line-interface-utility
**Retrieved**: 2026-11-07 15:52 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://docs.parallels.com/landing/parallels-desktop-developers-guide/command-line-interface-utility:
> For the complete documentation index, see [llms.txt](https://docs.parallels.com/landing/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](https://docs.parallels.com/landing/parallels-desktop-developers-guide/command-line-interface-utility.md).

# Command-Line Interface Utility

In Pro and Business/Enterprise Editions, you can control Parallels Desktop and virtual machines from the command-line interface. Our CLI utilities support the majority of the functions available via the graphical user interface.

{% hint style="info" %}
**Note**: This section of the guide covers all supported types of virtual machines (Windows, Linux, and Mac), unless explicitly stated otherwise.
{% endhint %}

The command-line interface includes the following utilities:

* **prlsrvctl —** the utility is used to manage Parallels Desktop. The tasks include getting general information about Parallels Desktop, modifying Parallels Desktop preferences, getting a list of users, obtaining statistics, installing a license, and others.
* **prlctl —** the utility is used to manage virtual machines. The tasks include creating and configuring virtual machines, snapshot management, cloning operations, installing Parallels Tools, obtaining statistics, generating problem reports, and many others.

The command-line utilities are installed on a Mac as part of Parallels Desktop installation. You can run the utilities in Terminal.

Note that to get help about a particular command, you can type `man <name_of_the_command>` in Terminal. This will list the command attributes and additional help.


---

# Agent Instructions
This documentation is published with GitBook. GitBook is the documentation platform designed so that both humans and AI agents can read, navigate, and reason over technical content effectively. Learn more at gitbook.com.

## Querying This Documentation
If you need additional information that is not directly available in this page, you can query the documentation by asking a question.

Perform an HTTP GET request on the following URL with the `ask` and `goal` query parameters:

```
GET https://docs.parallels.com/landing/parallels-desktop-developers-guide/command-line-interface-utility.md?ask=<question>&goal=<user_goal>
```

`ask` is the immediate question: it should be specific, self-contained, and written in natural language.
`goal` is what the user is ultimately trying to achieve, the reason they need the answer. Sharing it helps GitBook give you a better, more relevant answer. A goal is most helpful when it describes the outcome the user wants rather than restating the question. For example, with `ask=how do I create an API token`, a goal like `automate deployments from our CI pipeline` lets GitBook tailor the answer to that use case.

The response will contain a direct answer to the question and relevant excerpts and sources from the documentation.

Use this mechanism when the answer is not explicitly present in the current page, you need clarification or additional context, or you want to retrieve related documentation sections.

