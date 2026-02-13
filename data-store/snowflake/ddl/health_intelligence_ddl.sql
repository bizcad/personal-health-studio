-- Health Intelligence Database Schema
-- Snowflake DDL for Personal Health Studio
-- Created: 2026-02-12
-- Design: Three-table unified model per data-modeling-principles.md

-- ================================================================
-- DATABASE AND SCHEMA SETUP
-- ================================================================

CREATE DATABASE IF NOT EXISTS HEALTH_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS HEALTH_INTELLIGENCE.HEALTH_RECORDS;

-- ================================================================
-- TABLE 1: PATIENTS (Dimension)
-- ================================================================

CREATE TABLE IF NOT EXISTS HEALTH_INTELLIGENCE.HEALTH_RECORDS.PATIENTS (
    patient_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    patient_identity VARCHAR(500) NOT NULL,  -- Use IDENTITY not NAME (Cortex Analyst)
    date_of_birth DATE,
    gender VARCHAR(50),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    created_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
)
COMMENT = 'Master patient dimension table';

-- ================================================================
-- TABLE 2: IMPORTS (Metadata and Lineage)
-- ================================================================

CREATE TABLE IF NOT EXISTS HEALTH_INTELLIGENCE.HEALTH_RECORDS.IMPORTS (
    import_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    import_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    source_files VARCHAR(4000),  -- JSON array as VARCHAR: ["file1.json", "file2.json"]
    records_by_type VARCHAR(4000),  -- JSON object: {"LAB": 156, "VITAL": 89, ...}
    import_statistics VARCHAR(4000),  -- Detailed JSON with extraction metadata
    import_status VARCHAR(50) DEFAULT 'SUCCESS',  -- SUCCESS, PARTIAL, FAILED
    error_message VARCHAR(2000),
    created_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_import_patient FOREIGN KEY (patient_id) 
        REFERENCES HEALTH_INTELLIGENCE.HEALTH_RECORDS.PATIENTS(patient_id)
)
COMMENT = 'Tracks data imports and lineage for audit trail';

-- ================================================================
-- TABLE 3: HEALTH_RECORDS (Fact Table - Unified)
-- ================================================================

CREATE TABLE IF NOT EXISTS HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS (
    record_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    import_id INTEGER,
    record_class VARCHAR(50) NOT NULL,  -- Use CLASS not TYPE (Cortex Analyst) 
                                         -- Values: LAB, VITAL, MEDICATION, CONDITION, ALLERGY, IMMUNIZATION
    record_date DATE NOT NULL,
    provider_identity VARCHAR(500),  -- Use IDENTITY not NAME (Cortex Analyst)
    data_json VARCHAR(16000) NOT NULL,  -- Full JSON payload (not VARIANT per design)
    extraction_confidence DECIMAL(5, 2),  -- 0-100 confidence score
    verification_status VARCHAR(50) DEFAULT 'UNVERIFIED',  -- UNVERIFIED, VERIFIED, FLAGGED
    created_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    updated_date TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    CONSTRAINT fk_record_patient FOREIGN KEY (patient_id) 
        REFERENCES HEALTH_INTELLIGENCE.HEALTH_RECORDS.PATIENTS(patient_id),
    CONSTRAINT fk_record_import FOREIGN KEY (import_id)
        REFERENCES HEALTH_INTELLIGENCE.HEALTH_RECORDS.IMPORTS(import_id)
)
COMMENT = 'Unified fact table for all health records (labs, vitals, medications, conditions, allergies, immunizations)';

-- ================================================================
-- CLUSTERING KEYS FOR PERFORMANCE
-- ================================================================

ALTER TABLE HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS
CLUSTER BY (patient_id, record_class, record_date);

ALTER TABLE HEALTH_INTELLIGENCE.HEALTH_RECORDS.IMPORTS
CLUSTER BY (patient_id, import_date);

-- ================================================================
-- STAGE FOR SEMANTIC MODEL
-- ================================================================

CREATE STAGE IF NOT EXISTS HEALTH_INTELLIGENCE.HEALTH_RECORDS.RAW_DATA
    FILE_FORMAT = (TYPE = 'JSON')
    COMMENT = 'Raw data staging for semantic model upload';

-- ================================================================
-- PERMISSIONS FOR CORTEX ANALYST
-- ================================================================

GRANT USAGE ON DATABASE HEALTH_INTELLIGENCE TO ROLE ACCOUNTADMIN;
GRANT USAGE ON SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS TO ROLE ACCOUNTADMIN;
GRANT SELECT ON ALL TABLES IN SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS TO ROLE ACCOUNTADMIN;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE ACCOUNTADMIN;

-- ================================================================
-- VERIFICATION QUERIES (Run these to confirm schema creation)
-- ================================================================

-- Show created tables
SHOW TABLES IN SCHEMA HEALTH_INTELLIGENCE.HEALTH_RECORDS;

-- Describe table structure
DESCRIBE TABLE HEALTH_INTELLIGENCE.HEALTH_RECORDS.PATIENTS;
DESCRIBE TABLE HEALTH_INTELLIGENCE.HEALTH_RECORDS.IMPORTS;
DESCRIBE TABLE HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS;

-- Verify constraints
SELECT * FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS 
WHERE CONSTRAINT_SCHEMA = 'HEALTH_RECORDS';
