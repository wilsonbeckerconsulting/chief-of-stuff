# NËDL Data Quality

client: nedl
status: active

## ETL Pipeline
**Repo:** https://github.com/wilsonbeckerconsulting/nedl-data (local: `~/Desktop/src/nedl-data`)
**Prefect:** https://app.prefect.cloud/account/5306d9cd-95be-4d90-8e99-34e9b3295428/workspace/3557e215-f7a6-4392-bb5a-ca899ba0f13b/dashboard

Automated daily pipeline: Cherre → raw schema → analytics schema (dimensional model with SCD Type 2). Dev/prod environments, DQ checks, failure alerts, backfill scripts, full documentation.

## Current Todos

### P0: Ownership Map (who owns what property)
Goal: Entity resolution with SCD Type 2 historicals. **Pipeline deployed ✅**, needs additional data sources and validation.

- [ ] Validate ownership data with Brett (benchmark against his work)
- [ ] Migrate additional data to ETL (list TBD)
- [ ] Integrate Yardi flat files
- [ ] Integrate NMHC data (file from Stash needs cleanup)
- [ ] Replace Brett's `canonical_owner_*` tables with dimensional model

### App Layer (80% of migration from data perspective)
- [ ] Build data layer that serves the new application

### Migration Visibility
- [ ] Schedule Keegan call (he has context on v1 → v2 migration, data model mapping, scope)
- [ ] After Keegan: Provide leadership (Joe/Stash/Maher) visibility on timelines, effort, expenses, blockers

### Other
- [ ] Schedule Cherre call (not blocking - can access independently)

## Strategic Goal
Help NËDL exit relationship with offshore dev team. Once data pipelines are integrated, tested, and automated:
- Bugs fixable by AI (Claude Code)
- New data sources easy to add (patterns established in repo)
- No ongoing dev team dependency

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
