"""Data-first flow maps: a YAML map of components and flows rendered as one multi-page draw.io file. Stdlib only (PyYAML at the edge, in
model.read_map). Modules: profile (a project's settings), model (load, validate, the map's questions), overview_layout and overview (the
Overview page), e2e_grid and e2e (the End-to-end page), pages (flow pages, render, evaluate).

Imported, not run: put the skill's scripts/ on sys.path, then `from flowmap.pages import render`; the runnable front end is
scripts/render_flowmap.py.
"""
