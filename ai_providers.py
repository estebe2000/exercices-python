"""
Module de gestion des fournisseurs d'IA pour la génération de texte et l'évaluation de code.

Ce module définit les classes pour interagir avec différentes API d'IA (LocalAI, Gemini, Mistral)
et fournit une interface commune pour la génération de texte et l'évaluation de code.
"""

import requests
import json
import time
import logging
import mistral
from typing import Dict, Any, Optional, Union

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/ai_providers.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration des fournisseurs d'IA
class Config:
    """Configuration des différents fournisseurs d'IA."""
    
    # LocalAI
    LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"
    LOCALAI_MODEL = "mistral-7b-instruct-v0.3"
    
    # Gemini
    GEMINI_API_KEY = "AIzaSyDFjy8wVBrd4DUM3XjfbvTO4mRBSnTGCuw"
    GEMINI_MODEL = "gemini-2.0-flash"
    
    # Mistral
    MISTRAL_API_KEY = "DcCuwA1kbtGMShFRunnTJi6OtVgjQxGG"
    MISTRAL_URL = "https://codestral.mistral.ai/v1/chat/completions"
    MISTRAL_MODEL = "codestral-latest"
    
    # Paramètres communs
    DEFAULT_MAX_TOKENS = 1500
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_RETRY_COUNT = 2
    DEFAULT_RETRY_DELAY = 1
    
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

    @staticmethod
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


class APIError(Exception):
    """Exception levée en cas d'erreur lors de l'appel à une API."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)
    
    def __str__(self) -> str:
        result = self.message
        if self.status_code:
            result += f" (Code: {self.status_code})"
        if self.details:
            result += f" - {self.details}"
        return result
    
    def to_html(self) -> str:
        """Convertit l'erreur en HTML pour l'affichage."""
        return f"<h1>Erreur</h1><p>{self}</p>"


# Classe de base pour les fournisseurs d'IA
class AIProvider:
    """Classe de base pour tous les fournisseurs d'IA."""
    
    def generate_text(self, prompt: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE) -> str:
        """
        Méthode à implémenter par les classes enfants.
        
        Args:
            prompt: Le prompt à envoyer à l'API
            max_tokens: Nombre maximum de tokens à générer
            temperature: Température pour la génération
            
        Returns:
            Le texte généré par l'API
        """
        raise NotImplementedError("Cette méthode doit être implémentée par les classes enfants")
    
    def evaluate_code(self, code: str, enonce: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE) -> str:
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
        prompt = Config.get_evaluation_prompt(code, enonce)
        return self.generate_text(prompt, max_tokens, temperature)
    
    def _handle_api_error(self, e: Exception, provider_name: str, attempts: int, 
                         retry_count: int) -> Optional[str]:
        """
        Gère les erreurs d'API de manière uniforme.
        
        Args:
            e: L'exception levée
            provider_name: Nom du fournisseur d'IA
            attempts: Nombre de tentatives actuelles
            retry_count: Nombre maximum de tentatives
            
        Returns:
            Message d'erreur formaté en HTML si c'est la dernière tentative, None sinon
        """
        if isinstance(e, requests.exceptions.Timeout):
            logger.warning(f"Timeout lors de la requête à {provider_name}")
            if attempts == retry_count:
                return f"<h1>Erreur</h1><p>Erreur: Le serveur {provider_name} met trop de temps à répondre. Veuillez réessayer plus tard.</p>"
        elif isinstance(e, APIError):
            logger.error(f"Erreur API {provider_name}: {e}")
            if attempts == retry_count:
                return e.to_html()
        else:
            logger.error(f"Exception lors de la requête à {provider_name}: {str(e)}")
            if attempts == retry_count:
                return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte: {str(e)}</p>"
        
        return None


