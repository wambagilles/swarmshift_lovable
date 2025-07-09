"""
Client API pour les interactions avec le frontend
Remplace les appels directs aux fonctions Streamlit
"""
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class APIClient:
    """Client pour interagir avec l'API FastAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
    
    def set_token(self, token: str):
        """Définit le token d'authentification"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})
    
    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """Connexion utilisateur"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_id = data.get("user_id")
                    # En mode DEV, on peut utiliser l'user_id comme token
                    self.set_token(user_id or "dev_token")
                    return True, data.get("message", "Connexion réussie"), user_id
                else:
                    return False, data.get("message", "Erreur de connexion"), None
            else:
                return False, f"Erreur HTTP {response.status_code}", None
                
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            return False, f"Erreur de connexion: {str(e)}", None
    
    def signup(self, email: str, password: str, confirm_password: str) -> Tuple[bool, str, Optional[str]]:
        """Inscription utilisateur"""
        try:
            response = self.session.post(
                f"{self.base_url}/auth/signup",
                json={
                    "email": email,
                    "password": password,
                    "confirm_password": confirm_password
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    user_id = data.get("user_id")
                    self.set_token(user_id or "dev_token")
                    return True, data.get("message", "Inscription réussie"), user_id
                else:
                    return False, data.get("message", "Erreur d'inscription"), None
            else:
                return False, f"Erreur HTTP {response.status_code}", None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'inscription: {e}")
            return False, f"Erreur d'inscription: {str(e)}", None
    
    def logout(self) -> Tuple[bool, str]:
        """Déconnexion utilisateur"""
        try:
            response = self.session.post(f"{self.base_url}/auth/logout")
            
            if response.status_code == 200:
                data = response.json()
                self.token = None
                self.session.headers.pop("Authorization", None)
                return data.get("success", True), data.get("message", "Déconnexion réussie")
            else:
                return False, f"Erreur HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            return False, f"Erreur de déconnexion: {str(e)}"
    
    def get_user_rags(self) -> List[Dict[str, Any]]:
        """Récupère la liste des RAGs de l'utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/rags")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération des RAGs: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des RAGs: {e}")
            return []
    
    def get_rag_detail(self, rag_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les détails d'un RAG"""
        try:
            response = self.session.get(f"{self.base_url}/rags/{rag_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération du RAG: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du RAG: {e}")
            return None
    
    def create_rag(self, name: str, description: str = "", **config) -> Tuple[bool, str]:
        """Crée un nouveau RAG"""
        try:
            data = {
                "name": name,
                "description": description,
                **config
            }
            
            response = self.session.post(f"{self.base_url}/rags", json=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, result.get("rag_id", "")
                else:
                    return False, result.get("message", "Erreur lors de la création")
            else:
                return False, f"Erreur HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erreur lors de la création du RAG: {e}")
            return False, f"Erreur de création: {str(e)}"
    
    def update_rag(self, rag_id: str, **updates) -> bool:
        """Met à jour un RAG"""
        try:
            response = self.session.put(f"{self.base_url}/rags/{rag_id}", json=updates)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            else:
                logger.error(f"Erreur lors de la mise à jour du RAG: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du RAG: {e}")
            return False
    
    def delete_rag(self, rag_id: str) -> bool:
        """Supprime un RAG"""
        try:
            response = self.session.delete(f"{self.base_url}/rags/{rag_id}")
            
            if response.status_code == 200:
                result = response.json()
                return result.get("success", False)
            else:
                logger.error(f"Erreur lors de la suppression du RAG: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du RAG: {e}")
            return False
    
    def upload_documents(self, rag_id: str, files: List[str]) -> Tuple[bool, str]:
        """Upload des documents vers un RAG"""
        try:
            files_data = []
            for file_path in files:
                with open(file_path, 'rb') as f:
                    files_data.append(('files', (file_path, f, 'application/octet-stream')))
            
            response = self.session.post(
                f"{self.base_url}/rags/{rag_id}/documents/upload",
                files=files_data
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, result.get("message", "Documents uploadés avec succès")
                else:
                    return False, result.get("message", "Erreur lors de l'upload")
            else:
                return False, f"Erreur HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erreur lors de l'upload des documents: {e}")
            return False, f"Erreur d'upload: {str(e)}"
    
    def add_urls(self, rag_id: str, urls: List[str]) -> Tuple[bool, str]:
        """Ajoute des URLs à un RAG"""
        try:
            response = self.session.post(
                f"{self.base_url}/rags/{rag_id}/documents/urls",
                json={"urls": urls}
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return True, result.get("message", "URLs ajoutées avec succès")
                else:
                    return False, result.get("message", "Erreur lors de l'ajout des URLs")
            else:
                return False, f"Erreur HTTP {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des URLs: {e}")
            return False, f"Erreur d'ajout: {str(e)}"
    
    def chat(self, rag_id: str, message: str, display_reasoning: bool = False) -> Dict[str, Any]:
        """Chat avec un RAG"""
        try:
            response = self.session.post(
                f"{self.base_url}/chat",
                json={
                    "rag_id": rag_id,
                    "message": message,
                    "display_reasoning": display_reasoning
                }
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors du chat: {response.status_code}")
                return {
                    "response": "Erreur lors de la génération de la réponse",
                    "sources": [],
                    "reasoning": None
                }
                
        except Exception as e:
            logger.error(f"Erreur lors du chat: {e}")
            return {
                "response": f"Erreur de communication: {str(e)}",
                "sources": [],
                "reasoning": None
            }
    
    def get_user_stats(self) -> Dict[str, int]:
        """Récupère les statistiques de l'utilisateur"""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Erreur lors de la récupération des stats: {response.status_code}")
                return {"total_rags": 0, "total_documents": 0}
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des stats: {e}")
            return {"total_rags": 0, "total_documents": 0}

# Instance globale du client API
api_client = APIClient()

