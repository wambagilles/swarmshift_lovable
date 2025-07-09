"""
Module d'authentification pour l'application Streamlit RAG No-Code
Gère l'authentification des utilisateurs via Firebase en PROD et localement en DEV
"""
import json
from datetime import datetime
import os
import uuid
import pickle
from pathlib import Path

from src.config import FIREBASE_CONFIG, DEV_MODE
from src.user_store import check_user_exist, init_user_store, register_user
from src.user_store_session import check_user_logged, get_logged_user_id, terminate_session, update_session_value
import logging

logger = logging.getLogger(__name__)

# Import conditionnel pour Firebase en mode PROD
if not DEV_MODE:
    from src.firebase_auth import firebase_auth

# Chemin pour le stockage local des données en mode DEV
DEV_DATA_DIR = "dev_data"
DEV_USERS_FILE = os.path.join(DEV_DATA_DIR, "users.pkl")

def get_current_user_id():
    return get_logged_user_id()

def get_current_user():
    """Récupère les informations de l'utilisateur courant"""
    return get_logged_user_id()

# Initialisation des données de développement
def init_dev_data():
    """Initialise les données de développement si nécessaires"""
    if DEV_MODE:
        os.makedirs(DEV_DATA_DIR, exist_ok=True)
        if not os.path.exists(DEV_USERS_FILE):
            with open(DEV_USERS_FILE, 'wb') as f:
                pickle.dump({}, f)

# Fonctions d'authentification en mode DEV
def dev_login(email, password):
    """Simule une connexion en mode DEV (accepte n'importe quelles identifiants)"""
    # Vérifier si l'utilisateur existe, sinon le créer
    user_exist, uid = check_user_exist(email)
    if not user_exist:
        user_id = str(uuid.uuid4())
        user_data = {
            user_id: {
                "user_id": user_id,
                'email': email,
                'password': password,  # En DEV, on stocke en clair (ne jamais faire ça en PROD!)
                'created_at': datetime.now().isoformat()
            }
        }
        
        register_user(user_data)
        update_session_value({"user_id": user_data[user_id]})
        
    else:
        user_id = uid
        # Récupérer les données utilisateur
        user_store = init_user_store()
        user_data = user_store.get(user_id, {})
        update_session_value({"user_id": user_data})
    
    return True, "Connexion réussie (Mode DEV)"

def dev_signup(email, password, confirm_password):
    """Simule une inscription en mode DEV"""
    if password != confirm_password:
        return False, "Les mots de passe ne correspondent pas"
    
    user_exist, uid = check_user_exist(email)
    
    # Vérifier si l'email est déjà utilisé
    if user_exist:
        return False, "Cet email est déjà utilisé"
    
    # Créer un nouvel utilisateur
    user_id = str(uuid.uuid4())
    user_data = {
        user_id: {
            'user_id': user_id,
            'email': email,
            'password': password,  # En DEV, on stocke en clair (ne jamais faire ça en PROD!)
            'created_at': datetime.now().isoformat()
        }
    }
    register_user(user_data)
    update_session_value({"user_id": user_data[user_id]})
    
    return True, "Inscription réussie (Mode DEV)"

# Fonctions d'authentification communes (adaptées selon l'environnement)
def login(email, password):
    logger.info("User connected: email: {email}, password: {password}")
    """Connecte un utilisateur avec son email et mot de passe"""
    if DEV_MODE:
        return dev_login(email, password)
    else:
        return firebase_auth.sign_in(email, password)

def signup(email, password, confirm_password):
    """Inscrit un nouvel utilisateur"""
    if DEV_MODE:
        return dev_signup(email, password, confirm_password)
    else:
        if password != confirm_password:
            return False, "Les mots de passe ne correspondent pas"
        return firebase_auth.sign_up(email, password)

def logout():
    """Déconnecte l'utilisateur"""
    if terminate_session():
        return True, "Déconnexion réussie"
    return False, "Erreur lors de la déconnexion"

def is_authenticated():
    """Vérifie si l'utilisateur est authentifié"""
    return check_user_logged()

def get_current_user_id():
    """Récupère l'ID de l'utilisateur courant"""
    if is_authenticated():
        user_data = get_logged_user_id()
        if isinstance(user_data, dict):
            return user_data.get('user_id')
        return user_data
    return None

def get_current_user():
    """Récupère les informations complètes de l'utilisateur courant"""
    if is_authenticated():
        return get_logged_user_id()
    return None

# Initialisation des données de développement
init_dev_data()
