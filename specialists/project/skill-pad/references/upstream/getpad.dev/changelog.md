**Title:** Changelog

**Source:** [https://www.getpad.dev/changelog](https://www.getpad.dev/changelog)

---

# Page Structure Map
```text
Changelog
├── Why GitHub instead of an inline list?
└── Major versions
```

---

Pad uses GitHub Releases as the canonical changelog. Each tagged release includes conventional-commit-grouped notes for features, fixes, performance changes, and refactors.

[View releases on GitHub →](https://github.com/PerpetualSoftware/pad/releases)

## Why GitHub instead of an inline list?

- Each release is signed (cosign keyless via GitHub OIDC) and ships with SBOMs and SLSA build provenance. The release page is the source of truth for those artifacts.
- Release notes are auto-grouped by conventional commit type, so the formatting stays consistent without us editing both places on every release.
- Subscribing to releases (Watch → Custom → Releases on GitHub) gets you notified as soon as a new version ships.

## Major versions

Pad follows [SemVer](https://semver.org/). Breaking changes bump the major version and are called out at the top of the release notes with a migration path.
