import streamlit as st
from typing import List, Dict, Any





def initialize_chat_state():
    """Initialise l'état de la conversation dans la session Streamlit."""
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    if 'message_counter' not in st.session_state:
        st.session_state.message_counter = 0
    if 'last_processed_input' not in st.session_state:
        st.session_state.last_processed_input = ""
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False

def add_user_message(message: str):
    """Ajoute un message utilisateur à l'historique."""
    st.session_state.chat_messages.append({
        'type': 'user',
        'content': message,
        'timestamp': st.session_state.get('message_counter', 0)
    })
    st.session_state.message_counter = st.session_state.get('message_counter', 0) + 1

def add_assistant_response(stream_data):
    """Ajoute une réponse de l'assistant à l'historique."""
    # Traiter le stream pour extraire les informations
    all_technical_details = []
    last_message = None
    last_message_node = None
    
    for ns, update in stream_data:
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
                technical_info = {
                    'namespace': ns,
                    'node': node,
                    'update': node_update
                }
                all_technical_details.append(technical_info)
                
                messages_key = next(
                    (k for k in node_update.keys() if "messages" in k), None
                ) if isinstance(node_update, dict) else None
                
                if messages_key is not None and node_update[messages_key]:
                    last_message = node_update[messages_key][-1]
                    last_message_node = node

    # Ajouter la réponse à l'historique
    st.session_state.chat_messages.append({
        'type': 'assistant',
        'content': last_message.content if hasattr(last_message, 'content') else str(last_message),
        'node': last_message_node,
        'technical_details': all_technical_details,
        'timestamp': st.session_state.get('message_counter', 0)
    })
    st.session_state.message_counter = st.session_state.get('message_counter', 0) + 1

def render_user_message(message: Dict[str, Any]):
    """Affiche un message utilisateur (côté droit)."""
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
        <div style="
            background-color: #007bff;
            color: white;
            padding: 12px 16px;
            border-radius: 18px 18px 4px 18px;
            max-width: 70%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 14px; line-height: 1.4;">
                {message['content']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_assistant_message(message: Dict[str, Any]):
    """Affiche un message de l'assistant (côté gauche avec fond vert)."""
    # Conteneur principal pour le message assistant avec fond vert
    st.markdown(f"""
    <div style="display: flex; justify-content: flex-start; margin-bottom: 20px;">
        <div style="
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 12px 16px;
            border-radius: 18px 18px 18px 4px;
            max-width: 70%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <div style="margin-bottom: 8px;">
                <span style="
                    padding: 2px 6px; 
                    border-radius: 3px; 
                    font-size: 0.75em; 
                    color: #004085;
                    font-weight: 500;
                ">
                    {message.get('node', 'assistant')}
                </span>
            </div>
            <div style="font-size: 14px; line-height: 1.4;">
    """, unsafe_allow_html=True)
    
    # Traitement du contenu avec sources
    content = message['content']
    if message.get('node') == "rag" and "Sources:" in content:
        parts = content.split("Sources:")
        main_content = parts[0].strip()
        sources_text = "Sources:" + parts[1] if len(parts) > 1 else ""
        
        # Afficher le contenu principal
        st.markdown(main_content)
        
        # Afficher les sources
        if sources_text:
            with st.expander("📚 Sources citées", expanded=True):
                st.markdown(sources_text)
    else:
        st.markdown(content)
    
    # Fermer le conteneur HTML
    st.markdown("</div></div></div>", unsafe_allow_html=True)
    
    # Afficher les détails techniques si présents
    if message.get('technical_details'):
        with st.expander("🔧 Détails techniques", expanded=False):
            for i, detail in enumerate(message['technical_details']):
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
                    if len(messages) > 1:
                        st.markdown("*Messages intermédiaires:*")
                        for j, msg in enumerate(messages[:-1]):
                            if hasattr(msg, 'content'):
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
                if i < len(message['technical_details']) - 1:
                    st.markdown("---")

def render_chat_history():
    """Affiche tout l'historique de la conversation."""
    if not st.session_state.chat_messages:
        st.markdown("""
        <div style="text-align: center; color: #888; padding: 40px; font-style: italic;">
            Commencez une conversation en posant une question ci-dessous
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Afficher tous les messages dans l'ordre chronologique
    for message in st.session_state.chat_messages:
        if message['type'] == 'user':
            render_user_message(message)
        elif message['type'] == 'assistant':
            render_assistant_message(message)

def render_input_area():
    """Affiche la zone de saisie fixe en bas à droite."""
    st.markdown("""
    <style>

    
    /* Style pour le champ de saisie */
    .input-container .stTextInput > div > div > input {
        border-radius: 20px;
        border: 2px solid #e9ecef;
        padding: 12px 16px;
        font-size: 14px;
        width: 100%;
    }
    
    .input-container .stTextInput > div > div > input:focus {
        border-color: #007bff;
        box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .input-container {
            right: 0.5rem;
            left: 0.5rem;
            width: auto;
        }
    }
    
    @media (min-width: 1024px) {
        .input-container {
            width: 400px;
        }
    }
    
    /* Espace en bas pour éviter que le contenu soit caché */
    .main > div {
        padding-bottom: 8rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Créer un conteneur fixe pour la zone de saisie
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    # Déterminer la valeur du champ de saisie
    input_value = "" if st.session_state.get('clear_input', False) else st.session_state.get('current_input_value', "")
    #st.session_state["question_input_field"] = input_value
    # Zone de saisie avec gestion correcte de l'état
    
    current_input = st.text_input(
        "",
        value=input_value,
        placeholder="Posez une question...",
        key="question_input_field",
        label_visibility="collapsed",
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

  
    
    # Traitement de la soumission
    if current_input and current_input.strip() and current_input != st.session_state.get('last_processed_input', ''):
        # Ajouter le message utilisateur
        add_user_message(current_input.strip())
        
        # Marquer ce message comme traité
        st.session_state.last_processed_input = current_input
        
        # Marquer pour effacer le champ à la prochaine exécution
        st.session_state.clear_input = True
        st.session_state.current_input_value = ""
        
        # Rerun pour afficher le nouveau message et effacer le champ
        st.rerun()
    
    # Réinitialiser le flag de nettoyage après le rerun
    if st.session_state.get('clear_input', False):
        st.session_state.clear_input = False


def print_stream_chat_interface(stream=None):
    """
    Interface de chat complète avec gestion des messages persistants.
    
    Cette fonction:
    - Affiche les messages utilisateur à droite avec fond bleu
    - Affiche les réponses assistant à gauche avec fond vert
    - Maintient la zone de saisie "Posez une question" en bas à droite
    - Efface le champ de saisie après l'envoi d'un message
    - Conserve tous les messages précédents lors de nouvelles questions
    - Regroupe les détails techniques sous un expander minimaliste
    
    Args:
        stream: Le flux de données à traiter (optionnel, pour compatibilité)
    """
    # Initialiser l'état de la conversation
    initialize_chat_state()
    
    # Si un stream est fourni, traiter la réponse
    if stream is not None:
        add_assistant_response(stream)
    
    # Afficher l'historique de la conversation
    render_chat_history()
    
    # Zone de saisie fixe en bas à droite
    render_input_area()

# Fonction de compatibilité avec l'ancienne interface
def print_stream(stream):
    """
    Fonction de compatibilité qui redirige vers la nouvelle interface de chat.
    """
    return print_stream_chat_interface(stream)

