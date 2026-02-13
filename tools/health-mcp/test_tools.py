#!/usr/bin/env python3
"""
Test Health MCP Tools
Tests import and query functionality against Snowflake
"""

import sys
import json
from datetime import date, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from health_models import (
    HealthRecord,
    RecordClass,
    VitalRecord,
    LabRecord,
    MedicationRecord,
)
from snowflake_client import SnowflakeClient


# Test configuration
SNOWFLAKE_CONFIG = {
    "account_id": "kgqnwwa-zxb81952",
    "username": "bizcad",
    "password": "ImFW3&Z&#9vUa9Mn",
    "warehouse": "COMPUTE_WH",
}

TEST_PATIENT = "test_import_patient_001"


def test_connection():
    """Test basic Snowflake connection"""
    print("\n" + "=" * 70)
    print("TEST 1: Snowflake Connection")
    print("=" * 70)
    
    try:
        client = SnowflakeClient(**SNOWFLAKE_CONFIG)
        
        if not client.connect():
            print("❌ FAILED: Could not connect to Snowflake")
            return False
        
        print("✓ Connected to Snowflake")
        
        # Verify database and schema
        result = client.execute_query(
            "SELECT CURRENT_DATABASE() as db, CURRENT_SCHEMA() as schema"
        )
        
        if result:
            db = result[0].get("DB")
            schema = result[0].get("SCHEMA")
            print(f"✓ Database: {db}")
            print(f"✓ Schema:   {schema}")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def test_import_health_records():
    """Test importing health records"""
    print("\n" + "=" * 70)
    print("TEST 2: Import Health Records")
    print("=" * 70)
    
    try:
        client = SnowflakeClient(**SNOWFLAKE_CONFIG)
        
        if not client.connect():
            print("❌ FAILED: Could not connect to Snowflake")
            return False
        
        # Create sample records
        today = date.today()
        
        records = [
            # Lab record
            HealthRecord(
                record_class=RecordClass.LAB,
                record_date=today - timedelta(days=5),
                patient_identity=TEST_PATIENT,
                provider_identity="Dr. John Smith",
                data={
                    "test_name": "Glucose, Fasting",
                    "result_value": "105 mg/dL",
                    "reference_range": "70-100 mg/dL",
                    "abnormal_flag": "HIGH",
                },
                extraction_confidence=0.95,
                source_document="test_import.pdf",
            ),
            # Vital record
            HealthRecord(
                record_class=RecordClass.VITAL,
                record_date=today - timedelta(days=3),
                patient_identity=TEST_PATIENT,
                provider_identity="RN Sarah Jones",
                data={
                    "vital_type": "BP",
                    "value": "125/82 mmHg",
                },
                extraction_confidence=0.98,
            ),
            # Medication record
            HealthRecord(
                record_class=RecordClass.MEDICATION,
                record_date=today,
                patient_identity=TEST_PATIENT,
                data={
                    "medication_name": "Metformin",
                    "dosage": "500 mg",
                    "frequency": "twice daily",
                    "status": "active",
                },
                extraction_confidence=0.90,
            ),
        ]
        
        print(f"Importing {len(records)} test records for patient: {TEST_PATIENT}")
        
        result = client.import_health_records(
            patient_identity=TEST_PATIENT,
            records=records,
            import_source="test_mcp_import",
        )
        
        if result["success"]:
            print(f"✓ Import successful")
            print(f"  Patient ID:      {result['patient_id']}")
            print(f"  Import ID:       {result['import_id']}")
            print(f"  Records inserted: {result['records_inserted']}")
            print(f"  Records failed:   {result['records_failed']}")
            print(f"  Types: {result['record_types']}")
        else:
            print(f"⚠ Import completed with issues")
            print(f"  Records inserted: {result['records_inserted']}")
            print(f"  Records failed:   {result['records_failed']}")
        
        client.disconnect()
        return result["success"] or result["records_inserted"] > 0
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_query_health_records():
    """Test querying health records"""
    print("\n" + "=" * 70)
    print("TEST 3: Query Health Records")
    print("=" * 70)
    
    try:
        client = SnowflakeClient(**SNOWFLAKE_CONFIG)
        
        if not client.connect():
            print("❌ FAILED: Could not connect to Snowflake")
            return False
        
        # Test different query types
        query_types = [
            ("all_records", "All records for patient"),
            ("labs_recent", "Recent lab results"),
            ("medications_active", "Active medications"),
        ]
        
        all_results = {}
        for query_type, description in query_types:
            print(f"\nQuery: {query_type}")
            print(f"  ({description})")
            
            try:
                kwargs = {}
                if query_type == "labs_recent":
                    kwargs["parameters"] = {"limit": 5}
                
                results = client.query_health_data(
                    patient_identity=TEST_PATIENT,
                    query_type=query_type,
                    **kwargs
                )
                
                all_results[query_type] = len(results)
                
                if results:
                    print(f"  ✓ Found {len(results)} records")
                else:
                    print(f"  ⚠ No records found")
                    
            except Exception as e:
                print(f"  ❌ Query failed: {e}")
        
        client.disconnect()
        
        # Return success if we got any results
        total_results = sum(all_results.values())
        if total_results > 0:
            print(f"\n✓ Query tests completed. Total results: {total_results}")
            return True
        else:
            print(f"\n⚠ No results found in any query")
            return False
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_validation():
    """Test Pydantic model validation"""
    print("\n" + "=" * 70)
    print("TEST 4: Model Validation")
    print("=" * 70)
    
    try:
        # Test valid record
        record = HealthRecord(
            record_class=RecordClass.LAB,
            record_date=date.today(),
            patient_identity="Test Patient",
            data={
                "test_name": "Cholesterol Panel",
                "result_value": "180 mg/dL",
            }
        )
        print("✓ Valid HealthRecord created")
        print(f"  Class: {record.record_class}")
        print(f"  Date:  {record.record_date}")
        
        # Test invalid record (missing required field)
        try:
            invalid_record = HealthRecord(
                record_class=RecordClass.LAB,
                patient_identity="Test Patient",
                # Missing record_date
                data={}
            )
            print("❌ FAILED: Invalid record should have been rejected")
            return False
        except Exception as e:
            print("✓ Invalid record properly rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("HEALTH MCP TOOLS TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Connection", test_connection),
        ("Model Validation", test_model_validation),
        ("Import Records", test_import_health_records),
        ("Query Records", test_query_health_records),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test {test_name} crashed: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_flag in results.items():
        status = "✓ PASS" if passed_flag else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
