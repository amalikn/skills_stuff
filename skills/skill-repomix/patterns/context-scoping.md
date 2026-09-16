# Context Scoping

## Scoping Flow

```text
task
-> authority files
-> subsystem
-> language profile
-> include patterns
-> exclusions
-> token inspection
-> threshold decision
-> generate
-> validate
-> narrow and retry if required (maximum three attempts)
-> split or abort
-> report
```

Whole-repository packing is exceptional.

## Narrowing Order

When a pack is too large, remove content in this order:

1. Generated, archived, and historical files.
2. Examples, fixtures, and unrelated test files.
3. Broad documentation not directly relevant to the task.
4. Unrelated language ecosystems in mixed-repository packs.
5. Non-essential dependency lock files.

Authoritative governance files must not be removed.
