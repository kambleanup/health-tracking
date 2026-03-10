"""Health Tracking Agent CLI."""

import logging
import os
from datetime import datetime
from pathlib import Path

import click
import yaml
from anthropic import Anthropic

from .analysis.insights import HealthAnalyzer
from .models.health import PersonHealthData, VitalSigns
try:
    from .parsers.garmin_sync import GarminSync
except ImportError:
    GarminSync = None

try:
    from .parsers.pdf_parser import parse_pdf_report
except ImportError:
    parse_pdf_report = None
from .writers.obsidian import (
    append_garmin_activity,
    append_vital_signs,
    create_lab_report_note,
    create_monthly_summary,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> dict:
    """Load configuration from YAML file."""
    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Expand environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", config.get("anthropic", {}).get("api_key", ""))
    garmin_user = os.getenv("GARMIN_USERNAME", config.get("garmin", {}).get("username", ""))
    garmin_pass = os.getenv("GARMIN_PASSWORD", config.get("garmin", {}).get("password", ""))

    config["anthropic"]["api_key"] = anthropic_key
    config["garmin"]["username"] = garmin_user
    config["garmin"]["password"] = garmin_pass

    return config


@click.group()
def cli():
    """Health Tracking Agent CLI."""
    pass


@cli.command()
@click.option(
    "--person",
    required=True,
    type=click.Choice(["anup", "deepali"]),
    help="Person to ingest report for",
)
@click.option(
    "--pdf",
    required=True,
    type=click.Path(exists=True),
    help="Path to PDF lab report",
)
@click.option(
    "--doctor",
    default=None,
    help="Doctor's name",
)
@click.option(
    "--lab",
    default=None,
    help="Lab name",
)
@click.option(
    "--config",
    default="config.yaml",
    type=click.Path(exists=True),
    help="Path to config file",
)
def ingest(person: str, pdf: str, doctor: str, lab: str, config: str):
    """Ingest a PDF lab report and create vault note."""
    if parse_pdf_report is None:
        click.echo("[ERROR] PDF parsing dependencies not installed. Run: pip install pdfplumber pillow", err=True)
        raise click.Abort()

    click.echo(f"Ingesting {pdf} for {person}...")

    try:
        config_data = load_config(config)
        client = Anthropic()

        # Parse PDF
        lab_report = parse_pdf_report(
            pdf,
            person=person.capitalize(),
            doctor=doctor,
            lab=lab,
            client=client,
        )

        # Write to Obsidian
        vault_root = config_data["paths"]["vault_root"]
        note_path = create_lab_report_note(vault_root, lab_report)

        click.echo(f"[OK] Report ingested: {note_path}")

    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--person",
    default=None,
    type=click.Choice(["anup", "deepali"]),
    help="Specific person to sync (defaults to all)",
)
@click.option(
    "--days",
    default=7,
    type=int,
    help="Number of days to sync",
)
@click.option(
    "--config",
    default="config.yaml",
    type=click.Path(exists=True),
    help="Path to config file",
)
def sync_garmin(person: str, days: int, config: str):
    """Sync Garmin Connect activity data."""
    if GarminSync is None:
        click.echo("[ERROR] garminconnect not installed. Run: pip install garminconnect", err=True)
        raise click.Abort()

    click.echo("Syncing Garmin data...")

    try:
        config_data = load_config(config)
        vault_root = config_data["paths"]["vault_root"]

        # Get Garmin credentials
        username = config_data["garmin"]["username"]
        password = config_data["garmin"]["password"]

        if not username or not password:
            raise ValueError("Garmin credentials not configured. Set GARMIN_USERNAME and GARMIN_PASSWORD.")

        # Sync
        garmin = GarminSync(username, password)
        people = [p["name"] for p in config_data["people"]]
        if person:
            people = [person.capitalize()]

        for person_name in people:
            click.echo(f"  Syncing {person_name}...")
            activities = garmin.get_activity_data(days_back=days)

            for activity in activities:
                append_garmin_activity(vault_root, person_name, activity)

            click.echo(f"  [OK] {len(activities)} days synced for {person_name}")

    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--person",
    required=True,
    type=click.Choice(["anup", "deepali"]),
    help="Person to analyze",
)
@click.option(
    "--period",
    default="monthly",
    type=click.Choice(["monthly", "weekly"]),
    help="Analysis period",
)
@click.option(
    "--month",
    default=None,
    type=int,
    help="Month (1-12), defaults to current month",
)
@click.option(
    "--year",
    default=None,
    type=int,
    help="Year, defaults to current year",
)
@click.option(
    "--config",
    default="config.yaml",
    type=click.Path(exists=True),
    help="Path to config file",
)
def analyze(person: str, period: str, month: int, year: int, config: str):
    """Generate health analysis and summary."""
    click.echo(f"Analyzing {person}'s health...")

    try:
        config_data = load_config(config)
        vault_root = config_data["paths"]["vault_root"]

        # Determine month/year
        now = datetime.now()
        if month is None:
            month = now.month
        if year is None:
            year = now.year

        # Load health data from vault
        person_cap = person.capitalize()
        health_data = PersonHealthData(name=person_cap)

        # Create analyzer
        analyzer = HealthAnalyzer(
            client=Anthropic(),
            thresholds=config_data.get("thresholds", {})
        )

        # Generate summary
        summary = analyzer.generate_monthly_summary(health_data, month, year)

        # Write summary to vault
        summary_path = create_monthly_summary(vault_root, summary)

        click.echo(f"[OK] Analysis saved: {summary_path}")
        click.echo(f"\nKey Findings:")
        for finding in summary.key_findings:
            click.echo(f"  - {finding}")

    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--person",
    default="all",
    type=str,
    help="Specific person or 'all'",
)
@click.option(
    "--output",
    default=None,
    type=click.Path(),
    help="Output directory (defaults to vault)",
)
@click.option(
    "--config",
    default="config.yaml",
    type=click.Path(exists=True),
    help="Path to config file",
)
def report(person: str, output: str, config: str):
    """Generate comprehensive health report."""
    click.echo("Generating health report...")

    try:
        config_data = load_config(config)
        if output is None:
            output = config_data["paths"]["vault_root"]

        click.echo(f"Report would be generated to: {output}")
        click.echo("(Full report generation to be implemented)")

    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


