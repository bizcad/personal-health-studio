#!/usr/bin/env python3
"""
Test Semantic Query Executor
Tests natural language query parsing and execution
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from nl_mapper import NLMapper, RecordType, nl_to_sql
from snowflake_client import SnowflakeClient
from semantic_query_executor import SemanticQueryExecutor


SNOWFLAKE_CONFIG = {
    "account_id": "kgqnwwa-zxb81952",
    "username": "bizcad",
    "password": "ImFW3&Z&#9vUa9Mn",
    "warehouse": "COMPUTE_WH",
}


def test_nl_intent_parsing():
    """Test natural language intent parsing"""
    print("\n" + "=" * 70)
    print("TEST 1: Natural Language Intent Parsing")
    print("=" * 70)
    
    mapper = NLMapper()
    
    test_queries = [
        "What was my average blood glucose last year?",
        "How many active medications do I have?",
        "Show me my blood pressure readings from the last 30 days",
        "List all abnormal lab results",
        "What is my latest cholesterol level?",
        "Tell me about recent doctor visits",
        "Do I have any drug allergies?",
    ]
    
    all_passed = True
    for query in test_queries:
        try:
            intent = mapper.parse_intent(query)
            
            print(f"\n✓ Query: {query}")
            print(f"  Type:      {intent.record_type}")
            print(f"  Metric:    {intent.metric}")
            print(f"  Attribute: {intent.attribute}")
            print(f"  Time:      {intent.time_period}")
            print(f"  Filter:    {intent.filter_condition}")
            
        except Exception as e:
            print(f"\n❌ Query: {query}")
            print(f"  ERROR: {e}")
            all_passed = False
    
    return all_passed


def test_nl_to_sql_mapping():
    """Test NL to SQL conversion"""
    print("\n" + "=" * 70)
    print("TEST 2: Natural Language to SQL Mapping")
    print("=" * 70)
    
    test_cases = [
        (
            "What was my average blood glucose last year?",
            {
                "record_type": RecordType.LAB,
                "metric": "average",
                "attribute": "glucose",
                "time_period": "last year",
            }
        ),
        (
            "How many active medications do I take?",
            {
                "record_type": RecordType.MEDICATION,
                "metric": "count",
                "filter_condition": "active",
            }
        ),
        (
            "Show me recent vital signs",
            {
                "record_type": RecordType.VITAL,
                "metric": "list",
                "filter_condition": "recent",
            }
        ),
    ]
    
    all_passed = True
    
    for query, expected_intent in test_cases:
        try:
            intent, sql = nl_to_sql(query, patient_id=1)
            
            # Check that SQL was generated
            if not sql or "SELECT" not in sql:
                print(f"\n❌ Query: {query}")
                print(f"  ERROR: Invalid SQL generated")
                all_passed = False
                continue
            
            print(f"\n✓ Query: {query}")
            print(f"  SQL Generated: {sql[:100]}...")
            
            # Validate intent matches expected
            for key, expected_value in expected_intent.items():
                intent_value = getattr(intent, key)
                if intent_value == expected_value:
                    print(f"  ✓ {key}: {intent_value}")
                else:
                    print(f"  ⚠ {key}: {intent_value} (expected {expected_value})")
            
        except Exception as e:
            print(f"\n❌ Query: {query}")
            print(f"  ERROR: {e}")
            all_passed = False
    
    return all_passed


def test_semantic_query_executor():
    """Test semantic query executor against real data"""
    print("\n" + "=" * 70)
    print("TEST 3: Semantic Query Executor")
    print("=" * 70)
    
    try:
        # Connect to Snowflake
        client = SnowflakeClient(**SNOWFLAKE_CONFIG)
        if not client.connect():
            print("❌ FAILED: Could not connect to Snowflake")
            return False
        
        print("✓ Connected to Snowflake")
        
        # Create executor
        executor = SemanticQueryExecutor(client)
        
        # Test queries
        test_patient = "test_import_patient_001"
        test_queries = [
            "How many lab tests do I have?",
            "Show me all my medications",
            "What was my average blood glucose?",
            "List my vital signs from the last month",
        ]
        
        for query in test_queries:
            print(f"\n  Query: {query}")
            
            try:
                result = executor.query(test_patient, query)
                
                if result.get("success"):
                    print(f"    ✓ Result: {result.get('record_count')} records")
                    
                    # Show insights
                    for insight in result.get("insights", [])[:3]:
                        print(f"      - {insight['title']}")
                else:
                    print(f"    ⚠ Query failed: {result.get('error')}")
                    
            except Exception as e:
                print(f"    ❌ ERROR: {e}")
        
        # Test trend analysis
        print(f"\n  Trend Analysis: glucose over last 90 days")
        try:
            trend_result = executor.get_trend(test_patient, "glucose", days=90)
            
            if trend_result.get("success"):
                stats = trend_result.get("statistics", {})
                if stats:
                    print(f"    ✓ Found {stats.get('count')} data points")
                    print(f"      Average: {stats.get('average')}")
                    print(f"      Trend: {stats.get('trend')}")
                else:
                    print(f"    ⚠ No trend data available")
            else:
                print(f"    ❌ Trend query failed: {trend_result.get('error')}")
                
        except Exception as e:
            print(f"    ⚠ Trend analysis not available: {e}")
        
        client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("SEMANTIC QUERY TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Intent Parsing", test_nl_intent_parsing),
        ("NL→SQL Mapping", test_nl_to_sql_mapping),
        ("Semantic Executor", test_semantic_query_executor),
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
    
    print(f"\nTotal: {passed}/{total} test suites passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
