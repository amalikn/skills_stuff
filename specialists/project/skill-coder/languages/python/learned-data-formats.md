---
Title: python override - learned data formats
Category: reference
Status: current
Authority: local-supplement
Scope: one topic of languages/python.md (plist, JSON, TOML and other file formats read by stdlib parsers)
Last reviewed: 2026-11-25
Summary: Learned entries about parsing data formats in Python; started 2026-11-25 when learned-other.md reached its line budget.
---

# python: learned data formats

> **Learned 2026-11-25** · Python 3.12 to 3.15 `plistlib` · VERIFIED_PRIMARY (home NAS tests/test_ios_backup_job.sh failed until fixed, at a3f9526) ·
> Source: home NAS scripts/ios/ios_backup_job.sh · Falsifier: a plistlib that returns aware datetimes by default
> Plist `<date>` values are UTC, but `plistlib.load` returns naive datetimes (the `aware_datetime` option exists only from 3.13); `.timestamp()` then
> reads them as local time, so on a UTC+11 host a backup finished a minute ago looked 11 hours old and every success was reported as a failure.
> ```python
> d = st.get("Date")
> if d is not None and d.tzinfo is None:
>   d = d.replace(tzinfo=datetime.timezone.utc)  # plist dates are UTC
> ```
