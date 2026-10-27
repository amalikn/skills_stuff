"""Knowledge Curator library: the deterministic kernel behind scripts/knowledge_curator.py.

Imported by the front end and the tests, not run. Layers (lowest first): errors, settings, ids, the seams (yaml_io, schema,
mdparse, fuzzy, nli), ledger (the only writer), state (folds the ledgers), then the feature modules (inventory, claims, relations,
candidates, decisions, render, promote, archive_plan, query, intake, validate, report). A feature module never imports another
feature module's private helpers. Safety: nothing here writes except through ledger.py, and ledger.py writes only when the caller
passed apply=True.
"""
