# Verdicts and validity

## Contents

- [Recorded verdicts](#recorded-verdicts)
- [Derived states](#derived-states)
- [Append-only history](#append-only-history)
- [Invalidation events](#invalidation-events)

## Recorded verdicts

`pass` means the claim held at its stated layer. `fail` means it did not. `inconclusive` means the eval ran but the oracle could not establish truth. `error` means the evaluator broke. `blocked` means
preconditions or authority were absent. The last three are not failures of the system.

## Derived states

`not_evaluated` means no observation exists for a declared eval and population slice. `stale` means an observation exists but is older than `validity.max_age` or a later declared invalidation event
applies. Both are computed only when rendering. The observation schema deliberately excludes them from the verdict enum.

## Append-only history

Each JSONL line is an observation or invalidation event. `record_result.py` only appends. To correct an observation, record a newer one and set `supersedes` to the prior observation id. Renderers use
the newest `recorded_at` per eval/slice; history still retains the original belief and its correction.

## Invalidation events

`validity.invalidate_on` is a list of labels such as `implementation_change`, `config_change`, `oracle_change`, or `population_change`. A project script or operator records an event with one declared
label and a reference. In v0.1, invalidation is explicit. `validity.basis` is reserved for future references but no hashing, comparison, or automatic change detection exists.
