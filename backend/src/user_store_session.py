"""
Module de gestion du stockage utilisateur pour l'application Streamlit RAG No-Code
Gère la persistance des associations entre utilisateurs, vector stores et collections RAG
"""
import os
import json
import csv
import pickle
from typing import Dict, List, Any, Optional, Tuple
import uuid
import logging
from src.config import DEV_MODE


logger = logging.getLogger(__name__)



# Chemin pour le stockage des données utilisateur
USER_DATA_DIR = "dev_data/users"
USER_SESSION_FILE = os.path.join(USER_DATA_DIR, "user_session.json")
os.makedirs(USER_DATA_DIR, exist_ok=True)


def init_session():
    """if 'session_id' not in st.session_state:
       session_id = str(uuid.uuid4())
       st.session_state.session_id = session_id"""
    # Chemin pour le stockage des données utilisateur
    #global USER_SESSION_FILE 
    #USER_SESSION_FILE = os.path.join(USER_DATA_DIR, f"{ st.session_state['session_id']}_user_session.json")


    """Initialise la session"""
    
    
    if not os.path.exists(USER_SESSION_FILE):
        # Créer un dictionnaire utilisateur vide
        user_session = {}
        
        # Sauvegarder le dictionnaire
        with open(USER_SESSION_FILE, "w") as json_file:
            json.dump(user_session, json_file, indent=4)

        return user_session
    
    # Charger le dictionnaire existant
    try:
        with open(USER_SESSION_FILE, 'r') as file:
            user_session = json.load(file)
            return user_session
        print("loaded session")
    except Exception as e:
        logger.error(f"Erreur lors du chargement la session utilisateur: {str(e)}")
       

def save_session(user_session: Dict[str, Any]):
    #TODO this will push to database
    """Sauvegarde le dictionnaire de la session
    Args:
        user_session: session to store
        
    """
    try:
        with open(USER_SESSION_FILE, "w") as json_file:
            json.dump(user_session, json_file, indent=4)
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la session utilisateur: {str(e)}")
        return False




def get_session_value(key: str):
    """Récupère un valeur dans les données de session
    Args:
        key: key of the value to retrieve
    """
    return init_session().get(key)

def update_session_value( value: Dict[str, Any]):
    """Récupère un valeur dans les données de session
    Args:
        key: key of the value to put
        value: value to put in session
    """
    session =  init_session()
    session.update(value)
    save_session(session)



def terminate_session():
    if os.path.exists(USER_SESSION_FILE):
        os.remove(USER_SESSION_FILE)
    return True
    

def check_user_logged():
    if "user_id" in init_session():
        return True
    return False

def get_logged_user_id():
    return init_session().get("user_id", None).get("user_id", None)

def get_current_user():
    return  init_session()["user_id"]



