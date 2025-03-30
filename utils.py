"""
Fonctions utilitaires pour l'application Flask.

Ce module contient diverses fonctions utilitaires utilisées dans l'application.
"""

import json
import sys
import traceback
from io import StringIO
from typing import Dict, Any
from functools import lru_cache
from datetime import datetime, timedelta

# Cache pour les données d'exercice (expire après 5 minutes)
@lru_cache(maxsize=1)
def _cached_load_exercise_data() -> Dict[str, Any]:
    """Version interne avec cache du chargement des données"""
    try:
        with open('exercices/data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # Utiliser print au lieu de app.logger car app n'est pas importé ici
        print(f"Erreur lors du chargement des données d'exercice: {str(e)}")
        return {}

def load_exercise_data() -> Dict[str, Any]:
    """
    Charge les données des exercices depuis le fichier JSON avec cache.
    
    Returns:
        Dictionnaire contenant les données des exercices
    """
    # Invalider le cache après 5 minutes
    if hasattr(load_exercise_data, '_last_load'):
        if datetime.now() - load_exercise_data._last_load > timedelta(minutes=5):
            _cached_load_exercise_data.cache_clear()
    
    load_exercise_data._last_load = datetime.now()
    return _cached_load_exercise_data()


def find_exercise_description(niveau: str, theme: str, difficulte: int) -> tuple:
    """
    Trouve la description d'un exercice dans les données et si c'est un exercice pour débutant.
    
    Args:
        niveau: Niveau scolaire (ex: "Première", "Terminale")
        theme: Thème de l'exercice
        difficulte: Niveau de difficulté
        
    Returns:
        Tuple (description, debutant) où description est la description de l'exercice
        et debutant est un booléen indiquant si l'exercice est pour débutant
    """
    exercise_data = load_exercise_data()
    
    for theme_data in exercise_data.get(niveau, []):
        if theme_data.get('thème') == theme:
            for niveau_data in theme_data.get('niveaux', []):
                if niveau_data.get('niveau') == difficulte:
                    return niveau_data.get('description', ''), niveau_data.get('debutant', False)
    
    return "", False


def safe_import(module_name):
    """
    Importe un module de manière sécurisée, en retournant None si le module n'est pas disponible.
    
    Args:
        module_name: Nom du module à importer
        
    Returns:
        Le module importé ou None si le module n'est pas disponible
    """
    try:
        return __import__(module_name)
    except ImportError:
        print(f"⚠️ Module {module_name} non disponible. Certaines fonctionnalités peuvent ne pas fonctionner.")
        return None


def try_evaluate_last_expression(code: str, local_vars: Dict[str, Any]) -> str:
    """
    Tente d'évaluer la dernière expression du code.
    
    Args:
        code: Code Python
        local_vars: Variables locales de l'environnement d'exécution
        
    Returns:
        Résultat de l'évaluation ou chaîne vide
    """
    # Extraire la dernière expression (si elle existe)
    lines = code.strip().split('\n')
    last_lines = []
    
    # Parcourir les lignes en partant de la fin
    for line in reversed(lines):
        line = line.strip()
        # Ignorer les lignes vides et les commentaires
        if not line or line.startswith('#'):
            continue
        # Ignorer les lignes qui définissent des fonctions ou des classes
        if line.startswith(('def ', 'class ')):
            break
        # Ignorer les lignes qui se terminent par ':' (début de bloc)
        if line.endswith(':'):
            break
        # Ignorer les lignes d'assignation (var = ...)
        if '=' in line and not line.strip().startswith(('if', 'while', 'for')):
            if '==' not in line:  # Ne pas confondre avec l'opérateur de comparaison
                continue
        
        # Ajouter la ligne à notre liste
        last_lines.insert(0, line)
        
        # Si on a une ligne qui n'est pas une continuation, on s'arrête
        if not line.endswith('\\'):
            break
    
    # Si on a trouvé une expression potentielle
    if last_lines:
        last_expr = '\n'.join(last_lines)
        try:
            # Essayer d'évaluer l'expression
            expr_result = eval(last_expr, globals(), local_vars)
            if expr_result is not None:
                return str(expr_result)
        except:
            # Si l'évaluation échoue, on ignore simplement
            pass
    
    return ""
