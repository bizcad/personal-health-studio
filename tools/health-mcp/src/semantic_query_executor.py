"""
Semantic Query Executor
Executes natural language queries and returns human-readable results
"""

from typing import List, Dict, Any, Optional
import json
from datetime import datetime

from snowflake_client import SnowflakeClient
from nl_mapper import nl_to_sql, QueryIntent, NLMapper


class HealthInsight:
    """A single health insight from query results"""
    
    def __init__(
        self,
        title: str,
        value: Any,
        unit: Optional[str] = None,
        interpretation: Optional[str] = None,
        record_count: Optional[int] = None,
    ):
        self.title = title
        self.value = value
        self.unit = unit
        self.interpretation = interpretation
        self.record_count = record_count
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "value": self.value,
            "unit": self.unit,
            "interpretation": self.interpretation,
            "record_count": self.record_count,
            "timestamp": datetime.now().isoformat(),
        }
    
    def __str__(self) -> str:
        if self.unit:
            return f"{self.title}: {self.value} {self.unit}"
        return f"{self.title}: {self.value}"


class SemanticQueryExecutor:
    """Executes semantic (natural language) queries against health data"""
    
    def __init__(self, snowflake_client: SnowflakeClient):
        """
        Initialize executor
        
        Args:
            snowflake_client: Connected Snowflake client
        """
        self.client = snowflake_client
        self.mapper = NLMapper()
    
    def query(self, patient_identity: str, natural_language_query: str) -> Dict[str, Any]:
        """
        Execute a natural language health query
        
        Args:
            patient_identity: Patient name or identifier
            natural_language_query: Natural language question
            
        Returns:
            Dictionary with query results and interpretation
        """
        # Get patient ID
        patient_id = self.client.get_patient_id(patient_identity)
        if patient_id is None:
            return {
                "success": False,
                "error": f"Patient not found: {patient_identity}",
                "query": natural_language_query,
            }
        
        # Parse intent
        intent = self.mapper.parse_intent(natural_language_query)
        
        # Convert to SQL
        sql = self.mapper.intent_to_sql(intent, patient_id)
        
        # Execute query
        try:
            results = self.client.execute_query(sql)
        except Exception as e:
            return {
                "success": False,
                "error": f"Query execution failed: {str(e)}",
                "query": natural_language_query,
                "sql": sql,
            }
        
        # Interpret results
        insights = self._interpret_results(intent, results)
        
        return {
            "success": True,
            "query": natural_language_query,
            "intent": {
                "record_type": intent.record_type.value if intent.record_type else None,
                "metric": intent.metric,
                "time_period": intent.time_period,
                "attribute": intent.attribute,
                "filter": intent.filter_condition,
            },
            "sql": sql,
            "raw_results": results,
            "insights": [insight.to_dict() for insight in insights],
            "record_count": len(results),
        }
    
    def _interpret_results(self, intent: QueryIntent, results: List[Dict]) -> List[HealthInsight]:
        """
        Interpret query results and generate human-readable insights
        
        Args:
            intent: Parsed query intent
            results: Raw query results from database
            
        Returns:
            List of HealthInsight objects
        """
        insights = []
        
        if not results:
            insight = HealthInsight(
                title="No Results Found",
                value="No records match your query criteria",
            )
            return [insight]
        
        # Handle aggregation results (count, average, etc.)
        if intent.metric == "count":
            key = "RESULT_COUNT"
            count = results[0].get(key, 0)
            
            title = f"Total {intent.record_type.value.lower()} records"
            if intent.time_period:
                title += f" ({intent.time_period})"
            
            insight = HealthInsight(
                title=title,
                value=count,
                unit="records",
                record_count=1,
            )
            insights.append(insight)
        
        elif intent.metric == "average":
            key = "RESULT_AVERAGE"
            avg_value = results[0].get(key, 0) if results else 0
            
            title = f"Average {intent.attribute or intent.record_type.value.lower()}"
            unit = self._guess_unit(intent.attribute)
            
            insight = HealthInsight(
                title=title,
                value=round(avg_value, 2) if isinstance(avg_value, float) else avg_value,
                unit=unit,
                record_count=1,
            )
            insights.append(insight)
        
        elif intent.metric in ["maximum", "minimum"]:
            key = f"RESULT_{intent.metric.upper()}"
            value = results[0].get(key, 0) if results else 0
            
            title = f"{intent.metric.capitalize()} {intent.attribute or intent.record_type.value.lower()}"
            unit = self._guess_unit(intent.attribute)
            
            insight = HealthInsight(
                title=title,
                value=round(value, 2) if isinstance(value, float) else value,
                unit=unit,
                record_count=1,
            )
            insights.append(insight)
        
        # Handle list results
        else:
            for i, result in enumerate(results[:10]):  # Show top 10 results
                record_date = result.get("RECORD_DATE", "Unknown date")
                data_json = result.get("DATA_JSON", "{}")
                provider = result.get("PROVIDER_IDENTITY", "Unknown provider")
                confidence = result.get("EXTRACTION_CONFIDENCE", "Unknown")
                
                # Try to parse JSON data
                try:
                    if isinstance(data_json, str):
                        data = json.loads(data_json)
                    else:
                        data = data_json
                except:
                    data = {"raw": str(data_json)}
                
                # Create insight from record
                title = f"{intent.record_type.value if intent.record_type else 'Record'} on {record_date}"
                
                insight = HealthInsight(
                    title=title,
                    value=data,
                    interpretation=f"Provider: {provider}, Confidence: {confidence}",
                    record_count=1,
                )
                insights.append(insight)
            
            # If there are more results, indicate that
            if len(results) > 10:
                insight = HealthInsight(
                    title="Additional Records",
                    value=f"Plus {len(results) - 10} more records not shown",
                    record_count=len(results) - 10,
                )
                insights.append(insight)
        
        return insights
    
    def _guess_unit(self, attribute: Optional[str]) -> Optional[str]:
        """Guess appropriate unit for an attribute"""
        if not attribute:
            return None
        
        units = {
            "glucose": "mg/dL",
            "bp": "mmHg",
            "blood pressure": "mmHg",
            "heart rate": "bpm",
            "temperature": "°F",
            "cholesterol": "mg/dL",
            "ldl": "mg/dL",
            "hdl": "mg/dL",
            "triglycerides": "mg/dL",
            "a1c": "%",
            "hemoglobin": "g/dL",
            "creatinine": "mg/dL",
            "bun": "mg/dL",
        }
        
        return units.get(attribute.lower())
    
    def get_trend(
        self,
        patient_identity: str,
        attribute: str,
        days: int = 90,
    ) -> Dict[str, Any]:
        """
        Get trend data for a specific health metric
        
        Args:
            patient_identity: Patient identifier
            attribute: Health metric to analyze (glucose, blood pressure, etc.)
            days: Number of days to look back
            
        Returns:
            Dictionary with trend information
        """
        patient_id = self.client.get_patient_id(patient_identity)
        if patient_id is None:
            return {"success": False, "error": f"Patient not found: {patient_identity}"}
        
        # Build query for trend data
        sql = f"""
            SELECT 
                record_date,
                data_json,
                extraction_confidence
            FROM HEALTH_INTELLIGENCE.HEALTH_RECORDS.HEALTH_RECORDS
            WHERE patient_id = {patient_id}
            AND data_json LIKE '%{attribute}%'
            AND record_date >= DATEADD(day, -{days}, CURRENT_DATE())
            ORDER BY record_date ASC
        """
        
        try:
            results = self.client.execute_query(sql)
        except Exception as e:
            return {"success": False, "error": f"Query failed: {str(e)}"}
        
        if not results:
            return {"success": True, "trend_data": [], "message": f"No data found for {attribute}"}
        
        # Extract values from results
        trend_points = []
        for result in results:
            date = result.get("RECORD_DATE")
            data = result.get("DATA_JSON")
            
            try:
                if isinstance(data, str):
                    data_obj = json.loads(data)
                else:
                    data_obj = data
                
                # Try to extract numeric value
                value = None
                if isinstance(data_obj, dict):
                    # Look for common value fields
                    for key in ["value", "result_value", "result", "amount"]:
                        if key in data_obj:
                            try:
                                value = float(str(data_obj[key]).split()[0])
                                break
                            except:
                                pass
                
                if value is not None:
                    trend_points.append({
                        "date": str(date),
                        "value": value,
                        "raw_data": data_obj,
                    })
            except:
                pass
        
        # Calculate trend statistics
        if trend_points:
            values = [p["value"] for p in trend_points]
            avg = sum(values) / len(values)
            trend = "stable"
            
            if len(values) >= 2:
                slope = (values[-1] - values[0]) / len(values)
                if slope > 1:
                    trend = "increasing"
                elif slope < -1:
                    trend = "decreasing"
            
            return {
                "success": True,
                "attribute": attribute,
                "days": days,
                "data_points": trend_points,
                "statistics": {
                    "count": len(values),
                    "average": round(avg, 2),
                    "minimum": min(values),
                    "maximum": max(values),
                    "trend": trend,
                },
            }
        
        return {"success": True, "trend_data": [], "message": "Could not extract numeric values"}
