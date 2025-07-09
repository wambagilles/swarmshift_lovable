"""
Backend FastAPI pour l'application SwarmShift
Convertit la logique Streamlit en API REST
"""
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
import uuid
import os
import tempfile
import shutil
from datetime import datetime
import logging

# Imports des modules existants
from src.auth import login, signup, logout, is_authenticated, get_current_user_id, get_current_user
from src.firebase_db import (
    create_rag, get_rag, get_user_rags_ids, get_user_rags_details,
    update_rag, delete_rag, add_document_to_rag
)
from src.document_processor import save_uploaded_file, process_document, process_web_url
from src.agents.swarm_workflow import stream_agent_workflow, extract_rag_sources
from src.config import DEV_MODE, APP_NAME, APP_DESCRIPTION
from src.user_store_session import update_session_value, get_session_value, get_logged_user_id
from src.utils import get_documents_by_source

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version="1.0.0"
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier les domaines autorisés
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sécurité
security = HTTPBearer(auto_error=False)

# Modèles Pydantic
class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    password: str
    confirm_password: str

class CreateRAGRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    embedding_model: str = "openai"
    llm_model: str = "gpt-3.5-turbo"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    split_method: str = "recursive"
    vector_db: str = "chroma"

class AddURLRequest(BaseModel):
    urls: List[str]

class ChatRequest(BaseModel):
    message: str
    rag_id: str
    display_reasoning: Optional[bool] = False

class UpdateRAGRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

# Réponses
class AuthResponse(BaseModel):
    success: bool
    message: str
    user_id: Optional[str] = None

class RAGResponse(BaseModel):
    success: bool
    rag_id: Optional[str] = None
    message: str

class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[str]] = []
    reasoning: Optional[str] = None

class RAGDetail(BaseModel):
    id: str
    name: str
    description: str
    config: Dict[str, Any]
    created_at: str
    updated_at: str
    documents: List[Dict[str, Any]]
    document_count: int

class UserStats(BaseModel):
    total_rags: int
    total_documents: int

# Sessions utilisateur (en mémoire pour la démo)
user_sessions: Dict[str, Dict[str, Any]] = {}

# Fonctions utilitaires
def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère l'utilisateur actuel à partir du token"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Token manquant")
    
    # En mode DEV, on simule l'authentification
    if DEV_MODE:
        # Récupérer l'utilisateur depuis la session
        user_id = get_logged_user_id()
        if not user_id:
            raise HTTPException(status_code=401, detail="Utilisateur non authentifié")
        return user_id
    
    # En mode PROD, vérifier le token Firebase
    # TODO: Implémenter la vérification du token Firebase
    raise HTTPException(status_code=401, detail="Authentification non implémentée en mode PROD")

def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Récupère l'utilisateur actuel de manière optionnelle"""
    try:
        return get_current_user_from_token(credentials)
    except HTTPException:
        return None

# Routes d'authentification
@app.post("/api/auth/login", response_model=AuthResponse)
async def api_login(request: LoginRequest):
    """Connexion utilisateur"""
    try:
        success, message = login(request.email, request.password)
        if success:
            user_id = get_logged_user_id()
            return AuthResponse(success=True, message=message, user_id=user_id)
        else:
            return AuthResponse(success=False, message=message)
    except Exception as e:
        logger.error(f"Erreur lors de la connexion: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/api/auth/signup", response_model=AuthResponse)
