# MCP Tool Requirements - Health Intelligence

This document specifies the MCP (Model Context Protocol) tools required for the Health Intelligence System.

## Overview

MCP tools enable Claude agents to interact with external systems. For this project, we need two tools:

1. **snowflake_import_analyze_health_records_v2** - Import JSON health data into Snowflake
2. **execute_health_query_v2** - Run natural language queries against health data

## Project Structure

```
tools/health-mcp/
├── pyproject.toml          # Python project metadata and dependencies
├── src/
│   └── health_mcp.py       # MCP server with tool implementations
├── test_import.py          # Test script for import functionality
└── test_query.py           # Test script for query functionality
```

## pyproject.toml Configuration

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "health-mcp"
version = "0.1.0"
description = "MCP tools for Health Intelligence System"
requires-python = ">=3.10"
dependencies = [
    "mcp>=1.0.0",
    "snowflake-connector-python>=3.0.0",
    "cryptography>=42.0.0",
    "python-dateutil>=2.8.0",
    "requests>=2.31.0",
    "PyJWT>=2.8.0"
]

[tool.hatch.build.targets.wheel]
packages = ["src"]
```

**Key**: The `[tool.hatch.build.targets.wheel]` section tells hatchling where to find the package source.

## MCP Server Template

```python
"""Health MCP Server - Data import and query tools for Snowflake.

This module implements MCP tools for the Health Intelligence System:
- snowflake_import_analyze_health_records_v2: Import health JSON data
- execute_health_query_v2: Query health data via natural language
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import mcp.server.stdio
from mcp.types import Tool, TextContent, ToolResult
import snowflake.connector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ImportResult:
    """Result of health data import operation."""
    success: bool
    records_imported: int
    records_by_type: dict
    error_message: Optional[str] = None
    import_id: Optional[str] = None


class HealthMCPServer:
    """MCP server for health data operations."""
    
    def __init__(self):
        self.server = mcp.server.stdio.StdioServer(
            logging=logging.getLogger(__name__)
        )
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Register MCP tool handlers."""
        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict) -> ToolResult:
            if name == "snowflake_import_analyze_health_records_v2":
                return await self._import_health_records(
                    arguments.get("patient_name"),
                    arguments.get("date_of_birth"),
                    arguments.get("json_file_paths", [])
                )
            elif name == "execute_health_query_v2":
                return await self._execute_query(arguments.get("natural_language_query"))
            else:
                return ToolResult(
                    content=[TextContent(text=f"Unknown tool: {name}")],
                    isError=True
                )
    
    async def _import_health_records(
        self,
        patient_name: str,
        date_of_birth: str,
        json_file_paths: list[str]
    ) -> ToolResult:
        """Import health JSON files into Snowflake."""
        try:
            # Load and parse JSON files
            records = self._parse_json_files(json_file_paths)
            
            # Connect to Snowflake
            conn = self._get_snowflake_connection()
            
            # Insert data
            result = self._insert_records(conn, patient_name, date_of_birth, records)
            
            conn.close()
            
            # Return summary
            summary = f"""
            ✅ Data Import Successful
            
            Patient: {patient_name}
            DOB: {date_of_birth}
            Records Imported: {result.records_imported}
            
            Breakdown by Type:
            {self._format_counts(result.records_by_type)}
            
            Import ID: {result.import_id}
            """
            
            return ToolResult(
                content=[TextContent(text=summary)],
                isError=False
            )
            
        except Exception as e:
            logger.error(f"Import failed: {e}")
            return ToolResult(
                content=[TextContent(text=f"❌ Import Error: {str(e)}")],
                isError=True
            )
    
    async def _execute_query(self, query: str) -> ToolResult:
        """Execute natural language query against health data."""
        try:
            # Connect to Snowflake
            conn = self._get_snowflake_connection()
            
            # TODO: Implement Cortex Analyst integration for NL→SQL
            # For now, return template
            
            result = f"Running query: {query}"
            
            conn.close()
            
            return ToolResult(
                content=[TextContent(text=result)],
                isError=False
            )
            
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return ToolResult(
                content=[TextContent(text=f"❌ Query Error: {str(e)}")],
                isError=True
            )
    
    def _get_snowflake_connection(self):
        """Create Snowflake connection using environment variables."""
        # Configuration from environment
        return snowflake.connector.connect(
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            user=os.getenv("SNOWFLAKE_USER"),
            private_key_path=os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
    
    def _parse_json_files(self, file_paths: list[str]) -> dict:
        """Parse JSON files and consolidate records."""
        all_records = {
            "LAB": [],
            "VITAL": [],
            "MEDICATION": [],
            "CLINICAL": []
        }
        
        for file_path in file_paths:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Parse and categorize records
                ...
        
        return all_records
    
    def _insert_records(self, conn, patient_name: str, dob: str, records: dict):
        """Insert records into Snowflake."""
        # Implementation
        pass
    
    def _format_counts(self, counts: dict) -> str:
        """Format record counts for display."""
        lines = [f"  {k}: {v}" for k, v in counts.items() if v > 0]
        return "\n".join(lines)


async def main():
    """Run the MCP server."""
    server = HealthMCPServer()
    async with server.server:
        logger.info("Health MCP Server started")
        await server.server.wait_for_exit()


if __name__ == "__main__":
    import asyncio
    import os
    asyncio.run(main())
```

## Tool Definitions

### Tool 1: snowflake_import_analyze_health_records_v2

**Purpose**: Import extracted health JSON files into Snowflake

**Input Parameters**:
- `patient_name` (string, required): Patient name
- `date_of_birth` (string, required): DOB in YYYY-MM-DD format
- `json_file_paths` (array, required): List of extracted JSON file paths

**Output**:
- Summary of records imported
- Count by data type (labs, vitals, medications, clinical)
- Import ID for reference
- Any errors or warnings

**Example**:
```json
{
  "tool": "snowflake_import_analyze_health_records_v2",
  "arguments": {
    "patient_name": "John Doe",
    "date_of_birth": "1980-03-26",
    "json_file_paths": [
      "/data/lab_results_2024.json",
      "/data/vitals_2024.json",
      "/data/medications.json"
    ]
  }
}
```

### Tool 2: execute_health_query_v2

**Purpose**: Execute natural language queries against health data

**Input Parameters**:
- `natural_language_query` (string, required): User's health question

**Output**:
- Query results in formatted table/JSON
- Supporting insights or patterns found
- Confidence level if applicable
- Error message if query fails

**Example**:
```json
{
  "tool": "execute_health_query_v2",
  "arguments": {
    "natural_language_query": "What's my cholesterol trend over the past 5 years?"
  }
}
```

## Environment Variables Required

| Variable | Value | Example |
|----------|-------|---------|
| SNOWFLAKE_ACCOUNT | Account ID | xy12345.us-east-1 |
| SNOWFLAKE_USER | Username | user@company.com |
| SNOWFLAKE_WAREHOUSE | Warehouse name | COMPUTE_WH |
| SNOWFLAKE_DATABASE | Database | HEALTH_INTELLIGENCE |
| SNOWFLAKE_SCHEMA | Schema | HEALTH_RECORDS |
| SNOWFLAKE_ROLE | Role | ACCOUNTADMIN |
| SNOWFLAKE_PRIVATE_KEY_PATH | Path to RSA key | /path/to/rsa_key.p8 |

## Package Management with uv

```bash
# Install dependencies
cd tools/health-mcp
uv sync

# Run server
uv run src/health_mcp.py

# Run import test
uv run test_import.py

# Run query test
uv run test_query.py
```

## Claude Desktop Configuration

In `~/.claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "health-intelligence": {
      "command": "/path/to/.local/bin/uv",
      "args": [
        "--directory",
        "/path/to/tools/health-mcp",
        "run",
        "src/health_mcp.py"
      ],
      "env": {
        "SNOWFLAKE_ACCOUNT": "...",
        "SNOWFLAKE_USER": "...",
        "SNOWFLAKE_PRIVATE_KEY_PATH": "...",
        "SNOWFLAKE_WAREHOUSE": "COMPUTE_WH",
        "SNOWFLAKE_DATABASE": "HEALTH_INTELLIGENCE",
        "SNOWFLAKE_SCHEMA": "HEALTH_RECORDS",
        "SNOWFLAKE_ROLE": "ACCOUNTADMIN"
      }
    }
  }
}
```

## Error Handling

All tool responses should include:

- **Success case**: Clear summary of what was done
- **Error case**: Specific error message and recovery steps

Example error response:
```
❌ Import Error: Patient 'John Doe' not found in PATIENTS table.

Action: Either:
1. Create patient record first: INSERT INTO PATIENTS...
2. Check patient name spelling
3. Verify database connection
```

## Testing

Create `test_import.py`:
```python
# Test importing sample JSON files
import subprocess
import json

sample_data = {
    "header_fields": {...},
    "Lab_Results": [...]
}

result = subprocess.run([
    "python", "src/health_mcp.py"
], capture_output=True)

assert result.returncode == 0
print("✅ Import test passed")
```

---

**Reference**: Pattern from original `multi-agent-health-insight-system` MCP server implementation.
