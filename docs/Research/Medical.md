# Medical.md - Health Intelligence System Requirements

## Problem Statement

Your friends struggle with health data management:
- Apple Health aggregates 10-15+ years of health records
- Exports are 200+ page PDFs (unsearchable, unanalyzable)
- Data from multiple healthcare providers (fragmented)
- No way to spot trends, correlations, or anomalies
- Valuable health intelligence trapped in static documents

**Solution**: Transform health PDFs into structured, queryable health intelligence system.

## Core Use Cases

### 1. Trend Analysis
**"What's my cholesterol trend over 10 years?"**
- Extract LDL, HDL, total cholesterol values with dates
- Chart values over time
- Identify improvement/decline patterns
- Correlate with diet, exercise, medications

### 2. Medication Intelligence
**"Which medications I am I on and for what conditions?"**
- List all current medications with dosages
- Link medications to conditions being treated
- Identify potential interactions
- Track medication duration and status changes

### 3. Lab Abnormalities
**"Are there any abnormal labs?"**
- Identify values outside reference range
- Flag new abnormalities vs. chronic patterns
- Correlate abnormalities across multiple tests
- Track resolution over time

### 4. Multi-Provider Comparison
**"How do my results compare across different doctors?"**
- Consolidate data from multiple healthcare providers
- Standardize lab naming conventions
- Detect inconsistencies in diagnoses
- Identify provider-specific patterns

### 5. Health Timeline
**"What happened to my health in 2023?"**
- Create chronological view of health events
- Link diagnoses, medications, labs, vitals
- Identify causation patterns
- Build personalized health narrative

### 6. Condition Tracking
**"How long have I had this condition?"**
- Diagnosis date for each condition
- Current status (active, resolved, chronic)
- Related symptoms
- Treatment history with timeline

### 7. Vitals Monitoring
**"How have my weight and blood pressure changed?"**
- Monthly/yearly trends
- Correlation with diet changes, exercise
- Identify outlier measurements
- Track effectiveness of lifestyle changes

## Data Categories to Extract

### Lab Results
**Data Points**: Test date, test name, result value, unit, reference range, abnormal flag, test category

**Example**: 
- Date: 2025-04-07
- Test: Cholesterol Total
- Value: 185 mg/dL
- Range: 125-200 mg/dL
- Status: Normal

### Vitals
**Data Points**: Measurement date, vital type, value, units, reference range (if applicable)

**Example**:
- Date: 2025-02-14
- Type: Blood Pressure
- Systolic: 124 mmHg
- Diastolic: 80 mmHg
- Status: Normal

**Converted Units**: Height (cm→in), Weight (kg→lb), Temperature (°C→°F)

### Medications
**Data Points**: Prescription date, medication name, dosage, form, frequency, condition treated, end date, status

**Example**:
- Date: 2024-03-15
- Medication: Atorvastatin
- Dosage: 40 mg
- Form: Tablet
- Frequency: Once daily
- Condition: High Cholesterol
- Status: Active

### Clinical Data
**Data Points**: 
- Conditions: Diagnosis date, condition name, status, provider
- Allergies: Allergy name, severity, date recorded
- Immunizations: Vaccine, date, provider
- Procedures: Procedure type, date, indication, provider
- Providers: Provider names, types, specialties

**Example Condition**:
- Date: 2023-09-28
- Condition: Type 2 Diabetes
- Status: Active
- Provider: Primary Care Clinic

## System Architecture

```
Friend's Device
    ↓
[Exports Health PDF from App]
    ↓
[Uploads to Health Extractor Agent] (Claude Desktop)
    ↓
[EXTRACTION - 100% Accuracy]
    - PDF → Structured JSON
    - Year-by-year organization
    - Provider normalization
    - Unit standardization
    ↓
[JSON Files Downloaded]
    - lab_results_2024.json
    - vitals_2024.json
    - medications.json
    - clinical_data_2024.json
    ↓
[Uploads to Health Analyst Agent] (Claude Desktop)
    ↓
[DATA IMPORT - Snowflake]
    - Loads JSON to Snowflake tables
    - Creates import metadata
    - Generates statistics
    ↓
[ANALYSIS - Natural Language Queries]
    - "What's my cholesterol trend?"
    - "Show me medications for heart disease"
    - "Any abnormal labs in 2024?"
    ↓
[Insights & Visualizations]
    - Charts and trend analysis
    - Pattern identification
    - Health recommendations
```

