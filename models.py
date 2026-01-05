from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
from database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Nouveau Projet")
    region = Column(String, index=True)
    share_token = Column(String, unique=True, index=True, default=lambda: secrets.token_urlsafe(12))
    form_data = Column(Text) # JSON brut du repérage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    versions = relationship("ScriptVersion", back_populates="project", cascade="all, delete-orphan")

class GlobalRule(Base):
    __tablename__ = "global_rules"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ScriptVersion(Base):
    __tablename__ = "versions"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    
    version_number = Column(Integer)
    content = Column(Text)
    
    # Nouveaux champs Studio
    status = Column(String(50), default="Non Vu") # Non Vu, En cours, Validé
    characterization = Column(String(255)) # ex: "Angle Rupture - Premier jet"
    
    created_at = Column(DateTime, default=datetime.utcnow)
    project = relationship("Project", back_populates="versions")
