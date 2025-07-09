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

from src.config import DEV_MODE
import logging

logging.basicConfig(level=logging.INFO)

# Chemin pour le stockage des données utilisateur
USER_DATA_DIR = "dev_data/users"
USER_STORE_FILE = os.path.join(USER_DATA_DIR, "user_store.json")

# Structure du dictionnaire utilisateur
# {
#     "user_id": {
#         "vector_store_id": "unique_id",
#         "user_email": "user_email",
#         "collections": {
#             "rag_id_1": "collection_name_1",
#             "rag_id_2": "collection_name_2",
#             ...
#         }
#        rags : {
#                rag_id:
#                       {'name': name,
#                       'description': description,
#                       'config': config,
#                       'created_at': datetime.now().isoformat(),
#                       'updated_at': datetime.now().isoformat(),
#                       'documents': documents or [],
#                       'conversations': [],
#                       'collection_name': collection_name 
#             }
#            }
#     },
#     ...
# }

def check_user_exist(user_email):
    user_store = init_user_store()
    for uid, userdata in user_store.items():
        if user_email in userdata.values():
            return True, uid
    return False, None


def init_user_store():
    """Initialise le stockage utilisateur s'il n'existe pas"""
    os.makedirs(USER_DATA_DIR, exist_ok=True)
    
    if not os.path.exists(USER_STORE_FILE):
        # Créer un dictionnaire utilisateur vide
        user_store = {}
        
        # Sauvegarder le dictionnaire
        with open(USER_STORE_FILE, "w") as json_file:
            json.dump(user_store, json_file, indent=4)

        
        return user_store
    
    # Charger le dictionnaire existant
    try:
        with open(USER_STORE_FILE, 'r') as file:
            user_store = json.load(file)
            return user_store
    except Exception as e:
        print(f"Erreur lors du chargement du dictionnaire utilisateur: {str(e)}")
        # En cas d'erreur, créer un nouveau dictionnaire
        user_store = {}
        with open(USER_STORE_FILE, "w") as json_file:
            json.dump(user_store, json_file, indent=4)
        return user_store

def save_user_store(user_store: Dict[str, Any]):
    #TODO this will push to database
    """Sauvegarde le dictionnaire utilisateur
    Args:
        user_store: user_store to store
        
    """
    try:
        with open(USER_STORE_FILE, "w") as json_file:
            json.dump(user_store, json_file, indent=4)
        
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du dictionnaire utilisateur: {str(e)}")
        return False

def associate_user_to_rag(user_id: str, rag_id: str, rag_data: Dict):
    """
    Associe un RAG à un utilisateur et initialise la structure nécessaire
    
    Args:
        user_id: ID de l'utilisateur
        rag_id: ID du RAG
        rag_data: Données du RAG
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe dans le dictionnaire
    if user_id not in user_store:
        user_store[user_id] = {
            "vector_store_id": str(uuid.uuid4()),
            "collections": {},
            "rags": {}
        }
    
    # S'assurer que la structure rags existe
    if "rags" not in user_store[user_id]:
        user_store[user_id]["rags"] = {}
    
    # S'assurer que la structure collections existe
    if "collections" not in user_store[user_id]:
        user_store[user_id]["collections"] = {}
    
    # Ajouter le RAG à la structure rags
    rag_data_copy = rag_data.copy()
    if 'documents' in rag_data_copy:
        rag_data_copy['documents'] = len(rag_data_copy['documents'])
    
    user_store[user_id]["rags"][rag_id] = rag_data_copy
    
    # Ajouter le nom de la collection à la structure collections
    if 'collection_name' in rag_data:
        user_store[user_id]["collections"][rag_id] = rag_data['collection_name']
    
    # Sauvegarder le dictionnaire
    save_user_store(user_store)
    
    print(f"RAG {rag_id} associé à l'utilisateur {user_id}")

def remove_rag_from_user_store(user_id: str, rag_id: str) -> bool:
    """
    Supprime un RAG de la structure utilisateur
    
    Args:
        user_id: ID de l'utilisateur
        rag_id: ID du RAG à supprimer
        
    Returns:
        True si la suppression a réussi, False sinon
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        print(f"Utilisateur {user_id} non trouvé")
        return False
    
    # Supprimer le RAG de la structure rags
    if "rags" in user_store[user_id] and rag_id in user_store[user_id]["rags"]:
        del user_store[user_id]["rags"][rag_id]
        print(f"RAG {rag_id} supprimé de la structure rags")
    
    # Supprimer le RAG de la structure collections
    if "collections" in user_store[user_id] and rag_id in user_store[user_id]["collections"]:
        del user_store[user_id]["collections"][rag_id]
        print(f"RAG {rag_id} supprimé de la structure collections")
    
    # Sauvegarder le dictionnaire
    save_user_store(user_store)
    
    return True

