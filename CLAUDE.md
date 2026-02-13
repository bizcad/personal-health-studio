# CLAUDE.md - System Design for Claude Code Development

This document provides guidance to Claude Code (claude.ai/code) when working with this health intelligence repository.

## Project Overview

Personal Health Intelligence System - A multi-agent architecture that extracts, analyzes, and visualizes personal health data from health app PDF exports. Two specialized agents work together:

- **Health Data Extractor Agent** (PRIMARY): Converts health PDFs into structured JSON with 100% accuracy requirement
- **Health Analyst Agent** (SECONDARY): Imports data to Snowflake and enables natural language querying via Cortex Analyst

## Current Status

✅ **Completed:**
- Extractor Agent configuration and instructions
- Data extraction schemas (Labs, Vitals, Medications, Clinical Data)
- Agent descriptions and interaction protocols

🔨 **In Development:**
- Snowflake database schema (DDL)
- MCP tools for data import and querying
- Semantic model for natural language processing

⏳ **Planned:**
- Claude Desktop integration
- Sample data extraction workflows
- Visualization dashboards

## Your Task

Help build the health intelligence system following the incremental approach outlined in CLAUDE.md. Start with database foundation, then add tooling, then semantic models.

## How to Work With This Repository

### 1. Understand the Design Philosophy

This system follows **conservative engineering principles**:

- **Zero-Tolerance Accuracy**: Every health data point extracted must match source documents exactly (no approximations)
- **Fail-Safe Defaults**: If uncertain, block the operation and report the issue clearly
- **Data Integrity First**: Validate before processing; validate before storing
- **Deterministic Extraction**: Extraction logic is rule-based, reproducible, testable
- **Probabilistic Analysis**: Claude handles reasoning, pattern matching, insights
- **Clear Communication**: Every decision is logged and explained to the user
- **User Empowerment**: Provide clear next steps after every operation

### 2. Respect These Engineering Standards

From [Principles-and-Processes.md](Principles-and-Processes.md):

- **Type everything**: Full type hints on all Python code
- **Document thoroughly**: Docstrings on every function
- **Test conservatively**: Validate inputs before processing
- **Log clearly**: Report what happened, why, and what to do next
- **Fail safely**: Never approximate or guess with health data
- **Version carefully**: Semantic versioning; maintain backward compatibility

### 3. Work Incrementally

Build in phases:

**Phase 1: Database Foundation**
1. Analyze extraction schemas and sample data
2. Create Snowflake DDL in `/data-store/snowflake/ddl/`
3. Validate against data-modeling-principles.md

**Phase 2: Import Tool (First MCP Tool)**
4. Build ONLY the import tool in `/tools/health-mcp/`
5. Focus on data import, not querying yet

**Phase 3: Semantic Model**
6. Develop semantic model in `/semantic-model/snowflake/`
7. Test with sample data

**Phase 4: Query Tool (Second MCP Tool)**
8. Add query tool AFTER semantic model works

**Phase 5: Integration**
9. Configure Claude Desktop
10. Test end-to-end workflow

## Key Technical Requirements

### For All Code:
- Python 3.10+
- Full type hints (from __future__ import annotations)
- Docstrings on all functions
- Error handling that explains what went wrong

### For Snowflake Schema:
- Follow data-modeling-principles.md strictly
- No reserved words in column names
- Unified health_records table (not separate tables per type)
- VARCHAR for JSON storage (simpler than VARIANT)
- MERGE for upserts (not INSERT...ON DUPLICATE)

### For MCP Tools:
- Use @mcp.tool() decorator
- Require SNOWFLAKE_* environment variables
- Handle connection failures gracefully
- Return structured responses
- Include audit information in responses

### For Extraction Accuracy:
- Extract dates as YYYY-MM-DD (ISO 8601)
- Convert metrics to US customary (cm→in, kg→lb, °C→°F)
- Preserve decimal precision from source
- Never round or approximate values
- Handle null/empty values explicitly
- Validate against schemas

## Files You'll Work With

```
agents/
├── extractor-agent/
│   ├── config/
│   │   ├── agent-description.md       ← Instructions for the agent
│   │   └── agent-instructions.md      ← Detailed extraction protocol
│   └── knowledge/
│       ├── lab-results-extraction-schema.json
│       ├── vitals-extraction-schema.json
│       ├── medications-extraction-schema.json
│       └── clinical-data-extraction-schema.json
└── analyst-agent/
    └── config/
        ├── agent-description.md
        └── agent-instructions.md

data-store/snowflake/
├── ddl/
│   └── health_intelligence_ddl.sql    ← Create this
└── scripts/
    └── verify_import.sql              ← Create this

tools/health-mcp/
├── pyproject.toml                      ← Create this
├── src/
│   └── health_mcp.py                  ← Create this
├── test_import.py                     ← Create this
└── test_query.py                      ← Create this

semantic-model/snowflake/
└── health_intelligence_semantic_model.yaml  ← Create this

requirements/technical/
├── data-modeling-principles.md         ← Read this carefully!
├── mcp-tool-requirements.md            ← Reference this
└── cortex-analyst-semantic-model-requirements.txt
```

