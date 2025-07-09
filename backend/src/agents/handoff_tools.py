"""
Implémentation de create_handoff_tool pour le transfert explicite entre agents
Basé sur la documentation de langgraph-swarm-py
"""

import os
from typing import Dict, List, Any, TypedDict, Annotated, Literal, Optional, Union, Tuple, Callable
import json
from functools import partial

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool, BaseTool, StructuredTool, Tool
from langgraph.graph import StateGraph, END
from langgraph_swarm import Swarm, SwarmMessage, SwarmState, register_swarm

def create_handoff_tool(swarm: Swarm, agent_name: str) -> BaseTool:
    """
    Crée un outil de transfert (handoff) vers un agent spécifique
    
    Args:
        swarm: Instance du swarm contenant les agents
        agent_name: Nom de l'agent vers lequel transférer
        
    Returns:
        Outil de transfert vers l'agent spécifié
    """
    def _handoff(query: str, metadata: Dict[str, Any] = None) -> str:
        """
        Transfère la requête à un autre agent
        
        Args:
            query: Requête à transférer
            metadata: Métadonnées supplémentaires à transmettre
            
        Returns:
            Réponse de l'agent cible
        """
        if metadata is None:
            metadata = {}
        
        # Créer le message à transférer
        message = SwarmMessage(content=query)
        
        # Invoquer l'agent cible
        result = swarm.invoke(
            agent_name=agent_name,
            message=message,
            metadata=metadata
        )
        
        # Retourner la réponse
        return result.content
    
    # Créer l'outil de transfert
    return Tool(
        name=f"handoff_to_{agent_name}",
        description=f"Transfère la requête à l'agent {agent_name} pour traitement spécialisé",
        func=_handoff
    )

def create_all_handoff_tools(swarm: Swarm, agent_names: List[str]) -> Dict[str, BaseTool]:
    """
    Crée des outils de transfert pour tous les agents spécifiés
    
    Args:
        swarm: Instance du swarm contenant les agents
        agent_names: Liste des noms d'agents pour lesquels créer des outils de transfert
        
    Returns:
        Dictionnaire d'outils de transfert, indexé par nom d'agent
    """
    handoff_tools = {}
    
    for agent_name in agent_names:
        handoff_tools[agent_name] = create_handoff_tool(swarm, agent_name)
    
    return handoff_tools
