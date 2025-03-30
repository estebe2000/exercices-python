"""
Routes pour la génération et le téléchargement de notebooks Jupyter.

Ce module contient les routes pour préparer, générer et télécharger des notebooks Jupyter
à partir des exercices générés.
"""

import re
from html import unescape
from bs4 import BeautifulSoup
from flask import render_template, request, jsonify, session, send_file
from werkzeug.utils import secure_filename
from notebook_generator import create_notebook, save_notebook, extract_code_and_tests, clean_old_notebooks

def init_routes(app):
    """
    Initialise les routes pour les notebooks Jupyter.
    
    Args:
        app: L'application Flask
    """
    
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
