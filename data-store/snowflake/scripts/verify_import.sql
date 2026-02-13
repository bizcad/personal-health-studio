-- ============================================================================
-- HEALTH INTELLIGENCE - Schema Verification Queries
-- Run after deploying health_intelligence_ddl.sql to confirm everything loaded.
-- ============================================================================

USE DATABASE HEALTH_INTELLIGENCE;
USE SCHEMA HEALTH_RECORDS;

-- 1. Confirm all three tables exist
SHOW TABLES IN SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS;

-- 2. Verify PATIENTS structure
DESCRIBE TABLE PATIENTS;

-- 3. Verify IMPORTS structure
DESCRIBE TABLE IMPORTS;

-- 4. Verify HEALTH_RECORDS structure
DESCRIBE TABLE HEALTH_RECORDS;

-- 5. Confirm no reserved-word column names (NAME, TYPE, UNIT)
-- These should return zero rows:
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'HEALTH_RECORDS'
  AND TABLE_CATALOG = 'HEALTH_INTELLIGENCE'
  AND COLUMN_NAME IN ('NAME', 'TYPE', 'UNIT');

-- 6. Confirm foreign keys
SHOW IMPORTED KEYS IN TABLE HEALTH_RECORDS;
SHOW IMPORTED KEYS IN TABLE IMPORTS;

-- 7. Confirm clustering key on HEALTH_RECORDS
SHOW TABLES LIKE 'HEALTH_RECORDS' IN SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS;

-- 8. Confirm RAW_DATA stage exists
SHOW STAGES LIKE 'RAW_DATA' IN SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS;

-- 9. Sample insert and select (uncomment to test with sample data)
-- INSERT INTO PATIENTS (PATIENT_IDENTITY, DATE_OF_BIRTH)
-- VALUES ('JOHN DOE', '1980-03-26');
--
-- INSERT INTO IMPORTS (PATIENT_ID, SOURCE_FILES, RECORDS_BY_CATEGORY, STATUS)
-- VALUES (1, '["lab_results.json"]', '{"LAB": 5}', 'SUCCESS');
--
-- INSERT INTO HEALTH_RECORDS (PATIENT_ID, IMPORT_ID, RECORD_CATEGORY, RECORD_DATE, PROVIDER, DATA_JSON)
-- VALUES (1, 1, 'LAB', '2025-04-07', 'Health Clinic',
--   '{"test_description": "Glucose", "test_result": "98", "test_dimension": "mg/dL", "reference_range": "74 to 109", "flag": "NORMAL", "test_category": "Metabolic"}');
--
-- SELECT * FROM HEALTH_RECORDS WHERE RECORD_CATEGORY = 'LAB';
