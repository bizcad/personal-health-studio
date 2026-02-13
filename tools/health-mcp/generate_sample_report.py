#!/usr/bin/env python3
"""
Generate a sample health report HTML that can be printed to PDF

This script creates the sample_health_report.html file.
To convert to PDF:
1. Open sample_health_report.html in Chrome
2. Press Ctrl+P (Print)
3. Change printer to "Save as PDF"
4. Check "Background graphics"
5. Click "Save"
6. Save as "personal_health_report.pdf"

The PDF can then be opened in Acrobat where you can see:
- The formatted health report
- Acrobat's AI-generated summary (if available)
- All structured health data

For the demo, this shows:
1. Real source document (PDF)
2. AI extraction possible (Acrobat summary)
3. Your system's structured extraction and querying
"""

def generate_html():
    """Generate the sample health report HTML"""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Health Report - John Smith</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        @page {
            size: letter;
            margin: 0.5in;
        }
        .header {
            background-color: #1e88e5;
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 30px;
            text-align: center;
            page-break-after: avoid;
        }
        .header h1 {
            margin: 0;
            font-size: 28px;
        }
        .header p {
            margin: 5px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .section {
            background-color: white;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            page-break-inside: avoid;
        }
        .section h2 {
            color: #1e88e5;
            border-bottom: 2px solid #1e88e5;
            padding-bottom: 10px;
            margin-top: 0;
        }
        .section h3 {
            color: #333;
            margin-top: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f0f0f0;
            font-weight: 600;
            color: #333;
        }
        tr:hover {
            background-color: #f9f9f9;
        }
        .abnormal {
            color: #d32f2f;
            font-weight: 600;
        }
        .normal {
            color: #388e3c;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 12px;
            font-weight: 600;
        }
        .badge-abnormal {
            background-color: #ffcdd2;
            color: #c62828;
        }
        .badge-normal {
            background-color: #c8e6c9;
            color: #2e7d32;
        }
        .footer {
            text-align: center;
            color: #666;
            font-size: 12px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
        }
        .medication-list {
            background-color: #f5f5f5;
            padding: 15px;
            border-left: 4px solid #1e88e5;
            margin: 10px 0;
        }
        .medication-item {
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-radius: 3px;
        }
        .allergy-alert {
            background-color: #ffe0b2;
            border-left: 4px solid #f57c00;
            padding: 15px;
            margin: 15px 0;
            border-radius: 3px;
        }
        .timestamp {
            color: #999;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Personal Health Report</h1>
        <p>Patient: John Smith | DOB: 1975-03-15 | Report Date: February 12, 2026</p>
    </div>

    <div class="section">
        <h2>Recent Laboratory Results</h2>
        <p><span class="timestamp">Last Updated: 2026-02-10</span></p>
        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Result Value</th>
                    <th>Reference Range</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Blood Glucose (Fasting)</td>
                    <td class="abnormal">105 mg/dL</td>
                    <td>70-100 mg/dL</td>
                    <td><span class="badge badge-abnormal">HIGH</span></td>
                </tr>
                <tr>
                    <td>Blood Glucose</td>
                    <td class="abnormal">115 mg/dL</td>
                    <td>70-100 mg/dL</td>
                    <td><span class="badge badge-abnormal">HIGH</span></td>
                </tr>
                <tr>
                    <td>Hemoglobin A1C</td>
                    <td class="abnormal">6.8%</td>
                    <td>&lt;5.7%</td>
                    <td><span class="badge badge-abnormal">HIGH</span></td>
                </tr>
                <tr>
                    <td>Total Cholesterol</td>
                    <td class="abnormal">220 mg/dL</td>
                    <td>&lt;200 mg/dL</td>
                    <td><span class="badge badge-abnormal">HIGH</span></td>
                </tr>
                <tr>
                    <td>HDL Cholesterol</td>
                    <td class="normal">42 mg/dL</td>
                    <td>&gt;40 mg/dL</td>
                    <td><span class="badge badge-normal">NORMAL</span></td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Current Active Medications</h2>
        <p><span class="timestamp">Last Reviewed: 2026-02-08</span></p>
        <div class="medication-list">
            <div class="medication-item">
                <strong>Metformin 500 mg</strong><br>
                Frequency: Twice daily<br>
                Indication: Type 2 Diabetes Management<br>
                Started: 2024-06-15
            </div>
            <div class="medication-item">
                <strong>Lisinopril 10 mg</strong><br>
                Frequency: Once daily<br>
                Indication: Hypertension Control<br>
                Started: 2025-01-20
            </div>
            <div class="medication-item">
                <strong>Atorvastatin 20 mg</strong><br>
                Frequency: Once daily<br>
                Indication: Cholesterol Management<br>
                Started: 2025-08-10
            </div>
            <div class="medication-item">
                <strong>Aspirin 81 mg</strong><br>
                Frequency: Once daily<br>
                Indication: Cardiovascular Protection<br>
                Started: 2024-12-01
            </div>
        </div>
    </div>

    <div class="section">
        <h2>Active Medical Conditions</h2>
        <p><span class="timestamp">Last Updated: 2026-02-05</span></p>
        <table>
            <thead>
                <tr>
                    <th>Condition</th>
                    <th>ICD-10 Code</th>
                    <th>Status</th>
                    <th>Onset Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Type 2 Diabetes Mellitus</td>
                    <td>E11.9</td>
                    <td><span class="badge badge-abnormal">ACTIVE</span></td>
                    <td>2018-05-10</td>
                </tr>
                <tr>
                    <td>Essential Hypertension</td>
                    <td>I10</td>
                    <td><span class="badge badge-abnormal">ACTIVE</span></td>
                    <td>2015-03-22</td>
                </tr>
                <tr>
                    <td>Hyperlipidemia</td>
                    <td>E78.5</td>
                    <td><span class="badge badge-abnormal">ACTIVE</span></td>
                    <td>2019-07-14</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Allergies & Sensitivities</h2>
        <p><span class="timestamp">Last Updated: 2026-02-01</span></p>
        <div class="allergy-alert">
            <strong style="color: #e65100;">⚠ ALLERGY: Penicillin</strong><br>
            Reaction: Rash (mild)<br>
            Severity: Mild
        </div>
        <div class="allergy-alert">
            <strong style="color: #e65100;">⚠ ALLERGY: Shellfish</strong><br>
            Reaction: Angioedema (throat swelling)<br>
            Severity: Severe
        </div>
    </div>

    <div class="section">
        <h2>Immunization Records</h2>
        <p><span class="timestamp">Last Updated: 2026-02-12</span></p>
        <table>
            <thead>
                <tr>
                    <th>Vaccine</th>
                    <th>Dose</th>
                    <th>Administration Date</th>
                    <th>Provider</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Influenza (Flu Shot)</td>
                    <td>Dose 1</td>
                    <td>2026-01-15</td>
                    <td>Main Street Clinic</td>
                </tr>
                <tr>
                    <td>COVID-19</td>
                    <td>Dose 3 (Booster)</td>
                    <td>2026-01-08</td>
                    <td>CVS Pharmacy</td>
                </tr>
                <tr>
                    <td>Tdap (Tetanus, Diphtheria, Pertussis)</td>
                    <td>Dose 1</td>
                    <td>2025-11-20</td>
                    <td>Main Street Clinic</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>Recent Vital Signs</h2>
        <p><span class="timestamp">Last Updated: 2026-02-09</span></p>
        <table>
            <thead>
                <tr>
                    <th>Vital</th>
                    <th>Latest Reading</th>
                    <th>Normal Range</th>
                    <th>Status</th>
                    <th>Date</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Blood Pressure</td>
                    <td class="abnormal">140/90 mmHg</td>
                    <td>&lt;120/80 mmHg</td>
                    <td><span class="badge badge-abnormal">ELEVATED</span></td>
                    <td>2026-02-09</td>
                </tr>
                <tr>
                    <td>Heart Rate</td>
                    <td class="normal">72 bpm</td>
                    <td>60-100 bpm</td>
                    <td><span class="badge badge-normal">NORMAL</span></td>
                    <td>2026-02-09</td>
                </tr>
                <tr>
                    <td>Weight</td>
                    <td>185 lbs</td>
                    <td>Varies</td>
                    <td><span class="badge badge-normal">STABLE</span></td>
                    <td>2026-02-09</td>
                </tr>
                <tr>
                    <td>Temperature</td>
                    <td class="normal">98.6°F</td>
                    <td>98.6°F</td>
                    <td><span class="badge badge-normal">NORMAL</span></td>
                    <td>2026-02-09</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div class="footer">
        <p>This is an automated health report generated from patient health records.</p>
        <p>Exported from Personal Health Studio - Health Intelligence Platform</p>
        <p>Report generated: February 12, 2026 at 18:44 UTC</p>
    </div>
</body>
</html>
"""
    return html

if __name__ == "__main__":
    print("Generating sample health report HTML...")
    html_content = generate_html()
    
    with open("sample_health_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print("✓ Generated: sample_health_report.html")
    print("\nTo convert to PDF:")
    print("1. Open sample_health_report.html in Chrome")
    print("2. Press Ctrl+P (Print)")
    print("3. Change printer to 'Save as PDF'")
    print("4. Check 'Background graphics'")
    print("5. Click 'Save'")
    print("6. Save as 'personal_health_report.pdf'")
    print("\nThen open in Acrobat to see AI summary feature")
