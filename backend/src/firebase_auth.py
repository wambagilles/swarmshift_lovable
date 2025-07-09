"""
Module d'authentification Firebase pour l'application Streamlit RAG No-Code
Gère l'authentification des utilisateurs via Firebase Auth en mode production
"""
import json
import os
import streamlit as st
from datetime import datetime
import firebase_admin
from firebase_admin import auth, credentials, firestore
import requests
from typing import Tuple, Optional, Dict, Any

from src.config import FIREBASE_CONFIG, DEV_MODE
from src.user_store_session import update_session_value

class FirebaseAuth:
    """Classe pour gérer l'authentification Firebase"""
    
    def __init__(self):
        self.db = None
        self.firebase_config = FIREBASE_CONFIG
        self._init_firebase_admin()
    
    def _init_firebase_admin(self):
        """Initialise Firebase Admin SDK"""
        if not firebase_admin._apps:
            try:
                # Essayer de charger depuis un fichier de credentials
                if os.path.exists('firebase-credentials.json'):
                    cred = credentials.Certificate('firebase-credentials.json')
                else:
                    # Créer les credentials depuis les variables d'environnement
                    cred_dict = {
                        "type": "service_account",
                        "project_id": self.firebase_config["projectId"],
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                    }
                    
                    # Vérifier que les credentials essentiels sont présents
                    if not all([cred_dict["project_id"], cred_dict["private_key"], cred_dict["client_email"]]):
                        raise ValueError("Credentials Firebase manquants dans les variables d'environnement")
                    
                    cred = credentials.Certificate(cred_dict)
                
                firebase_admin.initialize_app(cred)
                self.db = firestore.client()
                print("Firebase Admin SDK initialisé avec succès")
                
            except Exception as e:
                print(f"Erreur lors de l'initialisation de Firebase Admin SDK: {e}")
                self.db = None
    
    def _make_auth_request(self, endpoint: str, data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Effectue une requête vers l'API Firebase Auth REST"""
        try:
            url = f"https://identitytoolkit.googleapis.com/v1/accounts:{endpoint}?key={self.firebase_config['apiKey']}"
            response = requests.post(url, json=data)
            response_data = response.json()
            
            if response.status_code == 200:
                return True, response_data
            else:
                error_message = response_data.get('error', {}).get('message', 'Erreur inconnue')
                return False, {'error': error_message}
                
        except Exception as e:
            return False, {'error': f'Erreur de connexion: {str(e)}'}
    
    def sign_up(self, email: str, password: str) -> Tuple[bool, str]:
        """Inscrit un nouvel utilisateur avec Firebase Auth"""
        try:
            # Validation basique
            if len(password) < 6:
                return False, "Le mot de passe doit contenir au moins 6 caractères"
            
            # Créer l'utilisateur via l'API REST Firebase
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            success, response = self._make_auth_request("signUp", data)
            
            if success:
                user_id = response.get('localId')
                id_token = response.get('idToken')
                
                # Créer le profil utilisateur dans Firestore
                if self.db:
                    try:
                        self.db.collection('users').document(user_id).set({
                            'email': email,
                            'created_at': datetime.now().isoformat(),
                            'rags': {},
                            'vector_store_id': user_id  # Utiliser l'ID utilisateur comme ID du vector store
                        })
                    except Exception as e:
                        print(f"Erreur lors de la création du profil utilisateur: {e}")
                
                # Stocker les informations dans la session
                user_data = {
                    'user_id': user_id,
                    'email': email,
                    'id_token': id_token,
                    'last_login': datetime.now().isoformat()
                }
                update_session_value({"user_id": user_data})
                
                return True, "Inscription réussie"
            else:
                error_msg = response.get('error', 'Erreur inconnue')
                if 'EMAIL_EXISTS' in error_msg:
                    return False, "Cet email est déjà utilisé"
                elif 'INVALID_EMAIL' in error_msg:
                    return False, "Format d'email invalide"
                else:
                    return False, f"Erreur d'inscription: {error_msg}"
                    
        except Exception as e:
            return False, f"Erreur lors de l'inscription: {str(e)}"
    
    def sign_in(self, email: str, password: str) -> Tuple[bool, str]:
        """Connecte un utilisateur avec Firebase Auth"""
        try:
            # Connexion via l'API REST Firebase
            data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            success, response = self._make_auth_request("signInWithPassword", data)
            
            if success:
                user_id = response.get('localId')
                id_token = response.get('idToken')
                
                # Vérifier/créer le profil utilisateur dans Firestore
                if self.db:
                    try:
                        user_doc = self.db.collection('users').document(user_id).get()
                        if not user_doc.exists:
                            # Créer le profil s'il n'existe pas
                            self.db.collection('users').document(user_id).set({
                                'email': email,
                                'created_at': datetime.now().isoformat(),
                                'rags': {},
                                'vector_store_id': user_id
                            })
                    except Exception as e:
                        print(f"Erreur lors de la vérification du profil utilisateur: {e}")
                
                # Stocker les informations dans la session
                user_data = {
                    'user_id': user_id,
                    'email': email,
                    'id_token': id_token,
                    'last_login': datetime.now().isoformat()
                }
                update_session_value({"user_id": user_data})
                
                return True, "Connexion réussie"
            else:
                error_msg = response.get('error', 'Erreur inconnue')
                if 'INVALID_LOGIN_CREDENTIALS' in error_msg or 'INVALID_PASSWORD' in error_msg:
                    return False, "Email ou mot de passe incorrect"
                elif 'INVALID_EMAIL' in error_msg:
                    return False, "Format d'email invalide"
                elif 'USER_DISABLED' in error_msg:
                    return False, "Ce compte a été désactivé"
                else:
                    return False, f"Erreur de connexion: {error_msg}"
                    
        except Exception as e:
            return False, f"Erreur lors de la connexion: {str(e)}"
    
    def verify_token(self, id_token: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Vérifie un token Firebase et retourne les informations utilisateur"""
        try:
            if not self.db:
                return False, None
                
            decoded_token = auth.verify_id_token(id_token)
            user_id = decoded_token.get('uid')
            
            # Récupérer les informations utilisateur depuis Firestore
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                user_data['user_id'] = user_id
                return True, user_data
            else:
                return False, None
                
        except Exception as e:
            print(f"Erreur lors de la vérification du token: {e}")
            return False, None
    
    def get_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Récupère les données utilisateur depuis Firestore"""
        try:
            if not self.db:
                return None
                
            user_doc = self.db.collection('users').document(user_id).get()
            if user_doc.exists:
                return user_doc.to_dict()
            else:
                return None
                
        except Exception as e:
            print(f"Erreur lors de la récupération des données utilisateur: {e}")
            return None
    
    def update_user_data(self, user_id: str, data: Dict[str, Any]) -> bool:
        """Met à jour les données utilisateur dans Firestore"""
        try:
            if not self.db:
                return False
                
            self.db.collection('users').document(user_id).update(data)
            return True
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour des données utilisateur: {e}")
            return False
    
    def delete_user(self, user_id: str) -> Tuple[bool, str]:
        """Supprime un utilisateur"""
        try:
            # Supprimer l'utilisateur de Firebase Auth
            auth.delete_user(user_id)
            
            # Supprimer les données utilisateur de Firestore
            if self.db:
                self.db.collection('users').document(user_id).delete()
            
            return True, "Utilisateur supprimé avec succès"
            
        except Exception as e:
            return False, f"Erreur lors de la suppression: {str(e)}"

# Instance globale
firebase_auth = FirebaseAuth()