## Development Approach - INCREMENTAL BUILD

👉 **DO NOT** try to build everything at once. Follow this sequence:

### Step 1: Database Foundation
- Study the extraction schemas to understand data types
- Design tables based on data-modeling-principles.md
- Create DDL file with PATIENTS, HEALTH_RECORDS, IMPORTS tables
- Validate SQL syntax

### Step 2: Import Tool Only
- Create pyproject.toml with dependencies
- Write health_mcp.py with ONLY snowflake_import_analyze_health_records_v2 tool
- Create test_import.py to validate the tool works
- Test with sample extracted data

### Step 3: Semantic Model
- Define entities (labs, vitals, medications, conditions)
- Map natural language to tables/columns
- Create YAML semantic model
- Test with sample queries

### Step 4: Query Tool
- Add execute_health_query_v2 to health_mcp.py
- Create test_query.py
- Test querying semantic model

### Step 5: Integration
- Configure claude_desktop_config.json
- Test agents with real health data

## How I Should Assist You

When you ask me to:

✅ **"Build the database schema"** → I will:
  - Review extraction schemas
  - Follow data-modeling-principles.md strictly
  - Create health_intelligence_ddl.sql
  - Generate verification queries

✅ **"Create the MCP server"** → I will:
  - Start with ONLY the import tool
  - Include proper error handling
  - Write comprehensive docstrings
  - Create test scripts

✅ **"Build the semantic model"** → I will:
  - Map to the Snowflake schema
  - Define entities and metrics
  - Create YAML configuration
  - Test with sample queries

✅ **"Help debug extraction"** → I will:
  - Review the extraction schema
  - Check for accuracy issues
  - Suggest schema improvements
  - Validate against source data

❌ **I will NOT**:
  - Approximate or guess health data values
  - Skip validation steps
  - Use complex schemas
  - Skip documentation or type hints
  - Build all phases at once

## Working With Extraction Schemas

Each schema (lab-results, vitals, medications, clinical-data) is a JSON Schema that defines:

- **header_fields**: Patient demographics (name, DOB, report date)
- **Data arrays**: Grouped by date, provider, and type
- **Field requirements**: What must be extracted vs. optional
- **Validation hints**: How to handle edge cases (dates, units, nulls)

When creating database tables:
1. Map schema fields to columns
2. Use VARCHAR for JSON storage (simple approach)
3. Include all required fields
4. Allow NULL for optional fields
5. Use appropriate data types (DATE, DECIMAL, VARCHAR)

## Design Decisions Documented

### Why Snowflake?
- ✅ Semantic model support (Cortex Analyst)
- ✅ Zero-operations (serverless)
- ✅ Excellent JSON handling
- ✅ Strong analytics capabilities

### Why Two Agents?
- ✅ Separation of concerns
- ✅ Specialization (extract vs analyze)
- ✅ Reusability
- ✅ Testability

### Why MCP?
- ✅ Standard agent ↔ tool protocol
- ✅ Works with Claude Desktop
- ✅ Type-safe tool definitions
- ✅ Easy to extend

### Why This Extraction Approach?
- ✅ Deterministic extraction (100% accuracy)
- ✅ Rule-based validation
- ✅ Clear audit trail
- ✅ Handles multiple PDF sources

## Questions I Expect You to Answer

When asking me to build something, please clarify:

1. **Which phase are we in?** (Foundation, Tools, Semantic, Query, Integration)
2. **What data sources?** (Apple Health, MyChart, Epic, etc.)
3. **What Snowflake setup?** (Account, credentials, warehouse)
4. **What's your timeline?** (To help prioritize)
5. **Any constraints?** (Budget, tools, preferences)

## Next Steps

1. ✅ You have the project structure
2. ✅ You have agent configurations
3. ✅ You have extraction schemas
4. 🔄 **Next**: Create Snowflake DDL schema
5. 🔄 **Then**: Build MCP import tool
6. 🔄 **Then**: Create semantic model
7. 🔄 **Then**: Build MCP query tool
8. 🔄 **Finally**: Integrate with Claude Desktop

---

**Design Philosophy**: Conservative, deterministic, testable, auditable, user-empowering.

**Key Principle**: With health data, accuracy is non-negotiable. Every decision is logged. Every process is validated.

**Last Updated**: February 12, 2026
