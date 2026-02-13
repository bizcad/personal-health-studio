# Principles and Processes - Personal Health Studio

**Version**: 1.0  
**Last Updated**: February 12, 2026  
**Status**: Active (Living Document)

## Core Engineering Principles

### 1. Zero-Tolerance Accuracy (For Health Data)

**"Health data must be extracted exactly as it appears in source documents."**

- Every value extracted must match the source with 100% fidelity
- No rounding, approximation, or intelligent "correction"
- Missing values are recorded as missing, not estimated
- Unit conversions are done precisely (specified decimal places)
- Extraction errors block the entire operation (fail-safe)

**Why**: Medical data drives clinical decisions. Inaccurate extraction could lead to misdiagnosis or treatment errors.

### 2. Conservative Defaults (Fail-Safe By Design)

**"If in doubt, block and report."**

- Default behavior rejects ambiguous data
- Operators must explicitly override safety checks
- Better to reject a valid record than accept an invalid one
- Every block action is logged with the reason
- Users always know why an operation was rejected

**Application Scope**:
- Data validation (missing required fields → reject)
- Provider identification (unknown provider → block and ask)
- Date parsing (ambiguous dates → ask user to clarify)
- Unit conversion (missing unit → reject)

### 3. Deterministic Extraction, Probabilistic Analysis

**Extraction Layer** (deterministic):
- Schema validation
- Unit conversion
- Date formatting
- Data type checking
- **These always produce the same output for the same input**
- **No ML, no guessing, no approximation**

**Analysis Layer** (probabilistic):
- Claude generates insights from structured data
- Natural language querying via Cortex Analyst
- Trend analysis and correlation detection
- **These may vary; confidence scores reflect uncertainty**
- **Claude thinks; extraction validates**

**Design Pattern**:
```
Raw PDF → Extract (Deterministic) → JSON → Analyze (Probabilistic) → Insights
                    ↓                           ↓
              100% Accuracy               Confidence Scores
              Clear Audit Trail           Reasoning Preserved
```

### 4. Data Integrity First

**All processing assumes this priority order:**

1. **Accuracy** - Does the result match the source exactly?
2. **Completeness** - Is all required data present?
3. **Validity** - Does the data pass type and value checks?
4. **Usefulness** - Can the data be analyzed effectively?

**Never trade accuracy for convenience.**

### 5. Clear Communication & Logging

**Every operation reports:**

- ✅ **What was done** - Specific action taken
- 📊 **How much was processed** - Records created, skipped, rejected
- ❌ **What went wrong** (if anything) - Specific errors with context
- 🔧 **What to do next** - Clear next steps for user
- 🔐 **Audit trail** - Who, what, when, why

**Log Format**:
```
[TIMESTAMP] [LEVEL] [COMPONENT] [ACTION]
- What: [specific operation]
- Status: [success/warning/error]
- Count: [records affected]
- Details: [specific values or errors]
- Next: [what user should do]
```

### 6. Transparent Error Handling

**Error Hierarchy** (most to least severe):

1. **Data Integrity Violation** → Hard block, no retry, alert immediately
   - Missing required field
   - Value outside valid range
   - Invalid date format
   
2. **Extraction Accuracy Loss** → Block extraction, ask user
   - Ambiguous provider name
   - Date in ambiguous format
   - Unit conversion needed but unit missing

3. **Processing Error** → Continue with logging
   - Partial JSON parsing
   - Missing optional fields
   - Reference range not found

4. **Validation Warning** → Log and continue
   - Unusual value (within range but unexpected)
   - New provider encountered
   - Data format variant

### 7. User Empowerment

**Users always know:**

- What data is being extracted
- Why specific records are rejected
- How to provide additional information
- What the system is capable of
- How to review and validate results

**Design Pattern**: Report first, block only if necessary, provide clear recovery paths.

### 8. Security & Privacy (By Design)

- Health data never enters external services
- All processing is local or in user's Snowflake instance
- No data caching or logging of sensitive values
- Full audit trail maintained
- User controls all data movement

## Software Engineering Standards

### Code Quality

Every Python file MUST include:

