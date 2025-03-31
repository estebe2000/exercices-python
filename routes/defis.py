"""
Routes pour le mode Défis de l'application.

Ce module contient les routes pour le mode Défis, permettant aux utilisateurs
de tester leurs compétences en programmation Python avec des QCM et des exercices pratiques.
"""

import os
import random
import time
import json
from flask import render_template, request, jsonify, session, redirect, url_for
from utils import load_exercise_data
from ai_providers import get_ai_provider
from prompts import get_exercise_prompt
from code_execution import execute_python_code
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qcm_generator import load_qcm_questions, add_questions_to_level, THEMES, QCM_FILE_PATH, load_qcm_settings

# Constantes
VALID_LEVELS = ['Troisième', 'SNT', 'Prépa NSI', 'Première Générale', 'Terminale Générale']

# Charger la configuration des QCM
qcm_settings = load_qcm_settings()
print(f"Chargement des paramètres QCM depuis qcm_generator.load_qcm_settings(): {qcm_settings}")  # Debug
if not qcm_settings:
    print("Utilisation des valeurs par défaut pour les QCM")
    qcm_settings = {
        "questions_par_niveau": {
            'Troisième': 10,
            'SNT': 10,
            'Prépa NSI': 10,
            'Première Générale': 6,
            'Terminale Générale': 6
        }
    }
QCM_COUNT_BY_LEVEL = qcm_settings['questions_par_niveau']
QCM_COUNT = 10  # Valeur par défaut
EXERCISE_WEIGHT = 0.25  # 25% du score total
QCM_WEIGHT = 0.75  # 75% du score total
CHALLENGE_TIME = 300  # 5 minutes en secondes

def init_routes(app):
    """
    Initialise les routes pour le mode Défis.
    
    Args:
        app: L'application Flask
    """
    
    @app.route('/defis')
    def defis():
        """Route principale pour le mode Défis."""
        # Réinitialiser les données de défi en session
        if 'defis_data' in session:
            del session['defis_data']
        
        return render_template('defis.html', levels=VALID_LEVELS)
    
    @app.route('/defis/start', methods=['POST'])
    def start_defis():
        """Route pour démarrer un défi."""
        level = request.form.get('level')
        
        if level == 'all':
            # Sélectionner un niveau aléatoire
            level = random.choice(VALID_LEVELS)
        elif level not in VALID_LEVELS:
            return jsonify({'error': 'Niveau invalide'}), 400
        
        # Générer le défi
        defis_data = generate_challenge(level)
        
        # Stocker les données du défi en session
        session['defis_data'] = defis_data
        session['defis_start_time'] = time.time()
        
        return redirect(url_for('challenge_page'))
    
    @app.route('/defis/challenge')
    def challenge_page():
        """Route pour afficher la page du défi en cours."""
        # Vérifier si un défi est en cours
        if 'defis_data' not in session:
            return redirect(url_for('defis'))
        
        defis_data = session['defis_data']
        start_time = session.get('defis_start_time', time.time())
        elapsed_time = time.time() - start_time
        remaining_time = max(0, CHALLENGE_TIME - elapsed_time)
        
        return render_template(
            'defis_challenge.html',
            defis_data=defis_data,
            remaining_time=remaining_time
        )
    
    @app.route('/defis/submit', methods=['POST'])
    def submit_defis():
        """Route pour soumettre les réponses d'un défi."""
        # Vérifier si un défi est en cours
        if 'defis_data' not in session:
            return redirect(url_for('defis'))
        
        defis_data = session['defis_data']
        
        # Récupérer les réponses aux QCM
        qcm_answers = {}
        for i in range(len(defis_data['qcm_questions'])):
            answer_key = f'q{i}'
            qcm_answers[answer_key] = request.form.get(answer_key)
        
        # Récupérer le code de l'exercice
        exercise_code = request.form.get('exercise_code', '')
        
        # Calculer le score
        score, details = calculate_score(defis_data, qcm_answers, exercise_code)
        
        # Stocker le résultat en session
        session['defis_result'] = {
            'score': score,
            'details': details,
            'level': defis_data['level']
        }
        
        # Supprimer les données du défi
        del session['defis_data']
        if 'defis_start_time' in session:
            del session['defis_start_time']
        
        return redirect(url_for('defis_result'))
    
    @app.route('/defis/result')
    def defis_result():
        """Route pour afficher le résultat d'un défi."""
        # Vérifier si un résultat est disponible
        if 'defis_result' not in session:
            return redirect(url_for('defis'))
        
        result = session['defis_result']
        
        return render_template('defis_result.html', result=result)
    

