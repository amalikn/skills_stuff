# Integration Guide

1. Run `scripts/detect-language-profile`.
2. Review the selected profile.
3. Run `scripts/install-skill-into-project --project PATH --auto-profile --with-config --with-ignore --with-instruction --with-wrappers --with-policy`.
4. Review generated files before commit.
5. Run a conservative smoke pack.
6. Confirm `.ai-context/` is Git-ignored.
