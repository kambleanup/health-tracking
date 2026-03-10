"""PDF lab report parser using Claude Vision API."""

import base64
import json
import logging
from datetime import datetime, date
from pathlib import Path
from typing import Optional

import pdfplumber
from anthropic import Anthropic

from ..models.health import BloodworkMetrics, LabReport

logger = logging.getLogger(__name__)


def pdf_to_images_base64(pdf_path: str) -> list[tuple[str, int]]:
    """
    Convert PDF pages to base64-encoded images.

    Returns list of (base64_data, page_number) tuples.
    """
    import io
    import numpy as np
    from PIL import Image as PILImage

    images = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Render page as image with high DPI for better OCR
                page_image = page.to_image(resolution=150)

                # Extract PIL image from pdfplumber PageImage
                if hasattr(page_image, 'src') and isinstance(page_image.src, PILImage.Image):
                    # Direct PIL Image
                    image = page_image.src
                    # Convert to RGB if needed
                    if image.mode != 'RGB':
                        image = image.convert('RGB')
                else:
                    # Try to convert numpy array
                    try:
                        arr = np.array(page_image)
                        # Handle different array shapes and dtypes
                        if arr.dtype == object or (len(arr.shape) == 3 and arr.shape[2] == 1):
                            # Palette/indexed image, try to convert
                            image = PILImage.fromarray(arr).convert('RGB')
                        elif len(arr.shape) == 2:
                            # Grayscale
                            image = PILImage.fromarray((arr * 255).astype(np.uint8) if arr.max() <= 1 else arr, mode='L').convert('RGB')
                        else:
                            # RGB or RGBA
                            if arr.dtype != np.uint8:
                                arr = (arr * 255).astype(np.uint8) if arr.max() <= 1 else arr.astype(np.uint8)
                            image = PILImage.fromarray(arr).convert('RGB')
                    except Exception as arr_err:
                        logger.warning(f"Array conversion failed, using fallback: {arr_err}")
                        # Last resort: save as PIL image directly
                        image = page_image if isinstance(page_image, PILImage.Image) else PILImage.new('RGB', (100, 100))

                # Convert PIL Image to PNG bytes then base64
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                base64_image = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
                images.append((base64_image, page_num))

                logger.info(f"Converted page {page_num} of {pdf_path}")
    except Exception as e:
        logger.error(f"Error converting PDF to images: {e}")
        raise

    return images


def extract_metrics_from_images(
    client: Anthropic,
    images_base64: list[tuple[str, int]],
    pdf_filename: str,
) -> BloodworkMetrics:
    """
    Use Claude Vision to extract lab metrics from PDF images.

    Returns BloodworkMetrics parsed from Claude's response.
    """

    # Build multi-turn conversation with Claude
    messages = []

    # Add all images to the initial message
    content = [
        {
            "type": "text",
            "text": f"""You are a medical data extraction specialist. I'm providing images of a lab report ({pdf_filename}).

Please carefully examine all pages and extract all health metrics found in the report. Focus on:
- Glucose, A1C
- Lipid panel (total cholesterol, HDL, LDL, triglycerides)
- Thyroid (TSH)
- Renal function (creatinine, BUN, GFR)
- Electrolytes (sodium, potassium, magnesium, calcium, phosphorus)
- Liver function (ALT, AST, alkaline phosphatase, albumin, total protein)
- Complete blood count (hemoglobin, hematocrit, WBC, RBC, platelets)

For each metric found, provide the value and unit. If a metric is not found or not applicable, omit it.

Return ONLY a valid JSON object with metric names as keys and numeric values as values. Example format:
{{
  "glucose": 95,
  "cholesterol_total": 185,
  "hdl": 55,
  ...
}}"""
        }
    ]

    # Add images
    for base64_image, page_num in images_base64:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image,
            },
        })

    messages.append({"role": "user", "content": content})

    # Get Claude's response
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=2000,
        messages=messages,
    )

    response_text = response.content[0].text
    logger.info(f"Claude response: {response_text}")

    # Parse JSON from response
    try:
        # Extract JSON if it's embedded in other text
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response_text[start_idx:end_idx]
            metrics_dict = json.loads(json_str)
            metrics = BloodworkMetrics(**metrics_dict)
            return metrics
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse metrics JSON: {e}")
        logger.error(f"Raw response: {response_text}")
        raise

    raise ValueError("Could not extract metrics from Claude response")


def parse_pdf_report(
    pdf_path: str,
    person: str,
    doctor: Optional[str] = None,
    lab: Optional[str] = None,
    report_type: str = "Blood Work",
    client: Optional[Anthropic] = None,
) -> LabReport:
    """
    Parse a PDF lab report and extract structured metrics.

    Args:
        pdf_path: Path to the PDF file
        person: Name of the person (Anup or Deepali)
        doctor: Doctor's name
        lab: Lab name
        report_type: Type of report (default: Blood Work)
        client: Anthropic client (creates new one if not provided)

    Returns:
        LabReport with extracted metrics
    """
    if client is None:
        client = Anthropic()

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    logger.info(f"Parsing PDF: {pdf_path}")

    # Convert PDF to images
    images = pdf_to_images_base64(str(pdf_path))
    if not images:
        raise ValueError(f"No pages found in PDF: {pdf_path}")

    # Extract metrics using Claude Vision
    metrics = extract_metrics_from_images(client, images, pdf_path.name)

    # Infer report date from filename or use today's date
    # Try to extract date from filename (YYYY-MM-DD format)
    report_date = date.today()
    for part in pdf_path.stem.split('_'):
        try:
            report_date = datetime.strptime(part, "%Y-%m-%d").date()
            break
        except ValueError:
            continue

    # Create LabReport
    lab_report = LabReport(
        person=person,
        date=report_date,
        report_type=report_type,
        doctor=doctor,
        lab=lab,
        metrics=metrics,
        file_path=str(pdf_path),
    )

    logger.info(f"Successfully parsed report for {person} dated {report_date}")
    return lab_report
