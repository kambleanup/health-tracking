"""Writer for Obsidian vault markdown files."""

import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import yaml

from ..models.health import LabReport, VitalSigns, GarminActivityDay, MonthlySummary

logger = logging.getLogger(__name__)


def create_lab_report_note(
    vault_root: str,
    lab_report: LabReport,
) -> Path:
    """
    Create or update a lab report markdown note in the vault.

    Returns the path to the created/updated file.
    """
    vault_path = Path(vault_root)
    reports_dir = vault_path / "People" / lab_report.person / "Reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Filename: YYYY-MM-DD_ReportType.md
    filename = f"{lab_report.date}_{lab_report.report_type.replace(' ', '-')}.md"
    file_path = reports_dir / filename

    # Build YAML frontmatter
    frontmatter = {
        "person": lab_report.person,
        "date": str(lab_report.date),
        "report_type": lab_report.report_type,
        "doctor": lab_report.doctor,
        "lab": lab_report.lab,
        "tags": ["labs", lab_report.report_type.lower().replace(" ", "-"), lab_report.person.lower()],
        "metrics": lab_report.metrics.model_dump(exclude_none=True),
    }

    # Build markdown content
    lines = []
    lines.append("---")
    lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False))
    lines.append("---")
    lines.append("")
    lines.append(f"# Lab Report - {lab_report.date}")
    lines.append("")
    lines.append(f"**Person:** {lab_report.person}")
    lines.append(f"**Date:** {lab_report.date}")
    if lab_report.doctor:
        lines.append(f"**Doctor:** {lab_report.doctor}")
    if lab_report.lab:
        lines.append(f"**Lab:** {lab_report.lab}")
    lines.append(f"**Report Type:** {lab_report.report_type}")
    lines.append("")
    lines.append("## Key Results")
    lines.append("")

    # Organize metrics by category
    metrics = lab_report.metrics.model_dump(exclude_none=True)

    if any(k in metrics for k in ["glucose", "a1c"]):
        lines.append("### Glucose Metabolism")
        if "glucose" in metrics:
            lines.append(f"- Glucose: {metrics['glucose']} mg/dL")
        if "a1c" in metrics:
            lines.append(f"- A1C: {metrics['a1c']}%")
        lines.append("")

    if any(k in metrics for k in ["cholesterol_total", "hdl", "ldl", "triglycerides"]):
        lines.append("### Lipid Panel")
        if "cholesterol_total" in metrics:
            lines.append(f"- Total Cholesterol: {metrics['cholesterol_total']} mg/dL")
        if "hdl" in metrics:
            lines.append(f"- HDL: {metrics['hdl']} mg/dL")
        if "ldl" in metrics:
            lines.append(f"- LDL: {metrics['ldl']} mg/dL")
        if "triglycerides" in metrics:
            lines.append(f"- Triglycerides: {metrics['triglycerides']} mg/dL")
        lines.append("")

    if "tsh" in metrics:
        lines.append("### Thyroid")
        lines.append(f"- TSH: {metrics['tsh']} mIU/L")
        lines.append("")

    if any(k in metrics for k in ["creatinine", "bun", "gfr"]):
        lines.append("### Renal Function")
        if "creatinine" in metrics:
            lines.append(f"- Creatinine: {metrics['creatinine']} mg/dL")
        if "bun" in metrics:
            lines.append(f"- BUN: {metrics['bun']} mg/dL")
        if "gfr" in metrics:
            lines.append(f"- GFR: {metrics['gfr']} mL/min")
        lines.append("")

    if any(k in metrics for k in ["sodium", "potassium", "magnesium", "calcium", "phosphorus"]):
        lines.append("### Electrolytes")
        if "sodium" in metrics:
            lines.append(f"- Sodium: {metrics['sodium']} mEq/L")
        if "potassium" in metrics:
            lines.append(f"- Potassium: {metrics['potassium']} mEq/L")
        if "magnesium" in metrics:
            lines.append(f"- Magnesium: {metrics['magnesium']} mg/dL")
        if "calcium" in metrics:
            lines.append(f"- Calcium: {metrics['calcium']} mg/dL")
        if "phosphorus" in metrics:
            lines.append(f"- Phosphorus: {metrics['phosphorus']} mg/dL")
        lines.append("")

    if any(k in metrics for k in ["alt", "ast", "alkaline_phosphatase", "albumin", "total_protein"]):
        lines.append("### Liver Function")
        if "alt" in metrics:
            lines.append(f"- ALT: {metrics['alt']} U/L")
        if "ast" in metrics:
            lines.append(f"- AST: {metrics['ast']} U/L")
        if "alkaline_phosphatase" in metrics:
            lines.append(f"- Alkaline Phosphatase: {metrics['alkaline_phosphatase']} U/L")
        if "albumin" in metrics:
            lines.append(f"- Albumin: {metrics['albumin']} g/dL")
        if "total_protein" in metrics:
            lines.append(f"- Total Protein: {metrics['total_protein']} g/dL")
        lines.append("")

    if any(k in metrics for k in ["hemoglobin", "hematocrit", "wbc", "rbc", "platelet_count"]):
        lines.append("### Complete Blood Count")
        if "hemoglobin" in metrics:
            lines.append(f"- Hemoglobin: {metrics['hemoglobin']} g/dL")
        if "hematocrit" in metrics:
            lines.append(f"- Hematocrit: {metrics['hematocrit']}%")
        if "wbc" in metrics:
            lines.append(f"- WBC: {metrics['wbc']} K/uL")
        if "rbc" in metrics:
            lines.append(f"- RBC: {metrics['rbc']} M/uL")
        if "platelet_count" in metrics:
            lines.append(f"- Platelet Count: {metrics['platelet_count']} K/uL")
        lines.append("")

    lines.append("## Notes")
    lines.append("[Add clinical notes here]")
    lines.append("")
    lines.append("## Next Steps")
    lines.append("- [ ] Follow-up appointment scheduled")
    lines.append("- [ ] Lifestyle modifications")
    lines.append("- [ ] Medication changes")
    lines.append("")

    # Write file
    content = "\n".join(lines)
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Created lab report note: {file_path}")

    return file_path


