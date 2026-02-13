# Phase 4: Health Data Extractor Agent Integration

## Overview

Phase 4 completes the Personal Health Studio by adding an intelligent **Health Data Extractor Agent** that:
- Extracts health records from PDFs, images, and documents
- Validates extraction quality
- Imports to Snowflake via MCP tools
- Queries and explores imported data

This phase transforms the multi-agent system into a fully functional **Extract → Store → Query** pipeline.

## Architecture

```
User Document (PDF/Image)
         ↓
Extractor Agent (Claude Vision)
    - Parse document
    - Extract health records
    - Validate quality
         ↓
MCP import_health_data Tool
    - Format records
    - Insert to Snowflake
         ↓
Snowflake Database
    - Store patient records
    - Maintain data lineage
         ↓
MCP query_health_data / semantic_query Tools
    - Retrieve records
    - Answer natural language questions
    - Generate insights
```

## Components

### 1. Health PDF Extractor (`health_pdf_extractor.py`)

The extractor uses Claude's vision capabilities to parse health documents.

**Location:** `agents/extractor-agent/health_pdf_extractor.py`

**Key Class:** `HealthPDFExtractor`

**Methods:**

```python
extract_from_pdf(pdf_path: str, patient_identity: str) 
  → Tuple[List[HealthRecord], Dict{stats}]
  
_extract_record_type(document_content: str, record_type: str)
  → List[HealthRecord]
  
validate_extraction(records: List[HealthRecord])
  → Dict[str, Any]  # validation_report, confidence_stats, warnings
  
extract_and_prepare()
  → Dict[str, Any]  # MCP-ready import payload
  
create_sample_extraction()
  → Dict[str, Any]  # Demo data for testing
```

**Extraction Prompts** (6 types):

Each record type has a structured extraction prompt that Claude uses to parse documents:

- **VITAL** → Blood pressure, heart rate, temperature, weight, oxygen saturation
- **LAB** → Test name, result value, reference range, abnormal flag
- **MEDICATION** → Drug name, dosage, frequency, indication, dates
- **CONDITION** → Diagnosis, ICD code, onset date, severity
- **ALLERGY** → Allergen, reaction, severity, onset date
- **IMMUNIZATION** → Vaccine name, date, dose number, provider, lot

### 2. Health Models (`src/health_models.py`)

Pydantic models for structured health records.

**Key Classes:**
- `VitalRecord` - Single vital sign measurement (BP, HR, temp, weight, etc.)
- `LabRecord` - Lab test with result value and reference range
- `MedicationRecord` - Prescription with dosage and frequency
- `ConditionRecord` - Diagnosis with ICD code
- `AllergyRecord` - Allergen with severity
- `ImmunizationRecord` - Vaccine with administration date
- `HealthRecord` - Wrapper supporting all types
- `RecordClass` - Enum: LAB, VITAL, MEDICATION, CONDITION, ALLERGY, IMMUNIZATION, ENCOUNTER, NOTE

**Example:**

```python
lab_record = LabRecord(
    test_name="Blood Glucose",
    result_value=105,
    result_unit="mg/dL",
    reference_range="70-100",
    abnormal_flag=True,
    test_date=datetime.now(),
    provider="Quest Labs"
)

health_record = HealthRecord(
    patient_identity="john.doe@example.com",
    record_class=RecordClass.LAB,
    record_data=lab_record
)
```

### 3. Snowflake Client (`src/snowflake_client.py`)

Database client for persistence and querying.

**Key Methods:**

```python
connect() → bool
  - Establish Snowflake connection

import_health_records(patient_identity: str, records: List[HealthRecord])
  → Dict[status, count, errors]
  - Insert extracted records to database

query_health_data(patient_identity: str, query_type: str, parameters: Dict)
  → List[Dict]
  - Execute predefined queries (all_records, labs_recent, medications_active, etc.)
```

### 4. MCP Server Integration (`src/health_mcp.py`)

Claude-accessible tools via Model Context Protocol.

**Tools:**

```python
@server.call_tool("import_health_data")
def handle_import_health_data(...)
  Input: patient_identity, records (JSON)
  Output: import_status, record_count, errors
  
@server.call_tool("query_health_data")
def handle_query_health_data(...)
  Input: patient_identity, query_type, parameters
  Output: records, summary statistics
  
@server.call_tool("semantic_query")
def handle_semantic_query(...)
  Input: patient_identity, natural_language_query
  Output: HealthInsight with interpretation
```

