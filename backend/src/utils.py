"""
Utilitaires pour l'application Streamlit RAG No-Code
"""
import streamlit as st
import re


def get_documents_by_source(rag):
    documents_by_source = {}
    for doc in rag.get('documents', []):
        source = doc.get('source', 'Inconnu')
        if source not in documents_by_source:
            documents_by_source[source] = []
        documents_by_source[source].append(doc)
    return documents_by_source

def print_stream_old(stream):
    """
    Affiche les mises à jour du stream de manière progressive sur Streamlit.
    
    Cette fonction simplifiée:
    - Regroupe toutes les interactions des outils et agents sous un seul expander minimaliste
    - Affiche uniquement le dernier message dans un conteneur avec les sources
    - Inclut les messages intermédiaires des nœuds dans les détails techniques
    - Présente le contenu en mode stream pour une meilleure expérience utilisateur
    
    Args:
        stream: Le flux de données à afficher
    """
    all_technical_details = []
    last_message = None
    last_message_node = None
    
    # Collecter toutes les informations techniques et identifier le dernier message
    for ns, update in stream:
        for node, node_updates in update.items():
            if node_updates is None:
                continue

            if isinstance(node_updates, (dict, tuple)):
                node_updates_list = [node_updates]
            elif isinstance(node_updates, list):
                node_updates_list = node_updates
            else:
                continue

            for node_update in node_updates_list:
                # Collecter les détails techniques
                technical_info = {
                    'namespace': ns,
                    'node': node,
                    'update': node_update
                }
                all_technical_details.append(technical_info)
                
                # Identifier le dernier message
                messages_key = next(
                    (k for k in node_update.keys() if "messages" in k), None
                ) if isinstance(node_update, dict) else None
                
                if messages_key is not None and node_update[messages_key]:
                    last_message = node_update[messages_key][-1]
                    last_message_node = node

    # Afficher l'expander minimaliste avec tous les détails techniques
    if all_technical_details:
        with st.expander("🔧 Détails techniques", expanded=False):
            for i, detail in enumerate(all_technical_details):
                st.markdown(f"**{detail['namespace']} → {detail['node']}**")
                
                # Afficher les outils utilisés si présents
                if isinstance(detail['update'], dict) and "tools" in detail['update']:
                    tools = detail['update']['tools']
                    st.markdown("*Outils utilisés:*")
                    for tool in tools:
                        st.markdown(f"  - `{tool['name']}`")
                        if 'args' in tool:
                            st.markdown(f"    *Arguments:* `{tool['args']}`")
                
                # Afficher les informations de raisonnement si présentes
                if isinstance(detail['update'], dict) and "reasoning" in detail['update']:
                    st.markdown("*Raisonnement:*")
                    st.markdown(f"```\n{detail['update']['reasoning']}\n```")
                
                # Afficher tous les messages intermédiaires du nœud
                messages_key = next(
                    (k for k in detail['update'].keys() if "messages" in k), None
                ) if isinstance(detail['update'], dict) else None
                
                if messages_key is not None and detail['update'][messages_key]:
                    messages = detail['update'][messages_key]
                    if len(messages) > 1:  # S'il y a plus d'un message, afficher les intermédiaires
                        st.markdown("*Messages intermédiaires:*")
                        for j, msg in enumerate(messages[:-1]):  # Exclure le dernier message
                            if hasattr(msg, 'content'):
                                # Tronquer les messages longs pour les détails techniques
                                content = msg.content
                                if len(content) > 200:
                                    content = content[:200] + "..."
                                st.markdown(f"  {j+1}. {content}")
                            elif hasattr(msg, 'type'):
                                st.markdown(f"  {j+1}. [{msg.type}] {str(msg)[:100]}...")
                            else:
                                st.markdown(f"  {j+1}. {str(msg)[:100]}...")
                
                # Afficher d'autres informations de mise à jour
                if isinstance(detail['update'], dict):
                    for key, value in detail['update'].items():
                        if key not in ['tools', 'reasoning'] and not key.endswith('messages'):
                            if isinstance(value, (str, int, float, bool)):
                                st.markdown(f"*{key}:* `{value}`")
                            elif isinstance(value, (list, dict)) and len(str(value)) < 200:
                                st.markdown(f"*{key}:* `{value}`")
                
                # Afficher les tuples et autres types
                elif isinstance(detail['update'], tuple):
                    st.markdown("*Données:*")
                    st.code(str(detail['update']))
                
                # Séparateur entre les détails (sauf pour le dernier)
                if i < len(all_technical_details) - 1:
                    st.markdown("---")

    # Afficher uniquement le dernier message dans un conteneur principal
    if last_message is not None:
        # Badge discret indiquant l'agent source
        st.markdown(f"""
        <div style="margin-bottom: 15px;">
            <span style="background-color: #e6f3ff; padding: 4px 8px; border-radius: 4px; font-size: 0.85em; color: #0066cc; font-weight: 500;">
                {last_message_node}
            </span>
        </div>
        """, unsafe_allow_html=True)
        
        # Conteneur principal pour le message
        with st.container():
            if hasattr(last_message, 'content'):
                message_content = last_message.content
                
                # Traitement spécial pour les messages avec sources (agent RAG)
                if last_message_node == "rag" and "Sources:" in message_content:
                    # Séparer le contenu et les sources
                    parts = message_content.split("Sources:")
                    main_content = parts[0].strip()
                    sources_text = "Sources:" + parts[1] if len(parts) > 1 else ""
                    
                    # Afficher le contenu principal
                    st.markdown(main_content)
                    
                    # Afficher les sources dans un format élégant (sans séparateur)
                    if sources_text:
                        with st.expander("📚 Sources citées", expanded=True):
                            st.markdown(sources_text)
                else:
                    # Afficher le message normalement
                    st.markdown(message_content)
            else:
                # Fallback si le message n'a pas d'attribut content
                st.write(last_message)
    
    # Indicateur de fin de conversation
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8em; margin-top: 20px; padding: 10px;'>
        ✓ Conversation terminée
    </div>
    """, unsafe_allow_html=True)



def extract_sources_from_response(response):
    """
    Extrait les sources citées dans une réponse RAG.
    
    Args:
        response: Réponse de l'agent RAG
        
    Returns:
        Liste des sources citées
    """
    sources = []
    
    # Chercher les sources dans le format [nom_du_document.pdf, page X]
    source_pattern = r'\[([^\]]+\.(?:pdf|docx|doc|txt)), page (\d+)\]'
    matches = re.findall(source_pattern, response)
    
    for match in matches:
        document, page = match
        sources.append(f"{document}, page {page}")
    
    # Chercher également les sources dans le format (nom_du_document.pdf, page X)
    source_pattern2 = r'\(([^)]+\.(?:pdf|docx|doc|txt)), page (\d+)\)'
    matches2 = re.findall(source_pattern2, response)
    
    for match in matches2:
        document, page = match
        sources.append(f"{document}, page {page}")
    
    return sources