def generate_challenge(level):
    """
    Génère un défi complet (QCM + exercice) pour un niveau donné.
    Rafraîchit la configuration des QCM à chaque appel.
    
    Args:
        level: Le niveau scolaire
    
    Returns:
        Un dictionnaire contenant les données du défi
    """
    global QCM_COUNT_BY_LEVEL
    # Recharger la configuration à chaque génération de défi
    qcm_settings = load_qcm_settings()
    if qcm_settings:
        QCM_COUNT_BY_LEVEL = qcm_settings['questions_par_niveau']
    # Charger les données des exercices
    data = load_exercise_data()
    
    # Déterminer le nombre de questions QCM pour ce niveau
    qcm_count = QCM_COUNT_BY_LEVEL.get(level, QCM_COUNT)
    
    # Générer les questions QCM
    qcm_questions = generate_qcm_questions(level, data, qcm_count)
    
    # Si aucune question QCM n'est disponible, créer une liste vide
    if qcm_questions is None:
        qcm_questions = []
    
    # Sélectionner un exercice pratique
    exercise = select_exercise(level, data)
    
    return {
        'level': level,
        'qcm_questions': qcm_questions,
        'exercise': exercise,
        'time_limit': CHALLENGE_TIME
    }

def generate_qcm_questions(level, data, count):
    """
    Génère des questions QCM pour un niveau donné en utilisant la configuration.
    
    Args:
        level: Le niveau scolaire
        data: Les données des exercices
        count: Le nombre de questions à générer (peut être spécifié ou utiliser la valeur par défaut)
    
    Returns:
        Une liste de questions QCM (peut être vide)
    """
    global QCM_COUNT_BY_LEVEL
    questions = []
    
    try:
        # Charger les questions depuis les fichiers par niveau
        all_questions = load_qcm_questions()
        
        if not all_questions:
            print("Avertissement: Aucune question trouvée dans les fichiers QCM")
            return questions
        
        # Vérifier si le niveau existe et contient des questions
        if level not in all_questions or not all_questions[level]:
            print(f"Avertissement: Aucune question trouvée pour le niveau {level}")
            return questions
        
        # Sélectionner des questions aléatoires pour ce niveau
        level_questions = all_questions[level]
        
        # Limiter le nombre de questions si nécessaire
        selected_questions = random.sample(level_questions, min(count, len(level_questions)))
        
        # Formater les questions pour l'affichage
        for q in selected_questions:
            options = q['options']
            correct = q['correct']
            
            # Créer une copie pour éviter de modifier l'original
            question = {
                'question': q['question'],
                'options': options.copy(),
                'correct': correct,
                'explanation': q['explanation']
            }
            
            # Mélanger les options
            random.shuffle(question['options'])
            
            # Mettre à jour l'index de la bonne réponse
            question['correct_index'] = question['options'].index(correct)
            
            questions.append(question)
    
    except Exception as e:
        print(f"Erreur lors de la génération des questions QCM: {str(e)}")
    
    return questions

