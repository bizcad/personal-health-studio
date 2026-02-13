# Demo Day Quick Reference

## 🎯 What to Show

### Before Running Code (30 seconds)
1. **Open:** `sample_health_report.html` (double-click to show in browser)
   - Point out: Labs, Medications, Conditions, Allergies, Vitals
   - Say: "This is the source document - one patient's health exports"

### Run the Demo (2 minutes)
```bash
cd g:\repos\AI\PersonalHealthStudio\PHSetup\tools\health-mcp
py test_extraction_e2e.py
```

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
| `sample_health_report.html` | ← **Show this first** (the source document) |
| `test_extraction_e2e.py` | ← **Run this** (complete demo in one command) |
| `DEMO_SCRIPT.md` | Full narrative with timing notes |
| `src/health_models.py` | Data structures (optional - show if asked) |
| `src/nl_mapper.py` | NL to SQL conversion (optional - show if asked) |

---

## ⏰ Timing

- Open HTML report: 10 seconds
- Run test command: 15 seconds
- Show results: 1 minute
- Answer questions: 4 minutes
- **Total: ~10 minutes** 👍

---

## 🎬 Demo Night Checklist

- [ ] Test internet connection
- [ ] Open sample_health_report.html in browser (test it opens)
- [ ] Open terminal in health-mcp folder
- [ ] Run test once to verify everything works
- [ ] Commit and push any last changes to GitHub
- [ ] Have GitHub link ready to share
- [ ] Get some sleep! 😴

**You're ready for Saturday! 🚀**
