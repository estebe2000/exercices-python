"""
Application Flask pour la génération et l'évaluation d'exercices Python.

Cette application permet de générer des énoncés d'exercices Python, d'exécuter du code
et d'évaluer les solutions soumises par les élèves.
"""

import json
import os
import sys
import time
import uuid
import threading
import traceback
from io import StringIO
from typing import Dict, Any, List, Optional, Tuple

# Configuration de matplotlib pour le mode non-interactif
try:
    import matplotlib
    matplotlib.use('Agg')  # Mode non-interactif
except ImportError:
    pass  # Matplotlib n'est pas installé

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from ai_providers import get_ai_provider
from prompts import get_exercise_prompt
import uuid
from notebook_generator import create_notebook, save_notebook, extract_code_and_tests, clean_old_notebooks

# Configuration base de données
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev_key_123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ged.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB

# Initialisation SQLAlchemy
db = SQLAlchemy(app)

# Ajout de la commande CLI init-db
@app.cli.command("init-db")
def init_db_command():
    """Crée les tables de la base de données"""
    db.create_all()
    print("Base de données initialisée avec succès")

# Modèle Document
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(255), nullable=False)
    nom_unique = db.Column(db.String(36), unique=True)  # UUID4
    date_upload = db.Column(db.DateTime, default=db.func.current_timestamp())
    taille_fichier = db.Column(db.Integer)  # Taille en octets
    type_mime = db.Column(db.String(100))  # Type MIME du fichier
    description = db.Column(db.Text)  # Description optionnelle
    user_id = db.Column(db.Integer)
    est_cours = db.Column(db.Boolean, default=False)  # Indique si le document est un cours
    tags = db.relationship('Tag', secondary='document_tags', backref='documents')

# Modèle Tag
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True)

# Table de liaison
class DocumentTag(db.Model):
    __tablename__ = 'document_tags'
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)


# Constantes
VALID_PROVIDERS = ['localai', 'gemini', 'mistral']
DEFAULT_PROVIDER = 'localai'


# Fonctions utilitaires
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
        app.logger.error(f"Erreur lors du chargement des données d'exercice: {str(e)}")
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


