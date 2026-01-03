import os
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

# IA Configuration
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# LA PASSERELLE (Bridge)
@app.post("/api/bridge/import")
async def import_from_scouting(request: Request, db: Session = Depends(get_db)):
    # Vérification de sécurité
    token = request.headers.get("X-Bridge-Token")
    if token != os.environ.get("BRIDGE_SECRET_TOKEN"):
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    data = await request.json()
    new_project = models.Project(
        title=f"IMPORT: {data.get('region')} - {data.get('pays')}",
        region=data.get('region'),
        form_data=str(data) # On stocke tout le dossier reçu
    )
    db.add(new_project)
    db.commit()
    return {"status": "success", "project_id": new_project.id}

# Autres routes (Generation, etc...) à ajouter ensuite
