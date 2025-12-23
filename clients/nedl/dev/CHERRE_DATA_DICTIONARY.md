# Cherre Data Dictionary

**Generated:** 2025-12-22 14:15

This documentation is based on large samples (10,000 records per table) to provide accurate completeness statistics and value distributions. Field descriptions are inferred from observed values and patterns.

**⚠️ Note:** This documentation covers only the **most important fields** for each table. Many tables have additional fields not documented here. For the complete schema with all fields and relationships, see: https://app.cherre.com/core-schema

---

## Tables

- [usa_owner_unmask_v2](#usa-owner-unmask-v2)
- [tax_assessor_v2](#tax-assessor-v2)
- [recorder_v2](#recorder-v2)
- [recorder_grantor_v2](#recorder-grantor-v2)
- [recorder_grantee_v2](#recorder-grantee-v2)
- [tax_assessor_history_v2](#tax-assessor-history-v2)

---

### usa_owner_unmask_v2

**Sample Size:** 100 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `cherre_usa_owner_unmask_pk` | 100.0% | 100 | int |
| `owner_id` | 100.0% | 100 | str |
| `owner_name` | 100.0% | 100 | str |
| `owner_type` | 100.0% | 100 | str |
| `owner_state` | 100.0% | 100 | str |
| `has_confidence` | 96.0% | 96 | bool |
| `occurrences_count` | 100.0% | 100 | int |
| `last_seen_date` | 100.0% | 100 | str |
| `tax_assessor_id` | 100.0% | 100 | int |

#### Field Details

**`cherre_usa_owner_unmask_pk`**
- Completeness: 100.0% (100/100)
- Min: -9,177,259,184,591,550,464.00
- Max: 9,197,909,214,646,516,736.00
- Avg: -196,085,272,836,163,392.00

**`owner_id`**
- Completeness: 100.0% (100/100)
- Sample values: `RICHMOND::I::AK`, `ALICE GEORGETTE THOMPSON::P::AK::870973 PO BOX, WA`, `DIANA REED::P::AK::877332 PO BOX, WASILLA, AK 9968`

**`owner_name`**
- Completeness: 100.0% (100/100)
- Sample values: `ROBERT MOORE`, `ERIC D NIELSEN`, `SUSAN ANDERSON SWANNER`

**`owner_type`**
- Completeness: 100.0% (100/100)
- Values:
  - `P`: 90 (90.0%)
  - `I`: 9 (9.0%)
  - `G`: 1 (1.0%)

**`owner_state`**
- Completeness: 100.0% (100/100)
- Values:
  - `AK`: 100 (100.0%)

**`occurrences_count`**
- Completeness: 100.0% (100/100)
- Values:
  - `1`: 87 (87.0%)
  - `2`: 11 (11.0%)
  - `4`: 1 (1.0%)
  - `30`: 1 (1.0%)

**`last_seen_date`**
- Completeness: 100.0% (100/100)
- Sample values: `2025-02-05`, `2024-06-17`, `2025-06-13`

**`tax_assessor_id`**
- Completeness: 100.0% (100/100)
- Min: 13,368,240.00
- Max: 699,475,788.00
- Avg: 251,561,882.20

**`has_confidence`**
- Completeness: 96.0% (96/100)
- Values:
  - `True`: 96 (100.0%)

---

### tax_assessor_v2

**Sample Size:** 1,000 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `tax_assessor_id` | 100.0% | 1,000 | int |
| `address` | 85.8% | 858 | str |
| `city` | 99.9% | 999 | str |
| `state` | 100.0% | 1,000 | str |
| `zip` | 99.9% | 999 | str |
| `latitude` | 100.0% | 1,000 | float |
| `longitude` | 100.0% | 1,000 | float |
| `building_sq_ft` | 100.0% | 1,000 | int |
| `year_built` | 62.4% | 624 | int |
| `units_count` | 23.9% | 239 | int |
| `assessed_value_total` | 99.6% | 996 | int |
| `last_sale_date` | 70.0% | 700 | str |
| `last_sale_amount` | 69.0% | 690 | int |
| `property_use_standardized_code` | 100.0% | 1,000 | str |
| `property_group_type` | 100.0% | 1,000 | str |

#### Field Details

**`tax_assessor_id`**
- Completeness: 100.0% (1,000/1,000)
- Min: 36,469,204.00
- Max: 51,389,648.00
- Avg: 41,908,793.36

**`state`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `AR`: 583 (58.3%)
  - `CA`: 417 (41.7%)

**`latitude`**
- Completeness: 100.0% (1,000/1,000)
- Min: 33.92
- Max: 39.46
- Avg: 35.40

**`longitude`**
- Completeness: 100.0% (1,000/1,000)
- Min: -122.03
- Max: -90.70
- Avg: -103.44

**`building_sq_ft`**
- Completeness: 100.0% (1,000/1,000)
- Min: 0.00
- Max: 15,800.00
- Avg: 1,304.74

**`property_use_standardized_code`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `1001`: 643 (64.3%)
  - `8001`: 347 (34.7%)
  - `7000`: 2 (0.2%)
  - `8000`: 2 (0.2%)
  - `8010`: 2 (0.2%)
  - `3000`: 1 (0.1%)
  - `9102`: 1 (0.1%)
  - `8003`: 1 (0.1%)
  - `7005`: 1 (0.1%)

**`property_group_type`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `RESIDENTIAL`: 643 (64.3%)
  - `VACANT`: 352 (35.2%)
  - `AGRICULTURAL`: 3 (0.3%)
  - `OFFICE`: 1 (0.1%)
  - `EXEMPT`: 1 (0.1%)

**`city`**
- Completeness: 99.9% (999/1,000)
- Values:
  - `INGLEWOOD`: 257 (25.7%)
  - `FRESNO`: 153 (15.3%)
  - `PALESTINE`: 133 (13.3%)
  - `FAYETTEVILLE`: 117 (11.7%)
  - `CHEROKEE VILLAGE`: 109 (10.9%)
  - `FARMINGTON`: 70 (7.0%)
  - `MADISON`: 67 (6.7%)
  - `GREENWOOD`: 45 (4.5%)
  - `FORREST CITY`: 34 (3.4%)
  - `BUTTE CITY`: 4 (0.4%)

**`zip`**
- Completeness: 99.9% (999/1,000)
- Values:
  - `90303`: 175 (17.5%)
  - `72372`: 133 (13.3%)
  - `72704`: 117 (11.7%)
  - `72529`: 109 (10.9%)
  - `93730`: 100 (10.0%)
  - `90305`: 82 (8.2%)
  - `72730`: 70 (7.0%)
  - `72359`: 67 (6.7%)
  - `93722`: 52 (5.2%)
  - `72936`: 45 (4.5%)

**`assessed_value_total`**
- Completeness: 99.6% (996/1,000)
- Min: 20.00
- Max: 1,509,886.00
- Avg: 187,164.92

**`address`**
- Completeness: 85.8% (858/1,000)
- Sample values: `9611 S 4TH AVE`, `2565 E PERRIN AVE`, `9610 S 5TH AVE`

**`last_sale_date`**
- Completeness: 70.0% (700/1,000)
- Sample values: `2012-04-10`, `2024-03-08`, `2022-11-15`

**`last_sale_amount`**
- Completeness: 69.0% (690/1,000)
- Min: 0.00
- Max: 3,800,000.00
- Avg: 217,294.63

**`year_built`**
- Completeness: 62.4% (624/1,000)
- Min: 1,900.00
- Max: 2,022.00
- Avg: 1,972.63

**`units_count`**
- Completeness: 23.9% (239/1,000)
- Values:
  - `0`: 236 (98.7%)
  - `1`: 3 (1.3%)

---

### recorder_v2

**Sample Size:** 1,000 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `recorder_id` | 100.0% | 1,000 | int |
| `tax_assessor_id` | 20.9% | 209 | int |
| `document_recorded_date` | 100.0% | 1,000 | str |
| `document_amount` | 99.6% | 996 | int |
| `document_type_code` | 100.0% | 1,000 | str |
| `transaction_type_code` | 100.0% | 1,000 | str |
| `arms_length_code` | 88.4% | 884 | int |
| `inter_family_flag` | 15.9% | 159 | bool |
| `is_quit_claim` | 100.0% | 1,000 | bool |
| `is_foreclosure_auction_sale` | 100.0% | 1,000 | bool |
| `owner_relationship_code` | 98.6% | 986 | str |

#### Field Details

**`recorder_id`**
- Completeness: 100.0% (1,000/1,000)
- Min: 14,000,513,944.00
- Max: 28,385,272,348.00
- Avg: 14,070,320,374.86

**`document_recorded_date`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `2011-05-10`, `2009-05-05`, `2011-01-04`

**`document_type_code`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `21`, `20`, `61`

**`transaction_type_code`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `2`: 452 (45.2%)
  - `1`: 432 (43.2%)
  - `4`: 115 (11.5%)
  - `3`: 1 (0.1%)

**`is_quit_claim`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `False`: 872 (87.2%)
  - `True`: 128 (12.8%)

**`is_foreclosure_auction_sale`**
- Completeness: 100.0% (1,000/1,000)
- Values:
  - `False`: 883 (88.3%)
  - `True`: 117 (11.7%)

**`document_amount`**
- Completeness: 99.6% (996/1,000)
- Min: 0.00
- Max: 900,000.00
- Avg: 45,316.39

**`owner_relationship_code`**
- Completeness: 98.6% (986/1,000)
- Sample values: `MM`, `GV`, `FM`

**`arms_length_code`**
- Completeness: 88.4% (884/1,000)
- Values:
  - `1`: 452 (51.1%)
  - `0`: 432 (48.9%)

**`tax_assessor_id`**
- Completeness: 20.9% (209/1,000)
- Min: 9,079,648.00
- Max: 555,592,880.00
- Avg: 485,229,107.54

**`inter_family_flag`**
- Completeness: 15.9% (159/1,000)
- Values:
  - `True`: 159 (100.0%)

---

### recorder_grantor_v2

**Sample Size:** 1,000 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `cherre_recorder_grantor_pk` | 100.0% | 1,000 | int |
| `recorder_id` | 100.0% | 1,000 | int |
| `grantor_name` | 100.0% | 1,000 | str |
| `grantor_first_name` | 100.0% | 1,000 | str |
| `grantor_last_name` | 100.0% | 1,000 | str |
| `grantor_entity_code` | 0.0% | 0 | unknown |
| `grantor_address` | 0.7% | 7 | str |
| `grantor_city` | 0.7% | 7 | str |
| `grantor_state` | 0.2% | 2 | str |
| `grantor_zip` | 0.0% | 0 | unknown |

#### Field Details

**`cherre_recorder_grantor_pk`**
- Completeness: 100.0% (1,000/1,000)
- Min: -9,193,034,912,652,883,968.00
- Max: 9,143,044,166,970,544,128.00
- Avg: 265,102,708,370,713,088.00

**`recorder_id`**
- Completeness: 100.0% (1,000/1,000)
- Min: 14,000,403,668.00
- Max: 14,721,887,280.00
- Avg: 14,355,126,409.00

**`grantor_name`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `STUART S DEANE`, `SUSAN JOY`, `DONNA J HARRIS`

**`grantor_first_name`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `W`, `A`, `SAU`

**`grantor_last_name`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `HAGGERTY`, `WILLIARD`, `MOSELL`

**`grantor_address`**
- Completeness: 0.7% (7/1,000)
- Values:
  - `40 RUE DU TEILLET`: 1 (14.3%)
  - `MILL VIEW KINGSMILL LANE PAINSWICK`: 1 (14.3%)
  - `946 EDGEWOOD LN`: 1 (14.3%)
  - `7 PINELLAS DR`: 1 (14.3%)
  - `8 TERRY RD`: 1 (14.3%)
  - `4529 MIDDLETON`: 1 (14.3%)
  - `SCHWENNINGER STRABE 3 72510`: 1 (14.3%)

**`grantor_city`**
- Completeness: 0.7% (7/1,000)
- Values:
  - `BELGIUM`: 1 (14.3%)
  - `GLOUCESTERSHIRE GL6 6RZ`: 1 (14.3%)
  - `LOWER SOUTHAMPTON`: 1 (14.3%)
  - `BRAMPTON ONTARIO CANADA`: 1 (14.3%)
  - `OMEMEE ONTARIO CANADA K0L 2W0`: 1 (14.3%)
  - `JACKSONVILLE`: 1 (14.3%)
  - `STETTEN GERMANY`: 1 (14.3%)

**`grantor_state`**
- Completeness: 0.2% (2/1,000)
- Values:
  - `PA`: 1 (50.0%)
  - `FL`: 1 (50.0%)

**`grantor_entity_code`**
- Completeness: 0.0% (0/1,000)

**`grantor_zip`**
- Completeness: 0.0% (0/1,000)

---

### recorder_grantee_v2

**Sample Size:** 1,000 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `cherre_recorder_grantee_pk` | 100.0% | 1,000 | int |
| `recorder_id` | 100.0% | 1,000 | int |
| `grantee_name` | 100.0% | 1,000 | str |
| `grantee_first_name` | 95.4% | 954 | str |
| `grantee_last_name` | 98.4% | 984 | str |
| `grantee_entity_code` | 0.1% | 1 | str |
| `grantee_address` | 5.5% | 55 | str |
| `grantee_city` | 3.0% | 30 | str |
| `grantee_state` | 1.9% | 19 | str |
| `grantee_zip` | 0.0% | 0 | unknown |

#### Field Details

**`cherre_recorder_grantee_pk`**
- Completeness: 100.0% (1,000/1,000)
- Min: -9,221,472,809,177,425,920.00
- Max: 9,218,037,841,593,588,736.00
- Avg: 105,114,682,345,583,088.00

**`recorder_id`**
- Completeness: 100.0% (1,000/1,000)
- Min: 14,003,685,276.00
- Max: 730,027,864,152.00
- Avg: 97,187,892,586.14

**`grantee_name`**
- Completeness: 100.0% (1,000/1,000)
- Sample values: `WARREN H PHILLIPP JR`, `VELMA FARRAR`, `JEFFREY H GURLEY`

**`grantee_last_name`**
- Completeness: 98.4% (984/1,000)
- Sample values: `ERDMAN`, `TORRES`, `FICORILLI`

**`grantee_first_name`**
- Completeness: 95.4% (954/1,000)
- Sample values: `W`, `ALTON`, `A`

**`grantee_address`**
- Completeness: 5.5% (55/1,000)
- Sample values: `61 INDIAN HILL RD`, `2681 FGREMONT DR`, `169 RIVER OAKS OAKVILLE BLVD E ON L6H`

**`grantee_city`**
- Completeness: 3.0% (30/1,000)
- Sample values: `GREENSBORO`, `GREENSBURG`, `WASHINGTON`

**`grantee_state`**
- Completeness: 1.9% (19/1,000)
- Values:
  - `XX`: 4 (21.1%)
  - `GA`: 4 (21.1%)
  - `TN`: 3 (15.8%)
  - `NJ`: 1 (5.3%)
  - `OH`: 1 (5.3%)
  - `ND`: 1 (5.3%)
  - `NY`: 1 (5.3%)
  - `AL`: 1 (5.3%)
  - `NC`: 1 (5.3%)
  - `IL`: 1 (5.3%)

**`grantee_entity_code`**
- Completeness: 0.1% (1/1,000)
- Values:
  - `Y`: 1 (100.0%)

**`grantee_zip`**
- Completeness: 0.0% (0/1,000)

---

### tax_assessor_history_v2

**Sample Size:** 100 records
**Fields Shown:** Key fields only (see [full schema](https://app.cherre.com/core-schema) for complete field list)

| Field | Completeness | Non-Null Count | Type |
|-------|--------------|----------------|------|
| `cherre_tax_assessor_history_v2_pk` | 100.0% | 100 | int |
| `tax_assessor_id` | 100.0% | 100 | int |
| `assessor_snap_shot_year` | 100.0% | 100 | int |
| `assessed_value_total` | 100.0% | 100 | int |
| `market_value_total` | 100.0% | 100 | int |
| `building_sq_ft` | 100.0% | 100 | int |
| `year_built` | 3.0% | 3 | int |
| `last_sale_date` | 2.0% | 2 | str |
| `last_sale_amount` | 2.0% | 2 | int |

#### Field Details

**`cherre_tax_assessor_history_v2_pk`**
- Completeness: 100.0% (100/100)
- Min: 359,134,520,191,227.00
- Max: 1,008,479,820,201,226.00
- Avg: 380,877,977,193,627.12

**`tax_assessor_id`**
- Completeness: 100.0% (100/100)
- Min: 14,365,380.00
- Max: 40,339,192.00
- Avg: 15,235,118.28

**`assessor_snap_shot_year`**
- Completeness: 100.0% (100/100)
- Values:
  - `2019`: 76 (76.0%)
  - `2020`: 24 (24.0%)

**`assessed_value_total`**
- Completeness: 100.0% (100/100)
- Min: 0.00
- Max: 323,300.00
- Avg: 38,281.94

**`market_value_total`**
- Completeness: 100.0% (100/100)
- Min: 0.00
- Max: 323,300.00
- Avg: 35,868.00

**`building_sq_ft`**
- Completeness: 100.0% (100/100)
- Values:
  - `0`: 97 (97.0%)
  - `1988`: 1 (1.0%)
  - `2610`: 1 (1.0%)
  - `480`: 1 (1.0%)

**`year_built`**
- Completeness: 3.0% (3/100)
- Values:
  - `2003`: 1 (33.3%)
  - `1991`: 1 (33.3%)
  - `1981`: 1 (33.3%)

**`last_sale_date`**
- Completeness: 2.0% (2/100)
- Values:
  - `2015-01-21`: 1 (50.0%)
  - `2006-03-03`: 1 (50.0%)

**`last_sale_amount`**
- Completeness: 2.0% (2/100)
- Values:
  - `235000`: 1 (50.0%)
  - `0`: 1 (50.0%)

---

