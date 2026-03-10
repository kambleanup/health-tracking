"""Extract report dates from PDFs to verify date accuracy."""

import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

import pdfplumber


def extract_date_from_pdf(pdf_path: str) -> Optional[Tuple[str, str]]:
    """
    Extract report date from PDF content.

    Returns tuple of (date_string, extraction_method).
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Get first page text
            first_page = pdf.pages[0]
            text = first_page.extract_text()

            if not text:
                return None, "No text extracted"

            # Try various date patterns
            patterns = [
                # ISO format: 2025-03-13, 03/13/2025
                (r'\b(\d{1,2}[-/]\d{1,2}[-/]\d{4})\b', 'MM/DD/YYYY format'),
                (r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b', 'YYYY-MM-DD format'),
                # Written dates: March 13, 2025 / 13 Mar 2025
                (r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})', 'Month DD, YYYY'),
                (r'(\d{1,2} (?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4})', 'DD Month YYYY'),
                # Date collected / Report date
                (r'(?:Date|Collected|Report Date|Test Date)[:\s]+([^;\n]+)', 'Label-based'),
            ]

            for pattern, method in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1).strip()
                    return date_str, method

            # Try to find any 4-digit year as fallback
            year_match = re.search(r'\b(20\d{2})\b', text)
            if year_match:
                year = year_match.group(1)
                return year, "Year only (fallback)"

            return None, "No date pattern matched"

    except Exception as e:
        return None, f"Error: {str(e)}"


def standardize_date(date_str: str) -> Optional[str]:
    """
    Convert various date formats to YYYY-MM-DD.

    Returns standardized date or None if cannot parse.
    """
    if not date_str:
        return None

    date_str = date_str.strip()

    # Try common formats
    formats = [
        '%m/%d/%Y',      # 03/13/2025
        '%m-%d-%Y',      # 03-13-2025
        '%Y-%m-%d',      # 2025-03-13
        '%Y/%m/%d',      # 2025/03/13
        '%d/%m/%Y',      # 13/03/2025
        '%B %d, %Y',     # March 13, 2025
        '%b %d, %Y',     # Mar 13, 2025
        '%d %B %Y',      # 13 March 2025
        '%d %b %Y',      # 13 Mar 2025
        '%B %d %Y',      # March 13 2025
        '%b %d %Y',      # Mar 13 2025
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def analyze_all_pdfs(source_dir: str) -> list:
    """Analyze all PDFs and extract dates."""
    source_path = Path(source_dir)
    results = []

    pdf_files = sorted(source_path.rglob("*.pdf"))

    for pdf_file in pdf_files:
        print(f"Scanning: {pdf_file.name}...", end=" ")

        # Try filename first
        filename = pdf_file.stem
        year_from_filename = re.search(r'20\d{2}', filename)
        year_hint = year_from_filename.group(0) if year_from_filename else None

        # Extract from PDF content
        date_str, method = extract_date_from_pdf(str(pdf_file))

        # Standardize
        standardized = standardize_date(date_str) if date_str else None

        # Fallback to year only
        if not standardized and year_hint:
            standardized = f"{year_hint}-01-01"
            method = f"{method} (year from filename)"

        result = {
            "file": pdf_file.name,
            "path": str(pdf_file),
            "extracted_date": date_str,
            "extraction_method": method,
            "standardized_date": standardized,
            "year_hint": year_hint,
        }

        results.append(result)
        print(f"[{standardized}] {method}")

    return results


def main():
    """Main entry point."""
    source_dir = "C:/Projects/health/ASK"

    print("="*80)
    print("PDF DATE EXTRACTION ANALYSIS")
    print("="*80)
    print()

    results = analyze_all_pdfs(source_dir)

    # Summary
    print()
    print("="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total PDFs scanned: {len(results)}")
    print()

    # Group by success
    successful = [r for r in results if r["standardized_date"]]
    partial = [r for r in results if not r["standardized_date"] and r["year_hint"]]
    failed = [r for r in results if not r["standardized_date"] and not r["year_hint"]]

    print(f"Fully extracted: {len(successful)}")
    for r in successful:
        print(f"  ✓ {r['file']:<50} → {r['standardized_date']}")

    if partial:
        print(f"\nPartial (year only): {len(partial)}")
        for r in partial:
            print(f"  ~ {r['file']:<50} → {r['standardized_date']} (from filename)")

    if failed:
        print(f"\nFailed: {len(failed)}")
        for r in failed:
            print(f"  ✗ {r['file']:<50} → NEEDS MANUAL DATE")

    print()
    print("="*80)

    # Export as JSON for reference
    import json
    output_file = Path("pdf_date_extraction_report.json")
    output_file.write_text(json.dumps(results, indent=2))
    print(f"Detailed report saved: {output_file}")

    return 0 if not failed else 1


if __name__ == "__main__":
    main()
