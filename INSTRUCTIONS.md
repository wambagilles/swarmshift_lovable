# Instructions de déploiement - SwarmShift Backend FastAPI

## Résumé des modifications

Le code Streamlit original a été converti en backend FastAPI tout en préservant la logique métier existante. Voici les changements principaux :

### ✅ Ce qui a été conservé
- **Tous les modules `src/`** : logique métier inchangée
- **Workflow des agents** : architecture multi-agent identique
- **Traitement des documents** : vectorisation ChromaDB identique
- **Authentification** : modes DEV/PROD préservés
- **Configuration** : variables d'environnement identiques

### 🔄 Ce qui a été adapté
- **Interface** : Streamlit → FastAPI REST API
- **État** : Session Streamlit → API stateless avec persistance
- **Upload** : Streamlit file_uploader → API multipart/form-data
- **Réponses** : Streaming Streamlit → JSON responses

## Structure du projet livré

```
backend_project/
├── main.py                 # ✨ NOUVEAU: Application FastAPI
├── src/                    # ✅ CONSERVÉ: Modules originaux
│   ├── auth.py            # Authentification (inchangé)
│   ├── config.py          # Configuration (inchangé)
│   ├── chroma_manager.py  # ChromaDB (inchangé)
│   ├── firebase_db.py     # Base de données (inchangé)
│   ├── document_processor.py # Traitement docs (inchangé)
│   ├── agents/            # Agents IA (inchangé)
│   └── ...
├── frontend/              # ✅ CONSERVÉ: Frontend fourni
├── requirements.txt       # ✨ NOUVEAU: Dépendances FastAPI
├── Dockerfile            # ✨ NOUVEAU: Image Docker backend
├── docker-compose.yml    # 🔄 MODIFIÉ: Orchestration mise à jour
├── .env.example          # ✨ NOUVEAU: Variables d'environnement
├── Dockerfile.backend    # ✅ CONSERVÉ: Dockerfile fourni
├── Dockerfile.chroma     # ✅ CONSERVÉ: Dockerfile fourni
├── Dockerfile.front      # ✅ CONSERVÉ: Dockerfile fourni
└── chroma_config.yaml    # ✅ CONSERVÉ: Config ChromaDB
```

## Déploiement rapide

### 1. Prérequis
- Docker et Docker Compose installés
- Clé API OpenAI valide

### 2. Configuration
```bash
cd backend_project
cp .env.example .env
```

Éditer `.env` et ajouter votre clé OpenAI :
```bash
OPENAI_API_KEY=sk-your-actual-openai-key-here
```

### 3. Démarrage
```bash
# Construire et démarrer tous les services
docker-compose up --build

# Ou en arrière-plan
docker-compose up --build -d
```

### 4. Accès
- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8002
- **Documentation API** : http://localhost:8002/docs
- **ChromaDB** : http://localhost:8000 (port ChromaDB interne)

## Services déployés

### 🔧 Backend FastAPI (Port 8000)
- Convertit toute la logique Streamlit en API REST
- Gère l'authentification, les RAGs, les documents, le chat
- Communique avec ChromaDB en interne
- **Le frontend ne communique JAMAIS directement avec ChromaDB**

### 🗄️ ChromaDB (Port 8000 interne)
- Base de données vectorielle
- Accessible uniquement par le backend
- Données persistantes via volumes Docker

### 🌐 Frontend React (Port 3000)
- Interface utilisateur fournie (non modifiée)
- Communique uniquement avec le backend FastAPI
- Toutes les interactions ChromaDB passent par l'API

## API Endpoints disponibles

### Authentification
```
POST /api/auth/login      # Connexion
POST /api/auth/signup     # Inscription  
POST /api/auth/logout     # Déconnexion
GET  /api/auth/me         # Info utilisateur
```

### RAGs
```
GET    /api/rags          # Liste des RAGs
GET    /api/rags/{id}     # Détails RAG
POST   /api/rags          # Créer RAG
PUT    /api/rags/{id}     # Modifier RAG
DELETE /api/rags/{id}     # Supprimer RAG
```

