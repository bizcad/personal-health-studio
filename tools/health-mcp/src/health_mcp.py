#!/usr/bin/env python3
"""
Health Intelligence MCP Server
Provides Model Context Protocol tools for health data import and querying
"""

import json
import os
import sys
from typing import Any

# MCP Server SDK
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool
from mcp.server import Server
import mcp.types as types

from health_models import (
    HealthRecord, 
    RecordClass, 
    HealthImportRequest,
    HealthQueryRequest,
    VitalRecord,
    LabRecord,
    MedicationRecord,
)
from snowflake_client import SnowflakeClient


# Initialize MCP Server
server = Server("health-intelligence")

# Snowflake configuration (from environment or defaults)
SNOWFLAKE_CONFIG = {
    "account_id": os.getenv("SNOWFLAKE_ACCOUNT", "kgqnwwa-zxb81952"),
    "username": os.getenv("SNOWFLAKE_USER", "bizcad"),
    "password": os.getenv("SNOWFLAKE_PASSWORD", os.getenv("SF_PASSWORD", "ImFW3&Z&#9vUa9Mn")),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
    "database": os.getenv("SNOWFLAKE_DATABASE", "HEALTH_INTELLIGENCE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA", "HEALTH_RECORDS"),
}

# Global Snowflake client (initialized on first request)
_snowflake_client: SnowflakeClient = None


def get_snowflake_client() -> SnowflakeClient:
    """Get or initialize Snowflake client"""
    global _snowflake_client
    
    if _snowflake_client is None:
        _snowflake_client = SnowflakeClient(**SNOWFLAKE_CONFIG)
        if not _snowflake_client.connect():
            raise RuntimeError("Failed to connect to Snowflake")
    
    return _snowflake_client


# ============================================================================
# TOOL 1: IMPORT HEALTH DATA
# ============================================================================

@server.call_tool()
async def handle_import_health_data(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Import health records into Snowflake from JSON
    
    This tool accepts structured health records and imports them into the
    Health Intelligence database.
    """
    if name != "import_health_data":
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        # Parse request
        patient_identity = arguments.get("patient_identity")
        records_json = arguments.get("records")
        import_source = arguments.get("import_source", "mcp_import")
        
        if not patient_identity:
            return [types.TextContent(
                type="text",
                text="ERROR: patient_identity is required"
            )]
        
        if not records_json:
            return [types.TextContent(
                type="text",
                text="ERROR: records is required"
            )]
        
        # Parse records (may be JSON string or list)
        if isinstance(records_json, str):
            records_data = json.loads(records_json)
        else:
            records_data = records_json
        
        if not isinstance(records_data, list):
            records_data = [records_data]
        
        # Convert to HealthRecord objects
        records = []
        for record_data in records_data:
            try:
                record = HealthRecord(**record_data)
                records.append(record)
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"ERROR parsing record: {str(e)}"
                )]
        
        # Import to Snowflake
        client = get_snowflake_client()
        
        import_stats = {
            "total_records": len(records),
            "import_timestamp": str(os.popen('date /t').read()),
            "source": import_source,
        }
        
        result = client.import_health_records(
            patient_identity=patient_identity,
            records=records,
            import_source=import_source,
            import_stats=import_stats,
        )
        
        response = f"""
✓ Health data imported successfully!

Patient ID:          {result['patient_id']}
Import ID:           {result['import_id']}
Records Inserted:    {result['records_inserted']}
Records Failed:      {result['records_failed']}

Record Types:
{chr(10).join(f"  - {k}: {v}" for k, v in result['record_types'].items())}

Status: {result['success']}
"""
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        error_msg = f"ERROR in import_health_data: {str(e)}"
        print(error_msg, file=sys.stderr)
        return [types.TextContent(type="text", text=error_msg)]


# ============================================================================
# TOOL 2: QUERY HEALTH DATA
# ============================================================================

@server.call_tool()
async def handle_query_health_data(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Query health records with natural language or structured queries
    
    This tool allows querying imported health data using predefined
    query patterns or natural language interpretation.
    """
    if name != "query_health_data":
        raise ValueError(f"Unknown tool: {name}")
    
    try:
        # Parse request
        patient_identity = arguments.get("patient_identity")
        query_type = arguments.get("query_type", "all_records")
        query_params = arguments.get("parameters", {})
        
        if not patient_identity:
            return [types.TextContent(
                type="text",
                text="ERROR: patient_identity is required"
            )]
        
        # Query Snowflake
        client = get_snowflake_client()
        results = client.query_health_data(
            patient_identity=patient_identity,
            query_type=query_type,
            parameters=query_params,
        )
        
        # Format results
        if not results:
            response = f"No records found for patient: {patient_identity}"
        else:
            # Format as readable table
            response = f"Query Results ({len(results)} records):\n\n"
            for i, row in enumerate(results, 1):
                response += f"{i}. {json.dumps(row, indent=2)}\n\n"
        
        return [types.TextContent(type="text", text=response)]
        
    except Exception as e:
        error_msg = f"ERROR in query_health_data: {str(e)}"
        print(error_msg, file=sys.stderr)
        return [types.TextContent(type="text", text=error_msg)]


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    
    return [
        Tool(
            name="import_health_data",
            description="Import health records into Snowflake database",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_identity": {
                        "type": "string",
                        "description": "Patient name or identifier",
                    },
                    "records": {
                        "type": "array",
                        "description": "Array of health records in HealthRecord format",
                        "items": {
                            "type": "object",
                            "properties": {
                                "record_class": {
                                    "type": "string",
                                    "enum": ["LAB", "VITAL", "MEDICATION", "CONDITION", "ALLERGY", "IMMUNIZATION"],
                                    "description": "Type of health record",
                                },
                                "record_date": {
                                    "type": "string",
                                    "description": "Date of record (YYYY-MM-DD)",
                                },
                                "data": {
                                    "type": "object",
                                    "description": "Structured data depending on record_class",
                                },
                                "provider_identity": {
                                    "type": "string",
                                    "description": "Provider name (optional)",
                                },
                                "extraction_confidence": {
                                    "type": "number",
                                    "description": "Confidence score 0-1 (optional)",
                                },
                            },
                            "required": ["record_class", "record_date", "data"],
                        },
                    },
                    "import_source": {
                        "type": "string",
                        "description": "Source of data (e.g., 'pdf_extraction', 'api')",
                    },
                },
                "required": ["patient_identity", "records"],
            },
        ),
        Tool(
            name="query_health_data",
            description="Query health records using predefined query patterns",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_identity": {
                        "type": "string",
                        "description": "Patient name or identifier",
                    },
                    "query_type": {
                        "type": "string",
                        "enum": [
                            "all_records",
                            "labs_recent",
                            "medications_active",
                            "vitals_by_type",
                            "abnormal_labs",
                        ],
                        "description": "Type of query to execute",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Query-specific parameters (e.g., limit, vital_type)",
                    },
                },
                "required": ["patient_identity", "query_type"],
            },
        ),
    ]


@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """List available resources"""
    return []


# ============================================================================
# SERVER LIFECYCLE
# ============================================================================

@server.connect()
async def on_connect():
    """Called when client connects"""
    print("✓ Health Intelligence MCP Server connected")


async def main():
    """Run the MCP server"""
    async with server:
        print("🏥 Health Intelligence MCP Server starting...")
        print(f"   Account:  {SNOWFLAKE_CONFIG['account_id']}")
        print(f"   Database: {SNOWFLAKE_CONFIG['database']}")
        print(f"   Schema:   {SNOWFLAKE_CONFIG['schema']}")
        print("\n✓ Server ready. Waiting for connections...\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
