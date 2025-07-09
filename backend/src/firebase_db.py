"""
Module de gestion de la base de données Firebase pour l'application RAG No-Code
Gère la persistance des données utilisateur et des RAGs en mode production
"""
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import uuid

from src.config import DEV_MODE
from src.user_store import (
    init_user_store, save_user_store, associate_user_to_rag, 
    remove_rag_from_user_store, get_rags_details, get_rags_list,
    get_collection_name, register_collection, get_user_vector_store_path
)

# Import conditionnel pour Firebase en mode PROD
if not DEV_MODE:
    from src.firebase_auth import firebase_auth

def dev_get_user_rags_details(user_id: str) -> Dict[str, Any]:
    """Récupère les détails des RAGs d'un utilisateur en mode DEV"""
    return get_rags_details(user_id)

def dev_create_rag(user_id: str, name: str, description: str, config: Dict[str, Any], 
                   documents: List[Any] = None, collection_name: str = None) -> Tuple[bool, str]:
    """Crée un nouveau RAG en mode DEV"""
    try:
        rag_id = str(uuid.uuid4())
        
        rag_data = {
            'name': name,
            'description': description,
            'config': config,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'documents': documents or [],
            'conversations': [],
            'collection_name': collection_name or f"rag_{rag_id}"
        }
        
        associate_user_to_rag(user_id, rag_id, rag_data)
        return True, rag_id
        
    except Exception as e:
        print(f"Erreur lors de la création du RAG: {e}")
        return False, str(e)

def dev_get_rag(user_id: str, rag_id: str) -> Optional[Dict[str, Any]]:
    """Récupère un RAG spécifique en mode DEV"""
    rags = get_rags_details(user_id)
    return rags.get(rag_id)

def dev_get_user_rags_ids(user_id: str) -> List[str]:
    """Récupère la liste des IDs des RAGs d'un utilisateur en mode DEV"""
    return get_rags_list(user_id)

def dev_update_rag(user_id: str, rag_id: str, updates: Dict[str, Any]) -> bool:
    """Met à jour un RAG en mode DEV"""
    try:
        user_store = init_user_store()
        
        if user_id not in user_store or "rags" not in user_store[user_id]:
            return False
        
        if rag_id not in user_store[user_id]["rags"]:
            return False
        
        # Mettre à jour les champs
        user_store[user_id]["rags"][rag_id].update(updates)
        user_store[user_id]["rags"][rag_id]["updated_at"] = datetime.now().isoformat()
        
        save_user_store(user_store)
        return True
        
    except Exception as e:
        print(f"Erreur lors de la mise à jour du RAG: {e}")
        return False

def dev_delete_rag(user_id: str, rag_id: str) -> bool:
    """Supprime un RAG en mode DEV"""
    try:
        return remove_rag_from_user_store(user_id, rag_id)
    except Exception as e:
        print(f"Erreur lors de la suppression du RAG: {e}")
        return False

def dev_add_document_to_rag(user_id: str, rag_id: str, document_info: Dict[str, Any]) -> bool:
    """Ajoute un document à un RAG en mode DEV"""
    try:
        user_store = init_user_store()
        
        if user_id not in user_store or "rags" not in user_store[user_id]:
            return False
        
        if rag_id not in user_store[user_id]["rags"]:
            return False
        
        # Ajouter le document
        if "documents" not in user_store[user_id]["rags"][rag_id]:
            user_store[user_id]["rags"][rag_id]["documents"] = []
        
        user_store[user_id]["rags"][rag_id]["documents"].append(document_info)
        user_store[user_id]["rags"][rag_id]["updated_at"] = datetime.now().isoformat()
        
        save_user_store(user_store)
        return True
        
    except Exception as e:
        print(f"Erreur lors de l'ajout du document: {e}")
        return False

