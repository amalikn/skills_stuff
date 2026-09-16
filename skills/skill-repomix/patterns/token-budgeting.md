# Token Budgeting

## Workflow Starting Budgets

| Workflow | Starting budget |
|---|---:|
| Small change | 20,000-50,000 |
| Code review | 50,000-100,000 |
| Project onboarding | 80,000-150,000 |
| Architecture review | 100,000-180,000 |
| Local LLM | 20,000-80,000 |
| Remote reference | 50,000-120,000 |

Model context size is not the same as an appropriate Repomix budget.

## Utilisation Thresholds

Budget utilisation = actual or estimated tokens / selected profile token budget x 100.

| Budget utilisation | Required action |
|---|---|
| 0-60% | Continue with the selected scope |
| 61-80% | Continue, but remove non-essential examples, broad documentation, and unrelated tests where safe |
| 81-100% | Narrow the pack to the directly relevant subsystem before final generation |
| Above 100% | Do not deliver the pack; execute the retry strategy |
| Unknown | Run token inspection or generate a narrowly scoped diagnostic pack first |

## Retry Behaviour

When utilisation exceeds 100%:

1. Remove generated, archived, historical, example, fixture, and unrelated test content.
2. Restrict scope to the affected package, service, module, or subsystem.
3. Retain governance files and directly relevant dependency manifests.
4. Remove unrelated language ecosystems from mixed-repository profiles.
5. Enable compression only when exact implementation bodies are not required.
6. Recalculate or regenerate the pack.
7. Repeat for a maximum of three attempts.
8. If still over budget, split into named logical packs or abort with a report.

## Prohibited Behaviours

- Do not silently truncate output to fit a budget.
- Do not silently deliver a pack that exceeds the token budget.
- Do not remove authoritative governance files to save tokens.
- Do not enable compression solely to satisfy the budget when exact implementation is required.
