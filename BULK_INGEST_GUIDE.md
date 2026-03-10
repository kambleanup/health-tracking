# Bulk Health Data Ingestion Guide

## Overview

You have **19 lab reports spanning 2011-2025** already organized in `C:\Projects\health\ASK\` by year. This guide will help you:

1. Process all PDFs through the AI extraction pipeline
2. Populate your Obsidian vault with 14 years of health history
3. Generate comprehensive trend analysis
4. Create a complete health timeline

---

## Your Historical Data

### Data Summary

```
Total Reports: 19 PDFs
Date Range: December 2011 - October 2025 (14 years)
Folder: C:\Projects\health\ASK\

Breakdown by Year:
2011 (1):  blood_urine_tests_18Dec2011.pdf
2012 (1):  LabResults_AK_2012.pdf
2014 (1):  AK2014_Labs.pdf
2015 (1):  Letter; Lab Results Male - Boyd2015.pdf
2017 (1):  Anup Kamble Labs 2017.pdf
2018 (1):  Anup Kamble Lab Results2018.pdf
2022 (1):  AKLABS2022.pdf
2023 (1):  AKLABS_2023_0220.pdf
2024 (1):  ASK_LABS_2024.pdf
2025 (9):
  - Mar2025: CBC, CMP, HbA1c, Lipid Panel, TSH, Hemoglobin/GI/Stool
  - Oct2025: CBC, CMP, Lipid Panel, VitaminD
```

---

## Installation

### 1. Install PDF Processing Dependencies

```bash
cd C:\Projects\health\agent
python -m pip install pdfplumber pillow
```

This enables PDF extraction and image processing for Claude Vision API.

### 2. Verify Installation

```bash
python -c "import pdfplumber; print('PDF support ready')"
```

---

## Bulk Ingestion Process

### Option A: Dry Run (Recommended First)

See what will be processed without making changes:

```bash
cd C:\Projects\health
python agent/bulk_ingest.py --dry-run
```

Expected output:
```
[INFO] Found 19 PDF files to process
[INFO] Starting bulk ingestion from C:/Projects/health/ASK
[INFO] DRY RUN MODE - no changes will be made
...
====================================================
INGESTION RESULTS
====================================================
Total files: 19
Successful: 0
Failed: 0
Skipped: 19
```

### Option B: Full Ingestion

Process all PDFs and populate vault:

```bash
cd C:\Projects\health
python agent/bulk_ingest.py
```

This will:
1. Read each PDF from `C:\Projects\health\ASK\`
2. Use Claude Vision API to extract metrics
3. Create markdown files in `vault/People/Anup/Reports/`
4. Organize by report date (YYYY-MM-DD_ReportType.md)

**Estimated time:** 5-10 minutes (depends on Claude API response time)

### Option C: Custom Source/Destination

```bash
python agent/bulk_ingest.py \
  --source C:\Projects\health\ASK \
  --vault C:\Projects\health\vault \
  --person Anup
```

---

## What Gets Created

After ingestion, your vault will contain:

```
vault/People/Anup/Reports/
├── 2011-12-18_Blood-Work.md
├── 2012-XX-XX_Lab-Work.md
├── 2014-XX-XX_Lab-Work.md
├── 2015-XX-XX_Lab-Work.md
├── 2017-XX-XX_Lab-Work.md
├── 2018-XX-XX_Lab-Work.md
├── 2022-XX-XX_Lab-Work.md
├── 2023-XX-XX_Lab-Work.md
├── 2024-XX-XX_Lab-Work.md
└── 2025-03-13_Blood-Work.md (multiple tests)
└── 2025-10-03_Blood-Work.md (multiple tests)
```

Each file contains:
- **YAML Frontmatter:** All extracted metrics (glucose, cholesterol, A1C, etc.)
- **Structured Sections:** Organized by metric category
- **Searchable:** Full-text search in Obsidian

---

## Generate Historical Timeline

After ingestion, create a 14-year health trend analysis:

```bash
cd C:\Projects\health
python agent/health_timeline.py
```

This generates `vault/People/Anup/Summaries/Health-Timeline.md` showing:
- Glucose trends (2011-2025)
- Cholesterol trends (total, HDL, LDL)
- A1C progression
- Triglycerides trends
- Other key metrics

---

## Manual PDF Organization (Optional)

If you're adding new PDFs to process:

```
raw_reports/
└── Anup/
    ├── 2025-03-13_BloodWork.pdf
    ├── 2025-03-13_Lipid.pdf
    └── 2025-03-13_TSH.pdf
```

Then ingest:
```bash
python -m agent.main ingest --person anup --pdf raw_reports/Anup/2025-03-13_BloodWork.pdf
```

---

## Viewing Your Data in Obsidian

### 1. Open Vault

- Launch Obsidian
- Open folder: `C:\Projects\health\vault`

### 2. Browse Reports

- Click: `People → Anup → Reports`
- See all parsed lab reports chronologically

### 3. View Timeline

- Click: `People → Anup → Summaries → Health-Timeline.md`
- See 14-year trend analysis

### 4. Dashboard

- Click: `Dashboard.md`
- See aggregate queries with Dataview plugin

---

## Expected Metrics Extracted

The system extracts these key lab metrics from your PDFs:

```
Glucose Metabolism:
- Glucose, A1C (HbA1c)

Lipid Panel:
- Total Cholesterol, HDL, LDL, Triglycerides

Thyroid:
- TSH

Renal Function:
- Creatinine, BUN, GFR

Electrolytes:
- Sodium, Potassium, Magnesium, Calcium, Phosphorus

Liver Function:
- ALT, AST, Alkaline Phosphatase, Albumin, Total Protein

Complete Blood Count:
- Hemoglobin, Hematocrit, WBC, RBC, Platelet Count
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pdfplumber'"

**Solution:**
```bash
python -m pip install pdfplumber pillow
```

### Issue: "ANTHROPIC_API_KEY not found"

**Solution:** Set your API key:
```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-xxxxx"

# Windows Command Prompt
set ANTHROPIC_API_KEY=sk-ant-xxxxx

# Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

Or edit `agent/config.yaml`:
```yaml
anthropic:
  api_key: "sk-ant-xxxxx"
```

### Issue: "Rate Limited" errors from Claude API

**Solution:** Add a delay between PDFs. Modify `bulk_ingest.py` to add:
```python
import time
time.sleep(5)  # 5 second delay between requests
```

### Issue: Some PDFs fail to extract metrics

**Reasons:**
- Poor PDF quality / scanned images
- Non-standard format
- Protected/encrypted PDF

**Solution:** Manually review and extract key metrics, then update the markdown file directly.

---

## Next Steps

1. **Run dry-run:** `python agent/bulk_ingest.py --dry-run`
2. **Install pdfplumber:** `pip install pdfplumber pillow`
3. **Run ingestion:** `python agent/bulk_ingest.py`
4. **Generate timeline:** `python agent/health_timeline.py`
5. **Open in Obsidian:** Launch Obsidian and open vault folder
6. **Explore data:** Browse reports and summaries

---

## Advanced: Adding More PDFs

As you add new lab reports to `ASK/2026/`, simply:

```bash
# Re-run bulk ingest to process new files
python agent/bulk_ingest.py

# Or ingest individual PDFs
python -m agent.main ingest --person anup --pdf "path/to/new/report.pdf"
```

---

## Questions?

For complete CLI reference, run:
```bash
python -m agent.main --help
python -m agent.main ingest --help
python -m agent.main analyze --help
```

Good luck with your health data organization!
