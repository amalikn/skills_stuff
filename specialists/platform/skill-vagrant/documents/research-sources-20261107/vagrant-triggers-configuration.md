<!-- capture: verbatim third-party text, not authored here -->
**Canonical URL**: https://developer.hashicorp.com/vagrant/docs/triggers/configuration
**Retrieved**: 2026-11-07 15:51 AEDT
**HTTP status**: fetched ok by all-scraper fetch --markdown (path: mcp-fetch(ok))

---

Contents of https://developer.hashicorp.com/vagrant/docs/triggers/configuration:
# Vagrant Triggers Configuration \| Vagrant \| HashiCorp Developer

Vagrant Triggers has a few options to define trigger behavior.

The trigger config block takes two different operations that determine when a trigger
should fire:

* [`before`](/vagrant/docs/triggers/configuration#before)
* [`after`](/vagrant/docs/triggers/configuration#after)

These define *how* the trigger behaves and when it should fire off during
the Vagrant life cycle. A simple example of a *before* operation could look like:

```
config.trigger.before :up do |t|
  t.info = "Bringing up your Vagrant guest machine!"
end
```

Triggers can also be used with [*commands*](/vagrant/docs/triggers/configuration#commands), [*actions*](/vagrant/docs/triggers/configuration#actions), or [*hooks*](/vagrant/docs/triggers/configuration#hooks).
By default triggers will be defined to run before or after a Vagrant guest. For more
detailed examples of how to use triggers, check out the [usage section](/vagrant/docs/triggers/usage).

The trigger class takes various options.

* [`action`](/vagrant/docs/triggers/configuration#action) (symbol, array) - Expected to be a single symbol value, an array of symbols, or a *splat* of symbols. The first argument that comes after either **before** or **after** when defining a new trigger. Can be any valid Vagrant command. It also accepts a special value `:all` which will make the trigger fire for every action. An action can be ignored with the `ignore` setting if desired. These are the valid action commands for triggers:

  + [`destroy`](/vagrant/docs/triggers/configuration#destroy)
  + [`halt`](/vagrant/docs/triggers/configuration#halt)
  + [`provision`](/vagrant/docs/triggers/configuration#provision)
  + [`reload`](/vagrant/docs/triggers/configuration#reload)
  + [`resume`](/vagrant/docs/triggers/configuration#resume)
  + [`suspend`](/vagrant/docs/triggers/configuration#suspend)
  + [`up`](/vagrant/docs/triggers/configuration#up)
* [`ignore`](/vagrant/docs/triggers/configuration#ignore) (symbol, array) - Symbol or array of symbols corresponding to the action that a trigger should not fire on.
* [`info`](/vagrant/docs/triggers/configuration#info) (string) - A message that will be printed at the beginning of a trigger.
* [`name`](/vagrant/docs/triggers/configuration#name) (string) - The name of the trigger. If set, the name will be displayed when firing the trigger.
* [`on_error`](/vagrant/docs/triggers/configuration#on_error) (symbol) - Defines how the trigger should behave if it encounters an error. By default this will be `:halt`, but can be configured to ignore failures and continue on with `:continue`.
* [`only_on`](/vagrant/docs/triggers/configuration#only_on) (string, regex, array) - Limit the trigger to these guests. Values can be a string or regex that matches a guest name.
* [`ruby`](/vagrant/docs/triggers/configuration#ruby) (block) - A block of Ruby code to be executed on the host. The block accepts two arguments that can be used with your Ruby code: `env` and `machine`. These options correspond to the Vagrant environment used (note: these are not your shell's environment variables), and the Vagrant guest machine that the trigger is firing on. This option can only be a `Proc` type, which must be explicitly called out when using the hash syntax for a trigger.

  ```
  ubuntu.trigger.after :up do |trigger|
    trigger.info = "More information"
    trigger.ruby do |env,machine|
      greetings = "hello there #{machine.id}!"
      puts greetings
    end
  end
  ```
* [`run_remote`](/vagrant/docs/triggers/configuration#run_remote) (hash) - A collection of settings to run a inline or remote script with on the guest. These settings correspond to the [shell provisioner](/vagrant/docs/provisioning/shell).
* [`run`](/vagrant/docs/triggers/configuration#run) (hash) - A collection of settings to run a inline or remote script on the host. These settings correspond to the [shell provisioner](/vagrant/docs/provisioning/shell). However, at the moment the only settings `run` takes advantage of are:

  + [`args`](/vagrant/docs/triggers/configuration#args)
  + [`inline`](/vagrant/docs/triggers/configuration#inline)
  + [`path`](/vagrant/docs/triggers/configuration#path)

    **Note:** The `run` option with `inline` is not entirely like a shell provisioner that runs bash.
    It executes binaries on your machine rather than a bash script. For example:
    If you wish you use bash to pipe some text to a file in your `run` option with `inline`, wrap
    your inline script with *`bash -c "<script goes here>"`*.:

    ```
    config.trigger.after :up do |trigger|
      trigger.info = "More information"
      trigger.run = {inline: "bash -c 'echo \"hey there!!\" > file.txt'"}
    end
    ```
* [`warn`](/vagrant/docs/triggers/configuration#warn) (string) - A warning message that will be printed at the beginning of a trigger.
* [`exit_codes`](/vagrant/docs/triggers/configuration#exit_codes) (integer, array) - A set of acceptable exit codes to continue on. Defaults to `0` if option is absent. For now only valid with the `run` option.
* [`abort`](/vagrant/docs/triggers/configuration#abort) (integer,boolean) - An option that will exit the running Vagrant process once the trigger fires. If set to `true`, Vagrant will use exit code 1. Otherwise, an integer can be provided and Vagrant will it as its exit code when aborting.

Optionally, it is possible to define a trigger that executes around Vagrant commands,
hooks, and actions.

A trigger can be one of three types:

* [`type`](/vagrant/docs/triggers/configuration#type) (symbol) - Optional
  + [`:action`](/vagrant/docs/triggers/configuration#action-1) - Action triggers run before or after a Vagrant action
  + [`:command`](/vagrant/docs/triggers/configuration#command) - Command triggers run before or after a Vagrant command
  + [`:hook`](/vagrant/docs/triggers/configuration#hook) - Action hook triggers run before or after a Vagrant hook

These types determine when and where a defined trigger will execute.

```
config.trigger.after :destroy, type: :command do |t|
  t.warn = "Destroy command completed"
end
```

#### Quick Note

Triggers *without* the type option will run before or after a Vagrant guest.

Older Vagrant versions will unfortunately not be able to properly parse the new
`:type` option. If you are worried about older clients failing to parse your Vagrantfile,
you can guard the new trigger based on the version of Vagrant:

```
if Vagrant.version?(">= 2.3.0")
  config.trigger.before :status, type: :command do |t|
    t.info = "before action!!!!!!!"
  end
end
```

### Commands

Command typed triggers can be defined for any valid Vagrant command. They will always
run before or after the command.

The difference between this and the default behavior is that these triggers are
not attached to any specific guest, and will always run before or after the given
command. A simple example might be running a trigger before the up command to give
a simple message to the user:

```
config.trigger.before :up, type: :command do |t|
  t.info = "Before command!"
end
```

For a more detailed example, please check out the [examples](/vagrant/docs/triggers/usage#commands)
page for more.

### Hooks

**Advanced topic!** This is an advanced topic for use only if
you want to execute triggers around Vagrant hooks. If you are just getting
started with Vagrant and triggers, you may safely skip this section.

Hook typed triggers can be defined for any valid Vagrant action hook that is defined.

A simple example would be running a trigger on a given hook called `action_hook_name`.

```
config.trigger.after :action_hook_name, type: :hook do |t|
  t.info = "After action hook!"
end
```

For a more detailed example, please check out the [examples](/vagrant/docs/triggers/usage#hooks)
page for more.

### Actions

**Advanced topic!** This is an advanced topic for use only if
you want to execute triggers around Vagrant actions. If you are just getting
started with Vagrant and triggers, you may safely skip this section.

Action typed triggers can be defined for any valid Vagrant action class. Actions
in this case refer to the Vagrant class `#Action`, which is used internally to
Vagrant and in every Vagrant plugin.

```
config.trigger.before :"Action::Class::Name", type: :action do |t|
  t.info = "Before action class!"
end
```

For a more detailed example, please check out the [examples](/vagrant/docs/triggers/usage#actions)
page for more.