# Gestionnaire d'exécution asynchrone pour le support de input()
class AsyncCodeExecutor:
    def __init__(self):
        self.execution_queue = {}  # Stocke les exécutions en cours par ID
        
    def start_execution(self, code):
        # Générer un ID unique pour cette exécution
        execution_id = str(uuid.uuid4())
        
        # Initialiser l'état d'exécution
        self.execution_queue[execution_id] = {
            'code': code,
            'status': 'pending',
            'input_required': False,
            'input_prompt': '',
            'result': None,
            'locals': {},
            'output_buffer': StringIO(),
            'error_buffer': StringIO(),
            'start_time': time.time()
        }
        
        # Lancer l'exécution dans un thread séparé
        threading.Thread(target=self._execute_code, args=(execution_id,)).start()
        
        return execution_id
    
    def _execute_code(self, execution_id):
        # Récupérer l'état d'exécution
        execution = self.execution_queue[execution_id]
        code = execution['code']
        
        # Rediriger stdout et stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = execution['output_buffer']
        sys.stderr = execution['error_buffer']
        
        try:
            # Vérifier si le code contient des appels à input()
            if 'input(' in code:
                print("ℹ️ INFO: Votre code utilise la fonction input(). L'exécution s'arrêtera pour attendre votre saisie.")
                print("")
            
            # Compiler le code en mode 'exec' pour exécuter les instructions
            compiled_code = compile(code, '<string>', 'exec')
            
            # Créer un environnement d'exécution avec notre version de input() et les modules préchargés
            exec_globals = {
                'input': lambda prompt='': self._handle_input(execution_id, prompt),
                # Modules scientifiques
                'np': safe_import('numpy'),
                'numpy': safe_import('numpy'),
                'pd': safe_import('pandas'),
                'pandas': safe_import('pandas'),
                'scipy': safe_import('scipy'),
                'sp': safe_import('sympy'),
                'sympy': safe_import('sympy'),
                'plt': safe_import('matplotlib.pyplot'),
                'matplotlib': safe_import('matplotlib'),
                # Modules de traitement de texte
                're': safe_import('re'),
                'string': safe_import('string'),
                'nltk': safe_import('nltk'),
                'textblob': safe_import('textblob'),
                # Modules standards
                'math': safe_import('math'),
                'random': safe_import('random'),
                'statistics': safe_import('statistics'),
                '__builtins__': __builtins__
            }
            
            # Exécuter le code
            exec(compiled_code, exec_globals, execution['locals'])
            
            # Récupérer la sortie standard
            output = execution['output_buffer'].getvalue()
            
            # Si aucune sortie n'a été produite, essayer d'évaluer la dernière expression
            if not output.strip():
                output = try_evaluate_last_expression(code, execution['locals'])
                if output:
                    print(output)
                    output = execution['output_buffer'].getvalue()
            
            # Marquer l'exécution comme terminée
            execution['status'] = 'completed'
            execution['result'] = {
                'output': output,
                'error': ''
            }
        except Exception as e:
            # Gérer les erreurs
            execution['status'] = 'error'
            execution['result'] = {
                'output': execution['output_buffer'].getvalue(),
                'error': str(e) + '\n' + traceback.format_exc()
            }
        finally:
            # Restaurer stdout et stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _handle_input(self, execution_id, prompt):
        execution = self.execution_queue[execution_id]
        
        # Afficher le prompt
        print(prompt, end='')
        
        # Marquer que l'exécution attend une entrée
        execution['status'] = 'waiting_for_input'
        execution['input_required'] = True
        execution['input_prompt'] = prompt
        
        # Attendre que l'entrée soit fournie (avec un timeout)
        start_time = time.time()
        while execution['input_required'] and time.time() - start_time < 300:  # 5 minutes timeout
            time.sleep(0.1)
        
        # Si le timeout est atteint, lever une exception
        if execution['input_required']:
            execution['input_required'] = False
            raise TimeoutError("L'attente d'entrée utilisateur a expiré")
        
        # Afficher la valeur saisie
        input_value = execution.get('input_value', '')
        print(input_value)
        
        # Retourner la valeur fournie
        return input_value
    
    def provide_input(self, execution_id, value):
        if execution_id not in self.execution_queue:
            return False
            
        execution = self.execution_queue[execution_id]
        if not execution['input_required']:
            return False
            
        # Fournir la valeur et marquer que l'entrée n'est plus requise
        execution['input_value'] = value
        execution['input_required'] = False
        return True
    
    def get_execution_status(self, execution_id):
        if execution_id not in self.execution_queue:
            return None
            
        execution = self.execution_queue[execution_id]
        return {
            'status': execution['status'],
            'input_required': execution['input_required'],
            'input_prompt': execution['input_prompt'],
            'result': execution['result']
        }
    
    def cleanup_old_executions(self, max_age=3600):  # 1 heure
        current_time = time.time()
        for execution_id in list(self.execution_queue.keys()):
            execution = self.execution_queue[execution_id]
            if 'start_time' in execution and current_time - execution['start_time'] > max_age:
                del self.execution_queue[execution_id]

# Initialiser le gestionnaire d'exécution
code_executor = AsyncCodeExecutor()

def safe_input(prompt=""):
    """
    Version sécurisée de input() qui affiche un message d'erreur au lieu de bloquer l'exécution.
    
    Args:
        prompt: Le message à afficher (ignoré dans cette implémentation)
        
    Returns:
        Une chaîne vide et affiche un message d'erreur
    """
    print("⚠️ ERREUR: La fonction input() n'est pas supportée dans cet environnement.")
    print("⚠️ Veuillez utiliser des variables prédéfinies au lieu de demander des entrées utilisateur.")
    return ""

