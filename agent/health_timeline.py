"""Generate historical health timeline and trends analysis."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml

logger = logging.getLogger(__name__)


def analyze_all_reports(vault_root: str) -> Dict:
    """
    Analyze all ingested lab reports and generate timeline.

    Returns timeline with key metrics over years.
    """
    vault_path = Path(vault_root)
    reports_dir = vault_path / "People" / "Anup" / "Reports"

    if not reports_dir.exists():
        logger.error(f"Reports directory not found: {reports_dir}")
        return {}

    # Load all report files
    reports = []
    for report_file in sorted(reports_dir.glob("*.md")):
        try:
            content = report_file.read_text(encoding="utf-8")

            # Extract YAML frontmatter
            if content.startswith("---"):
                end_idx = content.find("---", 3)
                yaml_content = content[3:end_idx]
                frontmatter = yaml.safe_load(yaml_content)

                if frontmatter and "metrics" in frontmatter:
                    frontmatter["file"] = report_file.name
                    reports.append(frontmatter)

        except Exception as e:
            logger.warning(f"Could not parse {report_file.name}: {e}")

    # Sort by date
    reports.sort(key=lambda x: x.get("date", ""))

    # Extract timeline of key metrics
    timeline = {
        "date_range": f"{reports[0].get('date')} to {reports[-1].get('date')}" if reports else "N/A",
        "total_reports": len(reports),
        "glucose": [],
        "cholesterol_total": [],
        "hdl": [],
        "ldl": [],
        "triglycerides": [],
        "a1c": [],
        "tsh": [],
        "hemoglobin": [],
        "creatinine": [],
    }

    # Build timeline for each metric
    for report in reports:
        date = report.get("date", "Unknown")
        metrics = report.get("metrics", {})

        if "glucose" in metrics:
            timeline["glucose"].append((date, metrics["glucose"]))
        if "cholesterol_total" in metrics:
            timeline["cholesterol_total"].append((date, metrics["cholesterol_total"]))
        if "hdl" in metrics:
            timeline["hdl"].append((date, metrics["hdl"]))
        if "ldl" in metrics:
            timeline["ldl"].append((date, metrics["ldl"]))
        if "triglycerides" in metrics:
            timeline["triglycerides"].append((date, metrics["triglycerides"]))
        if "a1c" in metrics:
            timeline["a1c"].append((date, metrics["a1c"]))
        if "tsh" in metrics:
            timeline["tsh"].append((date, metrics["tsh"]))
        if "hemoglobin" in metrics:
            timeline["hemoglobin"].append((date, metrics["hemoglobin"]))
        if "creatinine" in metrics:
            timeline["creatinine"].append((date, metrics["creatinine"]))

    return timeline


def generate_trend_summary(timeline: Dict) -> str:
    """Generate human-readable trend summary."""
    lines = []
    lines.append("# Health Timeline & Trend Analysis")
    lines.append("")
    lines.append(f"**Analysis Period:** {timeline.get('date_range', 'N/A')}")
    lines.append(f"**Total Reports:** {timeline.get('total_reports', 0)}")
    lines.append("")

    # Glucose trend
    if timeline.get("glucose"):
        glucose_vals = [v for _, v in timeline["glucose"]]
        lines.append("## Glucose Levels")
        lines.append(f"- First: {glucose_vals[0]} mg/dL ({timeline['glucose'][0][0]})")
        lines.append(f"- Latest: {glucose_vals[-1]} mg/dL ({timeline['glucose'][-1][0]})")
        lines.append(f"- Range: {min(glucose_vals)}-{max(glucose_vals)} mg/dL")
        lines.append(f"- Trend: {'INCREASING' if glucose_vals[-1] > glucose_vals[0] else 'DECREASING'}")
        lines.append("")

    # Cholesterol trend
    if timeline.get("cholesterol_total"):
        chol_vals = [v for _, v in timeline["cholesterol_total"]]
        lines.append("## Total Cholesterol")
        lines.append(f"- First: {chol_vals[0]} mg/dL ({timeline['cholesterol_total'][0][0]})")
        lines.append(f"- Latest: {chol_vals[-1]} mg/dL ({timeline['cholesterol_total'][-1][0]})")
        lines.append(f"- Range: {min(chol_vals)}-{max(chol_vals)} mg/dL")
        lines.append(f"- Trend: {'INCREASING' if chol_vals[-1] > chol_vals[0] else 'DECREASING'}")
        lines.append("")

    # A1C trend
    if timeline.get("a1c"):
        a1c_vals = [v for _, v in timeline["a1c"]]
        lines.append("## Hemoglobin A1C")
        lines.append(f"- First: {a1c_vals[0]}% ({timeline['a1c'][0][0]})")
        lines.append(f"- Latest: {a1c_vals[-1]}% ({timeline['a1c'][-1][0]})")
        lines.append(f"- Range: {min(a1c_vals)}-{max(a1c_vals)}%")
        lines.append(f"- Trend: {'INCREASING' if a1c_vals[-1] > a1c_vals[0] else 'DECREASING'}")
        lines.append("")

    # HDL trend
    if timeline.get("hdl"):
        hdl_vals = [v for _, v in timeline["hdl"]]
        lines.append("## HDL Cholesterol (Good)")
        lines.append(f"- First: {hdl_vals[0]} mg/dL ({timeline['hdl'][0][0]})")
        lines.append(f"- Latest: {hdl_vals[-1]} mg/dL ({timeline['hdl'][-1][0]})")
        lines.append(f"- Range: {min(hdl_vals)}-{max(hdl_vals)} mg/dL")
        lines.append(f"- Trend: {'INCREASING (GOOD)' if hdl_vals[-1] > hdl_vals[0] else 'DECREASING (CONCERN)'}")
        lines.append("")

    # LDL trend
    if timeline.get("ldl"):
        ldl_vals = [v for _, v in timeline["ldl"]]
        lines.append("## LDL Cholesterol (Bad)")
        lines.append(f"- First: {ldl_vals[0]} mg/dL ({timeline['ldl'][0][0]})")
        lines.append(f"- Latest: {ldl_vals[-1]} mg/dL ({timeline['ldl'][-1][0]})")
        lines.append(f"- Range: {min(ldl_vals)}-{max(ldl_vals)} mg/dL")
        lines.append(f"- Trend: {'DECREASING (GOOD)' if ldl_vals[-1] < ldl_vals[0] else 'INCREASING (CONCERN)'}")
        lines.append("")

    # Triglycerides trend
    if timeline.get("triglycerides"):
        trig_vals = [v for _, v in timeline["triglycerides"]]
        lines.append("## Triglycerides")
        lines.append(f"- First: {trig_vals[0]} mg/dL ({timeline['triglycerides'][0][0]})")
        lines.append(f"- Latest: {trig_vals[-1]} mg/dL ({timeline['triglycerides'][-1][0]})")
        lines.append(f"- Range: {min(trig_vals)}-{max(trig_vals)} mg/dL")
        lines.append(f"- Trend: {'INCREASING' if trig_vals[-1] > trig_vals[0] else 'DECREASING'}")
        lines.append("")

    return "\n".join(lines)


def main():
    """Generate timeline report."""
    vault_root = "C:/Projects/health/vault"

    logger.info("Analyzing all health reports...")
    timeline = analyze_all_reports(vault_root)

    if not timeline:
        print("No reports found to analyze.")
        return 1

    # Generate summary
    summary = generate_trend_summary(timeline)
    print(summary)

    # Save to file
    output_file = Path(vault_root) / "People" / "Anup" / "Summaries" / "Health-Timeline.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(summary)

    print(f"\n[OK] Timeline saved: {output_file}")
    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
