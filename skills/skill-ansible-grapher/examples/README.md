# Examples

Small, safe, local fixtures used by `just example` and the test suite. They use
`ansible.builtin.debug` only — nothing here manages real hosts, and none of these
commands ever run a playbook (only `--syntax-check` and graphing).

```bash
cd /Volumes/Data/_ai/_skills/skills_stuff/skills/skill-ansible-grapher
just example
ls -la .ai-artifacts/ansible-grapher-example
```

See `expected/README.md` for what a correct run should produce.
