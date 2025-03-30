"""
Routes principales de l'application Flask.

Ce module contient les routes principales de l'application, comme la page d'accueil,
la page des exercices, le bac à sable, etc.
"""

from flask import render_template, request, jsonify, session, redirect, url_for
from ai_providers import get_ai_provider
from prompts import get_exercise_prompt
from utils import find_exercise_description, load_exercise_data
from code_execution import execute_python_code, AsyncCodeExecutor

# Constantes
VALID_PROVIDERS = ['localai', 'gemini', 'mistral']
DEFAULT_PROVIDER = 'localai'

# Initialiser le gestionnaire d'exécution
code_executor = AsyncCodeExecutor()

def init_routes(app):
    """
    Initialise les routes principales de l'application.
    
    Args:
        app: L'application Flask
    """
    
    @app.route('/')
    def index():
        """Route principale affichant la page d'accueil."""
        # Définir le fournisseur d'IA par défaut si ce n'est pas déjà fait
        if 'ai_provider' not in session:
            session['ai_provider'] = DEFAULT_PROVIDER
        
        return render_template('accueil.html', ai_provider=session['ai_provider'])

    @app.route('/exercices')
    def exercices():
        """Route affichant le générateur d'exercices."""
        # Définir le fournisseur d'IA par défaut si ce n'est pas déjà fait
        if 'ai_provider' not in session:
            session['ai_provider'] = DEFAULT_PROVIDER
        
        data = load_exercise_data()
        return render_template('index.html', data=data, ai_provider=session['ai_provider'])

    @app.route('/sandbox')
    def sandbox():
        """Route affichant le bac à sable Python."""
        # Définir le fournisseur d'IA par défaut si ce n'est pas déjà fait
        if 'ai_provider' not in session:
            session['ai_provider'] = DEFAULT_PROVIDER
        
        return render_template('sandbox.html', ai_provider=session['ai_provider'])


    @app.route('/config')
    def config():
        """Route pour la page de configuration."""
        return render_template('config.html', ai_provider=session.get('ai_provider', DEFAULT_PROVIDER))


    @app.route('/set-provider', methods=['POST'])
    def set_provider():
        """Route pour changer le fournisseur d'IA."""
        provider = request.form.get('provider', DEFAULT_PROVIDER)
        if provider in VALID_PROVIDERS:
            session['ai_provider'] = provider
        return jsonify({'success': True, 'provider': provider})


    @app.route('/generate-exercise', methods=['POST'])
    def generate_exercise():
        """Route pour générer un énoncé d'exercice."""
        data = request.json
        niveau = data.get('niveau')
        theme = data.get('theme')
        difficulte = data.get('difficulte')
        
        # Trouver la description correspondante et si c'est un exercice pour débutant
        description, debutant = find_exercise_description(niveau, theme, difficulte)
        
        # Obtenir le fournisseur d'IA approprié
        ai_provider = get_ai_provider(session.get('ai_provider', DEFAULT_PROVIDER))
        
        # Générer l'énoncé avec le fournisseur d'IA
        prompt = get_exercise_prompt(niveau, theme, difficulte, description, debutant)
        response = ai_provider.generate_text(prompt)
        
        # Stocker l'exercice généré dans la session pour le téléchargement ultérieur
        session['last_exercise'] = {
            'enonce': response,
            'description_originale': description,
            'provider': session.get('ai_provider', DEFAULT_PROVIDER),
            'debutant': debutant,
            'niveau': niveau,
            'theme': theme,
            'difficulte': difficulte
        }
        
        return jsonify({
            'enonce': response,
            'description_originale': description,
            'provider': session.get('ai_provider', DEFAULT_PROVIDER),
            'debutant': debutant
        })


    @app.route('/evaluate-code', methods=['POST'])
    def evaluate_code():
        """Route pour évaluer le code soumis."""
        data = request.json
        code = data.get('code')
        enonce = data.get('enonce')
        
        # Obtenir le fournisseur d'IA approprié
        ai_provider = get_ai_provider(session.get('ai_provider', DEFAULT_PROVIDER))
        
        # Évaluer le code avec le fournisseur d'IA
        response = ai_provider.evaluate_code(code, enonce)
        
        return jsonify({
            'evaluation': response,
            'provider': session.get('ai_provider', DEFAULT_PROVIDER)
        })


    @app.route('/execute-code', methods=['POST'])
    def execute_code():
        """Route pour exécuter le code Python (sans support de input())."""
        data = request.json
        code = data.get('code')
        
        result = execute_python_code(code)
        return jsonify(result)

    @app.route('/start-execution', methods=['POST'])
    def start_execution():
        """Route pour démarrer l'exécution asynchrone (avec support de input())."""
        data = request.json
        code = data.get('code')
        
        if not code:
            return jsonify({'error': 'Aucun code fourni'}), 400
        
        # Démarrer l'exécution
        execution_id = code_executor.start_execution(code)
        
        return jsonify({
            'execution_id': execution_id
        })

    @app.route('/execution-status/<execution_id>')
    def execution_status(execution_id):
        """Route pour vérifier l'état d'une exécution."""
        status = code_executor.get_execution_status(execution_id)
        
        if status is None:
            return jsonify({'error': 'Exécution non trouvée'}), 404
        
        return jsonify(status)

    @app.route('/provide-input/<execution_id>', methods=['POST'])
    def provide_input(execution_id):
        """Route pour fournir une entrée à une exécution en attente."""
        data = request.json
        input_value = data.get('input')
        
        if input_value is None:
            return jsonify({'error': 'Aucune entrée fournie'}), 400
        
        success = code_executor.provide_input(execution_id, input_value)
        
        if not success:
            return jsonify({'error': 'Impossible de fournir l\'entrée'}), 400
        
        return jsonify({'success': True})