def select_exercise(level, data):
    """
    Sélectionne un exercice aléatoire pour un niveau donné.
    
    Args:
        level: Le niveau scolaire
        data: Les données des exercices
    
    Returns:
        Un dictionnaire contenant les informations de l'exercice
    """
    # Récupérer les thèmes et descriptions pour le niveau
    level_data = data.get(level, [])
    
    if not level_data:
        # Créer un exercice par défaut si aucune donnée n'est disponible
        return {
            'theme': 'Algorithmes de base',
            'description': 'Écrire un programme qui calcule la somme des entiers de 1 à n',
            'niveau': 2,
            'debutant': level in ['Troisième', 'SNT', 'Prépa NSI']
        }
    
    # Sélectionner un thème aléatoire
    theme_data = random.choice(level_data)
    theme = theme_data.get('thème', '')
    
    # Sélectionner un niveau aléatoire
    niveau_data = random.choice(theme_data.get('niveaux', []))
    description = niveau_data.get('description', '')
    niveau = niveau_data.get('niveau', 1)
    debutant = niveau_data.get('debutant', False)
    
    return {
        'theme': theme,
        'description': description,
        'niveau': niveau,
        'debutant': debutant
    }

def calculate_score(defis_data, qcm_answers, exercise_code):
    """
    Calcule le score d'un défi.
    
    Args:
        defis_data: Les données du défi
        qcm_answers: Les réponses aux QCM
        exercise_code: Le code de l'exercice
    
    Returns:
        Un tuple (score, details) où score est un pourcentage et details est un dictionnaire
        contenant les détails du calcul
    """
    # Calculer le score des QCM
    qcm_score = 0
    qcm_details = []
    
    for i, question in enumerate(defis_data['qcm_questions']):
        answer_key = f'q{i}'
        user_answer = qcm_answers.get(answer_key)
        
        if user_answer is not None:
            correct_option = question['options'][question['correct_index']]
            is_correct = (user_answer == correct_option)
            
            if is_correct:
                qcm_score += 1
            
            qcm_details.append({
                'question': question['question'],
                'user_answer': user_answer,
                'correct_answer': correct_option,
                'is_correct': is_correct,
                'explanation': question['explanation']
            })
    
    # Normaliser le score des QCM (sur 100)
    normalized_qcm_score = (qcm_score / len(defis_data['qcm_questions'])) * 100 if defis_data['qcm_questions'] else 0
    
    # Évaluer l'exercice pratique
    exercise_score = evaluate_exercise(defis_data['exercise'], exercise_code)
    
    # Calculer le score final
    final_score = (normalized_qcm_score * QCM_WEIGHT) + (exercise_score * EXERCISE_WEIGHT)
    
    return final_score, {
        'qcm_score': qcm_score,
        'qcm_total': len(defis_data['qcm_questions']),
        'qcm_percentage': normalized_qcm_score,
        'exercise_score': exercise_score,
        'qcm_details': qcm_details,
        'qcm_weight': QCM_WEIGHT * 100,
        'exercise_weight': EXERCISE_WEIGHT * 100
    }

def evaluate_exercise(exercise, code):
    """
    Évalue le code soumis pour un exercice.
    
    Args:
        exercise: Les informations de l'exercice
        code: Le code soumis
    
    Returns:
        Un score entre 0 et 100
    """
    # Pour l'instant, une évaluation simple basée sur la longueur du code
    if not code.strip():
        return 0
    
    # Exécuter le code pour vérifier s'il fonctionne
    result = execute_python_code(code)
    
    if result.get('error'):
        # Le code contient des erreurs
        return 25  # Score partiel pour avoir essayé
    
    # Analyse basique du code
    score = 50  # Score de base pour un code qui s'exécute sans erreur
    
    # Vérifier si le code contient des éléments attendus selon le niveau
    if exercise['niveau'] >= 3:
        # Pour les niveaux plus élevés, vérifier l'utilisation de fonctions
        if 'def ' in code:
            score += 20
    
    if exercise['niveau'] >= 4:
        # Pour les niveaux encore plus élevés, vérifier l'utilisation de structures de données
        if any(keyword in code for keyword in ['list', 'dict', 'set', 'tuple']):
            score += 15
    
    # Vérifier la présence de commentaires
    if '#' in code:
        score += 10
    
    # Limiter le score à 100
    return min(score, 100)