@cli.command()
@click.option(
    "--person",
    required=True,
    type=click.Choice(["anup", "deepali"]),
    help="Person to log vitals for",
)
@click.option(
    "--weight",
    type=float,
    help="Weight in lbs",
)
@click.option(
    "--systolic",
    type=int,
    help="Systolic BP",
)
@click.option(
    "--diastolic",
    type=int,
    help="Diastolic BP",
)
@click.option(
    "--hr",
    type=int,
    help="Heart rate (bpm)",
)
@click.option(
    "--temp",
    type=float,
    help="Temperature in Fahrenheit",
)
@click.option(
    "--notes",
    default="",
    help="Additional notes",
)
@click.option(
    "--config",
    default="config.yaml",
    type=click.Path(exists=True),
    help="Path to config file",
)
def log_vitals(
    person: str,
    weight: float,
    systolic: int,
    diastolic: int,
    hr: int,
    temp: float,
    notes: str,
    config: str,
):
    """Log vital signs for a person."""
    click.echo(f"Logging vitals for {person}...")

    try:
        config_data = load_config(config)
        vault_root = config_data["paths"]["vault_root"]

        vitals = VitalSigns(
            date=datetime.now().date(),
            time=datetime.now().strftime("%H:%M"),
            weight_lbs=weight,
            systolic_bp=systolic,
            diastolic_bp=diastolic,
            heart_rate=hr,
            temperature_f=temp,
            notes=notes or None,
        )

        append_vital_signs(vault_root, person.capitalize(), vitals)
        click.echo(f"[OK] Vitals logged for {person}")

    except Exception as e:
        click.echo(f"[ERROR] {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
