"""
Module pour la génération et la gestion des questions QCM.

Ce module contient les fonctions pour générer des questions QCM à partir de l'IA,
les sauvegarder dans un fichier JSON et les charger pour les utiliser dans l'application.
"""

import os
import json
import random
from ai_providers import get_ai_provider
from prompts import get_qcm_prompt

# Constantes
QCM_FILE_PATH = 'exercices/qcm_questions.json'
QCM_SETTINGS_PATH = 'exercices/qcm_settings.json'

def load_qcm_settings():
    """
    Charge la configuration des QCM depuis le fichier JSON.
    
    Returns:
        Un dictionnaire contenant la configuration ou None si le fichier n'existe pas
    """
    try:
        if os.path.exists(QCM_SETTINGS_PATH):
            with open(QCM_SETTINGS_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except json.JSONDecodeError:
        print(f"Erreur de décodage JSON dans {QCM_SETTINGS_PATH}")
    except Exception as e:
        print(f"Erreur lors du chargement des paramètres QCM: {e}")
    
    return None
THEMES = {
    'Troisième': ['Variables et types', 'Conditions', 'Boucles', 'Listes', 'Fonctions de base'],
    'SNT': ['Internet', 'Web', 'Réseaux sociaux', 'Données structurées', 'Informatique embarquée'],
    'Prépa NSI': ['Algorithmique', 'Programmation', 'Représentation des données', 'Architecture'],
    'Première Générale': ['Types de base', 'Types construits', 'Traitement de données', 'Interactions', 'Architectures matérielles', 'Langages et programmation', 'Algorithmique'],
    'Terminale Générale': ['Structures de données', 'Bases de données', 'Architectures matérielles', 'Langages et programmation', 'Algorithmique avancée', 'Programmation orientée objet']
}

def load_qcm_questions():
    """
    Charge les questions QCM depuis les fichiers JSON par niveau.
    
    Returns:
        Un dictionnaire contenant les questions par niveau
    """
    questions = {level: [] for level in THEMES.keys()}
    
    for level in THEMES.keys():
        level_file = f"exercices/{level}.json"
        
        # Si le fichier spécifique au niveau n'existe pas, utiliser autre.json
        if not os.path.exists(level_file):
            level_file = "exercices/autre.json"
            
        if os.path.exists(level_file):
            try:
                with open(level_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Gérer soit un tableau direct soit un objet avec sous-tableaux
                    if isinstance(data, list):  
                        level_questions = data
                    elif isinstance(data, dict):
                        # Prendre le premier tableau trouvé dans le dictionnaire
                        for key in data:
                            if isinstance(data[key], list):
                                level_questions = data[key]
                                break
                        else:
                            level_questions = []
                    else:
                        level_questions = []
                        
                    questions[level] = level_questions
            except json.JSONDecodeError:
                print(f"Erreur de décodage JSON dans {level_file}")
    
    return questions

def save_qcm_questions(questions):
    """
    Sauvegarde les questions QCM dans les fichiers JSON par niveau.
    
    Args:
        questions: Un dictionnaire contenant les questions par niveau
    """
    for level, level_questions in questions.items():
        level_file = f"exercices/{level}.json"
        
        # Si le niveau est valide et il y a des questions à sauvegarder
        if level in THEMES and level_questions:
            try:
                # Créer le répertoire si nécessaire
                os.makedirs(os.path.dirname(level_file), exist_ok=True)
                
                with open(level_file, 'w', encoding='utf-8') as f:
                    json.dump(level_questions, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"Erreur lors de la sauvegarde des questions pour {level}: {e}")

def add_questions_to_level(level, count=3, ai_provider_name=None):
    """
    Ajoute des questions QCM pour un niveau donné.
    
    Args:
        level: Le niveau scolaire
        count: Le nombre de questions à générer par thème
        ai_provider_name: Le nom du fournisseur d'IA à utiliser
    
    Returns:
        Le nombre de questions ajoutées
    """
    if level not in THEMES:
        return 0
    
    # Charger les questions existantes
    all_questions = load_qcm_questions()
    
    # Initialiser le niveau s'il n'existe pas
    if level not in all_questions:
        all_questions[level] = []
    
    # Sélectionner un thème aléatoire pour ce niveau
    theme = random.choice(THEMES[level])
    
    # Obtenir le fournisseur d'IA
    ai_provider = get_ai_provider(ai_provider_name)
    
    # Générer le prompt pour l'IA
    prompt = get_qcm_prompt(level, theme)
    
    # Générer les questions avec l'IA
    response = ai_provider.generate_text(prompt)
    
    # Extraire les questions du format JSON
    try:
        # Trouver le début et la fin du JSON dans la réponse
        start_idx = response.find('[')
        end_idx = response.rfind(']') + 1
        
        if start_idx >= 0 and end_idx > start_idx:
            json_str = response[start_idx:end_idx]
            new_questions = json.loads(json_str)
            
            # Ajouter les questions au niveau
            all_questions[level].extend(new_questions)
            
            # Sauvegarder les questions
            save_qcm_questions(all_questions)
            
            return len(new_questions)
        else:
            print(f"Format JSON non trouvé dans la réponse pour le niveau {level}")
            return 0
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON pour le niveau {level}: {e}")
        print(f"Réponse: {response}")
        return 0
    except Exception as e:
        print(f"Erreur lors de l'ajout de questions pour le niveau {level}: {e}")
        return 0

def get_random_questions(level, count=10):
    """
    Récupère des questions aléatoires pour un niveau donné.
    
    Args:
        level: Le niveau scolaire
        count: Le nombre de questions à récupérer
    
    Returns:
        Une liste de questions
    """
    all_questions = load_qcm_questions()
    
    if level not in all_questions or not all_questions[level]:
        return []
    
    # Sélectionner des questions aléatoires
    questions = all_questions[level]
    selected = random.sample(questions, min(count, len(questions)))
    
    return selected

def clear_questions(level=None):
    """
    Supprime toutes les questions pour un niveau donné ou pour tous les niveaux.
    
    Args:
        level: Le niveau scolaire (None pour tous les niveaux)
    """
    all_questions = load_qcm_questions()
    
    if level is None:
        # Réinitialiser tous les niveaux
        all_questions = {level: [] for level in THEMES.keys()}
    elif level in all_questions:
        # Réinitialiser un niveau spécifique
        all_questions[level] = []
    
    save_qcm_questions(all_questions)
