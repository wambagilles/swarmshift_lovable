"""
Flux agentique pour l'application Swarmshift
Implémente le workflow multi-agent avec create_swarm et le réceptionniste comme agent par défaut
"""
import os
from typing import Dict, List, Any,  Optional,  Callable, Iterator
import json
from datetime import datetime
import uuid

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool, Tool
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
# Importer le module de traitement des documents
from src.document_processor import search_documents as search_docs

# Outils pour l'agent calculateur
def addition(a: float, b: float) -> float:
    """
    Additionne deux nombres.
    
    Args:
        a: Premier nombre
        b: Deuxième nombre
        
    Returns:
        Somme des deux nombres
    """
    return a + b

def multiplication(a: float, b: float) -> float:
    """
    Multiplie deux nombres.
    
    Args:
        a: Premier nombre
        b: Deuxième nombre
        
    Returns:
        Produit des deux nombres
    """
    return a * b

# Outil pour l'agent RAG
def search_documents(query: str, embedding_model: str = "openai", n_results: int = 3) -> str:
    """
    Récupère les documents pertinents pour la requête.
    
    Args:
        query: Requête de recherche
        embedding_model: Modèle d'embedding à utiliser
        n_results: Nombre de résultats à retourner
        
    Returns:
        Documents pertinents formatés en texte
    """
    try:

        # Rechercher les documents pertinents
        results = search_docs(
            query=query,
            embedding_model=embedding_model,
            n_results=n_results
        )
        
        # Formater les résultats
        formatted_results = ""
        for i, doc in enumerate(results):
            source = doc.get("source", "inconnu")
            page = doc.get("page", 0)
            content = doc.get("content", "")
            formatted_results += f"\n--- Extrait {i+1} (Source: {source}, Page: {page}) ---\n{content}\n"
        
        return formatted_results
    except Exception as e:
        return f"Erreur lors de la recherche de documents: {str(e)}"

# Définir les prompts des agents
def make_prompt(base_system_prompt: str) -> Callable[[dict, RunnableConfig], list]:
    """
    Crée une fonction de prompt pour les agents
    
    Args:
        base_system_prompt: Prompt système de base
        
    Returns:
        Fonction de prompt
    """
    def prompt(state: dict, config: Optional[RunnableConfig] = None) -> list:
        return [{"role": "system", "content": base_system_prompt}] + state["messages"]
    
    return prompt

# Créer le workflow agentique
def create_agent_workflow(display_reasoning: bool = False):
    """
    Crée un workflow agentique avec le réceptionniste comme agent par défaut
    
    Args:
        display_reasoning: Afficher le raisonnement ou non
        
    Returns:
        Workflow agentique configuré
    """
    # Initialiser le modèle LLM
    model = ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0,
        streaming=True,
        api_key=os.getenv("OPENAI_API_KEY")
    )
    
    # Créer les outils de handoff
    transfer_to_calculator = create_handoff_tool(
        agent_name="calculator",
        description="Transférer l'utilisateur à l'agent calculateur qui peut effectuer des opérations mathématiques simples (addition, multiplication)."
    )
    
    transfer_to_rag = create_handoff_tool(
        agent_name="rag",
        description="Transférer l'utilisateur à l'agent RAG qui peut rechercher des informations dans les documents et répondre aux questions."
    )
    
    transfer_to_receptionist = create_handoff_tool(
        agent_name="receptionist",
        description="Transférer l'utilisateur à l'agent réceptionniste qui peut analyser la requête et la router vers l'agent approprié."
    )
    
    # Définir les prompts des agents
    receptionist_prompt = """Vous êtes l'agent réceptionniste de Swarmshift, pour créer et déployer facilement (no code) des Agent IA conversationnels, créé par Gilles Madi.
    
    Vos responsabilités :
    - Analyser les requêtes entrantes des utilisateurs
    - Identifier l'agent spécialisé approprié pour traiter la requête
    - Coordonner la réponse globale et assurer que tous les aspects de la requête sont traités
    
    Vous commencez toujours par analyser la nature de la requête pour déterminer l'agent approprié :
    
    1. Si la requête concerne un calcul mathématique simple (addition ou multiplication), transférez à l'agent calculateur
    2. Si la requête nécessite une recherche dans des documents ou une réponse basée sur des connaissances, transférez à l'agent RAG
   
    Les requetes qui ne concerne pas de calcul mathematique, tu les transfere directement à l'agent RAG
    
    Soyez efficace et précis dans votre analyse.
    """
    
    calculator_prompt = """Vous êtes l'agent calculateur de Swarmshift, spécialisé dans les opérations mathématiques simples.
    
    Vos responsabilités :
    - Effectuer des additions et des multiplications
    - Extraire les nombres et l'opération demandée de la requête utilisateur
    - Fournir une réponse claire avec le résultat du calcul
    
    Vous ne pouvez effectuer que des additions et des multiplications. Pour toute autre opération ou requête non mathématique, 
    transférez à l'agent réceptionniste.
    
    Soyez précis et montrez clairement votre raisonnement.
    """
    
    rag_prompt = """Vous êtes l'agent RAG (Retrieval Augmented Generation) de RAGnify, spécialisé dans la recherche documentaire.
    
    Vos responsabilités :
    - Rechercher des informations pertinentes dans les documents vectorisés
    - Générer des réponses basées sur le contexte trouvé
    - Citer vos sources avec précision (nom du document et numéro de page)
    
    Utilisez uniquement les informations trouvées dans les documents pour répondre. Si vous ne trouvez pas d'information pertinente,
    indiquez-le clairement et ne tentez pas d'inventer une réponse.
    
    Pour les requêtes mathématiques ou non documentaires, transférez à l'agent approprié.
    
    Format de citation : (nom_du_document.pdf, page X)
    
    IMPORTANT: À la fin de votre réponse, listez toujours vos sources sous la forme:
    
    Sources:
    - [nom_du_document.pdf, page X]
    - [nom_du_document.pdf, page Y]
    """
    
    # Créer les agents
    receptionist = create_react_agent(
        model,
        [transfer_to_calculator, transfer_to_rag],
        prompt=make_prompt(receptionist_prompt),
        name="receptionist"
    )
    
    calculator = create_react_agent(
        model,
        [addition, multiplication, transfer_to_receptionist, transfer_to_rag],
        prompt=make_prompt(calculator_prompt),
        name="calculator"
    )
    
    rag = create_react_agent(
        model,
        [search_documents, transfer_to_receptionist, transfer_to_calculator],
        prompt=make_prompt(rag_prompt),
        name="rag"
    )
    
    # Créer le checkpointer pour la mémoire
    checkpointer = MemorySaver()
    
    # Créer le swarm avec les trois agents et le réceptionniste comme agent par défaut
    builder = create_swarm(
        [receptionist, calculator, rag],
        default_active_agent="receptionist"
    )
    
    # Compiler le swarm avec le checkpointer
    app = builder.compile(checkpointer=checkpointer)
    
    return app