## Integration with Claude

### Using Vision API for PDF Extraction

The extractor uses Claude's vision capabilities:

```python
from anthropic import Anthropic

client = Anthropic()

# Convert PDF to images
images = pdf_to_images(pdf_path)

# Extract via vision
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=4096,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": EXTRACTION_PROMPT  # Lab/vital/medication prompt
            },
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": base64_image
                }
            }
        ]
    }]
)

# Parse response as JSON
extracted_data = json.loads(response.content[0].text)
```

### Calling MCP Tools

Once extracted, import via MCP:

```python
# Format for MCP tool
import_payload = {
    "patient_identity": "john.doe@example.com",
    "records": [
        {
            "record_class": "LAB",
            "record_data": {
                "test_name": "Blood Glucose",
                "result_value": 105,
                "result_unit": "mg/dL",
                ...
            }
        },
        ...
    ]
}

# Call via MCP (available in Claude)
# Agent calls: data = use_mcp_tool("import_health_data", import_payload)
```

## Workflow Example

### 1. Extract Phase

```
User: "I have an Apple Health export with my lab results and vitals"
[User uploads PDF]

Agent:
✓ Document received: apple-health-export.pdf
✓ Size: 4.2 MB, Pages: 87

Scanning document...
- Found labs: Glucose, Cholesterol, Hemoglobin, Thyroid, Liver Panel
- Found vitals: 247 blood pressure readings, 1,823 daily weights, 892 heart rates
- Found medications: 12 active prescriptions
- Found conditions: Diabetes Type 2, Hypertension

Ready to extract...
```

### 2. Validation Phase

```
Extraction Complete:
- LAB records: 156 labs extracted (avg confidence: 0.94)
- VITAL records: 2,962 vitals extracted (avg confidence: 0.97)
- MEDICATION records: 12 meds extracted (avg confidence: 0.99)
- CONDITION records: 8 conditions extracted (avg confidence: 0.92)

Validation:
✓ 3,138 total records
✓ 19 fields flagged as low-confidence (< 0.85)
⚠ 3 records missing provider information
✓ Data completeness: 98.7%

Proceeding with import...
```

### 3. Import Phase

```
Importing to Snowflake...

MCP Tool: import_health_data
Status: ✓ SUCCESS
Records Imported:
  - 156 lab records
  - 2,962 vital records
  - 12 medication records
  - 8 condition records
Total: 3,138 records

Patient created: john.doe@example.com
Patient ID: pat_abc123def456
```

### 4. Verification Phase

```
Verifying import...

MCP Tool: query_health_data (query_type: all_records)
Results:
- Patient has 3,138 health records
- Date range: 2021-01-15 to 2025-02-12 (4.1 years)
- Providers: 5 different providers
- Record distribution:
  • Labs: 156 (5.0%)
  • Vitals: 2,962 (94.4%)
  • Medications: 12 (0.4%)
  • Conditions: 8 (0.3%)

✓ Import successful and verified!
```

### 5. Exploration Phase

```
Exploring imported data...

MCP Tool: semantic_query
Query: "What was my average blood glucose last year?"
Result:
  Title: Average Blood Glucose (Last Year)
  Value: 105.4 mg/dL
  Interpretation: Slightly elevated for a non-fasting measurement.
                 Suggests possible pre-diabetes or need for diet adjustment.
  Records Analyzed: 47 glucose measurements
  Trend: Increasing by 2.3 mg/dL per quarter
  Confidence: 0.95

MCP Tool: semantic_query
Query: "What medications am I currently taking?"
Result:
  Title: Active Medications (As of Feb 2025)
  Value: 4 active prescriptions
  Medications:
    1. Metformin 500mg BID (Type 2 Diabetes)
    2. Lisinopril 10mg daily (Hypertension)
    3. Atorvastatin 20mg daily (Cholesterol)
    4. Aspirin 81mg daily (CVD Prevention)
  Confidence: 0.99
```

## Testing

### Unit Tests

```bash
# Test extraction logic
pytest test_extraction.py

# Test MCP integration
pytest test_mcp_tools.py

# Test Snowflake import
pytest test_snowflake_import.py
```

### Integration Tests

```bash
# End-to-end workflow
pytest test_end_to_end.py

# Real Snowflake integration
pytest test_live_snowflake.py
```

### Sample Data

```python
# Create demo data without PDF
extractor = HealthPDFExtractor()
demo_payload = extractor.create_sample_extraction()

# Use payload to test import
response = client.import_health_records(
    patient_identity="demo@example.com",
    records=demo_payload["records"]
)
```