# Fonctions Firebase pour le mode PROD
if not DEV_MODE:
    def prod_get_user_rags_details(user_id: str) -> Dict[str, Any]:
        """Récupère les détails des RAGs d'un utilisateur depuis Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if user_data:
                return user_data.get('rags', {})
            return {}
        except Exception as e:
            print(f"Erreur lors de la récupération des RAGs: {e}")
            return {}

    def prod_create_rag(user_id: str, name: str, description: str, config: Dict[str, Any], 
                       documents: List[Any] = None, collection_name: str = None) -> Tuple[bool, str]:
        """Crée un nouveau RAG dans Firestore"""
        try:
            rag_id = str(uuid.uuid4())
            
            rag_data = {
                'name': name,
                'description': description,
                'config': config,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'documents': documents or [],
                'conversations': [],
                'collection_name': collection_name or f"rag_{rag_id}"
            }
            
            # Récupérer les données utilisateur actuelles
            user_data = firebase_auth.get_user_data(user_id)
            if not user_data:
                user_data = {'rags': {}}
            
            # Ajouter le nouveau RAG
            if 'rags' not in user_data:
                user_data['rags'] = {}
            
            user_data['rags'][rag_id] = rag_data
            
            # Mettre à jour dans Firestore
            success = firebase_auth.update_user_data(user_id, {'rags': user_data['rags']})
            
            if success:
                return True, rag_id
            else:
                return False, "Erreur lors de la sauvegarde"
                
        except Exception as e:
            print(f"Erreur lors de la création du RAG: {e}")
            return False, str(e)

    def prod_get_rag(user_id: str, rag_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un RAG spécifique depuis Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if user_data and 'rags' in user_data:
                return user_data['rags'].get(rag_id)
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération du RAG: {e}")
            return None

    def prod_get_user_rags_ids(user_id: str) -> List[str]:
        """Récupère la liste des IDs des RAGs d'un utilisateur depuis Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if user_data and 'rags' in user_data:
                return list(user_data['rags'].keys())
            return []
        except Exception as e:
            print(f"Erreur lors de la récupération des IDs des RAGs: {e}")
            return []

    def prod_update_rag(user_id: str, rag_id: str, updates: Dict[str, Any]) -> bool:
        """Met à jour un RAG dans Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if not user_data or 'rags' not in user_data or rag_id not in user_data['rags']:
                return False
            
            # Mettre à jour les champs
            user_data['rags'][rag_id].update(updates)
            user_data['rags'][rag_id]['updated_at'] = datetime.now().isoformat()
            
            # Sauvegarder dans Firestore
            return firebase_auth.update_user_data(user_id, {'rags': user_data['rags']})
            
        except Exception as e:
            print(f"Erreur lors de la mise à jour du RAG: {e}")
            return False

    def prod_delete_rag(user_id: str, rag_id: str) -> bool:
        """Supprime un RAG de Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if not user_data or 'rags' not in user_data or rag_id not in user_data['rags']:
                return False
            
            # Supprimer le RAG
            del user_data['rags'][rag_id]
            
            # Sauvegarder dans Firestore
            return firebase_auth.update_user_data(user_id, {'rags': user_data['rags']})
            
        except Exception as e:
            print(f"Erreur lors de la suppression du RAG: {e}")
            return False

    def prod_add_document_to_rag(user_id: str, rag_id: str, document_info: Dict[str, Any]) -> bool:
        """Ajoute un document à un RAG dans Firestore"""
        try:
            user_data = firebase_auth.get_user_data(user_id)
            if not user_data or 'rags' not in user_data or rag_id not in user_data['rags']:
                return False
            
            # Ajouter le document
            if 'documents' not in user_data['rags'][rag_id]:
                user_data['rags'][rag_id]['documents'] = []
            
            user_data['rags'][rag_id]['documents'].append(document_info)
            user_data['rags'][rag_id]['updated_at'] = datetime.now().isoformat()
            
            # Sauvegarder dans Firestore
            return firebase_auth.update_user_data(user_id, {'rags': user_data['rags']})
            
        except Exception as e:
            print(f"Erreur lors de l'ajout du document: {e}")
            return False

# Fonctions communes qui s'adaptent selon l'environnement
def get_user_rags_details(user_id: str) -> Dict[str, Any]:
    """Récupère les détails des RAGs d'un utilisateur"""
    if DEV_MODE:
        return dev_get_user_rags_details(user_id)
    else:
        return prod_get_user_rags_details(user_id)

def create_rag(user_id: str, name: str, description: str, config: Dict[str, Any], 
               documents: List[Any] = None, collection_name: str = None) -> Tuple[bool, str]:
    """Crée un nouveau RAG"""
    if DEV_MODE:
        return dev_create_rag(user_id, name, description, config, documents, collection_name)
    else:
        return prod_create_rag(user_id, name, description, config, documents, collection_name)

def get_rag(user_id: str, rag_id: str) -> Optional[Dict[str, Any]]:
    """Récupère un RAG spécifique"""
    if DEV_MODE:
        return dev_get_rag(user_id, rag_id)
    else:
        return prod_get_rag(user_id, rag_id)

def get_user_rags_ids(user_id: str) -> List[str]:
    """Récupère la liste des IDs des RAGs d'un utilisateur"""
    if DEV_MODE:
        return dev_get_user_rags_ids(user_id)
    else:
        return prod_get_user_rags_ids(user_id)

def update_rag(user_id: str, rag_id: str, updates: Dict[str, Any]) -> bool:
    """Met à jour un RAG"""
    if DEV_MODE:
        return dev_update_rag(user_id, rag_id, updates)
    else:
        return prod_update_rag(user_id, rag_id, updates)

def delete_rag(user_id: str, rag_id: str) -> bool:
    """Supprime un RAG"""
    if DEV_MODE:
        return dev_delete_rag(user_id, rag_id)
    else:
        return prod_delete_rag(user_id, rag_id)

def add_document_to_rag(user_id: str, rag_id: str, document_info: Dict[str, Any]) -> bool:
    """Ajoute un document à un RAG"""
    if DEV_MODE:
        return dev_add_document_to_rag(user_id, rag_id, document_info)
    else:
        return prod_add_document_to_rag(user_id, rag_id, document_info)

# Alias pour la compatibilité avec l'ancien code
#dev_get_user_rags_details = get_user_rags_details

