"""
Module de gestion de Chroma DB pour le déploiement en production
Gère la connexion à Chroma DB local ou distant (GCP)
"""
import os
import chromadb
from chromadb.config import Settings
from typing import Optional

import logging

logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)


from src.config import DEV_MODE, CHROMA_CONFIG, GCP_CONFIG

class ChromaDBManager:
    """Gestionnaire pour Chroma DB en mode production"""
    
    def __init__(self):
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialise le client Chroma DB selon l'environnement"""
        try:
            if DEV_MODE:
                # Mode développement - Chroma DB distant via Docker Compose
                self.client = chromadb.HttpClient(
                host=os.getenv("CHROMA_SERVER_HOST", "chroma-db"),
                port=os.getenv("CHROMA_SERVER_PORT", "8000" ),
                settings=Settings(allow_reset=True, anonymized_telemetry=False)
            )   


                logger.info(f"Chroma DB initialisé en mode développement (Docker Compose): {os.getenv('CHROMA_SERVER_HOST', 'chroma-db')}:{os.getenv('CHROMA_SERVER_PORT', 8000)}")

            else:
                # Mode production - Chroma DB distant ou local selon la configuration
                # Chroma DB distant (GCP ou autre)
                self.client = chromadb.HttpClient(
                    host=CHROMA_CONFIG["host"],
                    port=CHROMA_CONFIG["port"],
                    ssl=CHROMA_CONFIG["ssl"]
                )
                print(f"Chroma DB initialisé en mode distant: {CHROMA_CONFIG['host']}:{CHROMA_CONFIG['port']}")

                    
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de Chroma DB: {e}")
            # En mode développement avec Docker Compose, Chroma DB est attendu comme un service séparé.
            # Si la connexion échoue, c'est une erreur critique.
            self.client = None
            raise ConnectionError(f"Impossible de se connecter au service Chroma DB: {e}. Assurez-vous que le conteneur 'chroma-db' est en cours d'exécution.")
    
    def get_client(self):
        """Retourne le client Chroma DB"""
        if not self.client:
            self._init_client()
        return self.client
    
    def get_or_create_collection(self, collection_name: str, embedding_function=None):
        """Récupère ou crée une collection"""
        try:
            client = self.get_client()
            if not client:
                raise Exception("Client Chroma DB non disponible")
            
            return client.get_or_create_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
        except Exception as e:
            print(f"Erreur lors de la création/récupération de la collection {collection_name}: {e}")
            return None
    
    def delete_collection(self, collection_name: str) -> bool:
        """Supprime une collection"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            client.delete_collection(name=collection_name)
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression de la collection {collection_name}: {e}")
            return False
    
    def list_collections(self):
        """Liste toutes les collections"""
        try:
            client = self.get_client()
            if not client:
                return []
            
            return client.list_collections()
        except Exception as e:
            print(f"Erreur lors de la liste des collections: {e}")
            return []
    
    def health_check(self) -> bool:
        """Vérifie la santé de la connexion Chroma DB"""
        try:
            client = self.get_client()
            if not client:
                return False
            
            # Essayer de lister les collections pour tester la connexion
            client.list_collections()
            return True
        except Exception as e:
            print(f"Health check Chroma DB échoué: {e}")
            return False

# Instance globale
chroma_manager = ChromaDBManager()

