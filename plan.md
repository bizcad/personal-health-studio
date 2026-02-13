# Implementation Plan - Personal Health Studio

**Status**: Active  
**Phase**: Foundation (Database & Tools)  
**Target Date**: February 22, 2026  
**Deadline for Demo**: February 15, 2026 (Saturday evening)

## Executive Summary

This document outlines the implementation roadmap for the Personal Health Studio health intelligence system. The system extracts health data from PDF exports using a specialized agent, analyzes it using natural language queries in Snowflake, and provides actionable health insights to the user.

## Phase 1: Foundation (Database & Core Tools)

### Milestone 1.1: Snowflake Schema (Week 1)
- **Owner**: Claude Code
- **Deliverable**: health_intelligence_ddl.sql
- **Acceptance Criteria**:
  - [ ] Three tables: PATIENTS, HEALTH_RECORDS, IMPORTS
  - [ ] All required columns from extraction schemas
  - [ ] Foreign key relationships established
  - [ ] Data types validated for analytics
  - [ ] DDL passes Snowflake syntax validation
  - [ ] Column names avoid reserved words (no "NAME", "TYPE", "UNIT")

**Specification Reference**: 
- `requirements/technical/data-modeling-principles.md`
- `agents/extractor-agent/knowledge/*.json` (schemas)

**Inputs**: 
- Four extraction schemas (4 JSON files)
- Data modeling principles document

**Output**:
- `data-store/snowflake/ddl/health_intelligence_ddl.sql`
- `data-store/snowflake/scripts/verify_import.sql` (validation queries)

---

### Milestone 1.2: MCP Import Tool (Week 1-2)
- **Owner**: Claude Code
- **Deliverable**: health-mcp server with import capability
- **Acceptance Criteria**:
  - [ ] snowflake-connector-python works with credentials
  - [ ] snowflake_import_analyze_health_records_v2 tool defined
  - [ ] Tool accepts JSON files and loads into Snowflake
  - [ ] Import statistics captured (counts by type)
  - [ ] Error handling with clear messages
  - [ ] test_import.py validates the tool works
  -  [ ] Runs with `uv run test_import.py`

**Specification Reference**:
- `requirements/technical/mcp-tool-requirements.md`
- `agents/analyst-agent/config/agent-instructions.md`

**Components to Create**:
- `tools/health-mcp/pyproject.toml`
- `tools/health-mcp/src/health_mcp.py`
- `tools/health-mcp/test_import.py`

**Environment Variables Required**:
- SNOWFLAKE_USER
- SNOWFLAKE_ACCOUNT
- SNOWFLAKE_WAREHOUSE
- SNOWFLAKE_DATABASE
- SNOWFLAKE_ROLE
- SNOWFLAKE_PRIVATE_KEY_PATH

---

## Phase 2: Analytics Layer (Semantic Model)

### Milestone 2.1: Cortex Analyst Semantic Model (Week 2)
- **Owner**: Claude Code
- **Deliverable**: health_intelligence_semantic_model.yaml
- **Acceptance Criteria**:
  - [ ] All HEALTH_RECORDS columns mapped to semantic entities
  - [ ] Natural language mappings for common health questions
  - [ ] Metrics defined (averages, trends, correlations)
  - [ ] Relationships between entities established
  - [ ] YAML syntax validates
  - [ ] Can be uploaded to Snowflake RAW_DATA stage

**Common Health Questions to Support**:
- "What's my average blood glucose over the past year?"
- "Show me my cholesterol trend"
- "Which medications am I currently on?"
- "When was my last lab test?"
- "What conditions have I been diagnosed with?"
- "Are there any abnormal lab results?"

**Specification Reference**:
- `requirements/technical/cortex-analyst-semantic-model-requirements.txt`

**Output**:
- `semantic-model/snowflake/health_intelligence_semantic_model.yaml`

---

