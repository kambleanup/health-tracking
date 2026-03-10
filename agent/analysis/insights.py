"""Health insights and analysis using Claude API."""

import json
import logging
from datetime import datetime
from typing import List, Optional

from anthropic import Anthropic

from ..models.health import (
    PersonHealthData,
    HealthAlert,
    MonthlySummary,
    VitalSigns,
    GarminActivityDay,
)

logger = logging.getLogger(__name__)


class HealthAnalyzer:
    """Analyzes health data and generates insights."""

    def __init__(self, client: Optional[Anthropic] = None, thresholds: Optional[dict] = None):
        """Initialize analyzer.

        Args:
            client: Anthropic client (creates new one if not provided)
            thresholds: Alert thresholds dictionary
        """
        self.client = client or Anthropic()
        self.thresholds = thresholds or self._default_thresholds()

    @staticmethod
    def _default_thresholds() -> dict:
        """Default health metric thresholds."""
        return {
            "glucose_high": 120,
            "glucose_low": 70,
            "systolic_high": 140,
            "systolic_low": 90,
            "diastolic_high": 90,
            "diastolic_low": 60,
            "cholesterol_high": 200,
            "triglycerides_high": 150,
            "a1c_high": 6.5,
        }

    def check_alerts(self, health_data: PersonHealthData) -> List[HealthAlert]:
        """
        Check latest metrics against thresholds and generate alerts.

        Args:
            health_data: Person's health data

        Returns:
            List of HealthAlert objects
        """
        alerts = []

        # Check latest vital signs
        if health_data.vital_signs:
            latest_vitals = health_data.vital_signs[-1]
            alerts.extend(self._check_vital_alerts(health_data.name, latest_vitals))

        # Check latest lab report
        if health_data.lab_reports:
            latest_report = health_data.lab_reports[-1]
            alerts.extend(self._check_lab_alerts(health_data.name, latest_report))

        return alerts

    def _check_vital_alerts(self, person: str, vitals: VitalSigns) -> List[HealthAlert]:
        """Check vital signs against thresholds."""
        alerts = []

        if vitals.systolic_bp:
            if vitals.systolic_bp > self.thresholds["systolic_high"]:
                alerts.append(
                    HealthAlert(
                        person=person,
                        date=datetime.now(),
                        metric="Systolic BP",
                        value=vitals.systolic_bp,
                        threshold=self.thresholds["systolic_high"],
                        severity="warning",
                        message=f"Elevated systolic BP: {vitals.systolic_bp} mmHg",
                    )
                )
            elif vitals.systolic_bp < self.thresholds["systolic_low"]:
                alerts.append(
                    HealthAlert(
                        person=person,
                        date=datetime.now(),
                        metric="Systolic BP",
                        value=vitals.systolic_bp,
                        threshold=self.thresholds["systolic_low"],
                        severity="warning",
                        message=f"Low systolic BP: {vitals.systolic_bp} mmHg",
                    )
                )

        return alerts

    def _check_lab_alerts(self, person: str, report) -> List[HealthAlert]:
        """Check lab metrics against thresholds."""
        alerts = []

        metrics = report.metrics

        if metrics.glucose and metrics.glucose > self.thresholds["glucose_high"]:
            alerts.append(
                HealthAlert(
                    person=person,
                    date=report.date,
                    metric="Glucose",
                    value=metrics.glucose,
                    threshold=self.thresholds["glucose_high"],
                    severity="warning",
                    message=f"Elevated glucose: {metrics.glucose} mg/dL",
                )
            )

        if metrics.a1c and metrics.a1c > self.thresholds["a1c_high"]:
            alerts.append(
                HealthAlert(
                    person=person,
                    date=report.date,
                    metric="A1C",
                    value=metrics.a1c,
                    threshold=self.thresholds["a1c_high"],
                    severity="warning",
                    message=f"Elevated A1C: {metrics.a1c}%",
                )
            )

        if metrics.cholesterol_total and metrics.cholesterol_total > self.thresholds["cholesterol_high"]:
            alerts.append(
                HealthAlert(
                    person=person,
                    date=report.date,
                    metric="Total Cholesterol",
                    value=metrics.cholesterol_total,
                    threshold=self.thresholds["cholesterol_high"],
                    severity="info",
                    message=f"Elevated cholesterol: {metrics.cholesterol_total} mg/dL",
                )
            )

        if metrics.triglycerides and metrics.triglycerides > self.thresholds["triglycerides_high"]:
            alerts.append(
                HealthAlert(
                    person=person,
                    date=report.date,
                    metric="Triglycerides",
                    value=metrics.triglycerides,
                    threshold=self.thresholds["triglycerides_high"],
                    severity="info",
                    message=f"Elevated triglycerides: {metrics.triglycerides} mg/dL",
                )
            )

        return alerts

    def generate_monthly_summary(
        self,
        health_data: PersonHealthData,
        month: int,
        year: int,
    ) -> MonthlySummary:
        """
        Generate AI-powered monthly health summary.

        Args:
            health_data: Person's health data
            month: Month (1-12)
            year: Year

        Returns:
            MonthlySummary with Claude-generated insights
        """

        # Prepare data for Claude
        recent_vitals = [v for v in health_data.vital_signs if v.date.month == month and v.date.year == year]
        recent_activity = [a for a in health_data.garmin_activity if a.date.month == month and a.date.year == year]
        recent_reports = [r for r in health_data.lab_reports if r.date.month == month and r.date.year == year]

        # Build prompt for Claude
        data_summary = f"""
Please analyze the following health data for {health_data.name} for {month}/{year}:

VITAL SIGNS (last 7 days):
"""
        if recent_vitals:
            for vital in recent_vitals[-7:]:
                data_summary += f"\n- {vital.date}: Weight={vital.weight_lbs}, BP={vital.systolic_bp}/{vital.diastolic_bp}, HR={vital.heart_rate}"
        else:
            data_summary += "\nNo vital signs recorded"

        data_summary += "\n\nGARMIN ACTIVITY (week):\n"
        if recent_activity:
            for activity in recent_activity[-7:]:
                data_summary += f"\n- {activity.date}: {activity.steps} steps, {activity.active_minutes} active min, {activity.sleep_seconds / 3600:.1f}h sleep"
        else:
            data_summary += "\nNo activity data recorded"

        data_summary += "\n\nLAB REPORTS (this month):\n"
        if recent_reports:
            for report in recent_reports:
                metrics = report.metrics.model_dump(exclude_none=True)
                data_summary += f"\n- {report.date}: {', '.join(f'{k}={v}' for k, v in list(metrics.items())[:5])}"
        else:
            data_summary += "\nNo lab reports this month"

        prompt = f"""{data_summary}

Based on this data, provide:
1. A brief weight trend assessment
2. Blood pressure assessment
3. Activity and sleep quality summary
4. Key findings and concerns
5. 2-3 recommended next steps

Format your response as a JSON object with these keys:
- weight_trend: string
- bp_trend: string
- activity_summary: string
- key_findings: list of strings
- next_steps: list of strings
"""

        # Call Claude for analysis
        response = self.client.messages.create(
            model="claude-opus-4-6",
            max_tokens=1500,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        response_text = response.content[0].text

        # Parse JSON from response
        try:
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                analysis = {
                    "weight_trend": "No data available",
                    "bp_trend": "No data available",
                    "activity_summary": "No data available",
                    "key_findings": ["Unable to generate analysis"],
                    "next_steps": ["Review health data manually"],
                }
        except json.JSONDecodeError:
            logger.warning("Failed to parse Claude response as JSON")
            analysis = {
                "weight_trend": "No data available",
                "bp_trend": "No data available",
                "activity_summary": "No data available",
                "key_findings": ["Unable to generate analysis"],
                "next_steps": ["Review health data manually"],
            }

        # Get alerts
        alerts = self.check_alerts(health_data)

        # Create summary
        summary = MonthlySummary(
            person=health_data.name,
            month=month,
            year=year,
            weight_trend=analysis.get("weight_trend"),
            bp_trend=analysis.get("bp_trend"),
            activity_summary=analysis.get("activity_summary"),
            key_findings=analysis.get("key_findings", []),
            alerts=alerts,
            next_steps=analysis.get("next_steps", []),
        )

        logger.info(f"Generated monthly summary for {health_data.name} ({month}/{year})")
        return summary

    def detect_trends(
        self,
        health_data: PersonHealthData,
        metric_name: str,
        window_days: int = 30,
    ) -> dict:
        """
        Detect trends in a specific metric over time.

        Args:
            health_data: Person's health data
            metric_name: Name of metric to analyze
            window_days: Number of days to look back

        Returns:
            Dictionary with trend information
        """
        # This would extract metric values over time and calculate trends
        # Placeholder for full implementation
        return {
            "metric": metric_name,
            "trend": "stable",
            "values": [],
        }
