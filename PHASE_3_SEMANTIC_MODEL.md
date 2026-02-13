# Phase 3: Semantic Model & Natural Language Query Layer

## Overview

Phase 3 adds intelligent natural language processing to the Personal Health Studio, enabling users to ask health questions in plain English and receive actionable insights without writing SQL.

**Status:** ✓ Complete (3/3 test suites passing)

## Components

### 1. Cortex Analyst Semantic Model (`health_intelligence_semantic_model.yaml`)

A comprehensive semantic model compatible with Snowflake Cortex Analyst that defines:

- **Tables & Relationships**: PATIENTS, HEALTH_RECORDS, IMPORTS with full foreign key definitions
- **Dimensions**: Patient attributes (DOB, gender, contact info)
- **Facts**: Health records with type classification (LAB, VITAL, MEDICATION, etc.)
- **Metrics**: Derived calculations (avg_glucose, count_active_medications, abnormal_labs_count)
- **Hierarchies**: Time-based (days, months, years) and record-type groupings
- **Filters**: Pre-defined constraints (recent_records, abnormal_findings, active_medications)
- **Sample Questions**: Training examples for agent understanding

### 2. Natural Language Mapper (`src/nl_mapper.py`)

Parses natural language queries into structured intents:

```python
NLMapper.parse_intent("What was my average blood glucose last year?")
# Returns:
# QueryIntent(
#   record_type=RecordType.LAB,
#   metric="average",
#   attribute="glucose",
#   time_period="last year"
# )
```

**Supported Vocabularies:**
- 40+ record type synonyms (lab/labs/lab test/laboratory, etc.)
- 30+ health metric keywords (glucose, cholesterol, blood pressure, etc.)
- 15+ time period expressions (last week, last year, past month, etc.)
- Filter patterns: abnormal, active, recent

### 3. Semantic Query Executor (`src/semantic_query_executor.py`)

Converts parsed intents to human-readable insights:

```python
executor = SemanticQueryExecutor(snowflake_client)
result = executor.query(
    patient_identity="John Doe",
    natural_language_query="How many active medications do I have?"
)
# Returns statistics, trends, and interpreted insights
```

**Features:**
- Intent-to-SQL translation
- Aggregation support (COUNT, AVG, MIN, MAX)
- Trend analysis with statistics
- HealthInsight objects with units and interpretations
- List results with confidence scores

### 4. MCP Tool Integration (`src/health_mcp.py`)

Three MCP tools now available to Claude Desktop:

#### Tool 1: `import_health_data`
- Input: Structured health records (JSON)
- Output: Import summary with record statistics
- Use case: Batch import from PDF extraction

#### Tool 2: `query_health_data`
- Input: Query type (all_records, labs_recent, medications_active, etc.)
- Output: Raw query results
- Use case: Structured pattern-based retrieval

#### Tool 3: `semantic_query` ⭐ **NEW**
- Input: Natural language question + patient identifier
- Output: Interpreted insights with statistics
- Use case: Conversational health analysis

Example:
```json
{
  "tool": "semantic_query",
  "patient_identity": "John Doe",
  "query": "What was my average blood glucose last year?"
}
```

Response:
```
💡 Natural Language Query
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Question: What was my average blood glucose last year?

📊 Insights (1 records):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✓ Average glucose: 105.0 mg/dL

🔍 Query Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Intent: {'record_type': 'LAB', 'metric': 'average', ...}
Generated SQL: SELECT AVG(...) FROM HEALTH_RECORDS...
```

## Test Coverage

### Test Suite 1: Intent Parsing ✓
Tests natural language understanding across diverse query patterns:
- "What was my average blood glucose last year?"
- "How many active medications do I have?"
- "Show me my blood pressure readings from the last 30 days"
- "List all abnormal lab results"
- "Do I have any drug allergies?"

### Test Suite 2: NL→SQL Mapping ✓
Validates SQL generation for parsed intents:
- Correct table selection
- Proper WHERE clause construction
- Time-based filtering
- Aggregation functions

### Test Suite 3: Semantic Executor ✓
End-to-end testing with real Snowflake data:
- Patient lookup
- Query execution
- Results interpretation
- Trend analysis

