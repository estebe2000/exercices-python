"""
Module de gestion des fournisseurs d'IA pour la génération de texte et l'évaluation de code.

Ce module définit les classes pour interagir avec différentes API d'IA (LocalAI, Gemini, Mistral)
et fournit une interface commune pour la génération de texte et l'évaluation de code.
"""

import os
from dotenv import load_dotenv
import requests
import json
import time
import logging
import mistral
from typing import Dict, Any, Optional, Union

load_dotenv()  # Charge les variables d'environnement depuis .env

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

from prompts import SYSTEM_MESSAGE, get_evaluation_prompt, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, DEFAULT_RETRY_COUNT, DEFAULT_RETRY_DELAY

# Configuration des fournisseurs d'IA
class Config:
    """Configuration des différents fournisseurs d'IA."""
    
    # LocalAI
    LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"
    LOCALAI_MODEL = "mistral-7b-instruct-v0.3"
    
    # Gemini
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("La clé API Gemini n'est pas configurée. Veuillez définir GEMINI_API_KEY dans .env")
    GEMINI_MODEL = "gemini-2.0-flash"
    
    # Mistral
    MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
    if not MISTRAL_API_KEY:
        raise ValueError("La clé API Mistral n'est pas configurée. Veuillez définir MISTRAL_API_KEY dans .env")
    MISTRAL_URL = "https://codestral.mistral.ai/v1/chat/completions"
    MISTRAL_MODEL = "codestral-latest"


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
    
    def generate_text(self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                     temperature: float = DEFAULT_TEMPERATURE) -> str:
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
    
    def evaluate_code(self, code: str, enonce: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
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
    
    def generate_text(self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
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
    
    def generate_text(self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                     temperature: float = DEFAULT_TEMPERATURE, 
                     retry_count: int = DEFAULT_RETRY_COUNT, 
                     retry_delay: int = DEFAULT_RETRY_DELAY) -> str:
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
    
    def generate_text(self, prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                     temperature: float = DEFAULT_TEMPERATURE) -> str:
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
    
    def evaluate_code(self, code: str, enonce: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
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