### Documents
```
POST /api/rags/{id}/documents/upload  # Upload fichiers
POST /api/rags/{id}/documents/urls    # Ajouter URLs
```

### Chat
```
POST /api/chat            # Chat avec RAG
```

### Utilitaires
```
GET /api/stats            # Statistiques utilisateur
GET /health               # Santé de l'API
```

## Fonctionnement en mode DEV

- **Authentification** : Accepte n'importe quel email/mot de passe
- **Données** : Stockées dans `./dev_data/` (volume Docker)
- **ChromaDB** : Instance locale avec persistance
- **Configuration** : Variables d'environnement locales

## Commandes utiles

### Gestion des services
```bash
# Démarrer
docker-compose up -d

# Arrêter
docker-compose down

# Redémarrer un service
docker-compose restart backend

# Voir les logs
docker-compose logs -f backend
docker-compose logs -f chroma-db
docker-compose logs -f frontend
```

### Développement
```bash
# Reconstruire après modification
docker-compose up --build

# Accéder au conteneur backend
docker-compose exec backend bash

# Nettoyer les volumes (⚠️ perte de données)
docker-compose down -v
```

## Vérification du déploiement

### 1. Santé des services
```bash
# API Backend
curl http://localhost:8000/health

# ChromaDB (via backend)
curl http://localhost:8000/api/stats
```

### 2. Test d'authentification
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

### 3. Interface web
- Ouvrir http://localhost:3000
- Tester la connexion avec n'importe quel email/mot de passe
- Créer un RAG de test
- Uploader un document
- Tester le chat

## Dépannage

### Problèmes courants

1. **Port déjà utilisé**
```bash
# Changer les ports dans docker-compose.yml
ports:
  - "3001:80"    # Frontend
  - "8001:8000"  # Backend
```

2. **ChromaDB non accessible**
```bash
# Vérifier les logs
docker-compose logs chroma-db

# Redémarrer ChromaDB
docker-compose restart chroma-db
```

3. **Erreur OpenAI**
```bash
# Vérifier la clé dans .env
cat .env | grep OPENAI_API_KEY

# Redémarrer le backend
docker-compose restart backend
```

4. **Volumes de données**
```bash
# Créer les dossiers si nécessaire
mkdir -p dev_data uploads chroma_db

# Vérifier les permissions
chmod 755 dev_data uploads chroma_db
```

### Logs détaillés
```bash
# Tous les services
docker-compose logs -f

# Service spécifique avec timestamps
docker-compose logs -f -t backend

# Dernières 100 lignes
docker-compose logs --tail=100 backend
```

## Migration depuis l'ancien système

Si vous avez des données existantes :

1. **Copier les données utilisateur**
```bash
cp -r /path/to/old/dev_data ./dev_data
```

2. **Copier les bases ChromaDB**
```bash
cp -r /path/to/old/chroma_db ./chroma_db
```

3. **Redémarrer les services**
```bash
docker-compose restart
```

## Personnalisation

### Modifier la configuration
- Éditer `.env` pour les variables d'environnement
- Modifier `docker-compose.yml` pour les ports/volumes
- Ajuster `src/config.py` pour la logique métier

### Ajouter des endpoints
1. Modifier `main.py`
2. Ajouter les modèles Pydantic
3. Implémenter la logique
4. Tester avec `/docs`

## Support et documentation

- **Documentation API interactive** : http://localhost:8000/docs
- **Santé de l'API** : http://localhost:8000/health
- **Logs en temps réel** : `docker-compose logs -f`
- **Code source** : Tous les fichiers sont documentés

## Résumé de la livraison

✅ **Backend FastAPI fonctionnel** avec toute la logique Streamlit convertie
✅ **Frontend React intégré** (fourni, non modifié)  
✅ **ChromaDB configuré** avec persistance
✅ **Docker Compose prêt** pour déploiement immédiat
✅ **Documentation complète** avec exemples
✅ **Mode DEV activé** pour tests rapides
✅ **API REST complète** remplaçant l'interface Streamlit
✅ **Isolation ChromaDB** : frontend → backend → ChromaDB uniquement

Le système est prêt à être déployé et testé immédiatement avec `docker-compose up --build`.