async def api_signup(request: SignupRequest):
    """Inscription utilisateur"""
    try:
        success, message = signup(request.email, request.password, request.confirm_password)
        if success:
            user_id = get_logged_user_id()
            return AuthResponse(success=True, message=message, user_id=user_id)
        else:
            return AuthResponse(success=False, message=message)
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/api/auth/logout")
async def api_logout(user_id: str = Depends(get_current_user_from_token)):
    """Déconnexion utilisateur"""
    try:
        success, message = logout()
        return {"success": success, "message": message}
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/auth/me")
async def get_current_user_info(user_id: str = Depends(get_current_user_from_token)):
    """Récupère les informations de l'utilisateur actuel"""
    try:
        user = get_current_user()
        return {"user_id": user_id, "user": user}
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Routes des RAGs
@app.get("/api/rags", response_model=List[RAGDetail])
async def get_user_rags(user_id: str = Depends(get_current_user_from_token)):
    """Récupère la liste des RAGs de l'utilisateur"""
    try:
        rags_details = get_user_rags_details(user_id)
        rags_list = []
        
        for rag_id, rag_data in rags_details.items():
            documents_by_source = get_documents_by_source(rag_data)
            document_count = sum(len(docs) for docs in documents_by_source.values())
            
            rag_detail = RAGDetail(
                id=rag_id,
                name=rag_data.get('name', ''),
                description=rag_data.get('description', ''),
                config=rag_data.get('config', {}),
                created_at=rag_data.get('created_at', ''),
                updated_at=rag_data.get('updated_at', ''),
                documents=rag_data.get('documents', []),
                document_count=document_count
            )
            rags_list.append(rag_detail)
        
        return rags_list
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des RAGs: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.get("/api/rags/{rag_id}", response_model=RAGDetail)
async def get_rag_detail(rag_id: str, user_id: str = Depends(get_current_user_from_token)):
    """Récupère les détails d'un RAG spécifique"""
    try:
        rag_data = get_rag(user_id, rag_id)
        if not rag_data:
            raise HTTPException(status_code=404, detail="RAG non trouvé")
        
        documents_by_source = get_documents_by_source(rag_data)
        document_count = sum(len(docs) for docs in documents_by_source.values())
        
        return RAGDetail(
            id=rag_id,
            name=rag_data.get('name', ''),
            description=rag_data.get('description', ''),
            config=rag_data.get('config', {}),
            created_at=rag_data.get('created_at', ''),
            updated_at=rag_data.get('updated_at', ''),
            documents=rag_data.get('documents', []),
            document_count=document_count
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du RAG: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/api/rags", response_model=RAGResponse)
async def create_new_rag(request: CreateRAGRequest, user_id: str = Depends(get_current_user_from_token)):
    """Crée un nouveau RAG"""
    try:
        config = {
            "embedding_model": request.embedding_model,
            "llm_model": request.llm_model,
            "chunk_size": request.chunk_size,
            "chunk_overlap": request.chunk_overlap,
            "split_method": request.split_method,
            "vector_db": request.vector_db
        }
        
        collection_name = f"rag_{uuid.uuid4().hex[:8]}"
        
        success, rag_id = create_rag(
            user_id=user_id,
            name=request.name,
            description=request.description,
            config=config,
            documents=[],
            collection_name=collection_name
        )
        
        if success:
            return RAGResponse(success=True, rag_id=rag_id, message="RAG créé avec succès")
        else:
            return RAGResponse(success=False, message=f"Erreur lors de la création: {rag_id}")
    except Exception as e:
        logger.error(f"Erreur lors de la création du RAG: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.put("/api/rags/{rag_id}", response_model=RAGResponse)
async def update_rag_details(rag_id: str, request: UpdateRAGRequest, user_id: str = Depends(get_current_user_from_token)):
    """Met à jour un RAG"""
    try:
        updates = {}
        if request.name is not None:
            updates["name"] = request.name
        if request.description is not None:
            updates["description"] = request.description
        
        if not updates:
            return RAGResponse(success=False, message="Aucune mise à jour fournie")
        
        success = update_rag(user_id, rag_id, updates)
        
        if success:
            return RAGResponse(success=True, rag_id=rag_id, message="RAG mis à jour avec succès")
        else:
            return RAGResponse(success=False, message="Erreur lors de la mise à jour")
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour du RAG: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.delete("/api/rags/{rag_id}")
async def delete_rag_endpoint(rag_id: str, user_id: str = Depends(get_current_user_from_token)):
    """Supprime un RAG"""
    try:
        success = delete_rag(user_id, rag_id)
        
        if success:
            return {"success": True, "message": "RAG supprimé avec succès"}
        else:
            return {"success": False, "message": "Erreur lors de la suppression"}
    except Exception as e:
        logger.error(f"Erreur lors de la suppression du RAG: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Routes pour les documents
@app.post("/api/rags/{rag_id}/documents/upload")
async def upload_documents(
    rag_id: str,
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_from_token)
):
    """Upload et traite des documents pour un RAG"""
    try:
        # Récupérer le RAG pour obtenir la configuration
        rag_data = get_rag(user_id, rag_id)
        if not rag_data:
            raise HTTPException(status_code=404, detail="RAG non trouvé")
        
        config = rag_data.get('config', {})
        
        all_documents = []
        
        for file in files:
            # Vérifier le type de fichier
            if not file.filename.lower().endswith(('.pdf', '.doc', '.docx')):
                continue
            
            # Sauvegarder le fichier temporairement
            with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = tmp_file.name
            
            try:
                # Traiter le document
                chunks, collection_name, vs = process_document(
                    file_path=tmp_path,
                    rag_id=rag_id,
                    split_method=config.get('split_method', 'recursive'),
                    chunk_size=config.get('chunk_size', 1000),
                    chunk_overlap=config.get('chunk_overlap', 200),
                    embedding_model=config.get('embedding_model', 'openai')
                )
                
                all_documents.extend(chunks)
                
            finally:
                # Nettoyer le fichier temporaire
                os.unlink(tmp_path)
        
        # Ajouter les documents au RAG
        for doc in all_documents:
            add_document_to_rag(user_id, rag_id, doc)
        
        return {
            "success": True,
            "message": f"{len(all_documents)} chunks ajoutés avec succès",
            "document_count": len(all_documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'upload des documents: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@app.post("/api/rags/{rag_id}/documents/urls")
async def add_urls_to_rag(
    rag_id: str,
    request: AddURLRequest,
    user_id: str = Depends(get_current_user_from_token)
):
    """Ajoute des URLs à un RAG"""
    try:
        # Récupérer le RAG pour obtenir la configuration
        rag_data = get_rag(user_id, rag_id)
        if not rag_data:
            raise HTTPException(status_code=404, detail="RAG non trouvé")
        
        config = rag_data.get('config', {})
        
        all_documents = []
        
        for url in request.urls:
            if not url.strip():
                continue
            
            try:
                # Traiter l'URL
                chunks, collection_name, vs = process_web_url(
                    url=url.strip(),
                    rag_id=rag_id,
                    split_method=config.get('split_method', 'recursive'),
                    chunk_size=config.get('chunk_size', 1000),
                    chunk_overlap=config.get('chunk_overlap', 200),
                    embedding_model=config.get('embedding_model', 'openai')
                )
                
                all_documents.extend(chunks)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de l'URL {url}: {e}")
                continue
        
        # Ajouter les documents au RAG
        for doc in all_documents:
            add_document_to_rag(user_id, rag_id, doc)
        
        return {
            "success": True,
            "message": f"{len(all_documents)} chunks ajoutés avec succès",
            "document_count": len(all_documents)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de l'ajout des URLs: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Routes de chat
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_rag(request: ChatRequest, user_id: str = Depends(get_current_user_from_token)):
    """Chat avec un RAG spécifique"""
    try:
        # Récupérer le RAG
        rag_data = get_rag(user_id, request.rag_id)
        if not rag_data:
            raise HTTPException(status_code=404, detail="RAG non trouvé")
        
        documents = rag_data.get('documents', [])
        config = rag_data.get('config', {})
        
        # Obtenir le flux de réponse de l'agent
        stream_data = stream_agent_workflow(
            query=request.message,
            display_reasoning=request.display_reasoning,
            rag_available=True,
            rag_id=request.rag_id,
            documents=documents,
            embedding_model=config.get('embedding_model', 'openai')
        )
        
        # Traiter le flux pour extraire la réponse finale
        final_response = ""
        reasoning = ""
        sources = []
        
        for event_type, data in stream_data:
            if event_type == "assistant":
                for assistant_data in data.get("assistant", []):
                    for message in assistant_data.get("messages", []):
                        if hasattr(message, 'content'):
                            final_response += message.content
            elif event_type == "reasoning" and request.display_reasoning:
                reasoning += str(data)
        
        # Extraire les sources
        try:
            sources = extract_rag_sources(documents, request.message)
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des sources: {e}")
            sources = []
        
        return ChatResponse(
            response=final_response or "Désolé, je n'ai pas pu générer une réponse.",
            sources=sources,
            reasoning=reasoning if request.display_reasoning else None
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors du chat: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Routes de statistiques
@app.get("/api/stats", response_model=UserStats)
async def get_user_stats(user_id: str = Depends(get_current_user_from_token)):
    """Récupère les statistiques de l'utilisateur"""
    try:
        rags_details = get_user_rags_details(user_id)
        total_rags = len(rags_details)
        total_documents = sum(
            len(get_documents_by_source(rag_data))
            for rag_data in rags_details.values()
        )
        
        return UserStats(
            total_rags=total_rags,
            total_documents=total_documents
        )
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Route de santé
@app.get("/api/health")
async def health_check():
    """Vérification de l'état de santé de l'API"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "mode": "DEV" if DEV_MODE else "PROD"
    }

# Route racine
@app.get("/")
async def root():
    """Route racine"""
    return {
        "message": f"Bienvenue sur l'API {APP_NAME}",
        "version": "1.0.0",
        "docs": "/docs"
    }

"""if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)"""