def update_rag_documents_count(user_id: str, rag_id: str, doc_count: int):
    """
    Met à jour le nombre de documents d'un RAG
    
    Args:
        user_id: ID de l'utilisateur
        rag_id: ID du RAG
        doc_count: Nombre de documents
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        print(f"Utilisateur {user_id} non trouvé")
        return False
    
    # S'assurer que la structure rags existe
    if "rags" not in user_store[user_id]:
        user_store[user_id]["rags"] = {}
    
    # S'assurer que le RAG existe
    if rag_id not in user_store[user_id]["rags"]:
        print(f"RAG {rag_id} non trouvé pour l'utilisateur {user_id}")
        return False
    
    # Mettre à jour le nombre de documents
    user_store[user_id]["rags"][rag_id]["documents"] = doc_count
    
    # Sauvegarder le dictionnaire
    save_user_store(user_store)
    return True

def get_rags_details(user_id):
    """
    Récupère les détails des RAGs d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Dictionnaire des RAGs de l'utilisateur
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        print(f"Utilisateur {user_id} non trouvé")
        return {}
    
    # S'assurer que la structure rags existe
    if "rags" not in user_store[user_id]:
        return {}
    
    return user_store[user_id].get("rags", {})

def get_rags_list(user_id: str):
    """
    Récupère la liste des IDs des RAGs d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Liste des IDs des RAGs
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        print(f"Utilisateur {user_id} non trouvé")
        return []
    
    # S'assurer que la structure collections existe
    if "collections" not in user_store[user_id]:
        return []
    
    return list(user_store[user_id].get("collections", {}).keys())

def get_vector_store_id(user_id: str):
    """
    Récupère l'ID du vector store d'un utilisateur
    
    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        ID du vector store ou None si l'utilisateur n'existe pas
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        print(f"Utilisateur {user_id} non trouvé")
        return None
    
    return user_store[user_id].get("vector_store_id")

def get_collection_name(user_id: str, rag_id: str) -> str:
    """
    Récupère le nom de la collection associée à un RAG
    
    Args:
        user_id: ID de l'utilisateur
        rag_id: ID du RAG
        
    Returns:
        Nom de la collection ou None si le RAG n'existe pas
    """
    user_store = init_user_store()
    
    # Vérifications en cascade avec gestion des None
    if user_id not in user_store:
        logging.error(f"Utilisateur {user_id} non trouvé")
        return None
    
    user_data = user_store.get(user_id, {})
    
    # Vérifier d'abord dans la structure rags
    if "rags" in user_data and rag_id in user_data.get("rags", {}):
        rag_data = user_data["rags"].get(rag_id, {})
        if "name" in rag_data:
            return rag_data.get("name")
    
    # Si non trouvé, vérifier dans la structure collections
    if "collections" in user_data and rag_id in user_data.get("collections", {}):
        return user_data["collections"].get(rag_id)
    
    logging.error(f"Collection pour RAG {rag_id} non trouvée pour l'utilisateur {user_id}")
    return None

def register_collection(user_id: str, rag_id: str, collection_name: str) -> str:
    """
    Enregistre une collection pour un RAG
    
    Args:
        user_id: ID de l'utilisateur
        rag_id: ID du RAG
        collection_name: Nom de la collection
        
    Returns:
        Nom de la collection enregistrée
    """
    user_store = init_user_store()
    
    # S'assurer que l'utilisateur existe
    if user_id not in user_store:
        user_store[user_id] = {
            "vector_store_id": str(uuid.uuid4()),
            "collections": {},
            "rags": {}
        }
    
    # S'assurer que la structure collections existe
    if "collections" not in user_store[user_id]:
        user_store[user_id]["collections"] = {}
    
    # Enregistrer la collection
    user_store[user_id]["collections"][rag_id] = collection_name
    
    # Sauvegarder le dictionnaire
    save_user_store(user_store)
    
    return collection_name

def get_user_vector_store_path(user_id: str) -> str:
    """
    Retourne le chemin de la base de données vectorielle d'un utilisateur

    Args:
        user_id: ID de l'utilisateur
    
    Returns:
        Chemin absolu vers la base de données vectorielle de l'utilisateur
    """
    # Récupérer l'ID du vector store
    vector_store_id = get_vector_store_id(user_id)
    
    if not vector_store_id:
        # Si l'utilisateur n'a pas encore de vector store, en créer un
        user_store = init_user_store()
        if user_id not in user_store:
            user_store[user_id] = {
                "vector_store_id": str(uuid.uuid4()),
                "collections": {},
                "rags": {}
            }
            save_user_store(user_store)
            vector_store_id = user_store[user_id]["vector_store_id"]
        else:
            user_store[user_id]["vector_store_id"] = str(uuid.uuid4())
            save_user_store(user_store)
            vector_store_id = user_store[user_id]["vector_store_id"]
    
    # Créer un chemin unique pour chaque utilisateur
    user_db_path = os.path.abspath(f"./chroma_db/{user_id}_{vector_store_id}")
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(user_db_path, exist_ok=True)
    
    return user_db_path

def register_user(user_data: Dict[str, Any]) -> dict:
    """
    Enregistre un nouvel utilisateur
    
    Args:
        user_data: Données de l'utilisateur
        
    Returns:
        Dictionnaire utilisateur mis à jour
    """
    # Charger le dictionnaire utilisateur
    user_store = init_user_store()
    
    # Enregistrer l'utilisateur
    user_store.update(user_data)
    
    # Sauvegarder le dictionnaire
    save_user_store(user_store)
    
    return user_store
