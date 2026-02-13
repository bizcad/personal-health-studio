"""
Snowflake Client
Wrapper for Snowflake connections and operations
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date
from decimal import Decimal

from snowflake.connector import connect, ProgrammingError, DatabaseError
from pydantic import BaseModel

from health_models import HealthRecord, RecordClass


class SnowflakeClient:
    """Manages Snowflake connections and health data operations"""
    
    def __init__(
        self,
        account_id: str,
        username: str,
        password: str,
        warehouse: str,
        database: str = "HEALTH_INTELLIGENCE",
        schema: str = "HEALTH_RECORDS",
    ):
        """
        Initialize Snowflake client
        
        Args:
            account_id: Snowflake account ID (format: account-region)
            username: Snowflake username
            password: Snowflake password
            warehouse: Warehouse name
            database: Database name
            schema: Schema name
        """
        self.account_id = account_id
        self.username = username
        self.warehouse = warehouse
        self.database = database
        self.schema = schema
        
        self._connection = None
        self._password = password
        
    def connect(self) -> bool:
        """Establish connection to Snowflake"""
        try:
            self._connection = connect(
                account=self.account_id,
                user=self.username,
                password=self._password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
            )
            return True
        except Exception as e:
            print(f"ERROR: Failed to connect to Snowflake: {e}")
            return False
    
    def disconnect(self):
        """Close Snowflake connection"""
        if self._connection:
            self._connection.close()
            self._connection = None
    
    def is_connected(self) -> bool:
        """Check if connection is active"""
        return self._connection is not None
    
    def execute_query(self, query: str, params: Optional[List] = None) -> List[Dict]:
        """
        Execute a query and return results as list of dicts
        
        Args:
            query: SQL query string
            params: Optional parameter list for parameterized queries
            
        Returns:
            List of result rows as dictionaries
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Snowflake")
        
        try:
            cursor = self._connection.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Get column names
            columns = [desc[0] for desc in cursor.description]
            
            # Fetch results and convert to dicts
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
            
        except Exception as e:
            print(f"ERROR executing query: {e}")
            raise
    
    def get_patient_id(self, patient_identity: str) -> Optional[int]:
        """Get patient_id from patient_identity"""
        try:
            results = self.execute_query(
                "SELECT patient_id FROM PATIENTS WHERE patient_identity = %s",
                [patient_identity]
            )
            return results[0]["PATIENT_ID"] if results else None
        except Exception as e:
            print(f"ERROR getting patient ID: {e}")
            return None
    
    def create_or_get_patient(self, patient_identity: str) -> int:
        """
        Create patient record if not exists, return patient_id
        
        Args:
            patient_identity: Patient name/identifier
            
        Returns:
            patient_id
        """
        # Check if exists
        patient_id = self.get_patient_id(patient_identity)
        if patient_id is not None:
            return patient_id
        
        # Create new patient
        try:
            cursor = self._connection.cursor()
            cursor.execute(
                """
                INSERT INTO PATIENTS (patient_identity, created_date, updated_date)
                VALUES (%s, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
                """,
                [patient_identity]
            )
            
            # Query the newly inserted patient using their identity (since they should be unique)
            results = self.execute_query(
                "SELECT patient_id FROM PATIENTS WHERE patient_identity = %s",
                [patient_identity]
            )
            
            patient_id = results[0]["PATIENT_ID"] if results else None
            cursor.close()
            return patient_id
            
        except Exception as e:
            print(f"ERROR creating patient: {e}")
            raise
    
    def import_health_records(
        self,
        patient_identity: str,
        records: List[HealthRecord],
        import_source: str = "pdf_extraction",
        import_stats: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Import health records for a patient
        
        Args:
            patient_identity: Patient identifier
            records: List of HealthRecord objects
            import_source: Source of import (e.g., "pdf_extraction")
            import_stats: Optional statistics about the import
            
        Returns:
            Import result summary
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Snowflake")
        
        try:
            cursor = self._connection.cursor()
            
            # Get or create patient
            patient_id = self.create_or_get_patient(patient_identity)
            
            # Create import record
            cursor.execute(
                """
                INSERT INTO IMPORTS (
                    patient_id, import_date, source_files, 
                    records_by_type, import_statistics, import_status
                )
                VALUES (%s, CURRENT_TIMESTAMP(), %s, %s, %s, %s)
                """,
                [
                    patient_id,
                    json.dumps({}),  # source_files
                    json.dumps({}),  # records_by_type
                    json.dumps(import_stats or {}),  # import_statistics
                    "IN_PROGRESS"
                ]
            )
            
            # Get the import_id - in Snowflake we need to query for it
            import_results = self.execute_query(
                """
                SELECT import_id FROM IMPORTS 
                WHERE patient_id = %s AND import_status = 'IN_PROGRESS'
                ORDER BY import_date DESC
                LIMIT 1
                """,
                [patient_id]
            )
            
            import_id = import_results[0]["IMPORT_ID"] if import_results else None
            
            # Insert health records
            inserted_count = 0
            failed_count = 0
            record_types = {}
            
            for record in records:
                try:
                    cursor.execute(
                        """
                        INSERT INTO HEALTH_RECORDS (
                            patient_id, import_id, record_class, 
                            record_date, provider_identity, data_json,
                            extraction_confidence, verification_status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        [
                            patient_id,
                            import_id,
                            record.record_class.value,
                            record.record_date,
                            record.provider_identity,
                            json.dumps(record.data),
                            record.extraction_confidence,
                            "unverified"
                        ]
                    )
                    inserted_count += 1
                    record_types[record.record_class.value] = record_types.get(record.record_class.value, 0) + 1
                    
                except Exception as e:
                    print(f"ERROR inserting record: {e}")
                    failed_count += 1
            
            # Update import status
            cursor.execute(
                """
                UPDATE IMPORTS 
                SET import_status = %s, records_by_type = %s
                WHERE import_id = %s
                """,
                [
                    "SUCCESS" if failed_count == 0 else "PARTIAL",
                    json.dumps(record_types),
                    import_id
                ]
            )
            
            cursor.close()
            
            return {
                "success": True,
                "patient_id": patient_id,
                "import_id": import_id,
                "records_inserted": inserted_count,
                "records_failed": failed_count,
                "record_types": record_types,
            }
            
        except Exception as e:
            print(f"ERROR in import_health_records: {e}")
            raise
    
    def query_health_data(
        self,
        patient_identity: str,
        query_type: str,
        parameters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Query health data with predefined query patterns
        
        Args:
            patient_identity: Patient identifier
            query_type: Type of query (e.g., "labs_by_date", "medications", "vitals")
            parameters: Additional parameters for the query
            
        Returns:
            Query results
        """
        if not self.is_connected():
            raise RuntimeError("Not connected to Snowflake")
        
        patient_id = self.get_patient_id(patient_identity)
        if patient_id is None:
            return []
        
        parameters = parameters or {}
        
        # Define query patterns (Snowflake-specific syntax)
        queries = {
            "all_records": """
                SELECT 
                    record_id, record_class, record_date, 
                    provider_identity, data_json, extraction_confidence
                FROM HEALTH_RECORDS
                WHERE patient_id = %s
                ORDER BY record_date DESC
            """,
            "labs_recent": """
                SELECT 
                    record_id, record_date, data_json, extraction_confidence
                FROM HEALTH_RECORDS
                WHERE patient_id = %s AND record_class = 'LAB'
                ORDER BY record_date DESC
                LIMIT %s
            """,
            "medications_active": """
                SELECT 
                    record_id, record_date, data_json
                FROM HEALTH_RECORDS
                WHERE patient_id = %s AND record_class = 'MEDICATION'
                AND (TRY_PARSE_JSON(data_json):status::STRING = 'active' OR data_json LIKE '%active%')
                ORDER BY record_date DESC
            """,
            "vitals_by_type": """
                SELECT 
                    record_id, record_date, data_json
                FROM HEALTH_RECORDS
                WHERE patient_id = %s AND record_class = 'VITAL'
                AND TRY_PARSE_JSON(data_json):'vital_type'::STRING = %s
                ORDER BY record_date DESC
            """,
            "abnormal_labs": """
                SELECT 
                    record_id, record_date, data_json
                FROM HEALTH_RECORDS
                WHERE patient_id = %s AND record_class = 'LAB'
                AND TRY_PARSE_JSON(data_json):'abnormal_flag'::STRING IS NOT NULL
                ORDER BY record_date DESC
            """,
        }
        
        if query_type not in queries:
            raise ValueError(f"Unknown query type: {query_type}")
        
        try:
            sql = queries[query_type]
            
            # Build parameters for query
            query_params = [patient_id]
            if query_type == "labs_recent":
                query_params.append(parameters.get("limit", 10))
            elif query_type == "vitals_by_type":
                query_params.append(parameters.get("vital_type"))
            
            results = self.execute_query(sql, query_params)
            return results
            
        except Exception as e:
            print(f"ERROR querying health data: {e}")
            raise
