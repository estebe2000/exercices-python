"""
Module pour interagir avec l'API LocalAI.

Ce module fournit des fonctions pour générer du texte et évaluer du code
en utilisant l'API LocalAI.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration de l'API LocalAI
LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"
MODEL = "codestral-latest"

# Paramètres par défaut
DEFAULT_MAX_TOKENS = 1500
DEFAULT_TEMPERATURE = 0.7
DEFAULT_RETRY_COUNT = 2
DEFAULT_RETRY_DELAY = 1

# Message système pour guider le modèle
SYSTEM_MESSAGE = """Tu es un expert en programmation Python et en pédagogie. 
Tu aides à créer des exercices de programmation pour des élèves de lycée et à évaluer leur code.

IMPORTANT: Tu dois formater tes réponses en HTML pur pour un affichage correct dans un navigateur.

Quand tu crées des exercices:
1. Utilise une structure claire avec des titres et sous-titres bien formatés (<h1>, <h2>, <h3>)
2. Fournis un squelette de code à trous avec des commentaires "# À COMPLÉTER" ou "# VOTRE CODE ICI"
3. Inclus des jeux de tests avec des messages de réussite (✅) ou d'échec (❌)
4. Adapte la difficulté au niveau de l'élève (Première ou Terminale)
5. Sois précis dans tes explications et tes attentes

Quand tu évalues du code:
1. Vérifie si le code répond correctement à l'énoncé
2. Identifie les erreurs potentielles (syntaxe, logique, etc.)
3. Suggère des améliorations (optimisation, lisibilité, etc.)
4. Donne des conseils pour aller plus loin
5. Sois encourageant et constructif dans tes retours

Utilise uniquement des balises HTML standard pour le formatage:
- <h1>, <h2>, <h3> pour les titres
- <p> pour les paragraphes
- <ul> et <li> pour les listes
- <pre><code class="language-python">...</code></pre> pour les blocs de code
- <strong> pour le texte en gras
- <em> pour le texte en italique
- <span class="text-success">✅ Texte</span> pour les messages de succès
- <span class="text-danger">❌ Texte</span> pour les messages d'erreur
- <span class="text-info">💡 Texte</span> pour les suggestions
- <span class="text-primary">🚀 Texte</span> pour les conseils d'amélioration

Ne mélange pas HTML et Markdown. Utilise uniquement du HTML pur.
"""


def get_evaluation_prompt(code: str, enonce: str) -> str:
    """
    Génère le prompt pour l'évaluation de code.
    
    Args:
        code: Le code Python à évaluer
        enonce: L'énoncé de l'exercice
        
    Returns:
        Le prompt formaté pour l'évaluation
    """
    return f"""
    Évalue le code Python suivant par rapport à l'énoncé donné:
    
    Énoncé:
    {enonce}
    
    Code soumis:
    ```python
    {code}
    ```
    
    IMPORTANT: Ton évaluation doit être formatée en HTML pur pour un affichage correct dans un navigateur.
    
    Ton évaluation doit toujours inclure:
    1. Un titre principal avec <h1>Évaluation du code</h1>
    2. Une section sur la conformité à l'énoncé avec <h2>Conformité à l'énoncé</h2>
    3. Une section sur les erreurs potentielles avec <h2>Erreurs potentielles</h2>
    4. Une section sur les suggestions d'amélioration avec <h2>Suggestions d'amélioration</h2>
    
    IMPORTANT: La section "Pour aller plus loin" avec <h2>Pour aller plus loin</h2> ne doit être incluse QUE si le code fonctionne correctement et répond à l'énoncé. Si le code contient des erreurs ou ne répond pas à l'énoncé, n'inclus PAS cette section.
    
    Utilise uniquement des balises HTML standard pour le formatage:
    - <h1>, <h2>, <h3> pour les titres
    - <p> pour les paragraphes
    - <ul> et <li> pour les listes
    - <pre><code class="language-python">...</code></pre> pour les blocs de code
    - <strong> pour le texte en gras
    - <em> pour le texte en italique
    
    Utilise des émojis et des classes pour rendre ton évaluation plus visuelle:
    - <span class="text-success">✅ Texte</span> pour les points positifs
    - <span class="text-danger">❌ Texte</span> pour les erreurs ou problèmes
    - <span class="text-info">💡 Texte</span> pour les suggestions
    - <span class="text-primary">🚀 Texte</span> pour les conseils d'amélioration
    
    TRÈS IMPORTANT:
    - NE DONNE JAMAIS LA SOLUTION COMPLÈTE à l'exercice
    - Fournis uniquement des notions de cours et des pistes de réflexion
    - Si tu dois donner un exemple de code, utilise un exemple différent de l'exercice ou montre seulement une petite partie de la solution
    - Guide l'élève vers la bonne direction sans faire le travail à sa place
    - Sois encourageant et constructif dans tes retours
    
    Ne mélange pas HTML et Markdown. Utilise uniquement du HTML pur.
    """


def generate_text(prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                 temperature: float = DEFAULT_TEMPERATURE, 
                 retry_count: int = DEFAULT_RETRY_COUNT, 
                 retry_delay: int = DEFAULT_RETRY_DELAY) -> str:
    """
    Génère du texte en utilisant l'API LocalAI.
    
    Args:
        prompt: Le prompt à envoyer à l'API
        max_tokens: Nombre maximum de tokens à générer
        temperature: Température pour la génération
        retry_count: Nombre de tentatives en cas d'échec
        retry_delay: Délai entre les tentatives en secondes
        
    Returns:
        Le texte généré par l'API
    """
    attempts = 0
    
    while attempts <= retry_count:
        try:
            # Préparer les données pour l'API
            data = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # Envoyer la requête à l'API
            response = requests.post(LOCALAI_URL, json=data, timeout=60)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                result = response.json()
                # Extraire le texte généré
                generated_text = result["choices"][0]["message"]["content"]
                return generated_text
            else:
                logger.error(f"Erreur lors de la requête à LocalAI: {response.status_code}")
                logger.error(f"Détails: {response.text}")
                
                # Si c'est la dernière tentative, retourner un message d'erreur
                if attempts == retry_count:
                    return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte. Code: {response.status_code}. Veuillez réessayer plus tard.</p>"
                
                # Sinon, attendre et réessayer
                time.sleep(retry_delay)
                attempts += 1
                
        except requests.exceptions.Timeout:
            logger.warning("Timeout lors de la requête à LocalAI")
            if attempts == retry_count:
                return "<h1>Erreur</h1><p>Erreur: Le serveur LocalAI met trop de temps à répondre. Veuillez réessayer plus tard.</p>"
            time.sleep(retry_delay)
            attempts += 1
            
        except Exception as e:
            logger.error(f"Exception lors de la requête à LocalAI: {str(e)}")
            if attempts == retry_count:
                return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte: {str(e)}</p>"
            time.sleep(retry_delay)
            attempts += 1


def evaluate_code(code: str, enonce: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                 temperature: float = DEFAULT_TEMPERATURE) -> str:
    """
    Évalue le code Python soumis par rapport à un énoncé.
    
    Args:
        code: Le code Python à évaluer
        enonce: L'énoncé de l'exercice
        max_tokens: Nombre maximum de tokens à générer
        temperature: Température pour la génération
        
    Returns:
        L'évaluation du code
    """
    prompt = get_evaluation_prompt(code, enonce)
    return generate_text(prompt, max_tokens, temperature)