def append_vital_signs(
    vault_root: str,
    person: str,
    vitals: VitalSigns,
) -> Path:
    """
    Append vital signs to the person's vital log.

    Returns the path to the log file.
    """
    vault_path = Path(vault_root)
    metrics_dir = vault_path / "People" / person / "Metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    file_path = metrics_dir / "Vital-Signs.md"

    # Create initial table header if file doesn't exist
    if not file_path.exists():
        lines = [
            f"# Vital Signs Log - {person}",
            "",
            "| Date | Time | Weight (lbs) | BP (Systolic/Diastolic) | HR (bpm) | Temp (°F) | Notes |",
            "|---|---|---|---|---|---|---|",
        ]
    else:
        lines = file_path.read_text(encoding="utf-8").rstrip().split("\n")

    # Build row
    time_str = vitals.time or ""
    weight_str = f"{vitals.weight_lbs}" if vitals.weight_lbs else ""
    bp_str = ""
    if vitals.systolic_bp and vitals.diastolic_bp:
        bp_str = f"{vitals.systolic_bp}/{vitals.diastolic_bp}"
    hr_str = f"{vitals.heart_rate}" if vitals.heart_rate else ""
    temp_str = f"{vitals.temperature_f}" if vitals.temperature_f else ""
    notes_str = vitals.notes or ""

    row = f"| {vitals.date} | {time_str} | {weight_str} | {bp_str} | {hr_str} | {temp_str} | {notes_str} |"
    lines.append(row)

    # Write file
    content = "\n".join(lines) + "\n"
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Appended vital signs for {person}: {file_path}")

    return file_path