# Classe pour gérer le workflow agentique
class AgentWorkflow:
    """Gestionnaire du workflow agentique"""
    
    def __init__(self):
        """Initialise le workflow agentique"""
        self.app = create_agent_workflow()
    
    def stream(self, query: str, 
              display_reasoning: bool = False, 
              rag_available: bool = False,
              rag_id: Optional[str] = None,
              documents: List[Dict[str, Any]] = None,
              embedding_model: str = "openai") -> Iterator[Dict[str, Any]]:
        """
        Exécute une requête utilisateur avec le workflow agentique en mode streaming
        
        Args:
            query: Requête de l'utilisateur
            display_reasoning: Afficher le raisonnement ou non
            rag_available: Si un RAG est disponible
            rag_id: ID du RAG
            documents: Documents du RAG
            embedding_model: Modèle d'embedding
            
        Returns:
            Itérateur sur les chunks de réponse
        """
        # Initialiser les valeurs par défaut
        if documents is None:
            documents = []
        
        # Préparer la requête actuelle
        messages = [{"role": "user", "content": query}]
        
        # Préparer les métadonnées
        config = {
            "configurable": {
                "display_reasoning": display_reasoning,
                "rag_available": rag_available,
                "rag_id": rag_id,
                "documents": documents,
                "embedding_model": embedding_model,
                "thread_id": str(uuid.uuid4())
            }
        }
        
        # Streamer le workflow
        return self.app.stream(
            {"messages": messages},
            config,
            subgraphs=True
        )

# Créer une instance du workflow agentique
agent_workflow = AgentWorkflow()

# Fonction pour exécuter une requête en streaming
def stream_agent_workflow(query: str, 
                         display_reasoning: bool = False, 
                         rag_available: bool = False,
                         rag_id: Optional[str] = None,
                         documents: List[Dict[str, Any]] = None,
                         embedding_model: str = "openai") -> Iterator[Dict[str, Any]]:
    """
    Exécute une requête utilisateur avec le workflow agentique en mode streaming
    
    Args:
        query: Requête de l'utilisateur
        display_reasoning: Afficher le raisonnement ou non
        rag_available: Si un RAG est disponible
        rag_id: ID du RAG
        documents: Documents du RAG
        embedding_model: Modèle d'embedding
        
    Returns:
        Itérateur sur les chunks de réponse
    """
    return agent_workflow.stream(
        query=query,
        display_reasoning=display_reasoning,
        rag_available=rag_available,
        rag_id=rag_id,
        documents=documents,
        embedding_model=embedding_model
    )

# Fonction pour extraire les sources d'une réponse RAG
def extract_rag_sources(response: str) -> List[str]:
    """
    Extrait les sources citées dans une réponse RAG
    
    Args:
        response: Réponse de l'agent RAG
        
    Returns:
        Liste des sources citées
    """
    sources = []
    
    # Chercher les sources dans le format [nom_du_document.pdf, page X]
    import re
    source_pattern = r'\[([^\]]+\.(?:pdf|docx|doc|txt)), page (\d+)\]'
    matches = re.findall(source_pattern, response)
    
    for match in matches:
        document, page = match
        sources.append(f"{document}, page {page}")
    
    return sources
