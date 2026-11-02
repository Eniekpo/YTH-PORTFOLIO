from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, Project
from ..schemas import ProjectCreate, ProjectOut
from ..auth import current_user

router = APIRouter(prefix="/api/projects", tags=["projects"])

@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), user: User = Depends(current_user)):
    return db.query(Project).filter(Project.owner_id == user.id).order_by(Project.created_at.desc()).all()

@router.post("", response_model=ProjectOut)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db), user: User = Depends(current_user)):
    project = Project(owner_id=user.id, **payload.model_dump())
    db.add(project); db.commit(); db.refresh(project)
    return project

@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not p: raise HTTPException(404, "Project not found")
    return p

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not p: raise HTTPException(404, "Project not found")
    db.delete(p); db.commit()
    return {"deleted": project_id}
