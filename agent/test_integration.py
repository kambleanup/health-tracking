"""Integration tests for the health tracking agent."""

import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from anthropic import Anthropic

from agent.models.health import (
    BloodworkMetrics,
    LabReport,
    GarminActivityDay,
    VitalSigns,
    PersonHealthData,
)
from agent.writers.obsidian import (
    append_garmin_activity,
    append_vital_signs,
    create_lab_report_note,
)


def test_create_lab_report_note():
    """Test creating a lab report note."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = tmpdir

        # Create test report
        metrics = BloodworkMetrics(
            glucose=95,
            cholesterol_total=185,
            hdl=55,
            ldl=110,
            triglycerides=140,
            a1c=5.4,
            tsh=2.1,
        )

        lab_report = LabReport(
            person="Anup",
            date=date.today(),
            report_type="Blood Work",
            doctor="Dr. Smith",
            lab="Quest Diagnostics",
            metrics=metrics,
        )

        # Create note
        path = create_lab_report_note(vault_root, lab_report)

        # Verify file was created
        assert path.exists(), f"Lab report note was not created at {path}"
        assert "Anup" in path.read_text(), "Person name not in report"
        assert "95" in path.read_text(), "Glucose metric not in report"

        print(f"[OK] Lab report note created: {path}")


def test_append_vital_signs():
    """Test appending vital signs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = tmpdir

        # Create test vitals
        vitals = VitalSigns(
            date=date.today(),
            time="09:30",
            weight_lbs=180,
            systolic_bp=120,
            diastolic_bp=80,
            heart_rate=60,
            temperature_f=98.6,
        )

        # Append vitals
        path = append_vital_signs(vault_root, "Anup", vitals)

        # Verify file was created and updated
        assert path.exists(), f"Vital signs file was not created at {path}"
        content = path.read_text()
        assert "180" in content, "Weight not in vitals"
        assert "120" in content, "Systolic BP not in vitals"

        # Append again with different values
        vitals2 = VitalSigns(
            date=date.today(),
            time="17:30",
            weight_lbs=181,
            systolic_bp=118,
            diastolic_bp=78,
            heart_rate=62,
            temperature_f=98.4,
        )

        path = append_vital_signs(vault_root, "Anup", vitals2)
        content = path.read_text()

        # Should have both entries
        assert "180" in content and "181" in content, "Both entries not found"

        print(f"[OK] Vital signs appended: {path}")


def test_append_garmin_activity():
    """Test appending Garmin activity."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vault_root = tmpdir

        # Create test activity
        activity = GarminActivityDay(
            date=date.today(),
            steps=8234,
            active_minutes=45,
            calories=2100,
            heart_rate_avg=72,
            heart_rate_max=125,
            sleep_seconds=27000,  # 7.5 hours
            sleep_quality="Good",
            stress_level=35,
            body_battery=65,
        )

        # Append activity
        path = append_garmin_activity(vault_root, "Anup", activity)

        # Verify file was created
        assert path.exists(), f"Activity file was not created at {path}"
        content = path.read_text()
        assert "8234" in content, "Steps not in activity"
        assert "45" in content, "Active minutes not in activity"

        print(f"[OK] Garmin activity appended: {path}")


def test_config_loading():
    """Test loading configuration."""
    # Check if config.yaml exists
    config_path = Path("config.yaml")
    if config_path.exists():
        import yaml
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "anthropic" in config, "anthropic not in config"
        assert "paths" in config, "paths not in config"
        assert "people" in config, "people not in config"
        print(f"[OK] Config loaded successfully")
    else:
        print(f"[SKIP] config.yaml not found, skipping config test")


def test_directory_structure():
    """Test that vault directory structure exists."""
    vault_paths = [
        "vault/.obsidian",
        "vault/People/Anup/Reports",
        "vault/People/Anup/Metrics",
        "vault/People/Anup/Summaries",
        "vault/People/Deepali/Reports",
        "vault/People/Deepali/Metrics",
        "vault/People/Deepali/Summaries",
        "vault/Templates",
    ]

    for path in vault_paths:
        full_path = Path(path)
        assert full_path.exists(), f"Directory not found: {path}"

    print(f"[OK] All vault directories exist")


def test_template_files():
    """Test that template files exist."""
    templates = [
        "vault/Templates/Lab-Report.md",
        "vault/Templates/Vital-Log.md",
        "vault/Templates/Monthly-Summary.md",
        "vault/Dashboard.md",
    ]

    for path in templates:
        full_path = Path(path)
        assert full_path.exists(), f"Template not found: {path}"
        content = full_path.read_text()
        assert len(content) > 0, f"Template is empty: {path}"

    print(f"[OK] All template files exist and have content")


def test_requirements():
    """Test that requirements.txt has all dependencies."""
    req_file = Path("requirements.txt")
    if req_file.exists():
        content = req_file.read_text()
        required_libs = [
            "anthropic",
            "garminconnect",
            "pdfplumber",
            "pydantic",
            "pandas",
            "PyYAML",
            "click",
        ]
        for lib in required_libs:
            assert lib.lower() in content.lower(), f"Missing dependency: {lib}"
        print(f"[OK] All required dependencies in requirements.txt")
    else:
        print(f"[SKIP] requirements.txt not found")


if __name__ == "__main__":
    print("Running Health Tracking Agent Integration Tests\n")

    tests = [
        ("Directory Structure", test_directory_structure),
        ("Template Files", test_template_files),
        ("Requirements", test_requirements),
        ("Config Loading", test_config_loading),
        ("Create Lab Report Note", test_create_lab_report_note),
        ("Append Vital Signs", test_append_vital_signs),
        ("Append Garmin Activity", test_append_garmin_activity),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            print(f"Testing: {test_name}...", end=" ")
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n[FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"\n[ERROR] {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")
