"""
reports/generate_pdf.py

Generates a professional PDF report combining file metadata and AI
detection results for the AI Deepfake Detection System.

Exposes:
    generate_report(metadata, result, confidence, output_path,
                     voice=None, lip_sync=None) -> str

This module is intentionally kept independent of Flask so it can be
imported and called directly by the backend team (Gopika).
"""

import os
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_CENTER


def generate_report(metadata, result, confidence, output_path,
                     voice=None, lip_sync=None):
    """
    Generate a PDF report for a single deepfake detection result.

    Args:
        metadata (dict): Output of metadata.extract_metadata().
                          Expected keys (all optional, missing keys
                          are handled gracefully):
                          file_name, file_size, format, resolution,
                          fps, duration.
        result (str): Detection status, e.g. "Real" or "Fake".
        confidence (int | float): Confidence score, e.g. 96 (percent).
        output_path (str): Full path (including filename) where the
                            PDF should be saved, e.g.
                            "generated_reports/report_CMP001.pdf".
        voice (str, optional): Voice analysis result, e.g. "Fake".
        lip_sync (str, optional): Lip sync result, e.g. "Mismatch".

    Returns:
        str: The path to the generated PDF file.

    Raises:
        ValueError: If output_path has no filename/extension.
    """

    if not output_path or not output_path.lower().endswith(".pdf"):
        raise ValueError("output_path must be a file path ending in .pdf")

    # Make sure the destination folder exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    metadata = metadata or {}

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        alignment=TA_CENTER,
        fontSize=18,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.grey,
        spaceAfter=16,
    )
    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=13,
        spaceBefore=12,
        spaceAfter=8,
        textColor=colors.HexColor("#1a1a1a"),
    )

    story = []

    # --- Title ---
    story.append(Paragraph("AI Deepfake Detection Report", title_style))
    story.append(Paragraph("Automated Analysis Summary", subtitle_style))

    # --- File Information Section ---
    story.append(Paragraph("File Information", section_style))
    file_info_rows = [
        ["File Name", _safe(metadata.get("file_name"))],
        ["File Size", _safe(metadata.get("file_size"))],
        ["Format", _safe(metadata.get("format"))],
        ["Resolution", _safe(metadata.get("resolution"))],
        ["FPS", _safe(metadata.get("fps"))],
        ["Duration", _format_duration(metadata.get("duration"))],
    ]
    story.append(_build_table(file_info_rows))

    # --- AI Analysis Section ---
    story.append(Paragraph("AI Analysis", section_style))

    status_text = _safe(result).upper()
    status_color = colors.red if str(result).lower() == "fake" else colors.green

    analysis_rows = [
        ["Detection Status", status_text],
        ["Confidence", _format_confidence(confidence)],
        ["Voice Analysis", _safe(voice).upper() if voice else "N/A"],
        ["Lip Sync", _safe(lip_sync).upper() if lip_sync else "N/A"],
    ]
    analysis_table = _build_table(analysis_rows)
    # Highlight the "Detection Status" value cell (row 0, col 1) in red/green
    analysis_table.setStyle(TableStyle([
        ("TEXTCOLOR", (1, 0), (1, 0), status_color),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
    ]))
    story.append(analysis_table)

    # --- Generated Info Section ---
    story.append(Paragraph("Generated Information", section_style))
    generated_rows = [
        ["Generated Time", datetime.now().strftime("%d-%m-%Y %I:%M %p")],
    ]
    story.append(_build_table(generated_rows))

    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.grey,
    )
    story.append(Paragraph(
        "This report was generated automatically by the AI Deepfake "
        "Detection System.", footer_style
    ))

    doc.build(story)
    return output_path


def _build_table(rows):
    """Build a consistently styled two-column table (label | value)."""
    table = Table(rows, colWidths=[55 * mm, 105 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2f2")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#333333")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#dddddd")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    return table


def _safe(value):
    """Return a safe display string for possibly-missing values."""
    if value is None or value == "":
        return "N/A"
    return str(value)


def _format_confidence(confidence):
    if confidence is None:
        return "N/A"
    try:
        return f"{float(confidence):.0f}%"
    except (ValueError, TypeError):
        return _safe(confidence)


def _format_duration(duration):
    if duration is None:
        return "N/A"
    try:
        return f"{float(duration):.1f} seconds"
    except (ValueError, TypeError):
        return _safe(duration)


# --- Quick manual test (run this file directly to sanity-check it) ---
if __name__ == "__main__":
    sample_metadata = {
        "file_name": "suspicious_video.mp4",
        "file_size": "12.5 MB",
        "format": "MP4",
        "resolution": "1920x1080",
        "fps": 30,
        "duration": 25.4,
    }

    path = generate_report(
        metadata=sample_metadata,
        result="Fake",
        confidence=96,
        output_path="generated_reports/test_report.pdf",
        voice="Fake",
        lip_sync="Mismatch",
    )
    print(f"Report generated at: {path}")