# justfile — RAG bridge tasks snippet
# Copy these tasks into your project justfile.
# Adjust PROJECT_SLUG if your project uses a different slug.

RAG_TOOLS_ROOT := "/Volumes/Data/_ai/_tool/tools_stuff/rag-tools"
RAG_TOOLS_BIN  := "/Volumes/Data/_ai/_tool/tools-working-cache/rag-tools/.venv/bin/python"
PROJECT_SLUG   := "<project_slug>"

# Validate the project retrieval policy against rag-tools rules
rag-validate-policy:
    {{RAG_TOOLS_BIN}} -m rag_tools.cli validate-policy rag/retrieval-policy.yaml

# Run the rag-tools doctor (all 10 health checks)
rag-tools-doctor:
    cd {{RAG_TOOLS_ROOT}} && {{RAG_TOOLS_BIN}} -m rag_tools.cli doctor

# Show Qdrant container and API status
rag-qdrant-status:
    cd {{RAG_TOOLS_ROOT}} && scripts/qdrant-status

# List all Qdrant collections
rag-collections:
    cd {{RAG_TOOLS_ROOT}} && scripts/qdrant-collections

# Dry-run index one wiki domain (no writes to Qdrant)
rag-index-domain-dry DOMAIN:
    cd {{RAG_TOOLS_ROOT}} && {{RAG_TOOLS_BIN}} -m rag_tools.cli index-domain --domain {{DOMAIN}} --dry-run

# Live index one wiki domain (runs dry-run first, then prompts for confirmation)
rag-index-domain DOMAIN:
    cd {{RAG_TOOLS_ROOT}} && {{RAG_TOOLS_BIN}} -m rag_tools.cli index-domain --domain {{DOMAIN}}

# Run embedding smoke test
rag-embedding-test:
    cd {{RAG_TOOLS_ROOT}} && scripts/embedding-smoke-test

# Start Qdrant (detached)
rag-qdrant-up:
    cd {{RAG_TOOLS_ROOT}} && scripts/qdrant-up

# Stop Qdrant
rag-qdrant-down:
    cd {{RAG_TOOLS_ROOT}} && scripts/qdrant-down

# Run rag-tools test suite
rag-test:
    cd {{RAG_TOOLS_ROOT}} && {{RAG_TOOLS_BIN}} -m pytest tests/ -v
