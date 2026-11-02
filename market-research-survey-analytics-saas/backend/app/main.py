from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import Base, engine
from .routers import auth, projects, datasets, analysis, reports

Base.metadata.create_all(bind=engine)

app = FastAPI(title="InsightForge Survey Analytics API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(datasets.router)
app.include_router(analysis.router)
app.include_router(reports.router)

@app.get("/api/health")
def health():
    return {"status":"ok","service":"InsightForge Survey Analytics API"}
