---
Title: Dependencies
Category: reference
Status: current
Authority: local-supplement
Scope: Adding, using and upgrading third-party libraries and tools
Last reviewed: 2026-10-19
Summary: >-
  Standard library in the core and third-party code at the edges; each dependency names the seam that uses it, its version
  range and the test that fails if an upgrade changes the behaviour relied on; declared, isolated, pinned and locked.
---

# Dependencies

## Rules

| Rule                                                                                                            | Why                                                                                |
| --------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| The core and pure policy layers use the standard library only                                                   | They stay easy to test and to upgrade                                              |
| A third-party library is used through one module (its seam)                                                     | An upgrade or replacement touches one file                                         |
| Each new dependency names, beside its declaration, the seam that uses it, its version range, and the            | A reader knows why it is there and how to know an upgrade broke it                 |
|   upgrade test                                                                                                  |                                                                                    |
| Each seam has a test that fails if an upgrade changes the behaviour relied on                                   | Upgrades are safe to take                                                          |
| Declare every dependency explicitly and isolate it (a venv, a module graph, a lock)                             | The Twelve-Factor App: "never relies on implicit existence of system-wide          |
|                                                                                                                 |   packages" (VERIFIED_PRIMARY)                                                     |
| Pin in deployed profiles and commit the lock file; a range in a library's manifest is fine                      | Deployments are repeatable; libraries stay installable                             |
| Remove a dependency that nothing imports                                                                        | Unused packages are attack surface and upgrade cost                                |
| Prefer a dependency already in the project, then the platform's own, before a new one ([design-principles.md](design-principles.md)) | Fewer moving parts                                                                 |

## Before adding one

1. Is it in the standard library or already in the project? Then do not add it.
2. Is it maintained (recent releases, issue responses), licensed compatibly, and widely used?
3. Check its supply-chain posture where available (an OpenSSF Scorecard result, signed releases, SLSA provenance) ([security.md](security.md)).
4. Read the documentation for the exact version you will pin, not the latest page ([configuration-and-literals.md](configuration-and-literals.md)).
5. Write the seam and its upgrade test in the same change.

## Upgrading

- Upgrade one dependency, or one coupled group, per change. Why: a failure points at its cause.
- Read the release notes between the old and new version, run the seam's upgrade test and the full suite, and record the version change where the project keeps versions.
- For an application, prefer hash-checked installs where the ecosystem supports them (pip `--require-hashes`, lock-file integrity fields). Why: a tampered package fails the install.
