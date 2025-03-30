"""
Module pour générer des fichiers Jupyter Notebook (.ipynb) à partir d'exercices Python.
"""

import json
import os
import re

def create_notebook(title, description, code, tests):
    """
    Crée un fichier Jupyter Notebook avec le contenu spécifié.
    
    Args:
        title (str): Titre de l'exercice
        description (str): Énoncé de l'exercice
        code (str): Squelette de code Python
        tests (str): Tests pour vérifier la solution
        
    Returns:
        dict: Structure JSON du notebook
    """
    # Extraire le titre et la description de l'énoncé
    # Supprimer les balises HTML et convertir en markdown
    import re
    from html import unescape
    
    # Nettoyer le HTML
    description = unescape(description)  # Convertir les entités HTML
    
    # Remplacer les balises HTML courantes par du markdown
    description = description.replace('<strong>', '**').replace('</strong>', '**')
    description = description.replace('<em>', '*').replace('</em>', '*')
    description = description.replace('<h1>', '# ').replace('</h1>', '\n')
    description = description.replace('<h2>', '## ').replace('</h2>', '\n')
    description = description.replace('<h3>', '### ').replace('</h3>', '\n')
    description = description.replace('<ul>', '').replace('</ul>', '')
    description = description.replace('<li>', '* ').replace('</li>', '')
    description = description.replace('<br>', '\n').replace('<br/>', '\n')
    description = description.replace('<p>', '').replace('</p>', '\n\n')
    
    # Supprimer les autres balises HTML
    description = re.sub(r'<[^>]*>', '', description)
    
    # Extraire le titre de l'exercice s'il est présent dans la description
    title_match = re.search(r'^#\s+(.+)$', description, re.MULTILINE)
    if title_match:
        extracted_title = title_match.group(1).strip()
        if extracted_title:
            title = extracted_title
            # Supprimer le titre de la description pour éviter la duplication
            description = re.sub(r'^#\s+.+\n', '', description, 1)
    
    # Créer la structure du notebook
    notebook = {
        "cells": [
            # Cellule titre (markdown)
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"# {title}"]
            },
            # Cellule énoncé (markdown)
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [description]
            },
            # Cellule code (code)
            {
                "cell_type": "code",
                "metadata": {},
                "source": [code],
                "execution_count": None,
                "outputs": []
            },
            # Cellule tests (code)
            {
                "cell_type": "code",
                "metadata": {},
                "source": [tests],
                "execution_count": None,
                "outputs": []
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.8.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    
    return notebook

def save_notebook(notebook, filename):
    """
    Sauvegarde un notebook au format JSON dans un fichier.
    
    Args:
        notebook (dict): Structure JSON du notebook
        filename (str): Nom du fichier à créer
        
    Returns:
        str: Chemin complet du fichier créé
    """
    # Créer le dossier notebooks s'il n'existe pas
    os.makedirs('notebooks', exist_ok=True)
    
    # Chemin complet du fichier
    filepath = os.path.join('notebooks', f"{filename}.ipynb")
    
    # Écrire le fichier
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, ensure_ascii=False, indent=2)
    
    return filepath

def extract_code_and_tests(description):
    """
    Extrait le code et les tests de l'énoncé généré.
    
    Args:
        description (str): Énoncé complet de l'exercice
        
    Returns:
        dict: Dictionnaire contenant le code et les tests
    """
    import re
    
    code = ""
    tests = ""
    
    # Nettoyer la description des balises HTML
    from html import unescape
    description = unescape(description)
    
    # Extraire les blocs de code Python
    code_blocks = re.findall(r'```python\s*(.*?)\s*```', description, re.DOTALL)
    
    if code_blocks:
        # Parcourir les blocs de code
        for block in code_blocks:
            # Si le bloc contient des tests
            if ("# Tests" in block or "assert" in block or 
                "print('✅" in block or "print('❌" in block or
                "print(\"✅" in block or "print(\"❌" in block):
                tests += block.strip() + "\n"
            else:
                code += block.strip() + "\n"
    
    # Si aucun test n'a été trouvé mais qu'il y a du code
    if not tests and code:
        # Chercher les tests dans le texte
        test_section = re.search(r'# Tests.*', description, re.DOTALL)
        if test_section:
            tests = test_section.group(0)
    
    # Si le code contient encore des tests, essayer de les séparer
    if "# Tests" in code:
        parts = code.split("# Tests", 1)
        code = parts[0].strip()
        if len(parts) > 1:
            tests = "# Tests" + parts[1].strip()
    
    # Nettoyer le code et les tests
    code = code.replace('```python', '').replace('```', '').strip()
    tests = tests.replace('```python', '').replace('```', '').strip()
    
    return {
        "code": code.strip(),
        "tests": tests.strip()
    }

def clean_old_notebooks(max_age_hours=24):
    """
    Nettoie les notebooks générés il y a plus de max_age_hours heures.
    
    Args:
        max_age_hours (int): Âge maximum des fichiers en heures
    """
    import time
    
    # Dossier des notebooks
    notebook_dir = 'notebooks'
    
    # Si le dossier n'existe pas, rien à faire
    if not os.path.exists(notebook_dir):
        return
    
    # Temps actuel
    current_time = time.time()
    
    # Parcourir les fichiers du dossier
    for filename in os.listdir(notebook_dir):
        filepath = os.path.join(notebook_dir, filename)
        
        # Si c'est un fichier et qu'il est plus vieux que max_age_hours
        if os.path.isfile(filepath):
            file_age = current_time - os.path.getmtime(filepath)
            if file_age > max_age_hours * 3600:
                try:
                    os.remove(filepath)
                    print(f"Fichier supprimé : {filepath}")
                except Exception as e:
                    print(f"Erreur lors de la suppression de {filepath}: {str(e)}")
