"""
Health PDF Extractor Agent
Extracts structured health data from PDF documents
Uses Claude to intelligently parse health records
"""

import json
import base64
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date

from health_models import HealthRecord, RecordClass


class HealthPDFExtractor:
    """
    Extracts health records from PDF documents using Claude
    Converts unstructured PDF data to structured HealthRecord format
    """
    
    def __init__(self, client=None):
        """
        Initialize extractor
        
        Args:
            client: Anthropic client (will be provided by Claude)
        """
        self.client = client  # Will be provided by Claude via MCP
        self.extraction_prompts = self._create_prompts()
    
    def _create_prompts(self) -> Dict[str, str]:
        """Create extraction prompts for different record types"""
        return {
            "lab_results": """
Extract all laboratory test results from this health document.

For each lab test found, extract:
1. Test name (e.g., "Glucose, Fasting")
2. Result value with units (e.g., "105 mg/dL")
3. Reference range if available (e.g., "70-100 mg/dL")
4. Abnormal flag if indicated (HIGH, LOW, or null)
5. Test date
6. Specimen type if available
7. Ordering provider name if available

Return as JSON array with structure:
[
  {
    "test_name": "Glucose, Fasting",
    "result_value": "105 mg/dL",
    "reference_range": "70-100 mg/dL",
    "abnormal_flag": "HIGH",
    "test_date": "2026-02-10",
    "specimen_type": "Serum",
    "ordering_provider": "Dr. Smith"
  }
]

Return empty array [] if no lab results found.
""",
            
            "vitals": """
Extract all vital sign measurements from this health document.

For each vital sign found, extract:
1. Vital type (BP, HR, Temp, RR, O2Sat, Weight, Height, BMI)
2. Value with units (e.g., "120/80 mmHg")
3. Measurement date
4. Provider name if available
5. Notes if available

Return as JSON array:
[
  {
    "vital_type": "BP",
    "value": "120/80 mmHg",
    "measured_date": "2026-02-12",
    "provider": "Dr. Johnson",
    "notes": "Patient sitting, right arm"
  }
]

Return empty array [] if no vitals found.
""",
            
            "medications": """
Extract all medications from this health document.

For each medication found, extract:
1. Medication name/trade name
2. Dosage (e.g., "500 mg")
3. Frequency (e.g., "twice daily")
4. Start date
5. End date (if discontinued)
6. Indication/reason if available
7. Prescribing provider
8. Current status (active, discontinued, stopped)

Return as JSON array:
[
  {
    "medication_name": "Metformin",
    "dosage": "500 mg",
    "frequency": "twice daily",
    "start_date": "2024-06-15",
    "end_date": null,
    "indication": "Type 2 Diabetes",
    "prescribing_provider": "Dr. Smith",
    "status": "active"
  }
]

Return empty array [] if no medications found.
""",
            
            "conditions": """
Extract all diagnosed conditions from this health document.

For each condition found, extract:
1. Condition/diagnosis name
2. ICD code if available
3. Onset date if available
4. Current status (active, resolved, inactive)
5. Severity if noted (mild, moderate, severe)
6. Notes

Return as JSON array:
[
  {
    "condition_name": "Type 2 Diabetes Mellitus",
    "icd_code": "E11.9",
    "onset_date": "2018-06-01",
    "status": "active",
    "severity": "moderate",
    "notes": "Well-controlled with medication"
  }
]

Return empty array [] if no conditions found.
""",
            
            "allergies": """
Extract all allergies and adverse reactions from this health document.

For each allergy found, extract:
1. Allergen (drug, food, environmental)
2. Reaction description
3. Severity (mild, moderate, severe, life-threatening)
4. Onset date if available
5. Current status

Return as JSON array:
[
  {
    "allergen": "Penicillin",
    "reaction": "Rash, itching",
    "severity": "moderate",
    "onset_date": "2015-03-20",
    "status": "active"
  }
]

Return empty array [] if no allergies found.
""",
            
            "immunizations": """
Extract all vaccinations from this health document.

For each vaccine found, extract:
1. Vaccine name (e.g., "COVID-19 (Pfizer-BioNTech)")
2. Administration date
3. Route (IM, IV, oral, intranasal)
4. Site of injection if noted
5. Dose number if part of series
6. Administering provider
7. Lot number if available
8. Next dose date if scheduled

Return as JSON array:
[
  {
    "vaccine_name": "COVID-19 (Pfizer-BioNTech)",
    "administration_date": "2026-01-15",
    "route": "IM",
    "site": "L arm",
    "dose_number": 1,
    "administering_provider": "Nurse Johnson",
    "lot_number": "ABC123",
    "next_dose_date": null
  }
]

Return empty array [] if no immunizations found.
"""
        }
    
    def extract_from_pdf(self, pdf_path: str, patient_identity: str) -> Tuple[List[HealthRecord], Dict[str, Any]]:
        """
        Extract health records from a PDF document
        
        Args:
            pdf_path: Path to PDF file
            patient_identity: Patient name/identifier
            
        Returns:
            Tuple of (extracted HealthRecords, extraction statistics)
        """
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        # For demo purposes, show extraction workflow
        # In production, this would use pypdf or pdfplumber to read PDF
        # and Claude to extract content via vision API
        
        extracted_records = []
        extraction_stats = {
            "source_file": Path(pdf_path).name,
            "extraction_date": datetime.now().isoformat(),
            "total_records_extracted": 0,
            "by_type": {},
            "extraction_confidence_avg": 0.0,
            "errors": [],
        }
        
        # Simulate extraction for demo
        # In production, this would call Claude with PDF content
        
        record_types_to_extract = [
            ("lab_results", RecordClass.LAB, 0.95),
            ("vitals", RecordClass.VITAL, 0.98),
            ("medications", RecordClass.MEDICATION, 0.90),
            ("conditions", RecordClass.CONDITION, 0.85),
            ("allergies", RecordClass.ALLERGY, 0.92),
            ("immunizations", RecordClass.IMMUNIZATION, 0.93),
        ]
        
        confidence_scores = []
        
        for record_type_key, record_class, confidence in record_types_to_extract:
            try:
                # This would call Claude API in production
                records = self._extract_record_type(
                    pdf_path,
                    record_type_key,
                    record_class,
                    patient_identity,
                    confidence,
                )
                
                extracted_records.extend(records)
                extraction_stats["by_type"][record_class.value] = len(records)
                
                confidence_scores.extend([confidence] * len(records))
                
            except Exception as e:
                extraction_stats["errors"].append({
                    "type": record_type_key,
                    "error": str(e),
                })
        
        # Calculate statistics
        extraction_stats["total_records_extracted"] = len(extracted_records)
        if confidence_scores:
            extraction_stats["extraction_confidence_avg"] = sum(confidence_scores) / len(confidence_scores)
        
        return extracted_records, extraction_stats
    
    def _extract_record_type(
        self,
        pdf_path: str,
        record_type_key: str,
        record_class: RecordClass,
        patient_identity: str,
        confidence: float,
    ) -> List[HealthRecord]:
        """
        Extract specific record type from PDF
        
        Args:
            pdf_path: Path to PDF
            record_type_key: Type of record (lab_results, medications, etc.)
            record_class: RecordClass enum
            patient_identity: Patient identifier
            confidence: Extraction confidence score
            
        Returns:
            List of extracted HealthRecords
        """
        records = []
        
        # In production, this would:
        # 1. Read PDF content (pypdf or pdfplumber)
        # 2. Call Claude API with vision capability
        # 3. Parse Claude's response as JSON
        # 4. Validate extracted data
        # 5. Create HealthRecord objects
        
        # For demonstration, return empty list
        # This lets the system show extraction capability
        
        return records
    
    def validate_extraction(self, records: List[HealthRecord]) -> Dict[str, Any]:
        """
        Validate extracted records for quality
        
        Args:
            records: Extracted health records
            
        Returns:
            Validation report
        """
        validation_report = {
            "total_records": len(records),
            "valid_records": 0,
            "invalid_records": 0,
            "warnings": [],
            "errors": [],
        }
        
        for i, record in enumerate(records):
            try:
                # Validate required fields
                if not record.patient_identity:
                    validation_report["warnings"].append(
                        f"Record {i}: Missing patient_identity"
                    )
                
                if not record.record_class:
                    validation_report["errors"].append(
                        f"Record {i}: Missing record_class"
                    )
                    continue
                
                if not record.record_date:
                    validation_report["warnings"].append(
                        f"Record {i}: Missing record_date"
                    )
                
                # Check extraction confidence
                if record.extraction_confidence and record.extraction_confidence < 0.7:
                    validation_report["warnings"].append(
                        f"Record {i}: Low confidence score ({record.extraction_confidence})"
                    )
                
                validation_report["valid_records"] += 1
                
            except Exception as e:
                validation_report["errors"].append(f"Record {i}: {str(e)}")
                validation_report["invalid_records"] += 1
        
        return validation_report
    
    def extract_and_prepare(
        self,
        pdf_path: str,
        patient_identity: str,
    ) -> Dict[str, Any]:
        """
        Extract from PDF and prepare for MCP import
        
        Args:
            pdf_path: Path to PDF file
            patient_identity: Patient identifier
            
        Returns:
            Dictionary with extracted records and metadata ready for import
        """
        # Extract records
        records, extraction_stats = self.extract_from_pdf(pdf_path, patient_identity)
        
        # Validate extraction
        validation = self.validate_extraction(records)
        
        # Prepare for MCP import
        mcp_payload = {
            "patient_identity": patient_identity,
            "records": [r.model_dump() for r in records],
            "import_source": f"pdf_extraction:{Path(pdf_path).name}",
            "metadata": {
                "extraction_stats": extraction_stats,
                "validation_report": validation,
                "extraction_timestamp": datetime.now().isoformat(),
            },
        }
        
        return mcp_payload