def append_garmin_activity(
    vault_root: str,
    person: str,
    activity: GarminActivityDay,
) -> Path:
    """
    Append daily Garmin activity to the person's activity log.

    Returns the path to the activity file.
    """
    vault_path = Path(vault_root)
    metrics_dir = vault_path / "People" / person / "Metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    file_path = metrics_dir / "Garmin-Activity.md"

    # Create initial table header if file doesn't exist
    if not file_path.exists():
        lines = [
            f"# Garmin Activity Log - {person}",
            "",
            "| Date | Steps | Active Min | Calories | HR Avg | HR Max | Sleep (hrs) | Quality | Stress | Battery |",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    else:
        lines = file_path.read_text(encoding="utf-8").rstrip().split("\n")

    # Build row
    steps_str = f"{activity.steps}" if activity.steps else ""
    active_min_str = f"{activity.active_minutes}" if activity.active_minutes else ""
    calories_str = f"{activity.calories}" if activity.calories else ""
    hr_avg_str = f"{activity.heart_rate_avg}" if activity.heart_rate_avg else ""
    hr_max_str = f"{activity.heart_rate_max}" if activity.heart_rate_max else ""
    sleep_str = f"{activity.sleep_seconds / 3600:.1f}" if activity.sleep_seconds else ""
    quality_str = activity.sleep_quality or ""
    stress_str = f"{activity.stress_level}" if activity.stress_level else ""
    battery_str = f"{activity.body_battery}" if activity.body_battery else ""

    row = f"| {activity.date} | {steps_str} | {active_min_str} | {calories_str} | {hr_avg_str} | {hr_max_str} | {sleep_str} | {quality_str} | {stress_str} | {battery_str} |"
    lines.append(row)

    # Write file
    content = "\n".join(lines) + "\n"
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Appended Garmin activity for {person}: {file_path}")

    return file_path


def create_monthly_summary(
    vault_root: str,
    summary: MonthlySummary,
) -> Path:
    """
    Create a monthly health summary note.

    Returns the path to the created file.
    """
    vault_path = Path(vault_root)
    summaries_dir = vault_path / "People" / summary.person / "Summaries"
    summaries_dir.mkdir(parents=True, exist_ok=True)

    # Filename: YYYY-MM_Summary.md
    filename = f"{summary.year}-{summary.month:02d}_Summary.md"
    file_path = summaries_dir / filename

    # Build YAML frontmatter
    frontmatter = {
        "person": summary.person,
        "month": summary.month,
        "year": summary.year,
        "tags": ["summary", "monthly", summary.person.lower()],
    }

    lines = []
    lines.append("---")
    lines.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False))
    lines.append("---")
    lines.append("")
    lines.append(f"# Monthly Health Summary - {summary.person}")
    lines.append("")
    lines.append(f"**Period:** {summary.month}/{summary.year}")
    lines.append("")
    lines.append("## Metrics Overview")
    lines.append("")

    if summary.weight_trend:
        lines.append("### Weight Trend")
        lines.append(summary.weight_trend)
        lines.append("")

    if summary.bp_trend:
        lines.append("### Blood Pressure")
        lines.append(summary.bp_trend)
        lines.append("")

    if summary.activity_summary:
        lines.append("### Activity Summary")
        lines.append(summary.activity_summary)
        lines.append("")

    if summary.key_findings:
        lines.append("## Key Findings")
        for finding in summary.key_findings:
            lines.append(f"- {finding}")
        lines.append("")

    if summary.alerts:
        lines.append("## Alerts")
        for alert in summary.alerts:
            lines.append(f"- **{alert.metric}**: {alert.message} (severity: {alert.severity})")
        lines.append("")

    if summary.next_steps:
        lines.append("## Next Steps")
        for step in summary.next_steps:
            lines.append(f"- [ ] {step}")
        lines.append("")

    lines.append(f"*Generated: {summary.generated_at.strftime('%Y-%m-%d %H:%M:%S')}*")

    # Write file
    content = "\n".join(lines)
    file_path.write_text(content, encoding="utf-8")
    logger.info(f"Created monthly summary: {file_path}")

    return file_path
