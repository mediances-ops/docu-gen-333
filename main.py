import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import google.generativeai as genai

import models
from database import engine, get_db

# Initialisation BDD
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montage des fichiers statiques
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# IA Configuration
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-1.5-flash')

# --- ROUTES INTERFACE ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API : LISTE ET DETAILS ---

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    try:
        projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
        return [{"id": p.id, "title": p.title, "region": p.region, "date": p.created_at.strftime("%d/%m/%Y")} for p in projects]
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    return {"form_data": json.loads(project.form_data), "date": project.created_at.strftime("%d/%m/%Y")}

# --- API : BRIDGE (IMPORT) ---

@app.post("/api/bridge/import")
async def import_from_scouting(request: Request, db: Session = Depends(get_db)):
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

# --- API : TRIPTYQUE (ANGLES) ---

@app.post("/api/analyze_angles")
async def analyze_angles(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...)):
    prompt = f"""
    AGIS COMME UN DIRECTEUR ARTISTIQUE. 
    Données : Région {ctx}, Gardiens: {g1}, {g2}, {g3}, Convergence: {evt}.
    Propose 3 trajectoires de 52 min. 
    REPONDS UNIQUEMENT EN JSON STRICT:
    [
      {{"type": "HARMONIE", "title": "Titre", "desc": "Explication"}},
      {{"type": "RUPTURE", "title": "Titre", "desc": "Explication"}},
      {{"type": "LIEN", "title": "Titre", "desc": "Explication"}}
    ]
    """
    try:
        response = model_ia.generate_content(prompt)
        raw = response.text.replace('```json', '').replace('```', '').strip()
        return JSONResponse(content=json.loads(raw))
    except:
        return JSONResponse(status_code=500, content=[{"type":"ERR","title":"Erreur IA","desc":"Vérifiez votre clé API ou vos données."}])

# --- API : GENERATION FINALE ---

@app.post("/api/generate_full")
async def generate_full(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...), angle: str = Form(...)):
    prompt = f"Rédige un séquencier de 52 minutes (format Courier New) pour le projet {ctx} avec l'angle {angle}. Gardiens: {g1}, {g2}, {g3}. Fête: {evt}. Pas de voix off."
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/refine")
async def refine_script(request: Request):
    data = await request.json()
    prompt = f"SCENARIO: {data['current_script']}\n\nMODIF: {data['instruction']}\n\nRéécris le script."
    response = model_ia.generate_content(prompt)
    return {"script": response.text}

@app.post("/api/memorize")
async def memorize_rule(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    db.add(models.GlobalRule(content=data['rule']))
    db.commit()
    return {"status": "ok"}
