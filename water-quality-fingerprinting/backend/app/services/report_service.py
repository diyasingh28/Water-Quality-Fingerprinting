"""Generates PDF/CSV reports per station for demo/paper purposes."""

import csv
import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.core.parameters import AVAILABLE_PARAMETERS


def _fieldnames():
    base = ["station_id", "year", "predicted_source", "confidence"]
    params = []
    for p in AVAILABLE_PARAMETERS:
        params += [f"{p}_min", f"{p}_max"]
    return base + params


def generate_csv_report(readings: list) -> io.StringIO:
    buffer = io.StringIO()
    if not readings:
        return buffer

    fieldnames = _fieldnames()
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for r in readings:
        writer.writerow({k: getattr(r, k, "") for k in fieldnames})
    buffer.seek(0)
    return buffer


def generate_pdf_report(station_id: str, readings: list) -> io.BytesIO:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    y = height - 50
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, f"Water Quality Report — Station {station_id}")
    y -= 30

    c.setFont("Helvetica", 10)
    for r in readings[:40]:
        line = (
            f"Year: {r.year} | Source: {r.predicted_source or 'N/A'} "
            f"| Confidence: {r.confidence or 0:.2f} | "
            f"BOD: {r.bod_min}-{r.bod_max} | pH: {r.ph_min}-{r.ph_max}"
        )
        c.drawString(50, y, line)
        y -= 15
        if y < 50:
            c.showPage()
            y = height - 50

    c.save()
    buffer.seek(0)
    return buffer
