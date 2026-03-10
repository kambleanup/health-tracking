"""Pydantic models for health data."""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BloodworkMetrics(BaseModel):
    """Blood work lab metrics."""
    glucose: Optional[float] = None
    cholesterol_total: Optional[float] = None
    hdl: Optional[float] = None
    ldl: Optional[float] = None
    triglycerides: Optional[float] = None
    a1c: Optional[float] = None
    tsh: Optional[float] = None
    creatinine: Optional[float] = None
    bun: Optional[float] = None
    gfr: Optional[float] = None
    sodium: Optional[float] = None
    potassium: Optional[float] = None
    magnesium: Optional[float] = None
    calcium: Optional[float] = None
    phosphorus: Optional[float] = None
    alt: Optional[float] = None
    ast: Optional[float] = None
    alkaline_phosphatase: Optional[float] = None
    albumin: Optional[float] = None
    total_protein: Optional[float] = None
    hemoglobin: Optional[float] = None
    hematocrit: Optional[float] = None
    wbc: Optional[float] = None
    rbc: Optional[float] = None
    platelet_count: Optional[float] = None


class VitalSigns(BaseModel):
    """Daily vital signs."""
    date: date
    time: Optional[str] = None
    weight_lbs: Optional[float] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    heart_rate: Optional[int] = None
    temperature_f: Optional[float] = None
    notes: Optional[str] = None


class LabReport(BaseModel):
    """Parsed lab report."""
    person: str
    date: date
    report_type: str  # e.g., "Blood Work", "Urinalysis"
    doctor: Optional[str] = None
    lab: Optional[str] = None
    metrics: BloodworkMetrics
    notes: Optional[str] = None
    file_path: Optional[str] = None


class GarminActivityDay(BaseModel):
    """Daily activity from Garmin."""
    date: date
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories: Optional[int] = None
    heart_rate_avg: Optional[int] = None
    heart_rate_max: Optional[int] = None
    sleep_seconds: Optional[int] = None  # Total sleep in seconds
    sleep_quality: Optional[str] = None  # e.g., "Good", "Fair", "Poor"
    stress_level: Optional[int] = None  # 0-100
    body_battery: Optional[int] = None  # 0-100
    spo2: Optional[float] = None  # Blood oxygen percentage


class PersonHealthData(BaseModel):
    """All health data for a person."""
    name: str
    date_of_birth: Optional[date] = None
    lab_reports: List[LabReport] = []
    vital_signs: List[VitalSigns] = []
    garmin_activity: List[GarminActivityDay] = []
    conditions: List[str] = []
    allergies: List[str] = []
    medications: List[str] = []


class HealthAlert(BaseModel):
    """Alert for abnormal metrics."""
    person: str
    date: datetime
    metric: str
    value: Any
    threshold: Any
    severity: str  # "info", "warning", "critical"
    message: str


class MonthlySummary(BaseModel):
    """AI-generated monthly health summary."""
    person: str
    month: int
    year: int
    weight_trend: Optional[str] = None
    bp_trend: Optional[str] = None
    activity_summary: Optional[str] = None
    key_findings: List[str] = []
    alerts: List[HealthAlert] = []
    next_steps: List[str] = []
    generated_at: datetime = Field(default_factory=datetime.now)
