# Compression Policy

Use compression for architecture discovery, external repositories, broad structural review, and constrained local models.

Do not use compression for debugging, SQL correctness, financial logic, validation code, exact configuration semantics, error handling, authentication, or authorisation.

## Budget and Truncation Rules

- Compression MUST NOT be used solely to satisfy the token budget.
- When exact implementation logic is required, narrow the scope first; do not compress.
- Compression decisions must be recorded in the run report under Compression justification.
- Do not silently compress output when full source was requested or required.
