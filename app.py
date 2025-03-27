import json
import os
from flask import Flask, render_template, request, jsonify, session
from ai_providers import get_ai_provider

app = Flask(__name__)
app.secret_key = 'exercices_python_secret_key'  # Nécessaire pour utiliser les sessions

# Charger les données des exercices
def load_exercise_data():
    with open('exercices/data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Route principale
@app.route('/')
def index():
    # Définir le fournisseur d'IA par défaut si ce n'est pas déjà fait
    if 'ai_provider' not in session:
        session['ai_provider'] = 'localai'
    
    data = load_exercise_data()
    return render_template('index.html', data=data, ai_provider=session['ai_provider'])

# Route pour la page de configuration
@app.route('/config')
def config():
    return render_template('config.html', ai_provider=session.get('ai_provider', 'localai'))

# Route pour changer le fournisseur d'IA
@app.route('/set-provider', methods=['POST'])
def set_provider():
    provider = request.form.get('provider', 'localai')
    if provider in ['localai', 'gemini']:
        session['ai_provider'] = provider
    return jsonify({'success': True, 'provider': provider})

# Route pour générer un énoncé d'exercice
@app.route('/generate-exercise', methods=['POST'])
def generate_exercise():
    data = request.json
    niveau = data.get('niveau')
    theme = data.get('theme')
    difficulte = data.get('difficulte')
    
    # Charger les données pour obtenir la description de l'exercice
    exercise_data = load_exercise_data()
    description = ""
    
    # Trouver la description correspondante
    for theme_data in exercise_data.get(niveau, []):
        if theme_data.get('thème') == theme:
            for niveau_data in theme_data.get('niveaux', []):
                if niveau_data.get('niveau') == difficulte:
                    description = niveau_data.get('description', '')
                    break
            break
    
    # Obtenir le fournisseur d'IA approprié
    ai_provider = get_ai_provider(session.get('ai_provider', 'localai'))
    
    # Générer l'énoncé avec le fournisseur d'IA
    prompt = f"""
    Génère un énoncé d'exercice Python pour un élève de {niveau} avec les caractéristiques suivantes:
    - Thème: {theme}
    - Niveau de difficulté: {difficulte}
    - Description: {description}
    
    IMPORTANT: Ton énoncé doit être formaté en HTML pur pour un affichage correct dans un navigateur.
    
    L'énoncé doit inclure:
    1. Un titre principal avec <h1>Titre de l'exercice</h1>
    2. Une description détaillée du problème avec des sous-titres <h2>Section</h2>
    3. Des exemples d'entrées/sorties si nécessaire
    4. Des contraintes ou indications si nécessaire
    
    IMPORTANT: Inclus également:
    5. Un squelette de code à trous que l'élève devra compléter. Utilise des commentaires comme "# À COMPLÉTER" ou "# VOTRE CODE ICI" pour indiquer les parties à remplir.
    6. Des jeux de tests avec des messages de réussite ou d'échec.
    
    Exemple de format pour le code et les tests:
    
    <pre><code class="language-python">
    def fonction(a, b):
        # À COMPLÉTER
        pass
        
    # Tests
    try:
        assert fonction(1, 2) == 3
        print("✅ Test 1 réussi: fonction(1, 2) == 3")
    except AssertionError:
        print("❌ Test 1 échoué: fonction(1, 2) devrait retourner 3")
    </code></pre>
    
    Utilise uniquement des balises HTML standard pour le formatage:
    - <h1>, <h2>, <h3> pour les titres
    - <p> pour les paragraphes
    - <ul> et <li> pour les listes
    - <pre><code class="language-python">...</code></pre> pour les blocs de code
    - <strong> pour le texte en gras
    - <em> pour le texte en italique
    - <span class="text-success">✅ Texte</span> pour les messages de succès
    - <span class="text-danger">❌ Texte</span> pour les messages d'erreur
    
    Ne mélange pas HTML et Markdown. Utilise uniquement du HTML pur.
    """
    
    response = ai_provider.generate_text(prompt)
    
    return jsonify({
        'enonce': response,
        'description_originale': description,
        'provider': session.get('ai_provider', 'localai')
    })

# Route pour évaluer le code soumis
@app.route('/evaluate-code', methods=['POST'])
def evaluate_code():
    data = request.json
    code = data.get('code')
    enonce = data.get('enonce')
    
    # Obtenir le fournisseur d'IA approprié
    ai_provider = get_ai_provider(session.get('ai_provider', 'localai'))
    
    # Évaluer le code avec le fournisseur d'IA
    response = ai_provider.evaluate_code(code, enonce)
    
    return jsonify({
        'evaluation': response,
        'provider': session.get('ai_provider', 'localai')
    })

# Route pour exécuter le code Python
@app.route('/execute-code', methods=['POST'])
def execute_code():
    import sys
    from io import StringIO
    import traceback
    
    data = request.json
    code = data.get('code')
    
    # Capturer la sortie standard et les erreurs
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    
    result = {
        'output': '',
        'error': ''
    }
    
    # Créer un environnement d'exécution local
    local_vars = {}
    
    try:
        # Compiler le code en mode 'exec' pour exécuter les instructions
        compiled_code = compile(code, '<string>', 'exec')
        
        # Exécuter le code compilé
        exec(compiled_code, globals(), local_vars)
        
        # Récupérer la sortie standard
        output = redirected_output.getvalue()
        
        # Si aucune sortie n'a été produite, essayons d'évaluer la dernière expression
        if not output.strip():
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
                        output += str(expr_result)
                except:
                    # Si l'évaluation échoue, on ignore simplement
                    pass
        
        result['output'] = output
    except Exception as e:
        result['error'] = str(e) + '\n' + traceback.format_exc()
    finally:
        # Restaurer stdout et stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