def execute_python_code(code: str) -> Dict[str, str]:
    """
    Exécute du code Python et capture la sortie ou les erreurs.
    
    Args:
        code: Code Python à exécuter
        
    Returns:
        Dictionnaire contenant la sortie ou l'erreur
    """
    # Capturer la sortie standard et les erreurs
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    
    result = {
        'output': '',
        'error': ''
    }
    
    # Créer un environnement d'exécution avec les modules préchargés
    exec_globals = {
        'input': safe_input,  # Version sécurisée de input()
        # Modules scientifiques
        'np': safe_import('numpy'),
        'numpy': safe_import('numpy'),
        'pd': safe_import('pandas'),
        'pandas': safe_import('pandas'),
        'scipy': safe_import('scipy'),
        'sp': safe_import('sympy'),
        'sympy': safe_import('sympy'),
        'plt': safe_import('matplotlib.pyplot'),
        'matplotlib': safe_import('matplotlib'),
        # Modules de traitement de texte
        're': safe_import('re'),
        'string': safe_import('string'),
        'nltk': safe_import('nltk'),
        'textblob': safe_import('textblob'),
        # Modules standards
        'math': safe_import('math'),
        'random': safe_import('random'),
        'statistics': safe_import('statistics'),
        '__builtins__': __builtins__
    }
    
    # Variables locales pour l'exécution
    local_vars = {}
    
    try:
        # Vérifier si le code contient des appels à input()
        if 'input(' in code:
            print("⚠️ ATTENTION: Votre code utilise la fonction input() qui n'est pas supportée dans ce mode d'exécution.")
            print("⚠️ Les appels à input() seront remplacés par une version qui retourne une chaîne vide.")
            print("⚠️ Pour utiliser input(), cliquez sur 'Exécuter avec input()' au lieu de 'Exécuter le code'.")
            print("")
        
        # Compiler le code en mode 'exec' pour exécuter les instructions
        compiled_code = compile(code, '<string>', 'exec')
        
        # Exécuter le code compilé avec notre version sécurisée de input()
        exec(compiled_code, exec_globals, local_vars)
        
        # Récupérer la sortie standard
        output = redirected_output.getvalue()
        
        # Si aucune sortie n'a été produite, essayer d'évaluer la dernière expression
        if not output.strip():
            output = try_evaluate_last_expression(code, local_vars)
        
        result['output'] = output
    except Exception as e:
        result['error'] = str(e) + '\n' + traceback.format_exc()
    finally:
        # Restaurer stdout et stderr
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    
    return result


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


# Routes de l'application
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


# Routes pour l'éditeur de data.json
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

# Routes pour la GED
@app.route('/ged')
def ged():
    """Route pour afficher la page principale de la GED."""
    # Récupérer tous les documents et tags
    documents = Document.query.order_by(Document.date_upload.desc()).all()
    tags = Tag.query.order_by(Tag.nom).all()
    return render_template('ged.html', documents=documents, tags=tags)

@app.route('/ged/upload', methods=['POST'])
def upload_document():
    """Route pour uploader un nouveau document."""
    if 'file' not in request.files:
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Aucun fichier sélectionné'}), 400
    
    # Générer un nom unique pour le fichier
    unique_filename = str(uuid.uuid4())
    
    # Récupérer les tags
    tag_names = request.form.get('tags', '').split(',')
    tag_names = [tag.strip() for tag in tag_names if tag.strip()]
    
    # Sauvegarder le fichier
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    
    # Créer le document en base de données
    document = Document(
        nom_fichier=filename,
        nom_unique=unique_filename,
        taille_fichier=os.path.getsize(file_path),
        type_mime=file.content_type,
        description=request.form.get('description', ''),
        user_id=1  # À remplacer par l'ID de l'utilisateur connecté
    )
    
    # Ajouter les tags
    for tag_name in tag_names:
        # Vérifier si le tag existe déjà
        tag = Tag.query.filter_by(nom=tag_name).first()
        if not tag:
            # Créer le tag s'il n'existe pas
            tag = Tag(nom=tag_name)
            db.session.add(tag)
        document.tags.append(tag)
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({'success': True, 'document_id': document.id})

