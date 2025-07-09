"""
Configuration adaptée pour le déploiement en production sur Cloud Run + Cloud SQL
"""
import os
import json
from dotenv import load_dotenv
from google.cloud import secretmanager

# Chargement des variables d'environnement
load_dotenv()

# Détermination de l'environnement (DEV ou PROD)
ENV = os.getenv("ENVIRONMENT", "DEV").upper()

# Fonction pour récupérer les secrets depuis Secret Manager (uniquement en PROD)
def get_secret(secret_id):
    if ENV != "PROD":
        return None
    
    try:
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        if not project_id:
            print("ATTENTION: Variable GOOGLE_CLOUD_PROJECT non définie")
            return None
            
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
        response = client.access_secret_version(name=name)
        return response.payload.data.decode("UTF-8")
    except Exception as e:
        print(f"Erreur lors de la récupération du secret {secret_id}: {e}")
        return None

# Chargement des configurations depuis Secret Manager en PROD
if ENV == "PROD":
    # Chargement de la configuration Firebase depuis Secret Manager
    firebase_config_json = get_secret("firebase-config")
    if firebase_config_json:
        FIREBASE_CONFIG = json.loads(firebase_config_json)
    else:
        FIREBASE_CONFIG = {}
        print("ATTENTION: Configuration Firebase non trouvée dans Secret Manager")
    
    # Chargement de la configuration de connexion à la base de données
    db_connection_json = get_secret("db-connection")
    if db_connection_json:
        DB_CONNECTION = json.loads(db_connection_json)
    else:
        DB_CONNECTION = {}
        print("ATTENTION: Configuration de connexion à la base de données non trouvée")
    
    # Clé API OpenAI depuis Secret Manager
    OPENAI_API_KEY = get_secret("openai-api-key")
    if not OPENAI_API_KEY:
        print("ATTENTION: Clé API OpenAI non trouvée dans Secret Manager")
else:
    # En mode DEV, utiliser les variables d'environnement
    FIREBASE_CONFIG = {
        "apiKey": os.getenv("FIREBASE_API_KEY"),
        "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
        "projectId": os.getenv("FIREBASE_PROJECT_ID"),
        "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
        "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
        "appId": os.getenv("FIREBASE_APP_ID"),
        "databaseURL": os.getenv("FIREBASE_DATABASE_URL", "")
    }
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    DB_CONNECTION = {
        "DB_HOST": os.getenv("DB_HOST", "localhost"),
        "DB_PORT": os.getenv("DB_PORT", "5432"),
        "DB_USER": os.getenv("DB_USER", "chromauser"),
        "DB_PASSWORD": os.getenv("DB_PASSWORD", ""),
        "DB_NAME": os.getenv("DB_NAME", "chromadb"),
        "INSTANCE_CONNECTION_NAME": os.getenv("INSTANCE_CONNECTION_NAME", "")
    }

# Configuration de l'application
APP_NAME = "SwarmShift Enterprise"
APP_DESCRIPTION = "Créez et déployez facilement des Agent IA conversationnels"

# Configuration des modèles par défaut
DEFAULT_EMBEDDING_MODEL = "text-embedding-ada-002"
DEFAULT_LLM_MODEL = "gpt-3.5-turbo"

# Configuration des chemins (adaptés pour conteneur)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(BASE_DIR, "temp")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")

# Création des répertoires s'ils n'existent pas
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Configuration de la base de données vectorielle
VECTOR_DB = os.getenv("VECTOR_DB", "chroma")
CHROMA_DB_IMPL = os.getenv("CHROMA_DB_IMPL", "duckdb+parquet")

# Configuration Chroma DB
if ENV == "PROD" and VECTOR_DB == "chroma" and CHROMA_DB_IMPL == "postgres":
    # Configuration pour PostgreSQL sur Cloud SQL
    CHROMA_CONFIG = {
        "chroma_db_impl": "postgres",
        "host": DB_CONNECTION.get("DB_HOST", "localhost"),
        "port": int(DB_CONNECTION.get("DB_PORT", "5432")),
        "user": DB_CONNECTION.get("DB_USER", "chromauser"),
        "password": DB_CONNECTION.get("DB_PASSWORD", ""),
        "database": DB_CONNECTION.get("DB_NAME", "chromadb"),
        "ssl": os.getenv("CHROMA_SSL", "false").lower() == "true",
        # Pour Cloud SQL Proxy (utilisé automatiquement par Cloud Run)
        "instance_connection_name": DB_CONNECTION.get("INSTANCE_CONNECTION_NAME", "")
    }
    
    # Chemin de persistance pour les collections
    CHROMA_PERSIST_DIRECTORY = "/tmp/chroma_db"
else:
    # Configuration par défaut (mode DEV ou autre)
    CHROMA_CONFIG = {
        "host": os.getenv("CHROMA_SERVER_HOST", "chroma-db"),
        "port": int(os.getenv("CHROMA_SERVER_PORT", "8000")),
        "ssl": os.getenv("CHROMA_SSL", "false").lower() == "true"
    }
    
    # Chemin de persistance pour les collections en mode local
    CHROMA_PERSIST_DIRECTORY = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Liste des bases de données vectorielles disponibles en PROD
AVAILABLE_VECTOR_DBS = ["chroma", "faiss", "qdrant", "weaviate"]

# Liste des méthodes de découpage disponibles
AVAILABLE_SPLIT_METHODS = ["recursive", "character"]

# Configuration du mode développement
DEV_MODE = ENV == "DEV"

# Configuration pour le déploiement
DEPLOYMENT_CONFIG = {
    "port": int(os.getenv("PORT", "8501")),  # Cloud Run utilise la variable PORT
    "host": os.getenv("HOST", "0.0.0.0"),
    "debug": DEV_MODE
}

# Configuration GCP
GCP_CONFIG = {
    "project_id": os.getenv("GOOGLE_CLOUD_PROJECT"),
    "credentials_path": os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
}

# Affichage des informations de configuration
if DEV_MODE:
    print("Application en mode DÉVELOPPEMENT - Aucune connexion aux services externes")
else:
    print("Application en mode PRODUCTION - Connexion aux services Firebase activée")
    print(f"Base de données vectorielle: {VECTOR_DB}")
    if VECTOR_DB == "chroma":
        if CHROMA_DB_IMPL == "postgres":
            print(f"Chroma DB (PostgreSQL): {CHROMA_CONFIG['host']}:{CHROMA_CONFIG['port']}/{CHROMA_CONFIG['database']}")
        else:
            print(f"Chroma DB: {CHROMA_CONFIG['host']}:{CHROMA_CONFIG['port']}")