## Claude Desktop Configuration

To use with Claude Desktop, register the MCP server:

**File:** `claude_desktop_config.json`

```json
{
  "mcpServers": {
    "health-intelligence": {
      "command": "python",
      "args": [
        "g:/repos/AI/PersonalHealthStudio/PHSetup/tools/health-mcp/src/health_mcp.py"
      ],
      "env": {
        "SNOWFLAKE_ACCOUNT": "kgqnwwa-zxb81952",
        "SNOWFLAKE_USER": "bizcad",
        "SNOWFLAKE_PASSWORD": "ImFW3&Z&#9vUa9Mn",
        "SNOWFLAKE_DATABASE": "HEALTH_INTELLIGENCE",
        "SNOWFLAKE_SCHEMA": "HEALTH_RECORDS",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH"
      }
    }
  }
}
```

## Next Steps

1. **Integrate Claude Vision API**
   - Add API key for PDF extraction
   - Test with sample health documents
   - Optimize extraction prompts

2. **Create Sample Health Data**
   - Generate test PDFs or export samples
   - Create expected extraction results
   - Document demo scenarios

3. **Test End-to-End**
   - PDF → Extraction → Import → Query
   - Verify all 3 MCP tools work together
   - Test with multi-year health data

4. **Prepare Demo**
   - Create demo narrative
   - Pre-test extraction workflows
   - Document step-by-step demo script
   - Show before/after (raw PDF → insights)

## Timeline

- **Phase 4 Integration**: This document (setup)
- **Claude Vision API**: 1-2 hours
- **Sample Data Creation**: 30 minutes
- **End-to-End Testing**: 1-2 hours
- **Demo Preparation**: 2-3 hours
- **Total**: ~6-8 hours to demo-ready state

## Success Criteria

✓ PDFs successfully parsed and health records extracted
✓ Extraction confidence > 0.85 for 95% of records
✓ All record types (labs, vitals, meds, conditions, allergies, immunizations) extracted
✓ Records successfully imported to Snowflake (verify with query tool)
✓ Imported data queryable via semantic_query tool
✓ Full workflow demonstrable: PDF → Extract → Store → Query → Insights

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              Claude Desktop / Chat Interface               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User Document (PDF/Image) ──→ Extractor Agent             │
│                                  (Vision Analysis)          │
│                                       ↓                     │
│                            HealthPDFExtractor               │
│                            - Parse document                 │
│                            - Extract records                │
│                            - Validate quality               │
│                                       ↓                     │
│                            MCP Server (health_mcp.py)       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                     3 MCP Tools:                            │
│  ┌─────────────────┬──────────────────┬───────────────┐    │
│  │ import_health  │ query_health    │ semantic_query │    │
│  │ _data          │ _data           │                │    │
│  └─────────────────┴──────────────────┴───────────────┘    │
│                            ↓                               │
├─────────────────────────────────────────────────────────────┤
│              Snowflake Cloud Database                       │
│  ┌────────────┬──────────────┬─────────────────────┐        │
│  │  PATIENTS  │   IMPORTS    │  HEALTH_RECORDS     │        │
│  │            │              │  (Unified Fact)     │        │
│  └────────────┴──────────────┴─────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

## Repository Structure (Phase 4)

```
agents/extractor-agent/
├── config/
│   ├── agent-description.md          # Agent profile
│   └── agent-instructions.md         # Detailed instructions
├── src/
│   └── health_pdf_extractor.py       # Extraction logic
├── test/
│   ├── test_extraction.py
│   ├── test_end_to_end.py
│   └── sample_health_data.json
└── README.md

tools/health-mcp/
├── src/
│   ├── health_models.py              # Pydantic models
│   ├── snowflake_client.py           # DB client
│   ├── health_mcp.py                 # MCP server + 3 tools
│   ├── nl_mapper.py                  # NL parsing
│   └── semantic_query_executor.py    # NL→SQL
├── test/
│   ├── test_tools.py
│   ├── test_semantic.py
│   └── test_extraction.py
└── pyproject.toml

semantic-model/
└── snowflake/
    └── health_intelligence_semantic_model.yaml

data-store/
└── snowflake/
    └── ddl/
        └── health_intelligence_ddl.sql

claude_desktop_config.json              # MCP registration
```

---

**Phase 4 Status**: Architecture and integration guide complete. 
**Next**: Claude Vision API integration and end-to-end testing.