@app.route('/ged/document/<int:document_id>')
def view_document(document_id):
    """Route pour visualiser un document."""
    document = Document.query.get_or_404(document_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], document.nom_unique)
    return send_file(file_path, download_name=document.nom_fichier)

@app.route('/ged/edit/<int:document_id>', methods=['GET', 'POST'])
def edit_document(document_id):
    """Route pour éditer un document."""
    document = Document.query.get_or_404(document_id)
    
    if request.method == 'POST':
        # Mettre à jour les informations du document
        document.nom_fichier = request.form.get('nom_fichier', document.nom_fichier)
        document.description = request.form.get('description', document.description)
        
        # Mettre à jour les tags
        tag_names = request.form.get('tags', '').split(',')
        tag_names = [tag.strip() for tag in tag_names if tag.strip()]
        
        # Supprimer tous les tags existants
        document.tags = []
        
        # Ajouter les nouveaux tags
        for tag_name in tag_names:
            # Vérifier si le tag existe déjà
            tag = Tag.query.filter_by(nom=tag_name).first()
            if not tag:
                # Créer le tag s'il n'existe pas
                tag = Tag(nom=tag_name)
                db.session.add(tag)
            document.tags.append(tag)
        
        db.session.commit()
        return redirect(url_for('ged'))
    
    # Récupérer tous les tags pour l'autocomplétion
    all_tags = Tag.query.order_by(Tag.nom).all()
    
    return render_template('edit_document.html', document=document, all_tags=all_tags)

@app.route('/ged/delete/<int:document_id>', methods=['POST'])
def delete_document(document_id):
    """Route pour supprimer un document."""
    document = Document.query.get_or_404(document_id)
    
    # Supprimer le fichier physique
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], document.nom_unique)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Supprimer le document de la base de données
    db.session.delete(document)
    db.session.commit()
    
    return redirect(url_for('ged'))

@app.route('/ged/toggle-cours/<int:document_id>', methods=['POST'])
def toggle_cours(document_id):
    """Route pour marquer/démarquer un document comme cours."""
    document = Document.query.get_or_404(document_id)
    
    # Inverser la valeur du champ est_cours
    document.est_cours = not document.est_cours
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'est_cours': document.est_cours
    })

@app.route('/cours')
def cours():
    """Route pour afficher la page des cours (documents en mode lecture avec style bibliothèque)."""
    query = request.args.get('q', '')
    tag = request.args.get('tag', '')
    
    # Base de la requête - ne récupérer que les documents marqués comme cours
    documents_query = Document.query.filter_by(est_cours=True)
    
    # Filtrer par texte de recherche
    if query:
        documents_query = documents_query.filter(Document.nom_fichier.ilike(f'%{query}%'))
    
    # Filtrer par tag
    if tag:
        documents_query = documents_query.join(Document.tags).filter(Tag.nom == tag)
    
    # Exécuter la requête
    documents = documents_query.order_by(Document.date_upload.desc()).all()
    
    # Récupérer tous les tags pour les filtres
    tags = Tag.query.order_by(Tag.nom).all()
    
    return render_template('cours.html', documents=documents, tags=tags, query=query, selected_tag=tag)

@app.route('/ged/search')
def search_documents():
    """Route pour rechercher des documents."""
    query = request.args.get('q', '')
    tag = request.args.get('tag', '')
    
    # Base de la requête
    documents_query = Document.query
    
    # Filtrer par texte de recherche
    if query:
        documents_query = documents_query.filter(Document.nom_fichier.ilike(f'%{query}%'))
    
    # Filtrer par tag
    if tag:
        documents_query = documents_query.join(Document.tags).filter(Tag.nom == tag)
    
    # Exécuter la requête
    documents = documents_query.order_by(Document.date_upload.desc()).all()
    
    # Récupérer tous les tags pour les filtres
    tags = Tag.query.order_by(Tag.nom).all()
    
    return render_template('ged.html', documents=documents, tags=tags, query=query, selected_tag=tag)

