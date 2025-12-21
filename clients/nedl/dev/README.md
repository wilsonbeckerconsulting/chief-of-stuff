# NËDL Dev Workspace

**Purpose:** Exploratory work, prototypes, testing, analysis for NËDL client work.

## What Lives Here

- **Exploratory scripts** - Testing Cherre API, data analysis, experiments
- **Prototypes** - Entity resolution experiments, data quality checks
- **Notebooks** - Jupyter notebooks for data exploration
- **Test queries** - GraphQL query development and testing
- **Findings** - Document what you learn before building production code

## What Does NOT Live Here

- Production pipelines (those go in `nedl-ai` repo)
- Official features (PR those to `nedl-ai`)
- Shared code (that belongs in the official repo)

## Structure

```
dev/
├── config.py              # Credentials (gitignored)
├── test_cherre_api.py     # Verify API access
├── notebooks/             # Jupyter notebooks
├── prototypes/            # Experimental code
└── findings/              # Document learnings
```

## Workflow

1. **Explore here** - Mess around, try things, learn
2. **Document in raw/** - Brain dump findings with tags
3. **Build clean in nedl-ai** - Production-ready implementation
4. **PR with context** - Reference your exploration when submitting

## Getting Started

```bash
# Test Cherre API access
python test_cherre_api.py

# For Jupyter notebooks
pip install jupyter pandas requests
jupyter notebook
```

## Credentials

All credentials are in `config.py` (gitignored). See `.secrets/nedl.md` for credential sources.

