from pathlib import Path
import shutil, uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project, Dataset
from ..schemas import DatasetOut
from ..auth import current_user
from ..file_utils import UPLOAD_DIR, safe_name, read_dataset

router = APIRouter(prefix="/api", tags=["datasets"])

def owned_project(db, user, project_id):
    p = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not p: raise HTTPException(404, "Project not found")
    return p

@router.get("/projects/{project_id}/datasets", response_model=list[DatasetOut])
def list_datasets(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    owned_project(db, user, project_id)
    return db.query(Dataset).filter(Dataset.project_id == project_id).order_by(Dataset.uploaded_at.desc()).all()

@router.post("/projects/{project_id}/datasets", response_model=DatasetOut)
def upload_dataset(project_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(current_user)):
    owned_project(db, user, project_id)
    cleaned = safe_name(file.filename or "dataset.csv")
    suffix = Path(cleaned).suffix.lower()
    if suffix not in {".csv", ".xlsx", ".xls"}:
        raise HTTPException(400, "Upload a CSV or Excel file")
    stored = f"{uuid.uuid4().hex}_{cleaned}"
    dest = UPLOAD_DIR / stored
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)
    try:
        df = read_dataset(dest)
    except Exception as exc:
        dest.unlink(missing_ok=True)
        raise HTTPException(400, f"Could not read dataset: {exc}") from exc
    ds = Dataset(project_id=project_id, original_filename=cleaned, stored_filename=stored, row_count=len(df), column_count=len(df.columns))
    db.add(ds); db.commit(); db.refresh(ds)
    return ds

@router.delete("/datasets/{dataset_id}")
def delete_dataset(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    ds = db.query(Dataset).join(Project).filter(Dataset.id == dataset_id, Project.owner_id == user.id).first()
    if not ds: raise HTTPException(404, "Dataset not found")
    (UPLOAD_DIR / ds.stored_filename).unlink(missing_ok=True)
    db.delete(ds); db.commit()
    return {"deleted": dataset_id}
