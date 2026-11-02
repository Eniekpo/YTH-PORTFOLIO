from io import BytesIO
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd
from ..database import get_db
from ..models import User, Project, Dataset
from ..auth import current_user
from ..file_utils import UPLOAD_DIR, read_dataset
from ..analytics import overview
from ..insights import generate_insights

router = APIRouter(prefix="/api/reports", tags=["reports"])

def owned_dataset(db, user, dataset_id):
    ds = db.query(Dataset).join(Project).filter(Dataset.id == dataset_id, Project.owner_id == user.id).first()
    if not ds: raise HTTPException(404, "Dataset not found")
    return ds

@router.get("/{dataset_id}/xlsx")
def export_xlsx(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    ds = owned_dataset(db,user,dataset_id)
    df = read_dataset(UPLOAD_DIR / ds.stored_filename)
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Responses", index=False)
        pd.DataFrame(overview(df)["profile"]).to_excel(writer, sheet_name="Variable Profile", index=False)
        pd.DataFrame({"Insight": generate_insights(df)["bullets"]}).to_excel(writer, sheet_name="Insights", index=False)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=survey_analysis.xlsx"})

@router.get("/{dataset_id}/pdf")
def export_pdf(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    ds = owned_dataset(db,user,dataset_id)
    df = read_dataset(UPLOAD_DIR / ds.stored_filename)
    ov, ins = overview(df), generate_insights(df)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    _, height = A4
    y=height-55
    c.setFont("Helvetica-Bold", 17); c.drawString(45,y,"Survey Analytics Report"); y-=30
    c.setFont("Helvetica", 10); c.drawString(45,y,f"Dataset: {ds.original_filename}"); y-=18
    c.drawString(45,y,f"Responses: {ov['rows']:,}   Variables: {ov['columns']}   Completeness: {ov['completeness_pct']}%"); y-=30
    c.setFont("Helvetica-Bold", 12); c.drawString(45,y,"Automated Research Snapshot"); y-=22
    c.setFont("Helvetica", 9)
    for bullet in ins["bullets"]:
        words=bullet.split(); line="•"
        for word in words:
            test=f"{line} {word}"
            if c.stringWidth(test,"Helvetica",9)>500:
                c.drawString(50,y,line); y-=14; line=word
            else:
                line=test
        c.drawString(50,y,line); y-=20
        if y<70:
            c.showPage(); y=height-55; c.setFont("Helvetica",9)
    c.save(); buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition":"attachment; filename=survey_analysis_report.pdf"})
