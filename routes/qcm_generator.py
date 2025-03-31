"""
Routes pour la génération et gestion des QCM.
"""

import os
import json
from flask import render_template, request, jsonify
from qcm_generator import load_qcm_questions, save_qcm_questions, THEMES

def init_routes(app):
    """
    Initialise les routes pour le générateur de QCM.
    """
    
    @app.route('/qcm-generator')
    def qcm_generator():
        """Route pour afficher la page de gestion des QCM"""
        # Charger les paramètres
        settings_path = os.path.join('exercices', 'qcm_settings.json')
        if os.path.exists(settings_path):
            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            # Valeurs par défaut si le fichier n'existe pas
            settings = {
                "questions_par_niveau": {
                    "Troisième": 10,
                    "SNT": 10,
                    "Prépa NSI": 10,
                    "Première Générale": 6,
                    "Terminale Générale": 6
                }
            }
        
        return render_template('qcm_generator.html', settings=settings)
    
    @app.route('/update-qcm-settings', methods=['POST'])
    def update_qcm_settings():
        """Route pour mettre à jour les paramètres des QCM"""
        try:
            data = request.json
            
            # Valider et convertir les valeurs
            settings = {
                "questions_par_niveau": {
                    level: int(data.get(level, 10))
                    for level in THEMES.keys()
                }
            }
            
            # Sauvegarder dans le fichier
            settings_path = os.path.join('exercices', 'qcm_settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2)
            
            return jsonify({"success": True})
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400


def load_qcm_settings():
    """Charge la configuration des QCM"""
    settings_path = os.path.join('exercices', 'qcm_settings.json')
    if os.path.exists(settings_path):
        with open(settings_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None