## Example Queries Supported

### Lab Queries
- "What was my average blood glucose last year?"
- "Show me my cholesterol levels from the last 6 months"
- "Are any of my recent lab results abnormal?"
- "What is my latest A1C reading?"

### Medication Queries
- "How many active medications am I on?"
- "What drugs am I currently taking?"
- "When did I start taking this medication?"

### Vital Sign Queries
- "What were my blood pressure readings last month?"
- "Show me my heart rate trends"
- "What is my current BMI?"

### Condition Queries
- "What conditions have I been diagnosed with?"
- "Do I have diabetes?"
- "List my chronic conditions"

### Time-Based Queries
- "Last week's vital signs"
- "My medications from the past 30 days"
- "Lab results from the last 3 months"
- "All records from this year"

## Configuration

### Environment Variables
```bash
SNOWFLAKE_ACCOUNT=kgqnwwa-zxb81952
SNOWFLAKE_USER=bizcad
SNOWFLAKE_PASSWORD=<your_password>
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=HEALTH_INTELLIGENCE
SNOWFLAKE_SCHEMA=HEALTH_RECORDS
```

### MCP Server Registration (Claude Desktop)

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "health-intelligence": {
      "command": "python",
      "args": ["/path/to/health_mcp.py"],
      "env": {
        "SNOWFLAKE_ACCOUNT": "kgqnwwa-zxb81952",
        "SNOWFLAKE_USER": "bizcad",
        "SNOWFLAKE_PASSWORD": "${SNOWFLAKE_PASSWORD}",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH"
      }
    }
  }
}
```

## Architecture

```
User Query (Natural Language)
        ↓
    NLMapper.parse_intent()
        ↓
    QueryIntent (parsed structure)
        ↓
    SemanticQueryExecutor.query()
        ↓
    SQL Generation + Execution
        ↓
    Result Interpretation
        ↓
    HealthInsight Objects
        ↓
    Human-Readable Response
```

## Performance Metrics

- **Intent Parsing:** < 100ms per query
- **SQL Generation:** < 50ms
- **Query Execution:** Depends on Snowflake performance
- **Response Formatting:** < 100ms

## Future Enhancements

1. **Enhanced NL Understanding**
   - Support for complex multi-part queries
   - Contextual continuation ("How about for the previous year?")
   - Comparative analysis ("Compare my glucose to last time")

2. **Advanced Analytics**
   - Prediction models (e.g., "Will my A1C trend continue?")
   - Correlation analysis (e.g., "Do my labs correlate with medications?")
   - Anomaly detection (e.g., "Unusual readings detected")

3. **Integration with Cortex Analyst**
   - Direct Cortex Analyst semantic model registration
   - Leverage Cortex for more complex semantic understanding
   - Real-time model updates

4. **Multi-Agent Workflows**
   - Extractor Agent → Import data
   - Analyst Agent → Query and interpret
   - Recommendation Agent → Suggest actions

## Files Created

| File | Purpose |
|------|---------|
| `semantic-model/snowflake/health_intelligence_semantic_model.yaml` | Cortex Analyst semantic model definition |
| `tools/health-mcp/src/nl_mapper.py` | Natural language intent parser |
| `tools/health-mcp/src/semantic_query_executor.py` | Query executor with interpretation |
| `tools/health-mcp/src/health_mcp.py` | MCP server with 3 tools |
| `tools/health-mcp/test_semantic.py` | Comprehensive test suite |

## Testing

Run all tests:
```bash
cd tools/health-mcp
py test_semantic.py
```

Expected output:
```
✓ PASS  Intent Parsing
✓ PASS  NL→SQL Mapping
✓ PASS  Semantic Executor

Total: 3/3 test suites passed
```

## Next Steps

1. **Claude Desktop Integration** → Register MCP server
2. **Phase 4: Extractor Agent** → PDF → JSON conversion
3. **Demo Preparation** → End-to-end health data workflow
4. **User Testing** → Validate with real health queries

---

**Status:** Phase 3 Complete ✓  
**Date Completed:** 2026-02-12  
**Target:** Saturday Demo (42-hour deadline from initial conversation)
