# Translation Policy

This policy makes Agent Stack’s English adaptations stable across upstream refreshes. The existing canonical English file is the translation memory and editorial source of truth.

## Rules

- Preserve the existing English wording exactly whenever the corresponding upstream meaning is unchanged.
- Translate only source text that is new or materially changed; do not regenerate an entire file with a model.
- Preserve paths, frontmatter keys, filenames, code blocks, commands, URLs, and source placeholders unless the source change requires a deliberate structural decision.
- Keep names, product names, shell commands, code identifiers, and technical terms accurate; do not translate them merely for stylistic consistency.
- Write all new explanatory prose in clear English matching the canonical file’s existing tone and terminology.
- Review the upstream proposal beside the current canonical file, then record the new source and canonical hashes with
  `just record-current <reviewed-auto-company-checkout>`.

## Why This Is Deterministic

The workflow does not ask a language model to retranslate unchanged material. It reuses the reviewed English file and limits judgment to the changed source content. This provides stable wording
without pretending that a generative translator is byte-for-byte reproducible.