def create_sample_extraction() -> Dict[str, Any]:
    """
    Create a sample extraction result for demonstration
    
    Returns:
        Sample MCP payload with test records
    """
    from datetime import timedelta
    
    today = date.today()
    
    sample_records = [
        HealthRecord(
            record_class=RecordClass.LAB,
            record_date=today - timedelta(days=5),
            patient_identity="Demo Patient",
            provider_identity="Dr. Sarah Johnson, MD",
            data={
                "test_name": "Comprehensive Metabolic Panel",
                "result_value": "Normal",
                "test_date": str(today - timedelta(days=5)),
            },
            extraction_confidence=0.96,
            source_document="health_records_202602.pdf",
        ),
        HealthRecord(
            record_class=RecordClass.VITAL,
            record_date=today - timedelta(days=2),
            patient_identity="Demo Patient",
            provider_identity="Nurse Maria",
            data={
                "vital_type": "BP",
                "value": "118/76 mmHg",
                "measured_date": str(today - timedelta(days=2)),
            },
            extraction_confidence=0.99,
            source_document="health_records_202602.pdf",
        ),
        HealthRecord(
            record_class=RecordClass.MEDICATION,
            record_date=today,
            patient_identity="Demo Patient",
            data={
                "medication_name": "Lisinopril",
                "dosage": "10 mg",
                "frequency": "once daily",
                "status": "active",
            },
            extraction_confidence=0.93,
            source_document="health_records_202602.pdf",
        ),
    ]
    
    return {
        "patient_identity": "Demo Patient",
        "records": [r.model_dump() for r in sample_records],
        "import_source": "pdf_extraction:demo_health_records.pdf",
        "metadata": {
            "extraction_stats": {
                "source_file": "demo_health_records.pdf",
                "extraction_date": datetime.now().isoformat(),
                "total_records_extracted": 3,
                "by_type": {"LAB": 1, "VITAL": 1, "MEDICATION": 1},
                "extraction_confidence_avg": 0.96,
            },
            "validation_report": {
                "total_records": 3,
                "valid_records": 3,
                "invalid_records": 0,
                "warnings": [],
                "errors": [],
            },
        },
    }
