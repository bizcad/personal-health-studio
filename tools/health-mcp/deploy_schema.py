#!/usr/bin/env python3
"""
Deploy Snowflake schema for Health Intelligence
Reads DDL file and executes it against Snowflake
"""

import sys
from pathlib import Path
from snowflake.connector import connect

# Snowflake connection details
SNOWFLAKE_CONFIG = {
    "account": "kgqnwwa-zxb81952",
    "user": "bizcad",
    "password": "ImFW3&Z&#9vUa9Mn",
    "warehouse": "COMPUTE_WH",
}

def deploy_schema():
    """Deploy the Snowflake schema for Health Intelligence"""
    
    print("=" * 70)
    print("SNOWFLAKE SCHEMA DEPLOYMENT")
    print("=" * 70)
    
    # Read the DDL file
    ddl_path = Path(__file__).parent.parent.parent / "data-store" / "snowflake" / "ddl" / "health_intelligence_ddl.sql"
    
    if not ddl_path.exists():
        print(f"❌ ERROR: DDL file not found at {ddl_path}")
        return False
    
    print(f"📄 Reading DDL from: {ddl_path.name}")
    
    with open(ddl_path, 'r') as f:
        ddl_content = f.read()
    
    # Parse the DDL into individual statements
    # Split by semicolon and filter out empty statements and comments
    statements = []
    current_statement = []
    
    for line in ddl_content.split('\n'):
        # Skip comment lines
        if line.strip().startswith('--') or line.strip().startswith('//'):
            continue
        
        current_statement.append(line)
        
        if ';' in line:
            statement = '\n'.join(current_statement).strip()
            if statement and not statement.startswith('--'):
                statements.append(statement)
            current_statement = []
    
    if current_statement:
        statement = '\n'.join(current_statement).strip()
        if statement and not statement.startswith('--'):
            statements.append(statement)
    
    print(f"📋 Found {len(statements)} SQL statements to execute")
    print()
    
    # Execute statements
    try:
        conn = connect(**SNOWFLAKE_CONFIG)
        cursor = conn.cursor()
        
        print("Executing statements:")
        print("-" * 70)
        
        executed_count = 0
        for i, statement in enumerate(statements, 1):
            # Skip empty lines
            if not statement.strip():
                continue
            
            try:
                # Get a nicer display name
                first_line = statement.split('\n')[0].strip()[:50]
                print(f"  [{i:2d}] {first_line}...", end=" ")
                
                cursor.execute(statement)
                executed_count += 1
                print("✓")
                
            except Exception as e:
                print(f"⚠ {str(e)[:60]}")
                # Continue with other statements
        
        print("-" * 70)
        print(f"✓ Executed {executed_count}/{len(statements)} statements")
        print()
        
        # Verify schema exists
        print("Verifying schema:")
        print("-" * 70)
        
        try:
            cursor.execute("USE DATABASE HEALTH_INTELLIGENCE")
            cursor.execute("USE SCHEMA HEALTH_RECORDS")
            print("✓ Database and schema selected successfully")
            
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"✓ Found {len(tables)} tables:")
            for table in tables:
                table_name = table[1]  # Name is in second column
                print(f"   - {table_name}")
            
            print()
            print("=" * 70)
            print("✓ SCHEMA DEPLOYMENT SUCCESSFUL")
            print("=" * 70)
            
            return True
            
        except Exception as e:
            print(f"❌ Verification failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
        
    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass

if __name__ == "__main__":
    success = deploy_schema()
    sys.exit(0 if success else 1)
