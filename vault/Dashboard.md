# Health Dashboard

Welcome to the personal health tracking system for Anup and Deepali.

## Quick Navigation

### Anup's Health
- [Full Profile](People/Anup/Profile.md)
- [Lab Reports](People/Anup/Reports)
- [Health Metrics](People/Anup/Metrics)
- [Monthly Summaries](People/Anup/Summaries)

### Deepali's Health
- [Full Profile](People/Deepali/Profile.md)
- [Lab Reports](People/Deepali/Reports)
- [Health Metrics](People/Deepali/Metrics)
- [Monthly Summaries](People/Deepali/Summaries)

---

## Recent Lab Reports

```dataview
TABLE person, report_type, doctor, lab
FROM "vault/People"
WHERE file.path contains "Reports"
SORT date descending
LIMIT 10
```

---

## Recent Vital Signs - Anup

```dataview
TABLE date, "BP (Systolic/Diastolic)", "Weight (lbs)", "HR (bpm)"
FROM "vault/People/Anup/Metrics"
WHERE file.name = "Vital-Signs"
LIMIT 5
```

## Recent Vital Signs - Deepali

```dataview
TABLE date, "BP (Systolic/Diastolic)", "Weight (lbs)", "HR (bpm)"
FROM "vault/People/Deepali/Metrics"
WHERE file.name = "Vital-Signs"
LIMIT 5
```

---

## Recent Activity - Anup

```dataview
TABLE date, steps, "Active Min", calories, "Sleep (hrs)"
FROM "vault/People/Anup/Metrics"
WHERE file.name = "Garmin-Activity"
LIMIT 7
```

## Recent Activity - Deepali

```dataview
TABLE date, steps, "Active Min", calories, "Sleep (hrs)"
FROM "vault/People/Deepali/Metrics"
WHERE file.name = "Garmin-Activity"
LIMIT 7
```

---

## Health Alerts

This section shows recent alerts from health metrics analysis. Alerts are generated automatically when metrics cross defined thresholds.

**For Anup:**
- Blood Pressure Alert: Systolic > 140 mmHg
- Glucose Alert: > 120 mg/dL
- Cholesterol Alert: > 200 mg/dL

**For Deepali:**
- Blood Pressure Alert: Systolic > 140 mmHg
- Glucose Alert: > 120 mg/dL
- Cholesterol Alert: > 200 mg/dL

---

## Monthly Summaries

### Anup's Latest Summaries
```dataview
TABLE month, year
FROM "vault/People/Anup/Summaries"
SORT year descending, month descending
LIMIT 6
```

### Deepali's Latest Summaries
```dataview
TABLE month, year
FROM "vault/People/Deepali/Summaries"
SORT year descending, month descending
LIMIT 6
```

---

## Templates

Quick access to templates for logging new data:

- [Lab Report Template](Templates/Lab-Report.md) — Use when creating a new lab report entry
- [Vital Signs Log Template](Templates/Vital-Log.md) — Use for manual vital sign logging
- [Monthly Summary Template](Templates/Monthly-Summary.md) — AI-generated health summaries

---

## Data Sources

This vault integrates health data from:

1. **PDF Lab Reports** — Parsed via Claude Vision API for metric extraction
   - Quest Diagnostics, LabCorp, and other major labs
   - Automatically extracted metrics: glucose, cholesterol, thyroid, kidney, liver, blood counts

2. **Garmin Connect** — Daily synced activity data
   - Steps, active minutes, calories burned
   - Heart rate (average and max)
   - Sleep duration and quality
   - Stress levels and body battery

3. **Manual Entries** — Vital sign logging
   - Weight, blood pressure, heart rate, temperature
   - Notes and observations

---

## System Status

- **Last Garmin Sync:** [Check sync logs]
- **Last PDF Ingestion:** [Check ingestion logs]
- **Vault Size:** Automatically tracked by Obsidian
- **Theme:** Currently using default theme

---

## Usage Instructions

### Adding a New Lab Report

1. Save the PDF to `raw_reports/{person}/`
2. Run: `python agent/main.py ingest --person {anup|deepali} --pdf path/to/report.pdf`
3. Review the generated note in `People/{person}/Reports/`

### Syncing Garmin Data

```bash
python agent/main.py sync-garmin --days 7
```

### Logging Vital Signs

```bash
python agent/main.py log-vitals --person anup --weight 180 --systolic 120 --diastolic 80 --hr 60
```

### Generating Monthly Analysis

```bash
python agent/main.py analyze --person anup --period monthly
```

---

## Notes

- All timestamps are in local timezone
- Metrics thresholds are customizable in `agent/config.yaml`
- The system respects data privacy — all files remain local
- Use Dataview plugin for live queries and aggregations
