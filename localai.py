import requests
import json
import time

# URL de l'API LocalAI
LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"

# Modèle à utiliser
MODEL = "mistral-7b-instruct-v0.3"

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

def generate_text(prompt, max_tokens=1500, temperature=0.7, retry_count=2, retry_delay=1):
    """
    Génère du texte en utilisant l'API LocalAI.
    
    Args:
        prompt (str): Le prompt à envoyer à l'API.
        max_tokens (int, optional): Nombre maximum de tokens à générer. Par défaut 1500.
        temperature (float, optional): Température pour la génération. Par défaut 0.7.
        retry_count (int, optional): Nombre de tentatives en cas d'échec. Par défaut 2.
        retry_delay (int, optional): Délai entre les tentatives en secondes. Par défaut 1.
        
    Returns:
        str: Le texte généré par l'API.
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
                print(f"Erreur lors de la requête à LocalAI: {response.status_code}")
                print(f"Détails: {response.text}")
                
                # Si c'est la dernière tentative, retourner un message d'erreur
                if attempts == retry_count:
                    return f"Erreur lors de la génération du texte. Code: {response.status_code}. Veuillez réessayer plus tard."
                
                # Sinon, attendre et réessayer
                time.sleep(retry_delay)
                attempts += 1
                
        except requests.exceptions.Timeout:
            print("Timeout lors de la requête à LocalAI")
            if attempts == retry_count:
                return "Erreur: Le serveur LocalAI met trop de temps à répondre. Veuillez réessayer plus tard."
            time.sleep(retry_delay)
            attempts += 1
            
        except Exception as e:
            print(f"Exception lors de la requête à LocalAI: {str(e)}")
            if attempts == retry_count:
                return f"Erreur lors de la génération du texte: {str(e)}"
            time.sleep(retry_delay)
            attempts += 1

def evaluate_code(code, enonce, max_tokens=1500, temperature=0.7):
    """
    Évalue le code Python soumis par rapport à un énoncé.
    
    Args:
        code (str): Le code Python à évaluer.
        enonce (str): L'énoncé de l'exercice.
        max_tokens (int, optional): Nombre maximum de tokens à générer. Par défaut 1500.
        temperature (float, optional): Température pour la génération. Par défaut 0.7.
        
    Returns:
        str: L'évaluation du code.
    """
    prompt = f"""
    Évalue le code Python suivant par rapport à l'énoncé donné:
    
    Énoncé:
    {enonce}
    
    Code soumis:
    ```python
    {code}
    ```
    
    IMPORTANT: Ton évaluation doit être formatée en HTML pur pour un affichage correct dans un navigateur.
    
    Ton évaluation doit inclure:
    1. Un titre principal avec <h1>Évaluation du code</h1>
    2. Une section sur la conformité à l'énoncé avec <h2>Conformité à l'énoncé</h2>
    3. Une section sur les erreurs potentielles avec <h2>Erreurs potentielles</h2>
    4. Une section sur les suggestions d'amélioration avec <h2>Suggestions d'amélioration</h2>
    5. Une section sur les conseils pour aller plus loin avec <h2>Pour aller plus loin</h2>
    
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
    
    Ne donne pas la solution complète, mais guide l'élève vers la bonne direction.
    Sois encourageant et constructif dans tes retours.
    
    Ne mélange pas HTML et Markdown. Utilise uniquement du HTML pur.
    """
    
    return generate_text(prompt, max_tokens, temperature)
