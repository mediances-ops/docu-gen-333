import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import google.generativeai as genai

# Imports locaux
import models
from database import engine, get_db

# Initialisation de la base de données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montage des fichiers statiques si le dossier existe
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configuration IA
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-1.5-flash')

# --- ROUTES INTERFACE ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API : LISTE DES PROJETS (Celle qui causait le 404) ---

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    """Récupère la liste de tous les repérages importés"""
    try:
        projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
        return [{"id": p.id, "title": p.title, "region": p.region, "date": p.created_at.strftime("%d/%m/%Y")} for p in projects]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: int, db: Session = Depends(get_db)):
    """Récupère les données d'un projet précis"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return {"form_data": json.loads(project.form_data)}

# --- API : IMPORTATION DEPUIS LE BRIDGE ---

@app.post("/api/bridge/import")
async def import_from_scouting(request: Request, db: Session = Depends(get_db)):
    # Vérification sécurité
    token = request.headers.get("X-Bridge-Token")
    if token != os.environ.get("BRIDGE_SECRET_TOKEN"):
        raise HTTPException(status_code=403, detail="Clé secrète invalide")
    
    try:
        raw_data = await request.json()
        new_project = models.Project(
            title=f"IMPORT: {raw_data.get('region', 'Inconnue')}",
            region=raw_data.get('region', 'Inconnue'),
            form_data=json.dumps(raw_data)
        )
        db.add(new_project)
        db.commit()
        return {"status": "success", "project_id": new_project.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# --- API : GÉNÉRATION & CHATBOT ---

@app.post("/api/generate_full")
async def generate_full(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...)):
    prompt = f"Rôle: Scénariste Docu. Structure 333+1. CTX: {ctx}. G1: {g1}. G2: {g2}. G3: {g3}. Fête: {evt}. Écris le scénario."
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/refine")
async def refine_script(request: Request):
    data = await request.json()
    prompt = f"SCÉNARIO: {data['current_script']}\n\nINSTRUCTION: {data['instruction']}\n\nRéécris en appliquant la modif."
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/memorize")
async def memorize_rule(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    new_rule = models.GlobalRule(content=data['rule'])
    db.add(new_rule)
    db.commit()
    return {"status": "ok"}
