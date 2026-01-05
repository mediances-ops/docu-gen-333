import os, json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import google.generativeai as genai

import models
from database import engine, get_db

# Initialisation de la Base de Données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montage des fichiers statiques pour le CSS/Images
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configuration de l'IA Gemini
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-1.5-flash')

# --- ROUTES INTERFACE ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# --- API : GESTION DES PROJETS & VERSIONS ---

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    """Liste tous les projets importés"""
    projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
    return [{"id": p.id, "title": p.title, "region": p.region, "date": p.created_at.strftime("%d/%m/%Y")} for p in projects]

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: int, db: Session = Depends(get_db)):
    """Détails d'un projet pour affichage Header (Vignette + Fixer)"""
    project = db.query(models.Project).get(project_id)
    if not project: raise HTTPException(status_code=404)
    return {
        "form_data": json.loads(project.form_data), 
        "date": project.created_at.strftime("%d/%m/%Y")
    }

@app.get("/api/projects/{project_id}/versions")
async def list_versions(project_id: int, db: Session = Depends(get_db)):
    """Historique des versions pour la sidebar coulissante"""
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
    """Sauvegarde manuelle d'une version"""
    last_v = db.query(models.ScriptVersion).filter_by(project_id=project_id).order_by(models.ScriptVersion.version_number.desc()).first()
    new_no = (last_v.version_number + 1) if last_v else 1
    new_v = models.ScriptVersion(project_id=project_id, version_number=new_no, content=content, status="En cours", characterization=note)
    db.add(new_v)
    db.commit()
    return {"status": "ok", "version_number": new_no}

@app.post("/api/versions/{version_id}/fork")
async def fork_version(version_id: int, db: Session = Depends(get_db)):
    """Duplication d'une version (Fork)"""
    old_v = db.query(models.ScriptVersion).get(version_id)
    last_v = db.query(models.ScriptVersion).filter_by(project_id=old_v.project_id).order_by(models.ScriptVersion.version_number.desc()).first()
    new_v = models.ScriptVersion(project_id=old_v.project_id, version_number=last_v.version_number+1, content=old_v.content, status="En cours", characterization=f"Copie de V{old_v.version_number}")
    db.add(new_v)
    db.commit()
    return {"status": "ok"}

# --- API : BRIDGE (IMPORTATION SÉCURISÉE) ---

@app.post("/api/bridge/import")
async def import_from_scouting(request: Request, db: Session = Depends(get_db)):
    token = request.headers.get("X-Bridge-Token")
    if token != os.environ.get("BRIDGE_SECRET_TOKEN"):
        raise HTTPException(status_code=403, detail="Accès non autorisé")
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

# --- API : IA (ANGLES & GÉNÉRATION) ---

@app.post("/api/analyze_angles")
async def analyze_angles(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...)):
    """L'IA analyse les données et propose 3 angles éditoriaux"""
    prompt = f"""
    AGIS COMME UN DIRECTEUR ARTISTIQUE. 
    Données : Région {ctx}, Gardiens: {g1}, {g2}, {g3}, Convergence: {evt}.
    Propose 3 trajectoires de 52 min. 
    REPONDS UNIQUEMENT EN JSON STRICT:
    [
      {{"type": "HARMONIE", "title": "...", "desc": "..."}},
      {{"type": "RUPTURE", "title": "...", "desc": "..."}},
      {{"type": "LIEN", "title": "...", "desc": "..."}}
    ]
    """
    try:
        response = model_ia.generate_content(prompt)
        raw = response.text.replace('```json', '').replace('```', '').strip()
        return JSONResponse(content=json.loads(raw))
    except:
        return JSONResponse(status_code=500, content=[{"type":"ERR","title":"Erreur IA","desc":"Vérifiez vos données."}])

@app.post("/api/generate_full")
async def generate_full(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...), angle: str = Form(...)):
    """Génération du script final de 52 minutes"""
    prompt = f"Rédige un séquencier de 52 min pour {ctx} avec l'angle {angle}. Gardiens: {g1}, {g2}, {g3}. Fête: {evt}. Pas de voix off."
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/refine")
async def refine_script(request: Request):
    """Chatbot de retouche"""
    data = await request.json()
    prompt = f"SCENARIO: {data['current_script']}\n\nMODIF: {data['instruction']}\n\nRéécris en appliquant la modif."
    response = model_ia.generate_content(prompt)
    return {"script": response.text}

@app.post("/api/memorize")
async def memorize_rule(request: Request, db: Session = Depends(get_db)):
    """Mémorise une règle dans PostgreSQL"""
    data = await request.json()
    db.add(models.GlobalRule(content=data['rule']))
    db.commit()
    return {"status": "ok"}
