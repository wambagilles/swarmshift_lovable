# SwarmShift Backend FastAPI

Ce projet convertit l'application Streamlit SwarmShift en backend FastAPI pour fonctionner avec un frontend React.

## Architecture

- **Backend**: FastAPI avec la logique métier existante
- **Frontend**: React (fourni, non modifié)
- **Base de données vectorielle**: ChromaDB
- **Authentification**: Mode DEV (local) et PROD (Firebase)

## Structure du projet

```
backend_project/
├── main.py                 # Application FastAPI principale
├── src/                    # Modules source (copiés de l'ancien projet)
│   ├── auth.py            # Authentification
│   ├── config.py          # Configuration
│   ├── chroma_manager.py  # Gestionnaire ChromaDB
│   ├── firebase_db.py     # Base de données Firebase
│   ├── user_store.py      # Stockage utilisateur
│   ├── document_processor.py # Traitement des documents
│   ├── agents/            # Agents IA
│   └── ...
├── frontend/              # Frontend React (non modifié)
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Image Docker backend
├── docker-compose.yml    # Orchestration des services
├── .env.example          # Variables d'environnement
└── README.md             # Cette documentation
```

## API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion utilisateur
- `POST /api/auth/signup` - Inscription utilisateur
- `POST /api/auth/logout` - Déconnexion
- `GET /api/auth/me` - Informations utilisateur

### RAGs
- `GET /api/rags` - Liste des RAGs utilisateur
- `GET /api/rags/{rag_id}` - Détails d'un RAG
- `POST /api/rags` - Créer un nouveau RAG
- `PUT /api/rags/{rag_id}` - Mettre à jour un RAG
- `DELETE /api/rags/{rag_id}` - Supprimer un RAG

### Documents
- `POST /api/rags/{rag_id}/documents/upload` - Upload de fichiers
- `POST /api/rags/{rag_id}/documents/urls` - Ajouter des URLs

### Chat
- `POST /api/chat` - Chat avec un RAG

### Statistiques
- `GET /api/stats` - Statistiques utilisateur
- `GET /health` - Santé de l'API

## Configuration

### Variables d'environnement

Copiez `.env.example` vers `.env` et configurez:

```bash
# Mode de fonctionnement
ENVIRONMENT=DEV

# OpenAI (requis)
OPENAI_API_KEY=your_openai_api_key_here

# ChromaDB
CHROMA_SERVER_HOST=chroma-db
CHROMA_SERVER_PORT=8000

# Serveur
PORT=8000
HOST=0.0.0.0
```

### Mode DEV vs PROD

- **DEV**: Authentification locale, données stockées localement
- **PROD**: Firebase Auth, données dans Firestore

## Installation et déploiement

### Prérequis

- Docker et Docker Compose
- Clé API OpenAI

### Déploiement avec Docker Compose

1. **Cloner et configurer**:
```bash
cd backend_project
cp .env.example .env
# Éditer .env avec votre clé OpenAI
```

2. **Construire et démarrer**:
```bash
docker-compose up --build
```

3. **Accès aux services**:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Documentation API: http://localhost:8000/docs
- ChromaDB: http://localhost:8000 (port ChromaDB)

### Déploiement manuel

1. **Installer les dépendances**:
```bash
pip install -r requirements.txt
```

2. **Démarrer ChromaDB** (dans un terminal séparé):
```bash
chroma run --path ./chroma_db
```

3. **Démarrer le backend**:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Démarrer le frontend** (dans le dossier frontend):
```bash
npm install
npm run dev
```

## Fonctionnalités

### Authentification
- Connexion/inscription en mode DEV (accepte tout email/mot de passe)
- Support Firebase pour le mode PROD

### Gestion des RAGs
- Création de RAGs avec configuration personnalisée
- Upload de documents (PDF, Word)
- Ajout d'URLs web
- Vectorisation automatique avec ChromaDB

### Chat intelligent
- Architecture multi-agent (réceptionniste, calculateur, RAG)
- Recherche sémantique dans les documents
- Réponses contextuelles avec sources

### Persistance
- Données utilisateur stockées localement en mode DEV
- Collections ChromaDB par utilisateur
- Gestion des sessions

## Différences avec Streamlit

### Changements principaux
1. **Interface**: Streamlit → React + FastAPI
2. **État**: Session Streamlit → API stateless avec persistance
3. **Fichiers**: Upload Streamlit → API multipart/form-data
4. **Streaming**: Streamlit streaming → Réponses JSON

### Logique préservée
- Tous les modules `src/` sont conservés sans modification
- Workflow des agents identique
- Traitement des documents inchangé
- Configuration ChromaDB identique

## Développement

### Structure des réponses API

```python
# Authentification
{
    "success": bool,
    "message": str,
    "user_id": str | None
}

# Chat
{
    "response": str,
    "sources": List[str],
    "reasoning": str | None
}

# RAG
{
    "id": str,
    "name": str,
    "description": str,
    "config": dict,
    "document_count": int,
    ...
}
```

### Ajout de nouvelles fonctionnalités

1. Ajouter l'endpoint dans `main.py`
2. Créer le modèle Pydantic si nécessaire
3. Implémenter la logique métier
4. Tester avec `/docs`

## Dépannage

### Erreurs communes

1. **ChromaDB non accessible**:
   - Vérifier que le service ChromaDB est démarré
   - Vérifier la configuration réseau Docker

2. **Erreur OpenAI**:
   - Vérifier la clé API dans `.env`
   - Vérifier les quotas OpenAI

3. **Erreur de permissions**:
   - Vérifier les volumes Docker
   - Créer les dossiers `dev_data`, `uploads`, `chroma_db`

### Logs

```bash
# Logs de tous les services
docker-compose logs -f

# Logs du backend uniquement
docker-compose logs -f backend

# Logs ChromaDB
docker-compose logs -f chroma-db
```

## Migration depuis Streamlit

Pour migrer des données existantes:

1. Copier le dossier `dev_data/` de l'ancien projet
2. Copier les bases ChromaDB si elles existent
3. Redémarrer les services

## Support

- Documentation API: http://localhost:8000/docs
- Santé de l'API: http://localhost:8000/health
- Logs: `docker-compose logs -f`

