from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))

from app.database import Base,engine,SessionLocal
from app.models import User,Project
from app.auth import hash_password
import app.seed_demo  # generates the demo CSV

Base.metadata.create_all(bind=engine)
db=SessionLocal()
try:
    email='demo@insightforge.dev'
    user=db.query(User).filter(User.email==email).first()
    if not user:
        user=User(email=email,full_name='Portfolio Analyst',password_hash=hash_password('portfolio123'))
        db.add(user);db.commit();db.refresh(user)
    if not db.query(Project).filter(Project.owner_id==user.id).first():
        db.add(Project(
            owner_id=user.id,
            name='Customer Experience Study',
            description='Synthetic customer experience research demo',
            research_objective='Understand satisfaction, recommendation intent, spending patterns and segment differences.'
        ))
        db.commit()
    print('Demo account ready: demo@insightforge.dev / portfolio123')
finally:
    db.close()
