"""
Module pour extraire le contenu des pages web pour l'application Streamlit RAG No-Code
"""
import requests
from bs4 import BeautifulSoup
import uuid
import os
from urllib.parse import urlparse
from typing import Dict, Any, List, Optional

def extract_text_from_url(url: str) -> List[Dict[str, Any]]:
    """
    Extrait le contenu textuel d'une page web
    
    Args:
        url: URL de la page web à extraire
        
    Returns:
        Liste de dictionnaires contenant le texte et les métadonnées
    """
    try:
        # Vérifier que l'URL est valide
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return [{
                "content": f"URL invalide: {url}",
                "page": 0,
                "source": url,
                "error": True
            }]
        
        # Faire la requête HTTP
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Lever une exception si la requête échoue
        
        # Analyser le contenu HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Supprimer les scripts, styles et balises non pertinentes
        for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Extraire le titre
        title = soup.title.string if soup.title else "Sans titre"
        
        # Extraire le contenu principal
        main_content = ""
        
        # Essayer de trouver le contenu principal
        main_elements = soup.find_all(['article', 'main', 'div', 'section'])
        
        # Trier les éléments par longueur de texte (heuristique simple)
        main_elements = sorted(main_elements, key=lambda x: len(x.get_text()), reverse=True)
        
        # Prendre les 3 plus grands éléments
        for element in main_elements[:3]:
            main_content += element.get_text(separator='\n', strip=True) + "\n\n"
        
        # Si aucun contenu principal n'a été trouvé, prendre tout le texte
        if not main_content.strip():
            main_content = soup.get_text(separator='\n', strip=True)
        
        # Nettoyer le texte (supprimer les lignes vides multiples)
        main_content = "\n".join([line for line in main_content.split('\n') if line.strip()])
        
        # Diviser le contenu en "pages" virtuelles (environ 3000 caractères par page)
        chars_per_page = 3000
        pages = []
        
        # Si le contenu est court, le mettre sur une seule page
        if len(main_content) <= chars_per_page:
            pages.append({
                "content": main_content,
                "page": 1,
                "source": f"Web: {title} ({url})",
                "url": url,
                "title": title
            })
        else:
            # Diviser le contenu en pages
            paragraphs = main_content.split('\n\n')
            current_page = 1
            current_content = ""
            
            for paragraph in paragraphs:
                if len(current_content) + len(paragraph) > chars_per_page and current_content:
                    # Ajouter la page courante
                    pages.append({
                        "content": current_content,
                        "page": current_page,
                        "source": f"Web: {title} ({url})",
                        "url": url,
                        "title": title
                    })
                    current_page += 1
                    current_content = paragraph + "\n\n"
                else:
                    current_content += paragraph + "\n\n"
            
            # Ajouter la dernière page
            if current_content:
                pages.append({
                    "content": current_content,
                    "page": current_page,
                    "source": f"Web: {title} ({url})",
                    "url": url,
                    "title": title
                })
        
        return pages
    
    except Exception as e:
        return [{
            "content": f"Erreur lors de l'extraction du contenu de la page web: {str(e)}",
            "page": 0,
            "source": url,
            "error": True
        }]

def save_web_content_as_file(url: str, save_dir: str = "temp") -> Optional[str]:
    """
    Sauvegarde le contenu d'une page web dans un fichier texte
    
    Args:
        url: URL de la page web
        save_dir: Répertoire où sauvegarder le fichier
        
    Returns:
        Chemin vers le fichier sauvegardé ou None en cas d'erreur
    """
    try:
        # Extraire le contenu
        pages = extract_text_from_url(url)
        
        # Vérifier s'il y a eu une erreur
        if pages and pages[0].get("error", False):
            return None
        
        # Créer le répertoire si nécessaire
        os.makedirs(save_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        filename = f"web_{uuid.uuid4().hex}.txt"
        file_path = os.path.join(save_dir, filename)
        
        # Écrire le contenu dans le fichier
        with open(file_path, 'w', encoding='utf-8') as f:
            for page in pages:
                f.write(f"--- Page {page['page']} ---\n\n")
                f.write(page['content'])
                f.write("\n\n")
        
        return file_path
    
    except Exception:
        return None
