"""
Module pour interagir avec l'API Mistral (Codestral).

Ce module fournit des fonctions pour générer du texte et évaluer du code
en utilisant l'API Mistral Codestral.
"""

import requests
import json
import time
import logging
from typing import Dict, Any, Optional

# Configuration du logging
logger = logging.getLogger(__name__)

# Configuration de l'API Mistral
from dotenv import load_dotenv
import os

load_dotenv()  # Charge les variables d'environnement depuis .env

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("La clé API Mistral n'est pas configurée. Veuillez définir MISTRAL_API_KEY dans .env")

MISTRAL_URL = "https://codestral.mistral.ai/v1/chat/completions"
MISTRAL_MODEL = "codestral-latest"

from prompts import SYSTEM_MESSAGE, get_evaluation_prompt, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, DEFAULT_RETRY_COUNT, DEFAULT_RETRY_DELAY


def generate_text(prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                 temperature: float = DEFAULT_TEMPERATURE, 
                 retry_count: int = DEFAULT_RETRY_COUNT, 
                 retry_delay: int = DEFAULT_RETRY_DELAY) -> str:
    """
    Génère du texte en utilisant l'API Mistral (Codestral).
    
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
                "model": MISTRAL_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            # En-têtes pour l'authentification
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {MISTRAL_API_KEY}"
            }
            
            # Envoyer la requête à l'API
            response = requests.post(MISTRAL_URL, headers=headers, json=data, timeout=60)
            
            # Vérifier si la requête a réussi
            if response.status_code == 200:
                result = response.json()
                # Extraire le texte généré
                generated_text = result["choices"][0]["message"]["content"]
                return generated_text
            else:
                logger.error(f"Erreur lors de la requête à Mistral: {response.status_code}")
                logger.error(f"Détails: {response.text}")
                
                # Si c'est la dernière tentative, retourner un message d'erreur
                if attempts == retry_count:
                    return f"<h1>Erreur</h1><p>Erreur lors de la génération du texte. Code: {response.status_code}. Veuillez réessayer plus tard.</p>"
                
                # Sinon, attendre et réessayer
                time.sleep(retry_delay)
                attempts += 1
                
        except requests.exceptions.Timeout:
            logger.warning("Timeout lors de la requête à Mistral")
            if attempts == retry_count:
                return "<h1>Erreur</h1><p>Erreur: Le serveur Mistral met trop de temps à répondre. Veuillez réessayer plus tard.</p>"
            time.sleep(retry_delay)
            attempts += 1
            
        except Exception as e:
            logger.error(f"Exception lors de la requête à Mistral: {str(e)}")
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
