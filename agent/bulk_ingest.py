"""Bulk ingestion script for processing all historical PDF lab reports."""

import logging
import os
import sys
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from anthropic import Anthropic

from agent.models.health import LabReport
from agent.parsers.pdf_parser import parse_pdf_report
from agent.writers.obsidian import create_lab_report_note

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def discover_pdf_files(source_dir: str) -> List[tuple[str, str]]:
    """
    Discover all PDF files organized by year.

    Returns list of (pdf_path, year) tuples.
    """
    source_path = Path(source_dir)
    pdf_files = []

    # Find all PDFs in year-organized folders
    for year_dir in sorted(source_path.iterdir()):
        if year_dir.is_dir():
            year = year_dir.name

            # Handle both flat and nested (month) structure
            pdfs_in_year = list(year_dir.rglob("*.pdf"))

            for pdf_file in sorted(pdfs_in_year):
                pdf_files.append((str(pdf_file), year))

    return pdf_files


def load_date_overrides(source_dir: str) -> dict:
    """Load manual date overrides from JSON file."""
    import json

    overrides_file = Path(source_dir) / "date_overrides.json"
    if overrides_file.exists():
        try:
            return json.loads(overrides_file.read_text())
        except Exception as e:
            logger.warning(f"Could not load date overrides: {e}")
    return {}


def ingest_all_reports(
    source_dir: str,
    vault_root: str,
    person: str = "Anup",
    dry_run: bool = False,
) -> dict:
    """
    Bulk ingest all historical PDF reports with accurate dates.

    Args:
        source_dir: Directory with year-organized PDFs
        vault_root: Obsidian vault root directory
        person: Person name
        dry_run: If True, only report what would be done

    Returns:
        Dictionary with ingestion statistics
    """
    from datetime import datetime

    pdf_files = discover_pdf_files(source_dir)
    logger.info(f"Found {len(pdf_files)} PDF files to process")

    # Load date overrides
    date_overrides = load_date_overrides(source_dir)
    logger.info(f"Loaded {len(date_overrides)} date overrides")

    # Ensure API key is available - check environment variable
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("ANTHROPIC_API_KEY environment variable not set")
        raise EnvironmentError(
            "ANTHROPIC_API_KEY environment variable must be set. "
            "Set it with: export ANTHROPIC_API_KEY='your-key'"
        )

    client = Anthropic(api_key=api_key)
    stats = {
        "total": len(pdf_files),
        "success": 0,
        "failed": 0,
        "skipped": 0,
        "errors": [],
        "dates_used": [],
    }

    for pdf_path, year in pdf_files:
        try:
            pdf_file = Path(pdf_path)
            logger.info(f"Processing: {pdf_file.name} ({year})")

            if dry_run:
                # Check if date override exists
                date_str = date_overrides.get(pdf_file.name, "no-override")
                logger.info(f"  Date: {date_str}")
                stats["skipped"] += 1
                continue

            # Get report date from overrides or fallback to year
            report_date_str = date_overrides.get(pdf_file.name)
            if report_date_str:
                try:
                    report_date = datetime.strptime(report_date_str, "%Y-%m-%d").date()
                    logger.info(f"  Date: {report_date} (from overrides)")
                except ValueError:
                    report_date = datetime.strptime(year, "%Y").date()
                    logger.warning(f"  Invalid override date, using year: {year}")
            else:
                report_date = datetime.strptime(year, "%Y").date()
                logger.info(f"  Date: {report_date} (year only)")

            # Try to extract doctor and lab from filename
            filename = pdf_file.stem.lower()
            doctor = None
            lab = None

            if "boyd" in filename:
                doctor = "Dr. Boyd"
                lab = "Unknown Lab"

            # Parse PDF
            lab_report = parse_pdf_report(
                pdf_path,
                person=person,
                doctor=doctor,
                lab=lab,
                client=client,
            )

            # Override report date with accurate date
            lab_report.date = report_date

            # Write to vault
            note_path = create_lab_report_note(vault_root, lab_report)
            logger.info(f"[OK] Ingested: {note_path}")
            stats["success"] += 1
            stats["dates_used"].append((pdf_file.name, str(report_date)))

        except FileNotFoundError as e:
            logger.warning(f"[FAIL] File not found: {pdf_path}")
            stats["failed"] += 1
            stats["errors"].append((pdf_path, str(e)))
        except Exception as e:
            logger.error(f"[ERROR] Error processing {pdf_path}: {e}")
            stats["failed"] += 1
            stats["errors"].append((pdf_path, str(e)))

    return stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulk ingest historical lab reports"
    )
    parser.add_argument(
        "--source",
        default="C:/Projects/health/ASK",
        help="Source directory with year-organized PDFs",
    )
    parser.add_argument(
        "--vault",
        default="C:/Projects/health/vault",
        help="Obsidian vault root directory",
    )
    parser.add_argument(
        "--person",
        default="Anup",
        help="Person name for reports",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    logger.info(f"Starting bulk ingestion from {args.source}")
    logger.info(f"Vault: {args.vault}")
    logger.info(f"Person: {args.person}")
    if args.dry_run:
        logger.info("DRY RUN MODE - no changes will be made")

    stats = ingest_all_reports(
        args.source,
        args.vault,
        person=args.person,
        dry_run=args.dry_run,
    )

    # Report results
    logger.info("\n" + "="*60)
    logger.info("INGESTION RESULTS")
    logger.info("="*60)
    logger.info(f"Total files: {stats['total']}")
    logger.info(f"Successful: {stats['success']}")
    logger.info(f"Failed: {stats['failed']}")
    logger.info(f"Skipped: {stats['skipped']}")

    if stats["dates_used"] and not args.dry_run:
        logger.info("\nDATES EXTRACTED:")
        for filename, date in sorted(stats["dates_used"]):
            logger.info(f"  {filename:<50} = {date}")

    if stats["errors"]:
        logger.info("\nERRORS:")
        for pdf_path, error in stats["errors"]:
            logger.info(f"  {pdf_path}: {error}")

    logger.info("="*60)

    return 0 if stats["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
