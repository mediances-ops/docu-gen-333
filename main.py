import os, json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import google.generativeai as genai
import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)
app = FastAPI()
templates = Jinja2Templates(directory="templates")

genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
    return [{"id": p.id, "title": p.title, "region": p.region} for p in projects]

@app.get("/api/projects/{project_id}/versions")
async def list_versions(project_id: int, db: Session = Depends(get_db)):
    v_list = db.query(models.ScriptVersion).filter_by(project_id=project_id).order_by(models.ScriptVersion.version_number.desc()).all()
    return [{
        "id": v.id, 
        "number": v.version_number, 
        "status": v.status, 
        "note": v.characterization, 
        "date": v.created_at.strftime("%d/%m %H:%M")
    } for v in v_list]

@app.post("/api/projects/{project_id}/save_version")
async def save_version(project_id: int, content: str = Form(...), note: str = Form(...), db: Session = Depends(get_db)):
    last_v = db.query(models.ScriptVersion).filter_by(project_id=project_id).order_by(models.ScriptVersion.version_number.desc()).first()
    new_no = (last_v.version_number + 1) if last_v else 1
    new_v = models.ScriptVersion(project_id=project_id, version_number=new_no, content=content, status="En cours", characterization=note)
    db.add(new_v)
    db.commit()
    return {"status": "ok", "version_number": new_no}

@app.post("/api/versions/{version_id}/fork")
async def fork_version(version_id: int, db: Session = Depends(get_db)):
    old_v = db.query(models.ScriptVersion).get(version_id)
    last_v = db.query(models.ScriptVersion).filter_by(project_id=old_v.project_id).order_by(models.ScriptVersion.version_number.desc()).first()
    new_v = models.ScriptVersion(project_id=old_v.project_id, version_number=last_v.version_number+1, content=old_v.content, status="En cours", characterization=f"Copie de V{old_v.version_number}")
    db.add(new_v)
    db.commit()
    return {"status": "ok"}
