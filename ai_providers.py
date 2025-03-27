import requests
import json
import time

# Configuration pour LocalAI
LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"
LOCALAI_MODEL = "mistral-7b-instruct-v0.3"

# Configuration pour Gemini
GEMINI_API_KEY = "AIzaSyDFjy8wVBrd4DUM3XjfbvTO4mRBSnTGCuw"
GEMINI_MODEL = "gemini-2.0-flash"

# Message système commun pour guider les modèles
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

# Classe de base pour les fournisseurs d'IA
class AIProvider:
    def generate_text(self, prompt, max_tokens=1500, temperature=0.7):
        """
        Méthode à implémenter par les classes enfants
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les classes enfants")
    
    def evaluate_code(self, code, enonce, max_tokens=1500, temperature=0.7):
        """
        Évalue le code Python soumis par rapport à un énoncé.
        
        Args:
            code (str): Le code Python à évaluer.
            enonce (str): L'énoncé de l'exercice.
            max_tokens (int, optional): Nombre maximum de tokens à générer.
            temperature (float, optional): Température pour la génération.
            
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
        
        return self.generate_text(prompt, max_tokens, temperature)

# Fournisseur LocalAI
class LocalAIProvider(AIProvider):
    def __init__(self, url=LOCALAI_URL, model=LOCALAI_MODEL):
        self.url = url
        self.model = model
    
    def generate_text(self, prompt, max_tokens=1500, temperature=0.7, retry_count=2, retry_delay=1):
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
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_MESSAGE},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                
                # Envoyer la requête à l'API
                response = requests.post(self.url, json=data, timeout=60)
                
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
                        return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte. Code: {response.status_code}. Veuillez réessayer plus tard.</p>"
                    
                    # Sinon, attendre et réessayer
                    time.sleep(retry_delay)
                    attempts += 1
                    
            except requests.exceptions.Timeout:
                print("Timeout lors de la requête à LocalAI")
                if attempts == retry_count:
                    return "<h1>Erreur</h1><p>Erreur: Le serveur LocalAI met trop de temps à répondre. Veuillez réessayer plus tard.</p>"
                time.sleep(retry_delay)
                attempts += 1
                
            except Exception as e:
                print(f"Exception lors de la requête à LocalAI: {str(e)}")
                if attempts == retry_count:
                    return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte: {str(e)}</p>"
                time.sleep(retry_delay)
                attempts += 1

# Fournisseur Gemini
class GeminiProvider(AIProvider):
    def __init__(self, api_key=GEMINI_API_KEY, model=GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def generate_text(self, prompt, max_tokens=1500, temperature=0.7, retry_count=2, retry_delay=1):
        """
        Génère du texte en utilisant l'API Gemini.
        
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
        
        # Construire le prompt complet avec le message système
        full_prompt = f"{SYSTEM_MESSAGE}\n\n{prompt}"
        
        while attempts <= retry_count:
            try:
                # URL de l'API Gemini
                url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
                
                # Corps de la requête
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": full_prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": temperature,
                        "maxOutputTokens": max_tokens
                    }
                }
                
                # En-têtes de la requête
                headers = {
                    "Content-Type": "application/json"
                }
                
                # Envoi de la requête POST
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
                
                # Vérification de la réponse
                if response.status_code == 200:
                    # Extraction du texte de la réponse
                    result = response.json()
                    return result['candidates'][0]['content']['parts'][0]['text']
                else:
                    print(f"Erreur lors de la requête à Gemini: {response.status_code}")
                    print(f"Détails: {response.text}")
                    
                    # Si c'est la dernière tentative, retourner un message d'erreur
                    if attempts == retry_count:
                        return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte. Code: {response.status_code}. Veuillez réessayer plus tard.</p>"
                    
                    # Sinon, attendre et réessayer
                    time.sleep(retry_delay)
                    attempts += 1
            
            except requests.exceptions.Timeout:
                print("Timeout lors de la requête à Gemini")
                if attempts == retry_count:
                    return "<h1>Erreur</h1><p>Erreur: Le serveur Gemini met trop de temps à répondre. Veuillez réessayer plus tard.</p>"
                time.sleep(retry_delay)
                attempts += 1
                
            except Exception as e:
                print(f"Exception lors de la requête à Gemini: {str(e)}")
                if attempts == retry_count:
                    return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte: {str(e)}</p>"
                time.sleep(retry_delay)
                attempts += 1

# Fonction pour obtenir le fournisseur d'IA approprié
def get_ai_provider(provider_name="localai"):
    """
    Retourne l'instance du fournisseur d'IA approprié.
    
    Args:
        provider_name (str): Le nom du fournisseur d'IA ('localai' ou 'gemini').
        
    Returns:
        AIProvider: Une instance du fournisseur d'IA.
    """
    if provider_name.lower() == "gemini":
        return GeminiProvider()
    else:
        return LocalAIProvider()
