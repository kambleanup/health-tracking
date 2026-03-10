"""Extract report dates from PDFs using Claude Vision for accuracy."""

import base64
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict

import pdfplumber
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

client = Anthropic()


def pdf_to_base64_image(pdf_path: str) -> Optional[str]:
    """Convert first page of PDF to base64 image."""
    try:
        import io

        with pdfplumber.open(pdf_path) as pdf:
            if not pdf.pages:
                return None
            first_page = pdf.pages[0]
            page_image = first_page.to_image(resolution=150)

            # pdfplumber PageImage wraps a PIL Image
            # Access the underlying PIL image
            if hasattr(page_image, 'src'):
                # PIL Image object
                image = page_image.src
            elif hasattr(page_image, '__array__'):
                # Numpy array, convert to PIL
                from PIL import Image as PILImage
                import numpy as np
                arr = np.array(page_image)
                image = PILImage.fromarray(arr)
            else:
                # Try direct conversion
                image = page_image

            # Convert PIL Image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_byte_arr.seek(0)
            base64_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
            return base64_image
    except Exception as e:
        logger.warning(f"Could not convert to image: {e}")
        return None


def extract_date_with_claude(pdf_path: str, base64_image: str) -> Dict:
    """Use Claude Vision to extract report date from PDF."""
    try:
        filename = Path(pdf_path).name

        response = client.messages.create(
            model="claude-opus-4-6",
            max_tokens=200,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"""Look at this lab report and extract the TEST DATE or REPORT DATE.

Return ONLY a JSON object with:
{{
  "date": "YYYY-MM-DD or the date you see",
  "confidence": "high/medium/low",
  "note": "brief note about where found"
}}

If no date found, return null for date.
If the date appears to be a processed/received date rather than test date, prioritize test date.

Filename for context: {filename}""",
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": base64_image,
                            },
                        },
                    ],
                }
            ],
        )

        response_text = response.content[0].text

        # Parse JSON
        try:
            # Extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                return data
        except json.JSONDecodeError:
            pass

        return {"date": None, "confidence": "low", "note": "Could not parse response"}

    except Exception as e:
        logger.error(f"Claude extraction error: {e}")
        return {"date": None, "confidence": "low", "note": str(e)}


def standardize_date(date_str: str) -> Optional[str]:
    """Convert various date formats to YYYY-MM-DD."""
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
        '%m/%d/%y',      # 03/13/25
        '%Y%m%d',        # 20250313
    ]

    for fmt in formats:
        try:
            parsed = datetime.strptime(date_str, fmt)
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            continue

    return None


def analyze_all_pdfs(source_dir: str) -> list:
    """Analyze all PDFs with Claude Vision."""
    source_path = Path(source_dir)
    results = []

    pdf_files = sorted(source_path.rglob("*.pdf"))
    total = len(pdf_files)

    for idx, pdf_file in enumerate(pdf_files, 1):
        status = f"[{idx}/{total}] {pdf_file.name}... "
        print(status, end="", flush=True)

        # Get base64 image
        base64_image = pdf_to_base64_image(str(pdf_file))

        if not base64_image:
            print("[SKIP] Could not convert to image")
            continue

        # Extract with Claude
        claude_result = extract_date_with_claude(str(pdf_file), base64_image)
        date_str = claude_result.get("date")
        confidence = claude_result.get("confidence", "low")

        # Standardize
        standardized = standardize_date(date_str)

        # Fallback to year from filename
        if not standardized:
            year_match = re.search(r'20\d{2}', pdf_file.stem)
            if year_match:
                year = year_match.group(0)
                standardized = f"{year}-01-01"
                confidence = "low (year only)"

        result = {
            "file": pdf_file.name,
            "path": str(pdf_file),
            "raw_date": date_str,
            "standardized_date": standardized,
            "confidence": confidence,
            "note": claude_result.get("note", ""),
        }

        results.append(result)
        print(f"[{standardized}] ({confidence})")

    return results


def main():
    """Main entry point."""
    source_dir = "C:/Projects/health/ASK"

    logger.info("=" * 80)
    logger.info("PDF DATE EXTRACTION - CLAUDE VISION")
    logger.info("=" * 80)
    logger.info("")

    results = analyze_all_pdfs(source_dir)

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("EXTRACTION RESULTS")
    logger.info("=" * 80)
    logger.info(f"Total PDFs analyzed: {len(results)}")
    logger.info("")

    # Group by confidence
    high_conf = [r for r in results if r["confidence"] == "high"]
    medium_conf = [r for r in results if r["confidence"] == "medium"]
    low_conf = [r for r in results if r["confidence"] in ["low", "low (year only)"]]

    if high_conf:
        logger.info(f"HIGH CONFIDENCE ({len(high_conf)}):")
        for r in high_conf:
            logger.info(f"  [OK] {r['file']:<50} = {r['standardized_date']}")

    if medium_conf:
        logger.info(f"\nMEDIUM CONFIDENCE ({len(medium_conf)}):")
        for r in medium_conf:
            logger.info(f"  [~]  {r['file']:<50} = {r['standardized_date']}")

    if low_conf:
        logger.info(f"\nLOW CONFIDENCE ({len(low_conf)}):")
        for r in low_conf:
            logger.info(f"  [!]  {r['file']:<50} = {r['standardized_date']}")
            if r['note']:
                logger.info(f"       Note: {r['note']}")

    logger.info("")
    logger.info("=" * 80)

    # Export for use in bulk_ingest.py
    output_file = Path("pdf_date_mapping.json")
    output_file.write_text(json.dumps(results, indent=2))
    logger.info(f"Date mapping saved: {output_file}")
    logger.info("")

    return 0


if __name__ == "__main__":
    main()
