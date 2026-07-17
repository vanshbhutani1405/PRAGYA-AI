from datetime import datetime, timezone
from io import BytesIO

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from services.supabase_service import _client

router = APIRouter(prefix="/api/v1/conflicts", tags=["conflicts"])

_RESPONSIBLE_ROLE = "shift_supervisor"


@router.get("")
async def list_conflicts():
    response = (
        _client.table("conflicts")
        .select("*")
        .order("severity", desc=True)
        .order("detected_at", desc=True)
        .execute()
    )
    return response.data


@router.get("/{conflict_id}")
async def get_conflict(conflict_id: str):
    response = (
        _client.table("conflicts").select("*").eq("id", conflict_id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return response.data[0]


@router.patch("/{conflict_id}/resolve")
async def resolve_conflict(conflict_id: str):
    resolved_at = datetime.now(timezone.utc).isoformat()
    response = (
        _client.table("conflicts")
        .update({"status": "resolved", "resolved_at": resolved_at})
        .eq("id", conflict_id)
        .execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Conflict not found")
    return response.data[0]


def _build_work_order_pdf(conflict: dict) -> bytes:
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 25 * mm
    y = height - 30 * mm

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(left, y, "PRAGYA AI - Pre-Filled Work Order")
    y -= 12 * mm

    fields = [
        ("Conflict Description", conflict.get("description", "")),
        ("Equipment Tag", conflict.get("equipment_tag", "")),
        ("Recommended Action", conflict.get("recommended_action", "")),
        ("Responsible Role", _RESPONSIBLE_ROLE),
        ("Deadline", conflict.get("deadline", "")),
        ("Regulatory Reference", conflict.get("regulatory_reference", "")),
        (
            "Financial Exposure (INR)",
            str(conflict.get("financial_exposure_inr", "")),
        ),
    ]

    for label, value in fields:
        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(left, y, f"{label}:")
        y -= 6 * mm
        pdf.setFont("Helvetica", 11)
        for line in _wrap(str(value), 90):
            pdf.drawString(left + 4 * mm, y, line)
            y -= 6 * mm
        y -= 3 * mm

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if len(candidate) > width:
            if current:
                lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines or [""]


@router.post("/{conflict_id}/generate")
async def generate_work_order(conflict_id: str):
    response = (
        _client.table("conflicts").select("*").eq("id", conflict_id).execute()
    )
    if not response.data:
        raise HTTPException(status_code=404, detail="Conflict not found")
    pdf_bytes = _build_work_order_pdf(response.data[0])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=work_order_{conflict_id}.pdf"
        },
    )
