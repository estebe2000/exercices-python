"""
Routes pour le générateur de QCM.

Ce module contient les routes pour le générateur de QCM, permettant aux utilisateurs
de générer des questions à choix multiples pour différents niveaux scolaires.
"""

from flask import render_template, request, jsonify, session, redirect, url_for
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from qcm_generator import load_qcm_questions, add_questions_to_level, THEMES

# Constantes
VALID_LEVELS = ['Troisième', 'SNT', 'Prépa NSI', 'Première Générale', 'Terminale Générale']

def init_routes(app):
    """
    Initialise les routes pour le générateur de QCM.
    
    Args:
        app: L'application Flask
    """
    
    @app.route('/qcm-generator')
    def qcm_generator():
        """Route principale pour le générateur de QCM."""
        # Charger les statistiques des questions
        all_questions = load_qcm_questions()
        stats = {level: len(questions) for level, questions in all_questions.items()}
        
        return render_template(
            'qcm_generator.html',
            levels=VALID_LEVELS,
            stats=stats,
            result=session.pop('qcm_result', None)
        )
    
    @app.route('/generate-qcm', methods=['POST'])
    def generate_qcm():
        """Route pour générer des questions QCM."""
        level = request.form.get('level')
        count = int(request.form.get('count', 5))
        ai_provider = request.form.get('ai_provider', '')
        
        result = {}
        
        if level == 'all':
            # Générer des questions pour tous les niveaux
            for level in VALID_LEVELS:
                result[level] = add_questions_to_level(level, count, ai_provider if ai_provider else None)
        else:
            # Générer des questions pour un seul niveau
            result[level] = add_questions_to_level(level, count, ai_provider if ai_provider else None)
        
        # Stocker le résultat en session pour l'afficher sur la page
        session['qcm_result'] = result
        
        return redirect(url_for('qcm_generator'))
