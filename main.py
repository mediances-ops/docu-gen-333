import os
import json
from datetime import datetime
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import google.generativeai as genai

# Imports des modules locaux
import models
from database import engine, get_db

# Initialisation de la Base de Données
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Montage des fichiers statiques (pour le CSS et les images locales)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Configuration de l'IA Gemini
# Assure-toi que la variable GOOGLE_API_KEY est bien configurée sur Railway
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model_ia = genai.GenerativeModel('gemini-1.5-flash')

# =================================================================
# 1. ROUTES D'INTERFACE
# =================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# =================================================================
# 2. API DE GESTION DES PROJETS (BRIDGE & STUDIO)
# =================================================================

@app.get("/api/projects")
async def list_projects(db: Session = Depends(get_db)):
    """Liste tous les repérages importés pour le modal de chargement"""
    projects = db.query(models.Project).order_by(models.Project.created_at.desc()).all()
    return [{
        "id": p.id, 
        "title": p.title, 
        "region": p.region, 
        "date": p.created_at.strftime("%d/%m/%Y")
    } for p in projects]

@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: int, db: Session = Depends(get_db)):
    """Récupère les données complètes (vignette, fixer, formulaire)"""
    project = db.query(models.Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Projet non trouvé")
    
    # On renvoie le JSON de Local Scouting et la date formatée
    return {
        "form_data": json.loads(project.form_data),
        "date": project.created_at.strftime("%d/%m/%Y")
    }

@app.get("/api/projects/{project_id}/versions")
async def list_versions(project_id: int, db: Session = Depends(get_db)):
    """Liste l'historique des versions pour la sidebar coulissante"""
    v_list = db.query(models.ScriptVersion).filter_by(project_id=project_id).order_by(models.ScriptVersion.version_number.desc()).all()
    return [{
        "id": v.id, 
        "number": v.version_number, 
        "status": v.status, 
        "note": v.characterization, 
        "date": v.created_at.strftime("%d/%m %H:%M")
    } for v in v_list]

# =================================================================
# 3. API BRIDGE (IMPORTATION DEPUIS LOCAL SCOUTING)
# =================================================================

@app.post("/api/bridge/import")
async def import_from_scouting(request: Request, db: Session = Depends(get_db)):
    """Route sécurisée recevant le paquet JSON de Local Scouting"""
    token = request.headers.get("X-Bridge-Token")
    if token != os.environ.get("BRIDGE_SECRET_TOKEN"):
        raise HTTPException(status_code=403, detail="Clé secrète invalide")
    
    try:
        raw_data = await request.json()
        region_name = raw_data.get('region', 'Inconnue')
        
        # Création du dossier projet dans Docu-Gen
        new_project = models.Project(
            title=f"IMPORT: {region_name}",
            region=region_name,
            form_data=json.dumps(raw_data)
        )
        db.add(new_project)
        db.commit()
        db.refresh(new_project)
        
        return {"status": "success", "project_id": new_project.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# =================================================================
# 4. API IA (TRIPTYQUE & RÉDACTION)
# =================================================================

@app.post("/api/analyze_angles")
async def analyze_angles(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...)):
    """L'IA analyse le terrain et propose les 3 visions artistiques"""
    prompt = f"""
    AGIS COMME UN DIRECTEUR ARTISTIQUE DE DOCUMENTAIRE.
    Données terrain : Région {ctx}.
    Gardiens identifiés : {g1}, {g2}, {g3}.
    Célébration finale : {evt}.

    Propose 3 angles éditoriaux (trajectoires narratives) différents pour ce film.
    RÉPONDS EXCLUSIVEMENT EN JSON STRICT AU FORMAT SUIVANT :
    [
      {{"type": "HARMONIE", "title": "...", "desc": "..."}},
      {{"type": "RUPTURE", "title": "...", "desc": "..."}},
      {{"type": "LIEN", "title": "...", "desc": "..."}}
    ]
    """
    try:
        response = model_ia.generate_content(prompt)
        # Nettoyage pour extraire le JSON
        json_clean = response.text.replace('```json', '').replace('```', '').strip()
        return JSONResponse(content=json.loads(json_clean))
    except Exception as e:
        return JSONResponse(status_code=500, content=[{"type":"ERR","title":"Erreur IA","desc":"Vérifiez vos données."}])

@app.post("/api/generate_full")
async def generate_full(ctx: str = Form(...), g1: str = Form(...), g2: str = Form(...), g3: str = Form(...), evt: str = Form(...), angle: str = Form(...)):
    """Rédige le script final de 52 minutes basé sur l'angle choisi"""
    prompt = f"""
    Rédige un séquencier de documentaire de 52 minutes.
    CONTEXTE : {ctx}
    ANGLE CHOISI : {angle}
    TRINITÉ : {g1}, {g2}, {g3}
    FINAL : {evt}
    RÈGLES : Format Courier New, narration par verbatims uniquement, pas de voix-off descriptive.
    """
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/refine")
async def refine_script(request: Request):
    """Chatbot : Applique une modification locale au script"""
    data = await request.json()
    prompt = f"""
    SCÉNARIO ACTUEL : {data['current_script']}
    INSTRUCTION DE MODIFICATION : {data['instruction']}
    Réécris le scénario en appliquant la consigne technique. Garde le format.
    """
    try:
        response = model_ia.generate_content(prompt)
        return {"script": response.text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# =================================================================
# 5. GESTION DES VERSIONS & MÉMOIRE
# =================================================================

@app.post("/api/projects/{project_id}/save_version")
async def save_version(project_id: int, content: str = Form(...), note: str = Form(...), db: Session = Depends(get_db)):
    """Enregistre une nouvelle itération du travail"""
    last_v = db.query(models.ScriptVersion).filter_by(project_id=project_id).order_by(models.ScriptVersion.version_number.desc()).first()
    new_no = (last_v.version_number + 1) if last_v else 1
    
    new_v = models.ScriptVersion(
        project_id=project_id, 
        version_number=new_no, 
        content=content, 
        status="En cours", 
        characterization=note
    )
    db.add(new_v)
    db.commit()
    return {"status": "ok", "version_number": new_no}

@app.post("/api/memorize")
async def memorize_rule(request: Request, db: Session = Depends(get_db)):
    """Ajoute une règle d'or définitive dans le cerveau PostgreSQL"""
    data = await request.json()
    new_rule = models.GlobalRule(content=data['rule'])
    db.add(new_rule)
    db.commit()
    return {"status": "ok"}

# =================================================================
# 6. DÉMARRAGE
# =================================================================

if __name__ == "__main__":
    import uvicorn
    # Le port est géré par Railway via la variable d'environnement
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
