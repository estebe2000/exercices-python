"""
Routes pour l'éditeur de data.json.

Ce module contient les routes pour l'éditeur de data.json, qui permet de gérer
les données des exercices.
"""

import json
from flask import render_template, request, jsonify
from utils import _cached_load_exercise_data

def init_routes(app):
    """
    Initialise les routes pour l'éditeur de data.json.
    
    Args:
        app: L'application Flask
    """
    
    @app.route('/data-editor')
    def data_editor():
        """Route pour afficher l'éditeur de data.json."""
        try:
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            return render_template('data_editor.html', data=data)
        except Exception as e:
            return render_template('data_editor.html', error=str(e), data={})

    @app.route('/data-editor/save', methods=['POST'])
    def save_data():
        """Route pour sauvegarder les modifications de data.json."""
        try:
            data = request.json
            
            # Valider que les données sont correctes
            if not isinstance(data, dict):
                return jsonify({'error': 'Format de données invalide'}), 400
            
            # Sauvegarder les données
            with open('exercices/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Invalider le cache après modification
            _cached_load_exercise_data.cache_clear()
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/data-editor/add-niveau', methods=['POST'])
    def add_niveau():
        """Route pour ajouter un niveau scolaire."""
        try:
            niveau = request.json.get('niveau')
            
            if not niveau or not isinstance(niveau, str):
                return jsonify({'error': 'Niveau invalide'}), 400
            
            # Charger les données existantes
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier si le niveau existe déjà
            if niveau in data:
                return jsonify({'error': 'Ce niveau existe déjà'}), 400
            
            # Ajouter le nouveau niveau
            data[niveau] = []
            
            # Sauvegarder les données
            with open('exercices/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/data-editor/add-theme', methods=['POST'])
    def add_theme():
        """Route pour ajouter un thème à un niveau scolaire."""
        try:
            niveau = request.json.get('niveau')
            theme = request.json.get('theme')
            
            if not niveau or not theme or not isinstance(niveau, str) or not isinstance(theme, str):
                return jsonify({'error': 'Données invalides'}), 400
            
            # Charger les données existantes
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier si le niveau existe
            if niveau not in data:
                return jsonify({'error': 'Ce niveau n\'existe pas'}), 400
            
            # Vérifier si le thème existe déjà
            for t in data[niveau]:
                if t.get('thème') == theme:
                    return jsonify({'error': 'Ce thème existe déjà pour ce niveau'}), 400
            
            # Ajouter le nouveau thème
            data[niveau].append({
                'thème': theme,
                'niveaux': []
            })
            
            # Sauvegarder les données
            with open('exercices/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/data-editor/add-exercice', methods=['POST'])
    def add_exercice():
        """Route pour ajouter un exercice à un thème."""
        try:
            niveau_scolaire = request.json.get('niveau_scolaire')
            theme = request.json.get('theme')
            niveau_difficulte = request.json.get('niveau_difficulte')
            description = request.json.get('description')
            debutant = request.json.get('debutant', False)  # Par défaut, non débutant
            
            if (not niveau_scolaire or not theme or not description or 
                not isinstance(niveau_scolaire, str) or not isinstance(theme, str) or 
                not isinstance(description, str)):
                return jsonify({'error': 'Données invalides'}), 400
            
            try:
                niveau_difficulte = int(niveau_difficulte)
            except:
                return jsonify({'error': 'Le niveau de difficulté doit être un nombre'}), 400
            
            # Charger les données existantes
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier si le niveau scolaire existe
            if niveau_scolaire not in data:
                return jsonify({'error': 'Ce niveau scolaire n\'existe pas'}), 400
            
            # Trouver le thème
            theme_found = False
            for t in data[niveau_scolaire]:
                if t.get('thème') == theme:
                    theme_found = True
                    
                    # Vérifier si le niveau de difficulté existe déjà
                    for n in t.get('niveaux', []):
                        if n.get('niveau') == niveau_difficulte:
                            return jsonify({'error': 'Ce niveau de difficulté existe déjà pour ce thème'}), 400
                    
                    # Ajouter le nouvel exercice
                    t['niveaux'].append({
                        'niveau': niveau_difficulte,
                        'description': description,
                        'debutant': debutant  # Ajouter le paramètre débutant
                    })
                    
                    # Trier les niveaux par ordre croissant
                    t['niveaux'] = sorted(t['niveaux'], key=lambda x: x.get('niveau', 0))
                    break
            
            if not theme_found:
                return jsonify({'error': 'Ce thème n\'existe pas pour ce niveau scolaire'}), 400
            
            # Sauvegarder les données
            with open('exercices/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/data-editor/get-exercice-info')
    def get_exercice_info():
        """Route pour récupérer les informations d'un exercice."""
        try:
            niveau = request.args.get('niveau')
            theme = request.args.get('theme')
            niveau_difficulte = request.args.get('niveau_difficulte')
            
            if not niveau or not theme or not niveau_difficulte:
                return jsonify({'success': False, 'error': 'Paramètres manquants'}), 400
            
            try:
                niveau_difficulte = int(niveau_difficulte)
            except:
                return jsonify({'success': False, 'error': 'Le niveau de difficulté doit être un nombre'}), 400
            
            # Charger les données existantes
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Chercher l'exercice
            for t in data.get(niveau, []):
                if t.get('thème') == theme:
                    for n in t.get('niveaux', []):
                        if n.get('niveau') == niveau_difficulte:
                            return jsonify({
                                'success': True,
                                'description': n.get('description', ''),
                                'debutant': n.get('debutant', False)
                            })
            
            return jsonify({'success': False, 'error': 'Exercice non trouvé'}), 404
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500

    @app.route('/data-editor/update-exercice', methods=['POST'])
    def update_exercice():
        """Route pour mettre à jour un exercice existant."""
        try:
            niveau_scolaire = request.json.get('niveau_scolaire')
            theme = request.json.get('theme')
            niveau_difficulte = request.json.get('niveau_difficulte')
            description = request.json.get('description')
            debutant = request.json.get('debutant')  # Peut être None si non fourni
            
            if (not niveau_scolaire or not theme or not description or 
                not isinstance(niveau_scolaire, str) or not isinstance(theme, str) or 
                not isinstance(description, str)):
                return jsonify({'error': 'Données invalides'}), 400
            
            try:
                niveau_difficulte = int(niveau_difficulte)
            except:
                return jsonify({'error': 'Le niveau de difficulté doit être un nombre'}), 400
            
            # Charger les données existantes
            with open('exercices/data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Vérifier si le niveau scolaire existe
            if niveau_scolaire not in data:
                return jsonify({'error': 'Ce niveau scolaire n\'existe pas'}), 400
            
            # Trouver le thème et mettre à jour l'exercice
            theme_found = False
            exercice_found = False
            
            for t in data[niveau_scolaire]:
                if t.get('thème') == theme:
                    theme_found = True
                    
                    # Trouver l'exercice par son niveau de difficulté
                    for i, n in enumerate(t.get('niveaux', [])):
                        if n.get('niveau') == niveau_difficulte:
                            exercice_found = True
                            # Mettre à jour la description
                            t['niveaux'][i]['description'] = description
                            # Mettre à jour le paramètre débutant si fourni
                            if debutant is not None:
                                t['niveaux'][i]['debutant'] = debutant
                            break
                    
                    break
            
            if not theme_found:
                return jsonify({'error': 'Ce thème n\'existe pas pour ce niveau scolaire'}), 400
            
            if not exercice_found:
                return jsonify({'error': 'Cet exercice n\'existe pas pour ce thème'}), 400
            
            # Sauvegarder les données
            with open('exercices/data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