# Fournisseur LocalAI
class LocalAIProvider(AIProvider):
    """Fournisseur d'IA utilisant LocalAI."""
    
    def __init__(self, url: str = Config.LOCALAI_URL, model: str = Config.LOCALAI_MODEL):
        self.url = url
        self.model = model
    
    def generate_text(self, prompt: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE, 
                     retry_count: int = Config.DEFAULT_RETRY_COUNT, 
                     retry_delay: int = Config.DEFAULT_RETRY_DELAY) -> str:
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
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": Config.SYSTEM_MESSAGE},
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
                    logger.error(f"Erreur lors de la requête à LocalAI: {response.status_code}")
                    logger.error(f"Détails: {response.text}")
                    
                    # Si c'est la dernière tentative, lever une exception
                    if attempts == retry_count:
                        raise APIError(
                            "Erreur lors de la génération du texte", 
                            response.status_code, 
                            response.text
                        )
                    
                    # Sinon, attendre et réessayer
                    time.sleep(retry_delay)
                    attempts += 1
                    
            except Exception as e:
                error_message = self._handle_api_error(e, "LocalAI", attempts, retry_count)
                if error_message and attempts == retry_count:
                    return error_message
                
                time.sleep(retry_delay)
                attempts += 1


# Fournisseur Gemini
class GeminiProvider(AIProvider):
    """Fournisseur d'IA utilisant l'API Gemini de Google."""
    
    def __init__(self, api_key: str = Config.GEMINI_API_KEY, model: str = Config.GEMINI_MODEL):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    def generate_text(self, prompt: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE, 
                     retry_count: int = Config.DEFAULT_RETRY_COUNT, 
                     retry_delay: int = Config.DEFAULT_RETRY_DELAY) -> str:
        """
        Génère du texte en utilisant l'API Gemini.
        
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
        
        # Construire le prompt complet avec le message système
        full_prompt = f"{Config.SYSTEM_MESSAGE}\n\n{prompt}"
        
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
                    logger.error(f"Erreur lors de la requête à Gemini: {response.status_code}")
                    logger.error(f"Détails: {response.text}")
                    
                    # Si c'est la dernière tentative, lever une exception
                    if attempts == retry_count:
                        raise APIError(
                            "Erreur lors de la génération du texte", 
                            response.status_code, 
                            response.text
                        )
                    
                    # Sinon, attendre et réessayer
                    time.sleep(retry_delay)
                    attempts += 1
            
            except Exception as e:
                error_message = self._handle_api_error(e, "Gemini", attempts, retry_count)
                if error_message and attempts == retry_count:
                    return error_message
                
                time.sleep(retry_delay)
                attempts += 1


# Fournisseur Mistral
class MistralProvider(AIProvider):
    """Fournisseur d'IA utilisant l'API Mistral."""
    
    def __init__(self, api_key: str = Config.MISTRAL_API_KEY, 
                url: str = Config.MISTRAL_URL, 
                model: str = Config.MISTRAL_MODEL):
        self.api_key = api_key
        self.url = url
        self.model = model
    
    def generate_text(self, prompt: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE) -> str:
        """
        Génère du texte en utilisant l'API Mistral.
        
        Args:
            prompt: Le prompt à envoyer à l'API
            max_tokens: Nombre maximum de tokens à générer
            temperature: Température pour la génération
            
        Returns:
            Le texte généré par l'API
        """
        return mistral.generate_text(prompt, max_tokens, temperature)
    
    def evaluate_code(self, code: str, enonce: str, max_tokens: int = Config.DEFAULT_MAX_TOKENS, 
                     temperature: float = Config.DEFAULT_TEMPERATURE) -> str:
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
        return mistral.evaluate_code(code, enonce, max_tokens, temperature)


# Fonction pour obtenir le fournisseur d'IA approprié
def get_ai_provider(provider_name: str = "localai") -> AIProvider:
    """
    Retourne l'instance du fournisseur d'IA approprié.
    
    Args:
        provider_name: Le nom du fournisseur d'IA ('localai', 'gemini' ou 'mistral')
        
    Returns:
        Une instance du fournisseur d'IA
    """
    if provider_name.lower() == "gemini":
        return GeminiProvider()
    elif provider_name.lower() == "mistral":
        return MistralProvider()
    else:
        return LocalAIProvider()
