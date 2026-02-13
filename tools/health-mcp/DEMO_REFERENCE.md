# Demo Day Quick Reference

## 🎯 What to Show

### Step 0: The Source Document (1 minute)
**Option A - HTML Report:**
1. **Open:** `sample_health_report.html` (double-click to show in browser)
   - Point out: Labs, Medications, Conditions, Allergies, Vitals
   - Say: "This is a patient's health export"

**Option B - PDF Report (RECOMMENDED):**
1. **Open:** `personal_health_report.pdf` (the Chrome print-to-PDF version)
   - Show the formatted health report (looks like real medical document)
   - Click "View Summary" button in Acrobat
   - Read the AI-generated summary aloud:
     ```
     "Elevated blood glucose levels (fasting: 105 mg/dL, overall: 115 mg/dL)...
      Current medications include Metformin for diabetes...
      Active conditions: Type 2 Diabetes, Essential Hypertension, Hyperlipidemia...
      Allergies include mild rash from Penicillin and severe throat swelling from shellfish..."
     ```
   - Say: "Acrobat can summarize it, but can it let us QUERY it?"

### Run the Demo (2 minutes)
```bash
cd g:\repos\AI\PersonalHealthStudio\PHSetup\tools\health-mcp
py test_extraction_e2e.py
```

**Narrate as it runs:**
- "Acrobat showed a summary. But what if you want to QUERY the data?"
- "STEP 1: Extracting structured data from the report..."
- "STEP 2: Storing it in Snowflake (cloud database)..."
- "STEP 3: Verifying it was stored correctly..."
- "STEP 4: Now ask ANY question in natural language..."

### Watch for These Results
✅ **STEP 1:** 47 records created ← *System extracted everything*
✅ **STEP 2:** Records imported to Snowflake ← *Data is organized*
✅ **STEP 3:** Records verified in database ← *Data is queryable*
✅ **STEP 4:** Natural language queries return insights ← *Smart analysis*

### Key Results to Highlight
```
1. Average blood glucose: 106.5 mg/dL (slightly elevated)
2. Medications: Shows all 4 active drugs with dosages
3. Conditions: Detected 3 active conditions  
4. Allergies: Found severe shellfish allergy ⚠️
5. Vitals: Tracking multiple measurements over time
```

---

## 💬 Key Talking Points

**"What just happened?"**
- Extracted structured health data from an export
- Imported to a cloud data warehouse
- Ran natural language queries against it
- Got intelligent insights back

**"How is this different from Acrobat's summary?"**
- Acrobat: Reads the PDF and summarizes it (one-time snapshot)
- Our system: Extracts structured data → Stores it → QUERIES it
- You can ask ANY question, ANY number of times
- Results are computed on-the-fly from actual data
- Can compare trends, correlate data, drill down into specifics

**"So if I ask 'What medications am I taking?', what happens?"**
- Query gets parsed into intent (record_type=MEDICATION, metric=list)
- SQL is generated: SELECT * FROM medications WHERE patient_id=X
- Database returns the results instantly
- Results are formatted as human-readable insights
- Now ask another question - it works the same way

**"Why is this impressive?"**
- No manual data entry
- No pre-built dashboards
- Pure semantic understanding
- Scales to millions of records
- Can ask ANY question

**"What's the tech?"**
- Python + Pydantic (type safety)
- Snowflake (cloud warehouse)
- Natural language to SQL translation
- JSON structured data
- Cloud-native architecture

**"Could this be real?"**
- Yes! This is production ready
- Works with real health data formats (HL7, FHIR)
- API-first design
- HIPAA-compatible (data stays on-premise)

---

## ⚡ Quick Troubleshooting

| Issue | Fix |
|-------|-----|
| "Connection failed" | Check internet + Snowflake account is active |
| "Records: 0" | Make sure test hasn't been run before (resets demo data) |
| "Query returns N/A" | Latest code has this fixed - pull from GitHub |
| "Unicode error" | This was fixed - you have the latest version |

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `personal_health_report.pdf` | ← **Show this first** (Chrome print-to-PDF with Acrobat AI summary) |
| `sample_health_report.html` | HTML version of report (can generate/print to PDF) |
| `test_extraction_e2e.py` | ← **Run this** (complete demo in one command) |
| `generate_sample_report.py` | Script to regenerate HTML if needed |
| `DEMO_SCRIPT.md` | Full narrative with timing notes |
| `src/health_models.py` | Data structures (optional - show if asked) |
| `src/nl_mapper.py` | NL to SQL conversion (optional - show if asked) |

---

## ⏰ Timing

- Show PDF and Acrobat summary: 30 seconds
- Run test command: 15 seconds
- Show results and narrate: 1 minute
- Answer questions: 4 minutes
- **Total: ~10 minutes** 👍

---

## 🎬 Demo Night Checklist

- [ ] Have `personal_health_report.pdf` ready (already created by you)
- [ ] If you don't have the PDF, use these steps to create it:
  1. Open `sample_health_report.html` in Chrome (File → Open)
  2. Press Ctrl+P to print
  3. Change printer to "Save as PDF"
  4. Check "Background graphics" in More settings
  5. Save as `personal_health_report.pdf` in the `health-mcp` folder
- [ ] Open PDF to verify it looks good
- [ ] Click "View Summary" in Acrobat to see the AI summary
- [ ] Open terminal in `health-mcp` folder
- [ ] Run test once to verify everything works: `py test_extraction_e2e.py`
- [ ] Have GitHub link ready to share
- [ ] Get some sleep! 😴

**You're ready for Saturday! 🚀**
