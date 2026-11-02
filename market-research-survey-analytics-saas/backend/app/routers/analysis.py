from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project, Dataset
from ..auth import current_user
from ..file_utils import UPLOAD_DIR, read_dataset
from .. import analytics
from ..insights import generate_insights

router = APIRouter(prefix="/api/analysis", tags=["analysis"])

def owned_dataset(db, user, dataset_id):
    ds = db.query(Dataset).join(Project).filter(Dataset.id == dataset_id, Project.owner_id == user.id).first()
    if not ds: raise HTTPException(404, "Dataset not found")
    return ds

def frame(db, user, dataset_id):
    ds = owned_dataset(db, user, dataset_id)
    try: return read_dataset(UPLOAD_DIR / ds.stored_filename)
    except Exception as exc: raise HTTPException(400, f"Cannot read dataset: {exc}") from exc

@router.get("/{dataset_id}/overview")
def get_overview(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return analytics.overview(frame(db,user,dataset_id))

@router.get("/{dataset_id}/frequency")
def get_frequency(dataset_id: int, column: str, top_n: int = Query(15, ge=1, le=50), db: Session = Depends(get_db), user: User = Depends(current_user)):
    try: return analytics.frequency(frame(db,user,dataset_id), column, top_n)
    except KeyError: raise HTTPException(400, "Unknown column")

@router.get("/{dataset_id}/crosstab")
def get_crosstab(dataset_id: int, row: str, col: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    try: return analytics.crosstab(frame(db,user,dataset_id), row, col)
    except (KeyError, ValueError) as exc: raise HTTPException(400, str(exc))

@router.get("/{dataset_id}/numeric")
def get_numeric(dataset_id: int, column: str, db: Session = Depends(get_db), user: User = Depends(current_user)):
    try: return analytics.numeric_summary(frame(db,user,dataset_id), column)
    except (KeyError, ValueError) as exc: raise HTTPException(400, str(exc))

@router.get("/{dataset_id}/correlation")
def get_corr(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return analytics.correlation_matrix(frame(db,user,dataset_id))

@router.get("/{dataset_id}/insights")
def get_insights(dataset_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    return generate_insights(frame(db,user,dataset_id))
