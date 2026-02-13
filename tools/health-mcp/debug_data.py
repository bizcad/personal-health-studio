#!/usr/bin/env python3
"""Debug script to see what data is in Snowflake"""

import sys
sys.path.insert(0, 'src')

from snowflake_client import SnowflakeClient
import json

# Initialize Snowflake client
client = SnowflakeClient(
    account_id="kgqnwwa-zxb81952",
    username="bizcad",
    password="ImFW3&Z&#9vUa9Mn",
    warehouse="COMPUTE_WH"
)

# Connect to Snowflake
if not client.connect():
    print("Failed to connect to Snowflake")
    sys.exit(1)

print("Connected to Snowflake!")
print("\n" + "="*80)
print("SAMPLE LAB RECORDS (first 3)")
print("="*80)

# Query for LAB records
query = """
SELECT record_class, data_json, extraction_confidence
FROM HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS
WHERE record_class = 'LAB'
LIMIT 3
"""

results = client.execute_query(query)
for i, result in enumerate(results, 1):
    print(f"\nRecord {i}:")
    print(f"  Class: {result.get('RECORD_CLASS')}")
    try:
        data = json.loads(result.get('DATA_JSON', '{}'))
        print(f"  Data: {json.dumps(data, indent=4)}")
    except:
        print(f"  Data: {result.get('DATA_JSON')}")
    print(f"  Confidence: {result.get('EXTRACTION_CONFIDENCE')}")

print("\n" + "="*80)
print("TEST GLUCOSE AVERAGE QUERY")
print("="*80)

# Test the glucose average query
glucose_query = """
SELECT 
    AVG(TRY_CAST(SPLIT_PART(TRY_PARSE_JSON(data_json):result_value::STRING, ' ', 1) AS FLOAT)) as result_average,
    COUNT(*) as record_count
FROM HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS
WHERE patient_id = (
    SELECT patient_id FROM PATIENTS WHERE patient_identity LIKE 'demo_test_%@example.com' LIMIT 1
)
AND record_class = 'LAB'
AND data_json ILIKE '%glucose%'
"""

print(f"\nQuery:\n{glucose_query}\n")
try:
    results = client.execute_query(glucose_query)
    print(f"Results: {results}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("ALL LAB RECORDS FOR CURRENT PATIENT")
print("="*80)

all_labs = """
SELECT data_json
FROM HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS
WHERE patient_id = (
    SELECT patient_id FROM PATIENTS WHERE patient_identity LIKE 'demo_test_%@example.com' LIMIT 1
)
AND record_class = 'LAB'
"""

try:
    results = client.execute_query(all_labs)
    print(f"Total LAB records: {len(results)}\n")
    for i, result in enumerate(results[:5], 1):
        try:
            data = json.loads(result.get('DATA_JSON', '{}'))
            print(f"{i}. {json.dumps(data)}")
        except:
            print(f"{i}. {result.get('DATA_JSON')}")
except Exception as e:
    print(f"Error: {e}")

client.disconnect()