### Milestone 2.2: MCP Query Tool (Week 2-3)
- **Owner**: Claude Code
- **Deliverable**: Query tool for Cortex Analyst integration
- **Acceptance Criteria**:
  - [ ] execute_health_query_v2 tool added to health_mcp.py
  - [ ] Natural language → Cortex Analyst → JSON results pipeline
  - [ ] Handles common health questions
  - [ ] Error handling for invalid queries
  - [ ] Returns formatted, readable results
  - [ ] test_query.py validates tool works

**Output**:
- Updates to `tools/health-mcp/src/health_mcp.py`
- `tools/health-mcp/test_query.py`

---

## Phase 3: Integration

### Milestone 3.1: Claude Desktop Configuration (Week 3)
- **Owner**: User
- **Deliverable**: Configured claude_desktop_config.json
- **Acceptance Criteria**:
  - [ ] Config points to health-mcp server
  - [ ] All environment variables set
  - [ ] Analyst Agent has access to both tools
  - [ ] Can successfully import sample data
  - [ ] Can successfully query health data

---

### Milestone 3.2: End-to-End Testing (Week 3)
- **Owner**: User + Claude
- **Deliverable**: Tested health intelligence workflow
- **Acceptance Criteria**:
  - [ ] Extractor Agent successfully extracts from health PDF
  - [ ] JSON output valid and accurate
  - [ ] Analyst Agent imports JSON to Snowflake
  - [ ] Data visible in Snowflake tables
  - [ ] Natural language queries work
  - [ ] Can ask 5+ health questions successfully

---

## Phase 4: Demonstration Ready (Saturday Evening Target)

### Milestone 4.1: Sample Data & Documentation
- Working sample extraction showing 5-10 years of health data
- Configuration guide for friends
- Quick-start tutorial
- Troubleshooting guide

### Deliverables for Demo
- ✅ GitHub repo with full code
- ✅ README.md with quick start
- ✅ CLAUDE.md with system design
- ✅ Principles-and-Processes.md documenting approach
- ✅ Working database schema
- ✅ Working MCP tools
- ✅ Semantic model for health queries
- ✅ Sample health data extracted
- ✅ Queries working and returning insights
- ⏳ Configuration guide for friend setup
- ⏳ Visual dashboard (optional)

---

## Key Design Decisions

### Why This Phasing?
1. **Database first** - Everything depends on clear schema
2. **Import next** - Need to get data into Snowflake
3. **Semantic model** - Enables NL queries
4. **Query tool** - Uses semantic model to answer questions

### Why Two Separate Agents?
- **Extractor**: 100% fidelity extraction (deterministic)
- **Analyst**: Natural language analysis (probabilistic)
- Separation of concerns enables specialization

### Why Snowflake + Cortex Analyst?
- Semantic model = NL→SQL translation
- Zero-ops database (no maintenance)
- Strong analytics capabilities
- Works with Claude agents via MCP

### Why Conservative Extraction?
- Health data errors can lead to misdiagnosis
- Better to block ambiguous data than approximate
- Clear audit trail required for medical data

---

## Risk Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Snowflake connectivity issues | Low | High | Test early, use environment variables |
| Column name reserved word conflicts | Medium | Medium | Validate against data-modeling-principles |
| Extraction schema mismatches | Medium | High | Validate with sample PDFs early |
| Semantic model complexity | High | Medium | Keep simple, test incrementally |
| Permission/role issues | Medium | High | Document Snowflake setup upfront |

### Schedule Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Underestimating schema complexity | Medium | High | Start Week 1 immediately |
| Tool development delays | Medium | Medium | Use incremental development |
| Testing taking longer than expected | High | Medium | Start testing early, use sample data |

### User Adoption Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Complexity of setup | High | Provide clear configuration guide |
| Privacy concerns with cloud database | Medium | Show Snowflake is user-controlled, document security |

---

## Success Criteria

### By February 15 (Saturday Demo Target):
- [ ] Database schema created and tested
- [ ] Sample health data extracted (5+ years)
- [ ] Data successfully imported to Snowflake
- [ ] Natural language queries working
- [ ] Can answer 5+ health questions
- [ ] GitHub repo ready to share
- [ ] Documentation complete

