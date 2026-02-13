# Data Modeling Principles - Health Intelligence

This document outlines the database design philosophy for Personal Health Studio. Follows the Snowflake-specific patterns from the original architecture.

## Core Philosophy

**Keep it simple. Optimize for analytics. Minimize joins.**

- Favor unified designs over complex normalization
- Optimize for NL→SQL query generation  
- Prefer VARCHAR for JSON storage (simpler than VARIANT)
- Use single-table design with discriminator column

## Table Design

### Three Core Tables

```
PATIENTS
├─ patient_id (PK)
├─ patient_name
├─ date_of_birth
├─ gender (optional)
└─ created_date

HEALTH_RECORDS
├─ record_id (PK)
├─ patient_id (FK → PATIENTS)
├─ import_id (FK → IMPORTS)
├─ record_type (discriminator: 'LAB', 'VITAL', 'MEDICATION', 'CONDITION', 'ALLERGY', 'IMMUNIZATION')
├─ record_date
├─ provider
├─ data_json (or individual columns)
├─ created_date
└─ updated_date

IMPORTS
├─ import_id (PK)
├─ patient_id (FK → PATIENTS)
├─ import_date
├─ source_files (JSON array as VARCHAR)
├─ records_by_type (JSON object as VARCHAR)
├─ import_statistics (detailed JSON as VARCHAR)
└─ status ('SUCCESS', 'PARTIAL', 'FAILED')
```

## Column Naming - CRITICAL CONSTRAINT

**Never use these strings in column names**:
- "NAME" (breaks Cortex Analyst)
- "TYPE" (breaks Cortex Analyst)
- "UNIT" (breaks Cortex Analyst)

**Instead use**:
- NAME → IDENTITY, DESCRIPTION, LABEL, TITLE
- TYPE → CATEGORY, KIND, CLASS, ROLE
- UNIT → DIMENSION, SCALE, MEASURE

## Data Types

| Purpose | Type | Example |
|---------|------|---------|
| Dates | DATE | '2025-04-07' |
| Numeric values | DECIMAL(10,2) or FLOAT | 98.5 |
| Text/codes | VARCHAR(255-4000) | 'mg/dL', 'Once daily' |
| JSON data | VARCHAR (not VARIANT) | '{"lab":"result"}' |
| Counts/integers | INTEGER | 42 |
| Flags | VARCHAR or BOOLEAN | 'OUT_OF_RANGE' |

## Example: Lab Results in HEALTH_RECORDS

Instead of separate LAB_RESULTS table:

```sql
-- Single table approach
INSERT INTO HEALTH_RECORDS 
(patient_id, import_id, record_type, record_date, provider, data_json, created_date)
VALUES
(
  1,
  100,
  'LAB',
  '2025-04-07',
  'Duly Health and Care',
  '{
    "test_description": "Cholesterol Total",
    "test_result": "185",
    "test_dimension": "mg/dL",
    "reference_range": "125-200",
    "flag": "NORMAL",
    "test_category": "Lipid"
  }',
  NOW()
);
```

Query it simply:
```sql
SELECT 
  p.patient_name,
  h.record_date,
  JSON_EXTRACT_PATH_TEXT(h.data_json, 'test_description') as test_name,
  JSON_EXTRACT_PATH_TEXT(h.data_json, 'test_result') as result
FROM HEALTH_RECORDS h
JOIN PATIENTS p ON h.patient_id = p.patient_id
WHERE h.record_type = 'LAB'
  AND JSON_EXTRACT_PATH_TEXT(h.data_json, 'test_category') = 'Lipid'
ORDER BY h.record_date DESC;
```

## JSON Storage Strategy

**Use VARCHAR, not VARIANT**:
- Simpler type handling
- No conversion issues with json.dumps()
- Works directly with Python/MCP tools
- Still queryable with JSON functions

When storing:
```python
import json
data = {...}
json_str = json.dumps(data)  # Returns string
# Store json_str in VARCHAR column
```

When querying:
```sql
SELECT PARSE_JSON(data_json)::variant as parsed
FROM HEALTH_RECORDS
```

