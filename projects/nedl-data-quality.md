# NËDL Data Quality

client: nedl
status: active


## Cherre Data Quality
Primary data source. Field completeness validated Dec 16: **PASSED** (MF properties 94-100%, AVMs 100%, transactions 85% with amounts).


## Current Todos

### P0: Ownership Map (who owns what property)
Goal: Entity resolution with SCD Type 2 historicals. Dimensional model script exists (`nedl/dev/build_dimensional_model_2025.py`), needs additional data sources.

- [ ] Clean up NMHC file (received from Stash, Wilson + Brett own cleanup)
- [ ] Integrate Yardi flat files into dimensional model
- [ ] Integrate NMHC data into dimensional model
- [ ] Load dimensional model to Supabase (analytics schema)
- [ ] Replace Brett's `canonical_owner_*` tables with dimensional model

### Migration Visibility
- [ ] Schedule Keegan call (he has context on v1 → v2 migration, data model mapping, scope)
- [ ] After Keegan: Provide leadership (Joe/Stash/Maher) visibility on timelines, effort, expenses, blockers

### Other
- [ ] Schedule Cherre call (not blocking - can access independently)

## Comp Proposal (Due This Week)
- Working WITHOUT comp arrangement since project start
- **Decision needed:** Sub Brett through Wilson, or bill separately?
- Proposal due by end of week (Jan 3)

## Brett's Progress (as of Dec 22)
- Building linking table in Supabase
- `canonical_owner_rollup` + `canonical_owner_*` tables created
- ~14k entities across top 100 addresses identified
- **Fixed SQL issue** - recorder_id + tax_assessor_id no longer null
- Confirmed 1:1 relationship (testing completeness)
- NMHC file received from Stash

## Parking Lot (not now)
- Alternative data sources (Brett's specialty, but team said no for now)
