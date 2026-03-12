---
person:
date:
report_type: Blood Work
doctor:
lab:
tags: [labs]
metrics:
  glucose:
  cholesterol_total:
  hdl:
  ldl:
  triglycerides:
  a1c:
  tsh:
  creatinine:
  bun:
  gfr:
  sodium:
  potassium:
  magnesium:
  calcium:
  phosphorus:
  alt:
  ast:
  alkaline_phosphatase:
  albumin:
  total_protein:
  hemoglobin:
  hematocrit:
  wbc:
  rbc:
  platelet_count:
---

# Lab Report - {{date}}

**Person:** {{person}}
**Date:** {{date}}
**Doctor:** {{doctor}}
**Lab:** {{lab}}
**Report Type:** {{report_type}}

## Key Results

### Glucose Metabolism
- Glucose: {{metrics.glucose}} mg/dL
- A1C: {{metrics.a1c}}%

### Lipid Panel
- Total Cholesterol: {{metrics.cholesterol_total}} mg/dL
- HDL: {{metrics.hdl}} mg/dL
- LDL: {{metrics.ldl}} mg/dL
- Triglycerides: {{metrics.triglycerides}} mg/dL

### Thyroid
- TSH: {{metrics.tsh}} mIU/L

### Renal Function
- Creatinine: {{metrics.creatinine}} mg/dL
- BUN: {{metrics.bun}} mg/dL
- GFR: {{metrics.gfr}} mL/min

### Electrolytes
- Sodium: {{metrics.sodium}} mEq/L
- Potassium: {{metrics.potassium}} mEq/L

### Liver Function
- ALT: {{metrics.alt}} U/L
- AST: {{metrics.ast}} U/L

### Complete Blood Count
- Hemoglobin: {{metrics.hemoglobin}} g/dL
- Hematocrit: {{metrics.hematocrit}}%
- WBC: {{metrics.wbc}} K/uL
- Platelet Count: {{metrics.platelet_count}} K/uL

## Notes
[Add any clinical notes or doctor's observations here]

## Next Steps
- [ ] Follow-up appointment scheduled
- [ ] Lifestyle modifications
- [ ] Medication changes