## Import Metadata Pattern

Track data lineage with the IMPORTS table:

```sql
INSERT INTO IMPORTS (patient_id, import_date, source_files, records_by_type, import_statistics)
VALUES (
  1,
  CURRENT_TIMESTAMP,
  '["lab_results_2024.json", "vitals_2024.json"]',
  '{"LAB": 156, "VITAL": 89, "MEDICATION": 23}',
  '{
    "total_records": 268,
    "date_range": {"start": "2013-01-15", "end": "2025-02-12"},
    "providers": ["Duly Health", "Northwestern Medicine"],
    "extraction_version": "1.0",
    "accuracy_check": "PASSED"
  }'
);
```

## Foreign Key Relationships

```sql
ALTER TABLE HEALTH_RECORDS 
ADD CONSTRAINT fk_patient 
FOREIGN KEY (patient_id) 
REFERENCES PATIENTS(patient_id);

ALTER TABLE HEALTH_RECORDS 
ADD CONSTRAINT fk_import 
FOREIGN KEY (import_id) 
REFERENCES IMPORTS(import_id);

ALTER TABLE IMPORTS 
ADD CONSTRAINT fk_patient_import 
FOREIGN KEY (patient_id) 
REFERENCES PATIENTS(patient_id);
```

## Snowflake-Specific Considerations

### No Explicit Indexes
Snowflake automatically manages micro-partitions. Don't create indexes.

### Clustering Keys for Performance
For frequently filtered columns:
```sql
ALTER TABLE HEALTH_RECORDS 
CLUSTER BY (patient_id, record_type, record_date);
```

### Permissions for Cortex Analyst
```sql
GRANT USAGE ON DATABASE HEALTH_INTELLIGENCE TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA HEALTH_RECORDS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA HEALTH_RECORDS TO ROLE ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE ACCOUNTADMIN;
```

### Stage for Semantic Model
```sql
CREATE STAGE IF NOT EXISTS RAW_DATA
  FILE_FORMAT = (TYPE = 'JSON');

-- Upload semantic model
-- PUT file://path/to/health_intelligence_semantic_model.yaml @RAW_DATA;
```

## Design Checklist

Before finalizing schema:

- [ ] Three tables: PATIENTS, HEALTH_RECORDS, IMPORTS
- [ ] No column names containing "NAME", "TYPE", "UNIT"
- [ ] All dates in ISO 8601 format (YYYY-MM-DD)
- [ ] JSON stored in VARCHAR, not VARIANT
- [ ] Foreign keys defined between tables
- [ ] Table creation order: PATIENTS → IMPORTS → HEALTH_RECORDS
- [ ] Permissions granted for Cortex Analyst
- [ ] RAW_DATA stage created for semantic model
- [ ] Clustering keys defined for large tables
- [ ] Comments added to column purposes

## Anti-Patterns to Avoid

❌ **Separate table per data type**
```sql
CREATE TABLE LAB_RESULTS (...)
CREATE TABLE VITALS (...)
CREATE TABLE MEDICATIONS (...)
```
→ This complicates NL→SQL query generation, makes Cortex Analyst slower

❌ **Over-normalization with lookup tables**
```sql
CREATE TABLE TEST_CATEGORIES (id, category)…
CREATE TABLE PROVIDERS (id, name, type)…
```
→ Unnecessary joins; slows semantic layer

❌ **Complex hierarchical structures**
```sql
CREATE TABLE ENCOUNTERS (...)
CREATE TABLE ENCOUNTER_DETAILS (...)
CREATE TABLE ENCOUNTER_RESULTS (...)
```
→ Makes natural language queries harder to generate

❌ **Views in base DDL**
```sql
CREATE VIEW latest_labs AS …
```
→ Let semantic model define common query patterns

✅ **INSTEAD: Simple, unified design**
- One HEALTH_RECORDS table with discriminator column
- Direct, flat structure
- Easy for semantic model to map
- Fast to query
- Simple to understand

---

**Reference**: This design pattern from the original `multi-agent-health-insight-system` has proven effective for health data analytics.