# Routes pour la génération et le téléchargement de notebooks Jupyter
@app.route('/prepare-notebook', methods=['POST'])
def prepare_notebook():
    """Route pour préparer le téléchargement d'un notebook."""
    # Récupérer le dernier exercice généré depuis la session
    last_exercise = session.get('last_exercise', {})
    
    if not last_exercise:
        return jsonify({'error': 'Aucun exercice généré récemment'}), 400
    
    # Rendre le template avec le formulaire de téléchargement
    return render_template('download_notebook.html', exercise=last_exercise)

@app.route('/download-notebook', methods=['POST'])
def download_notebook():
    """Route pour générer et télécharger un notebook Jupyter."""
    # Récupérer les données du formulaire
    title = request.form.get('title', 'Exercice Python')
    
    # Récupérer le dernier exercice généré depuis la session
    last_exercise = session.get('last_exercise', {})
    
    if not last_exercise:
        return jsonify({'error': 'Aucun exercice généré récemment'}), 400
    
    # Extraire l'énoncé
    html_description = last_exercise.get('enonce', '')
    
    # Extraire le titre et la description de l'énoncé
    import re
    from html import unescape
    from bs4 import BeautifulSoup
    
    # Utiliser BeautifulSoup pour extraire le texte et les blocs de code
    soup = BeautifulSoup(html_description, 'html.parser')
    
    # Extraire le texte de l'énoncé (sans les blocs de code)
    description_parts = []
    code_blocks = []
    
    # Fonction pour extraire le texte et les blocs de code
    def extract_text_and_code(element):
        if element.name == 'pre' and element.find('code'):
            # C'est un bloc de code
            code_element = element.find('code')
            code_text = code_element.get_text()
            language = ''
            if 'class' in code_element.attrs:
                for cls in code_element['class']:
                    if cls.startswith('language-'):
                        language = cls[9:]  # Extraire le langage (après 'language-')
            code_blocks.append((language, code_text))
            # Remplacer le bloc de code par un marqueur
            return f"[CODE_BLOCK_{len(code_blocks)-1}]"
        elif element.name:
            # C'est un élément HTML
            content = ''.join(extract_text_and_code(child) for child in element.children)
            if element.name == 'h1':
                return f"# {content}\n\n"
            elif element.name == 'h2':
                return f"## {content}\n\n"
            elif element.name == 'h3':
                return f"### {content}\n\n"
            elif element.name == 'p':
                return f"{content}\n\n"
            elif element.name == 'ul':
                return content
            elif element.name == 'li':
                return f"* {content}\n"
            elif element.name == 'strong':
                return f"**{content}**"
            elif element.name == 'em':
                return f"*{content}*"
            elif element.name == 'br':
                return "\n"
            else:
                return content
        else:
            # C'est du texte
            return element.string or ''
    
    # Extraire le texte et les blocs de code
    markdown_description = ''.join(extract_text_and_code(child) for child in soup.children)
    
    # Réinsérer les blocs de code
    for i, (language, code_text) in enumerate(code_blocks):
        if language:
            markdown_description = markdown_description.replace(
                f"[CODE_BLOCK_{i}]",
                f"```{language}\n{code_text}\n```"
            )
        else:
            markdown_description = markdown_description.replace(
                f"[CODE_BLOCK_{i}]",
                f"```\n{code_text}\n```"
            )
    
    # Extraire le code et les tests
    code_parts = extract_code_and_tests(html_description)
    code = code_parts.get('code', '')
    tests = code_parts.get('tests', '')
    
    # Créer le notebook
    notebook = create_notebook(title, markdown_description, code, tests)
    
    # Sauvegarder le notebook
    filename = secure_filename(title.replace(' ', '_'))
    filepath = save_notebook(notebook, filename)
    
    # Nettoyer les anciens notebooks (plus de 24h)
    clean_old_notebooks()
    
    # Envoyer le fichier
    return send_file(filepath, 
                    mimetype='application/x-ipynb+json',
                    as_attachment=True,
                    download_name=f"{filename}.ipynb")

# Point d'entrée principal
if __name__ == '__main__':
    # Créer le répertoire de logs s'il n'existe pas
    os.makedirs('logs', exist_ok=True)
    app.run(debug=True)
