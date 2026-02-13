"""
Health Data Models
Pydantic models for structured health record extraction and validation
"""

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, validator


class RecordClass(str, Enum):
    """Health record type classification"""
    LAB = "LAB"
    VITAL = "VITAL"
    MEDICATION = "MEDICATION"
    CONDITION = "CONDITION"
    ALLERGY = "ALLERGY"
    IMMUNIZATION = "IMMUNIZATION"
    ENCOUNTER = "ENCOUNTER"
    NOTE = "NOTE"


class VitalRecord(BaseModel):
    """Vital signs record"""
    vital_type: str = Field(..., description="Type: BP, HR, Temp, RR, O2Sat, Weight, Height, BMI")
    value: str = Field(..., description="Numeric value with units")
    measured_date: date
    provider: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "vital_type": "BP",
                "value": "120/80 mmHg",
                "measured_date": "2026-02-12",
            }
        }


class LabRecord(BaseModel):
    """Laboratory test result"""
    test_name: str = Field(..., description="Lab test name")
    result_value: str = Field(..., description="Result with units")
    reference_range: Optional[str] = None
    abnormal_flag: Optional[str] = None  # "HIGH", "LOW", or None
    test_date: date
    specimen_type: Optional[str] = None
    ordering_provider: Optional[str] = None
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "test_name": "Glucose, Fasting",
                "result_value": "105 mg/dL",
                "reference_range": "70-100 mg/dL",
                "abnormal_flag": "HIGH",
                "test_date": "2026-02-10",
            }
        }


class MedicationRecord(BaseModel):
    """Medication record"""
    medication_name: str = Field(..., description="Drug name/trade name")
    dosage: str = Field(..., description="Dose with units")
    frequency: str = Field(..., description="e.g., 'once daily', 'every 6 hours'")
    start_date: date
    end_date: Optional[date] = None
    indication: Optional[str] = None
    prescribing_provider: Optional[str] = None
    pharmacy: Optional[str] = None
    status: Optional[str] = Field(default="active", description="active, discontinued, stopped")

    class Config:
        json_schema_extra = {
            "example": {
                "medication_name": "Metformin",
                "dosage": "500 mg",
                "frequency": "twice daily",
                "start_date": "2024-01-15",
                "indication": "Type 2 Diabetes",
                "status": "active",
            }
        }


class ConditionRecord(BaseModel):
    """Condition/diagnosis record"""
    condition_name: str = Field(..., description="Diagnosis or condition")
    icd_code: Optional[str] = None
    onset_date: Optional[date] = None
    status: Optional[str] = Field(default="active", description="active, resolved, inactive")
    severity: Optional[str] = None  # mild, moderate, severe
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "condition_name": "Type 2 Diabetes Mellitus",
                "icd_code": "E11.9",
                "onset_date": "2018-06-01",
                "status": "active",
                "severity": "moderate",
            }
        }


class AllergyRecord(BaseModel):
    """Allergy/adverse reaction record"""
    allergen: str = Field(..., description="Drug, food, or environmental allergen")
    reaction: str = Field(..., description="Observed reaction")
    severity: Optional[str] = Field(None, description="mild, moderate, severe, life-threatening")
    onset_date: Optional[date] = None
    status: Optional[str] = Field(default="active")

    class Config:
        json_schema_extra = {
            "example": {
                "allergen": "Penicillin",
                "reaction": "Rash, itching",
                "severity": "moderate",
                "status": "active",
            }
        }


class ImmunizationRecord(BaseModel):
    """Immunization/vaccination record"""
    vaccine_name: str = Field(..., description="Vaccine name")
    administration_date: date
    route: Optional[str] = None  # IM, IV, oral, etc.
    site: Optional[str] = None  # L arm, R arm, etc.
    dose_number: Optional[int] = None
    administering_provider: Optional[str] = None
    lot_number: Optional[str] = None
    next_dose_date: Optional[date] = None

    class Config:
        json_schema_extra = {
            "example": {
                "vaccine_name": "COVID-19 (Pfizer-BioNTech)",
                "administration_date": "2026-01-15",
                "route": "IM",
                "site": "L arm",
                "dose_number": 1,
            }
        }


class HealthRecord(BaseModel):
    """
    Unified health record wrapper
    Can contain any typed health data
    """
    record_class: RecordClass
    record_date: date
    patient_identity: str = Field(..., description="Patient identifier (name, MRN, or unique ID)")
    provider_identity: Optional[str] = None
    data: Dict[str, Any] = Field(..., description="Structured data per record_class")
    source_document: Optional[str] = None  # PDF filename or source
    extraction_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    notes: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "record_class": "LAB",
                "record_date": "2026-02-10",
                "patient_identity": "John Doe",
                "provider_identity": "Dr. Jane Smith",
                "data": {
                    "test_name": "Glucose, Fasting",
                    "result_value": "105 mg/dL",
                },
                "source_document": "apple_health_export.pdf",
                "extraction_confidence": 0.95,
            }
        }


class HealthImportRequest(BaseModel):
    """Request to import health records"""
    patient_identity: str = Field(..., description="Patient identifier")
    records: List[HealthRecord] = Field(..., description="List of health records to import")
    import_source: str = Field(default="pdf_extraction", description="Where data came from")
    verification_status: str = Field(default="unverified")
    metadata: Optional[Dict[str, Any]] = None


class HealthQueryRequest(BaseModel):
    """Request to query health data with natural language"""
    patient_identity: str = Field(..., description="Patient identifier")
    query: str = Field(..., description="Natural language question")
    include_recommendations: bool = Field(default=False)
    context_window_days: int = Field(default=365, description="Look back this many days")