### By February 22 (Extended Target):
- [ ] Friends' feedback incorporated
- [ ] Configuration guide written
- [ ] Sample PDFs processed successfully
- [ ] Query speed acceptable
- [ ] Error handling robust

---

## Architecture Overview

```
Health PDF Export (Apple Health, MyChart, etc.)
    ↓
[Extractor Agent]
    - Reads PDF
    - Validates against schemas
    - Extracts with 100% accuracy
    ↓
JSON Files (yearly, by type)
    ↓
[MCP Import Tool]
    - Snowflake_import_analyze_health_records_v2
    - Loads JSON to HEALTH_RECORDS table
    - Tracks import metadata
    ↓
Snowflake Database
    - PATIENTS (demographics)
    - HEALTH_RECORDS (all data)
    - IMPORTS (metadata)
    ↓
[Semantic Model - Cortex Analyst]
    - Maps NL to schema
    - Defines metrics
    - Enables query generation
    ↓
[MCP Query Tool]
    - execute_health_query_v2
    - Converts NL to SQL
    - Returns formatted results
    ↓
[Analyst Agent]
    - Interprets results
    - Generates insights
    - Creates visualizations
```

---

## Detailed Week-by-Week Schedule

### Week 1 (Feb 12-18) - Foundation
- **Mon-Tue**: Create Snowflake schema (DDL)
- **Tue-Wed**: Test schema with sample data
- **Wed-Thu**: Build MCP import tool
- **Thu-Fri**: Test import with sample data
- **Fri**: Review and document

### Week 2 (Feb 19-22 deadline approaches)  
- **Mon-Tue**: Create semantic model
- **Tue**: Build query tool
- **Tue-Wed**: Integration testing
- **Wed**: Documentation & configuration guide
- **Thu**: Friend setup walkthrough
- **Fri-Sat**: Demo preparation

### Saturday Evening (Feb 15/22): Demo Ready
- Show extraction working on real health PDF
- Display imported data in Snowflake
- Live natural language queries
- Explain architecture and replicability

---

## Technical Specifications

### Language & Tools
- **Python**: 3.10+ (type hints required)
- **Package Manager**: uv (not pip/poetry)
- **Database**: Snowflake (free tier acceptable)
- **MCP Server**: Python with @mcp.tool() decorator
- **Semantic Model**: YAML format for Cortex Analyst

### Branching Strategy
- `main` = production-ready code
- Work directly on main (personal project)
- Tag releases with semantic versioning (v1.0.0, etc.)

### Code Standards
- Full type hints on all functions
- Docstrings on all modules/functions
- Test scripts for all tools
- Clear error messages (why it failed, what to do)

### Documentation
- This plan.md (updated as phases complete)
- CLAUDE.md (design decisions)
- Principles-and-Processes.md (engineering standards)
- README.md (for downstream users)
- Inline code comments for complex logic

---

## Open Questions & Decisions Needed

1. **Snowflake Credentials**: Will you use service principal or user key?
2. **Data Import Frequency**: One-time import or ongoing updates?
3. **Visualization**: Use Snowflake dashboard or Claude-generated charts?
4. **Friends' Setup**: Will they use their own Snowflake or shared account?
5. **PDF Sources**: Starting with one source (Apple Health) or multiple?

---

## Next Steps (Immediate - This Week)

1. ✅ Repository structure created
2. ✅ Agent configurations in place
3. ✅ Extraction schemas defined
4. 🔄 **Snowflake account setup** (if needed)
5. 🔄 **Start Milestone 1.1** - Database schema
6. 🔄 **Gather sample health PDF** for testing

---

## Version History

- **v1.0** (Feb 12, 2026) - Initial plan created, targeting Feb 15 demo
- **v1.1** (Feb 12, 2026) - Refined milestones and schedule

---

**Owner**: Personal Health Studio Development Team  
**Last Updated**: February 12, 2026  
**Next Review**: February 15, 2026 (Post-Demo)
