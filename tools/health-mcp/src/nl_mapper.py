"""
Natural Language to SQL Mapping
Maps domain vocabulary and natural language patterns to SQL queries
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class RecordType(str, Enum):
    """Health record type classifications"""
    LAB = "LAB"
    VITAL = "VITAL"
    MEDICATION = "MEDICATION"
    CONDITION = "CONDITION"
    ALLERGY = "ALLERGY"
    IMMUNIZATION = "IMMUNIZATION"
    ENCOUNTER = "ENCOUNTER"
    NOTE = "NOTE"


@dataclass
class QueryIntent:
    """Parsed natural language query intent"""
    record_type: Optional[RecordType]
    metric: Optional[str]  # e.g., "average", "count", "trend"
    time_period: Optional[str]  # e.g., "last year", "last 30 days"
    attribute: Optional[str]  # e.g., "blood glucose", "medications", "blood pressure"
    filter_condition: Optional[str]  # e.g., "abnormal", "active"
    sort_order: Optional[str]  # e.g., "ascending", "descending"
    raw_query: str


class NLMapper:
    """Maps natural language queries to SQL"""
    
    # Vocabulary mappings
    RECORD_TYPE_SYNONYMS = {
        # Lab tests
        "lab": RecordType.LAB,
        "labs": RecordType.LAB,
        "lab test": RecordType.LAB,
        "lab result": RecordType.LAB,
        "lab results": RecordType.LAB,
        "laboratory": RecordType.LAB,
        "test": RecordType.LAB,
        "results": RecordType.LAB,
        
        # Vitals
        "vital": RecordType.VITAL,
        "vitals": RecordType.VITAL,
        "vital sign": RecordType.VITAL,
        "vital signs": RecordType.VITAL,
        "blood pressure": RecordType.VITAL,
        "bp": RecordType.VITAL,
        "heart rate": RecordType.VITAL,
        "hr": RecordType.VITAL,
        "temperature": RecordType.VITAL,
        "temp": RecordType.VITAL,
        "oxygen": RecordType.VITAL,
        "resp rate": RecordType.VITAL,
        
        # Medications
        "medication": RecordType.MEDICATION,
        "medications": RecordType.MEDICATION,
        "med": RecordType.MEDICATION,
        "meds": RecordType.MEDICATION,
        "drug": RecordType.MEDICATION,
        "drugs": RecordType.MEDICATION,
        "prescription": RecordType.MEDICATION,
        "prescriptions": RecordType.MEDICATION,
        
        # Conditions
        "condition": RecordType.CONDITION,
        "conditions": RecordType.CONDITION,
        "diagnosis": RecordType.CONDITION,
        "diagnoses": RecordType.CONDITION,
        "problem": RecordType.CONDITION,
        "problems": RecordType.CONDITION,
        
        # Allergies
        "allergy": RecordType.ALLERGY,
        "allergies": RecordType.ALLERGY,
        "sensitivity": RecordType.ALLERGY,
        "sensitivities": RecordType.ALLERGY,
        
        # Immunizations
        "immunization": RecordType.IMMUNIZATION,
        "immunizations": RecordType.IMMUNIZATION,
        "vaccine": RecordType.IMMUNIZATION,
        "vaccines": RecordType.IMMUNIZATION,
        "shot": RecordType.IMMUNIZATION,
        "shots": RecordType.IMMUNIZATION,
        
        # Encounters
        "encounter": RecordType.ENCOUNTER,
        "encounters": RecordType.ENCOUNTER,
        "visit": RecordType.ENCOUNTER,
        "visits": RecordType.ENCOUNTER,
        "appointment": RecordType.ENCOUNTER,
        "appointments": RecordType.ENCOUNTER,
        
        # Notes
        "note": RecordType.NOTE,
        "notes": RecordType.NOTE,
        "clinical note": RecordType.NOTE,
        "doctor note": RecordType.NOTE,
    }
    
    # Test name mappings (for lab results)
    TEST_NAME_PATTERNS = {
        "glucose": ["Glucose", "Fasting Glucose", "Blood Sugar"],
        "cholesterol": ["Cholesterol", "Total Cholesterol", "LDL", "HDL", "Triglycerides"],
        "ldl": ["LDL", "Low-density lipoprotein"],
        "hdl": ["HDL", "High-density lipoprotein"],
        "triglycerides": ["Triglycerides"],
        "a1c": ["A1C", "HbA1c", "Hemoglobin A1c"],
        "thyroid": ["TSH", "T3", "T4", "Free T4"],
        "hemoglobin": ["Hemoglobin", "Hgb", "CBC"],
        "creatinine": ["Creatinine", "Kidney Function"],
        "bun": ["BUN", "Blood Urea Nitrogen"],
    }
    
    # Time period mappings
    TIME_PERIOD_PATTERNS = {
        "today": 0,
        "yesterday": 1,
        "last week": 7,
        "last 7 days": 7,
        "last 2 weeks": 14,
        "last month": 30,
        "last 30 days": 30,
        "last 3 months": 90,
        "last 6 months": 180,
        "last year": 365,
        "last 12 months": 365,
        "this year": 365,
        "past year": 365,
        "all time": None,  # No time limit
    }
    
    # Metric patterns
    METRIC_PATTERNS = {
        "average": ["average", "avg", "mean"],
        "maximum": ["maximum", "max", "highest"],
        "minimum": ["minimum", "min", "lowest"],
        "count": ["count", "how many", "number of"],
        "trend": ["trend", "change", "improvement"],
        "list": ["list", "show", "display", "get"],
    }
    
    def parse_intent(self, query: str) -> QueryIntent:
        """Parse natural language query into intent"""
        query_lower = query.lower().strip()
        
        # Initialize intent
        intent = QueryIntent(
            record_type=None,
            metric=None,
            time_period=None,
            attribute=None,
            filter_condition=None,
            sort_order=None,
            raw_query=query,
        )
        
        # Extract record type
        for synonym, record_type in self.RECORD_TYPE_SYNONYMS.items():
            if synonym in query_lower:
                intent.record_type = record_type
                break
        
        # Extract metric type
        for metric, patterns in self.METRIC_PATTERNS.items():
            for pattern in patterns:
                if pattern in query_lower:
                    intent.metric = metric
                    break
            if intent.metric:
                break
        
        # Extract time period
        for time_phrase, days in self.TIME_PERIOD_PATTERNS.items():
            if time_phrase in query_lower:
                intent.time_period = time_phrase
                break
        
        # Extract test name (for labs)
        for test_key, test_names in self.TEST_NAME_PATTERNS.items():
            for test_name in test_names:
                if test_name.lower() in query_lower:
                    intent.attribute = test_key
                    break
            if intent.attribute:
                break
        
        # Extract filter keywords
        if "abnormal" in query_lower:
            intent.filter_condition = "abnormal"
        elif "active" in query_lower:
            intent.filter_condition = "active"
        elif "recent" in query_lower:
            intent.filter_condition = "recent"
        
        # Extract sort order
        if "ascending" in query_lower or "oldest first" in query_lower:
            intent.sort_order = "ASC"
        elif "descending" in query_lower or "newest first" in query_lower or "most recent" in query_lower:
            intent.sort_order = "DESC"
        else:
            intent.sort_order = "DESC"  # Default to recent first
        
        return intent
    
    def intent_to_sql(self, intent: QueryIntent, patient_id: int) -> str:
        """Convert parsed intent to SQL query"""
        
        # Build SELECT clause
        if intent.metric == "count":
            select_clause = "SELECT COUNT(*) as result_count"
        elif intent.metric == "average":
            # Extract numeric values from JSON result_value field
            # Handle values like "98 mg/dL" by splitting on space and taking first part
            select_clause = """SELECT 
                AVG(TRY_CAST(SPLIT_PART(TRY_PARSE_JSON(data_json):result_value::STRING, ' ', 1) AS FLOAT)) as result_average,
                COUNT(*) as record_count"""
        elif intent.metric == "maximum":
            select_clause = """SELECT 
                MAX(TRY_CAST(SPLIT_PART(TRY_PARSE_JSON(data_json):result_value::STRING, ' ', 1) AS FLOAT)) as result_maximum,
                COUNT(*) as record_count"""
        elif intent.metric == "minimum":
            select_clause = """SELECT 
                MIN(TRY_CAST(SPLIT_PART(TRY_PARSE_JSON(data_json):result_value::STRING, ' ', 1) AS FLOAT)) as result_minimum,
                COUNT(*) as record_count"""
        else:  # list/show
            select_clause = "SELECT record_date, data_json, provider_identity, extraction_confidence"
        
        # Build FROM clause
        from_clause = "FROM HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS"
        
        # Build WHERE clause
        where_conditions = [f"patient_id = {patient_id}"]
        
        # Add record type filter
        if intent.record_type:
            where_conditions.append(f"record_class = '{intent.record_type.value}'")
        
        # Add attribute filter (for lab tests, etc.) - use ILIKE for case-insensitive matching
        if intent.attribute:
            where_conditions.append(f"data_json ILIKE '%{intent.attribute}%'")
        
        # Add filter condition - use ILIKE for case-insensitive matching
        if intent.filter_condition:
            if intent.filter_condition == "abnormal":
                where_conditions.append(f"data_json ILIKE '%abnormal%'")
            elif intent.filter_condition == "active":
                where_conditions.append(f"(data_json ILIKE '%active%' OR data_json ILIKE '%ongoing%')")
            elif intent.filter_condition == "recent":
                where_conditions.append(f"record_date >= DATEADD(day, -30, CURRENT_DATE())")
        
        # Add time period filter
        if intent.time_period:
            days = self.TIME_PERIOD_PATTERNS.get(intent.time_period)
            if days is not None:
                where_conditions.append(
                    f"record_date >= DATEADD(day, -{days}, CURRENT_DATE())"
                )
        
        where_clause = "WHERE " + " AND ".join(where_conditions)
        
        # Build ORDER BY clause
        if intent.metric not in ["count", "average", "maximum", "minimum"]:
            order_clause = f"ORDER BY record_date {intent.sort_order}"
        else:
            order_clause = ""
        
        # Assemble final query
        sql_parts = [select_clause, from_clause, where_clause]
        if order_clause:
            sql_parts.append(order_clause)
        
        return "\n".join(sql_parts)


def nl_to_sql(query: str, patient_id: int) -> Tuple[QueryIntent, str]:
    """
    Convert natural language query to SQL
    
    Args:
        query: Natural language question
        patient_id: Patient database ID
        
    Returns:
        Tuple of (parsed intent, SQL query)
    """
    mapper = NLMapper()
    intent = mapper.parse_intent(query)
    sql = mapper.intent_to_sql(intent, patient_id)
    return intent, sql
