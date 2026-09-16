# Profile Schema

Each profile is JSON with these fields:

- `id`: unique machine identifier
- `displayName`: human-readable name
- `description`: profile purpose
- `detect.anyFiles`: manifest or marker files
- `detect.anyDirectories`: marker directories
- `include`: default Repomix include patterns
- `ignore`: default ignore patterns
- `priorityFiles`: files that should be read first
- `securitySensitivePatterns`: sensitive paths requiring exclusion
- `defaultCompression`: default compression state
- `defaultTokenBudget`: default token budget
- `notes`: operational notes
