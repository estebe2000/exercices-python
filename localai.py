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
from dotenv import load_dotenv
import os

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/localai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Charger les variables d'environnement
try:
    load_dotenv()
    logger.info("Variables d'environnement chargées avec succès")
except Exception as e:
    logger.error(f"Erreur lors du chargement des variables d'environnement: {str(e)}")
    raise

# Configuration de l'API LocalAI
LOCALAI_URL = os.getenv("LOCALAI_URL", "http://127.0.0.1:8080/v1/chat/completions")
MODEL = os.getenv("LOCALAI_MODEL", "codestral-latest")

if not LOCALAI_URL:
    raise ValueError("URL LocalAI non configurée. Veuillez définir LOCALAI_URL dans .env")

def check_localai_connection():
    """Vérifie que le serveur LocalAI est accessible"""
    try:
        response = requests.get(f"{LOCALAI_URL.replace('/v1/chat/completions', '')}/health", timeout=5)
        if response.status_code != 200:
            raise ConnectionError(f"Le serveur LocalAI répond mais avec un statut {response.status_code}")
    except Exception as e:
        raise ConnectionError(
            f"Impossible de se connecter au serveur LocalAI à {LOCALAI_URL}\n"
            "Veuillez vérifier que:\n"
            "1. Le serveur LocalAI est bien installé et démarré\n"
            "2. L'URL dans .env est correcte\n"
            "3. Le port n'est pas bloqué par un pare-feu\n"
            f"Erreur détaillée: {str(e)}"
        )

# Vérifier la connexion au démarrage
check_localai_connection()

from prompts import SYSTEM_MESSAGE, get_evaluation_prompt, DEFAULT_MAX_TOKENS, DEFAULT_TEMPERATURE, DEFAULT_RETRY_COUNT, DEFAULT_RETRY_DELAY



def generate_text(prompt: str, max_tokens: int = DEFAULT_MAX_TOKENS, 
                 temperature: float = DEFAULT_TEMPERATURE, 
                 retry_count: int = DEFAULT_RETRY_COUNT, 
                 retry_delay: int = DEFAULT_RETRY_DELAY) -> str:
    """
    Génère du texte en utilisant l'API LocalAI.
    
    Args:
        prompt: Le prompt à envoyer à l'API (doit contenir au moins 20 caractères)
        max_tokens: Nombre maximum de tokens à générer (entre 100 et 4000)
        temperature: Température pour la génération (entre 0.1 et 2.0)
        retry_count: Nombre de tentatives en cas d'échec (entre 0 et 5)
        retry_delay: Délai entre les tentatives en secondes (entre 1 et 10)
        
    Returns:
        str: Le texte généré par l'API au format HTML
        
    Raises:
        ValueError: Si les paramètres sont invalides
        requests.exceptions.RequestException: En cas d'échec de la requête API
    """
    # Validation des paramètres
    if not prompt or len(prompt.strip()) < 20:
        raise ValueError("Le prompt doit contenir au moins 20 caractères")
    if not 100 <= max_tokens <= 4000:
        raise ValueError("max_tokens doit être entre 100 et 4000")
    if not 0.1 <= temperature <= 2.0:
        raise ValueError("temperature doit être entre 0.1 et 2.0")
    if not 0 <= retry_count <= 5:
        raise ValueError("retry_count doit être entre 0 et 5")
    if not 1 <= retry_delay <= 10:
        raise ValueError("retry_delay doit être entre 1 et 10")
        
    logger.info(f"Début de génération avec max_tokens={max_tokens}, temperature={temperature}")
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
        max_tokens: Nombre maximum de tokens à générer (entre 100 et 4000)
        temperature: Température pour la génération (entre 0.1 et 2.0)
        
    Returns:
        str: L'évaluation du code au format HTML
        
    Raises:
        ValueError: Si les paramètres sont invalides
        requests.exceptions.RequestException: En cas d'échec de la requête API
    """
    logger.info(f"Début d'évaluation de code (longueur: {len(code)} caractères)")
    prompt = get_evaluation_prompt(code, enonce)
    return generate_text(prompt, max_tokens, temperature)