## Technology Stack

### Extraction
- **Agent**: Health Data Extractor (Claude)
- **Platform**: Claude Desktop (local, no cloud extraction)
- **Output**: JSON with 100% fidelity to source

### Data Storage
- **Database**: Snowflake (free tier works for personal use)
- **Schema**: 3 simple tables (PATIENTS, HEALTH_RECORDS, IMPORTS)
- **Alternative**: CockroachDB, PostgreSQL, or local DuckDB

### Analysis
- **Semantic Model**: Snowflake Cortex Analyst (NL→SQL)
- **MCP Tools**: health_mcp server (import + query tools)
- **Agent**: Health Analyst (Claude Desktop)

### Integration
- **MCP Protocol**: Model Context Protocol for agent ↔ database communication
- **Environment**: Local + Snowflake (no third-party services)

## Design Principles

### 1. Zero-Tolerance Accuracy
- Health data must match source documents exactly
- No rounding, approximation, or intelligent "correction"
- Missing values recorded as missing, not estimated
- Extraction errors block the entire operation

### 2. Conservative Defaults
- If ambiguous, ask user before proceeding
- Block rather than risk inaccuracy
- All blocks logged with reasons
- Users always understand why something was rejected

### 3. Privacy First
- No cloud-based extraction of personal health data
- All processing local to user's machine or user-controlled Snowflake
- Clear data handling policies
- User maintains complete control

### 4. User Empowerment
- Clear instructions for every step
- Transparent logging of all operations
- Ability to review extracted data before analysis
- Easy to audit and validate

## Deployment Model for Friends

### For Non-Technical Friends

**Phase 1: Setup (30 minutes)**
1. Install Claude Desktop (free)
2. Create Snowflake account (free tier available)
3. Copy agents to Claude Desktop config
4. Input database credentials

**Phase 2: Use (5 minutes per health PDF)**
1. Export health PDF from health app
2. Upload to Extractor Agent
3. Download extracted JSON files
4. Upload JSON to Analyst Agent
5. Start asking health questions

### Minimum Requirements
- Claude Desktop (free)
- Snowflake account (free tier)
- Health PDF export from any health app
- About 15 minutes for setup

### Alternative: Fully Local Version
Could run everything locally using:
- DuckDB (embedded, requires no server)
- Local semantic layer (custom NL→SQL or LLM-based)
- Eliminates need for Snowflake credentials

## Success Metrics

### By Saturday Evening Demo
- [ ] System successfully extracts 10+ years of health data with 100% accuracy
- [ ] Extracted data successfully imports to database
- [ ] Can answer 5+ health questions using natural language
- [ ] Friends can replicate setup on their machines
- [ ] No sensitive data exposed or logged

### Long-term
- [ ] Friends use system to manage their health data
- [ ] System identifies medically relevant patterns
- [ ] Reduces time spent on health data analysis from hours to minutes
- [ ] Becomes a trusted tool in their health management toolkit

## Out of Scope (For Now)

- [ ] Integration with doctor portals (MyChart, Epic)
- [ ] Wearable device data (Apple Watch, Fitbit)
- [ ] Real-time notifications
- [ ] Mobile app or web interface
- [ ] Integration with insurance systems
- [ ] Doctor recommendation features

## Open Questions

1. **Data Sources**: Start with Apple Health or support multiple sources immediately?
2. **Visualization**: Snowflake dashboard, Tableau, or Claude-generated charts?
3. **Sharing**: Will friends have their own Snowflake accounts or shared database?
4. **Timeline**: Can extract system be ready by Saturday for demo?
5. **Scaling**: How many years of historical data is realistic to process?

## Next Steps

1. Create Snowflake schema (PATIENTS, HEALTH_RECORDS, IMPORTS)
2. Build Extractor Agent with extraction schemas
3. Build MCP import tool
4. Create semantic model for natural language queries
5. Configure Claude Desktop integration
6. Test with sample health PDF
7. Document setup guide for friends

---

**Created**: February 12, 2026  
**Status**: Requirements document for Personal Health Studio  
**Target Demo**: Saturday evening, February 15, 2026