```python
"""Module docstring explaining purpose and design."""

from __future__ import annotations  # PEP 563: modern type hints

from dataclasses import dataclass
from typing import Optional
from datetime import date

@dataclass
class ExtractionResult:
    """Result of health data extraction."""
    
    patient_name: str
    date_of_birth: date
    records_extracted: int
    errors: list[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

def extract_health_data(
    pdf_path: str,
    schema: dict,
    strict_mode: bool = True
) -> ExtractionResult:
    """Extract health data from PDF following schema.
    
    Args:
        pdf_path: Path to health PDF file
        schema: JSON schema for extraction
        strict_mode: If True, reject ambiguous data
        
    Returns:
        ExtractionResult with extracted data and any errors
        
    Raises:
        FileNotFoundError: If PDF not found
        ValueError: If schema is invalid
    """
    # Implementation
    pass
```

### Testing

- All extraction logic has unit tests
- All schemas validated against sample data
- All date formats and unit conversions tested
- Error cases tested explicitly

### Documentation

- Purpose statement in every module
- Docstrings on every public function
- Design decisions documented in comments
- Examples provided for typical usage
- Edge cases called out explicitly

### Validation

- Input validation (before processing)
- Schema validation (during extraction)
- Output validation (before storing)
- Cross-validation (results match source)

## Health Data Specifics

### Accuracy Standards

| Data Type | Accuracy | Example |
|-----------|----------|---------|
| Lab Values | Exact | "98 mg/dL" not "~100" |
| Dates | ISO 8601 | "2025-04-07" not "4/7/25" |
| Units | Precise | "5 mg" with unit, not just "5" |
| Vitals | US Standard | "185.5 lb" not "84.4 kg" |
| Reference Ranges | Preserved | "74 to 109 mg/dL" as-is |

### Data Categories

The system handles four health data categories:

1. **Lab Results** - Test names, values, units, reference ranges, dates
2. **Vitals** - Blood pressure, weight, height, temperature, pulse
3. **Medications** - Names, dosages, frequency, conditions, dates
4. **Clinical Data** - Conditions, allergies, immunizations, procedures

Each has a defined extraction schema (see agents/extractor-agent/knowledge/)

### Provider Mapping

Standardize provider names from source documents:
- Apple Health may show different provider names for the same provider
- Consolidate to canonical names
- Document provider name mappings
- Create provider lookup table

## Workflow Integration

### Extraction Workflow

```
1. Receive PDF
2. Validate PDF format
3. Scan all pages (identify sections)
4. Extract using schemas
5. Validate extracted data
6. Report results (with errors if any)
7. Store in JSON format
8. Hand off to analyst
```

### Analysis Workflow

```
1. Receive extracted JSON
2. Validate schema compliance
3. Load to Snowflake
4. Create import record
5. Validate data loaded correctly
6. Create semantic model mappings
7. Enable natural language queries
8. Provide visualization framework
```

## Decision Log

Document all significant decisions with:

- **Decision**: What was decided
- **Context**: Why this was important
- **Alternatives**: What else was considered
- **Rationale**: Why this was preferred
- **Constraints**: What limits the decision
- **Potential Issues**: What could go wrong

**Example**:
```
Decision: Use unified HEALTH_RECORDS table instead of separate tables

Context: Need to simplify NL→SQL query generation for Cortex Analyst

Alternatives:
  - Separate tables per data type (LABS, VITALS, MEDS, CLINICAL)
  - Normalized schema with fact/dimension tables
  - NoSQL document store

Rationale:
  - Fewer tables = simpler Cortex Analyst mappings
  - Discriminator column (record_type) provides clarity
  - Single-table scans faster than complex joins
  - Easier to add new data types

Constraints:
  - Cannot use "NAME" or "TYPE" in column names (Cortex issue)
  - All optional fields must be NULL, not omitted

Potential Issues:
  - Very large HEALTH_RECORDS table may need partitioning
  - Queries with multiple record types may be slower
  - Need to validate record_type values
```

## Process Improvements

This document is a living document. Updates should:

1. Be documented with rationale
2. Reference specific examples
3. Update version number
4. Note date of change
5. Explain impact on existing code

## Summary

The Personal Health Studio is built on these foundations:

| Principle | Application | Why |
|-----------|-------------|-----|
| Accuracy | Exact data extraction | Health decisions depend on accuracy |
| Safety | Conservative defaults | Block risky operations by default |
| Clarity | Transparent logging | Users must understand what happened |
| Validation | Multi-layer checking | Catch errors early |
| Determinism | Rule-based extraction | Reproduci ble, testable results |
| Documentation | Comprehensive guides | Health data is sensitive |
| Privacy | Local-first processing | Users control their data |

---

**Next Review**: April 12, 2026  
**Maintainer**: Personal Health Studio Team
