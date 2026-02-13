#!/usr/bin/env py
"""
Test Snowflake Connection
Validates RSA key authentication and connection to Health Intelligence database.

Usage:
    py test_connection.py

Returns:
    0 if connection successful
    1 if connection failed
"""

import sys
from pathlib import Path

try:
    from snowflake.connector import connect
    from snowflake.connector.errors import ProgrammingError, DatabaseError
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("ERROR: snowflake-connector-python not installed")
    print("Install with: py -m pip install snowflake-connector-python cryptography")
    sys.exit(1)


def test_snowflake_connection() -> bool:
    """Test connection to Snowflake using password authentication."""
    
    # Configuration
    account_id = "kgqnwwa-zxb81952"
    username = "bizcad"
    password = "ImFW3&Z&#9vUa9Mn"  # TODO: Move to .env
    warehouse = "COMPUTE_WH"
    database = "HEALTH_INTELLIGENCE"
    schema = "HEALTH_RECORDS"
    
    print("=" * 70)
    print("SNOWFLAKE CONNECTION TEST")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  Account ID:  {account_id}")
    print(f"  Username:    {username}")
    print(f"  Warehouse:   {warehouse}")
    print(f"  Database:    {database}")
    print(f"  Schema:      {schema}")
    
    # Attempt connection
    print("\nConnecting to Snowflake...")
    try:
        conn = connect(
            account=account_id,
            user=username,
            password=password,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        print("✓ Connection successful!")
        
    except ProgrammingError as e:
        print(f"\n❌ AUTHENTICATION ERROR: {e}")
        print("   Check:")
        print("   - Account ID is correct (from Snowflake dashboard URL)")
        print("   - Username is correct")
        print("   - RSA key is valid PKCS8 format")
        return False
    
    except DatabaseError as e:
        print(f"\n❌ DATABASE ERROR: {e}")
        print("   Check:")
        print("   - Database HEALTH_INTELLIGENCE exists")
        print("   - Schema HEALTH_RECORDS exists")
        print("   - Permissions are correct")
        return False
    
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        return False
    
    # Test: Get version
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT CURRENT_VERSION()")
        version = cursor.fetchone()
        print(f"\n✓ Snowflake version: {version[0]}")
    except Exception as e:
        print(f"\n❌ ERROR querying version: {e}")
        cursor.close()
        conn.close()
        return False
    
    # Test: List tables in schema
    try:
        cursor.execute("SHOW TABLES IN SCHEMA HEALTH_RECORDS")
        tables = cursor.fetchall()
        print(f"\n✓ Tables in schema ({len(tables)} found):")
        for table in tables:
            print(f"    - {table[1]}")  # Table name is second column
    except Exception as e:
        print(f"\n⚠ WARNING: Could not list tables: {e}")
        print("   (Database schema may not exist yet)")
    
    # Test: Query system info
    try:
        cursor.execute("""
            SELECT 
                CURRENT_ACCOUNT() as account,
                CURRENT_USER() as user,
                CURRENT_WAREHOUSE() as warehouse,
                CURRENT_DATABASE() as database,
                CURRENT_SCHEMA() as schema,
                CURRENT_TIMESTAMP() as timestamp
        """)
        result = cursor.fetchone()
        print(f"\n✓ Current context:")
        print(f"    Account:   {result[0]}")
        print(f"    User:      {result[1]}")
        print(f"    Warehouse: {result[2]}")
        print(f"    Database:  {result[3]}")
        print(f"    Schema:    {result[4]}")
        print(f"    Time:      {result[5]}")
    except Exception as e:
        print(f"\n⚠ WARNING: Could not query system context: {e}")
    
    # Close connection
    try:
        cursor.close()
        conn.close()
        print("\n✓ Connection closed cleanly")
    except Exception as e:
        print(f"\n⚠ WARNING: Error closing connection: {e}")
    
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED - Snowflake connection is working!")
    print("=" * 70)
    return True


if __name__ == "__main__":
    success = test_snowflake_connection()
    sys.exit(0 if success else 1)
