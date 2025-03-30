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
from qcm_generator import load_qcm_questions, add_questions_to_level, THEMES, QCM_FILE_PATH

# Constantes
VALID_LEVELS = ['Troisième', 'SNT', 'Prépa NSI', 'Première Générale', 'Terminale Générale']
# Nombre de questions QCM par niveau
QCM_COUNT_BY_LEVEL = {
    'Troisième': 10,
    'SNT': 10,
    'Prépa NSI': 10,
    'Première Générale': 6,  # Réduit pour éviter les problèmes de taille de cookie
    'Terminale Générale': 6  # Réduit pour éviter les problèmes de taille de cookie
}
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
    
    Args:
        level: Le niveau scolaire
    
    Returns:
        Un dictionnaire contenant les données du défi
    """
    # Charger les données des exercices
    data = load_exercise_data()
    
    # Déterminer le nombre de questions QCM pour ce niveau
    qcm_count = QCM_COUNT_BY_LEVEL.get(level, QCM_COUNT)
    
    # Générer les questions QCM
    qcm_questions = generate_qcm_questions(level, data, qcm_count)
    
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
    Génère des questions QCM pour un niveau donné.
    
    Args:
        level: Le niveau scolaire
        data: Les données des exercices
        count: Le nombre de questions à générer
    
    Returns:
        Une liste de questions QCM
    """
    # Charger les questions depuis le fichier JSON
    if os.path.exists(QCM_FILE_PATH):
        all_questions = load_qcm_questions()
        
        # Vérifier si le niveau existe et contient des questions
        if level in all_questions and all_questions[level]:
            # Sélectionner des questions aléatoires pour ce niveau
            level_questions = all_questions[level]
            selected_questions = random.sample(level_questions, min(count, len(level_questions)))
            
            # Formater les questions pour l'affichage
            questions = []
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
            
            return questions
    
    # Si le fichier n'existe pas ou si le niveau n'a pas de questions,
    # utiliser la méthode existante
    pdf_path = get_program_pdf_path(level)
    
    if pdf_path and os.path.exists(pdf_path):
        # Générer des questions basées sur le programme officiel
        questions = generate_questions_from_pdf(pdf_path, level, count)
    else:
        # Générer des questions basées sur data.json
        questions = generate_questions_from_data(data, level, count)
    
    return questions

def get_program_pdf_path(level):
    """
    Retourne le chemin du fichier PDF du programme officiel pour un niveau donné.
    
    Args:
        level: Le niveau scolaire
    
    Returns:
        Le chemin du fichier PDF ou None si non trouvé
    """
    pdf_mapping = {
        'Terminale Générale': 'programmes/programme nsi_terminal.pdf',
        'Première Générale': 'programmes/programme nsi_premiere.pdf',
        'SNT': 'programmes/programme_snt.pdf'
    }
    
    return pdf_mapping.get(level)

def generate_questions_from_pdf(pdf_path, level, count):
    """
    Génère des questions QCM basées sur le contenu d'un fichier PDF.
    
    Args:
        pdf_path: Le chemin du fichier PDF
        level: Le niveau scolaire
        count: Le nombre de questions à générer
    
    Returns:
        Une liste de questions QCM
    """
    # Pour l'instant, nous utilisons des questions prédéfinies
    # Dans une implémentation complète, il faudrait extraire le contenu du PDF
    # et générer des questions pertinentes
    
    questions = []
    
    # Questions pour NSI Première
    premiere_questions = [
        {
            'question': 'Quelle est la représentation binaire du nombre décimal 42 ?',
            'options': ['101010', '110010', '100001', '101100'],
            'correct': '101010',
            'explanation': 'La représentation binaire de 42 est 101010 (32 + 8 + 2).'
        },
        {
            'question': 'Quelle structure de données permet de stocker des paires clé-valeur ?',
            'options': ['Liste', 'Dictionnaire', 'Tuple', 'Ensemble'],
            'correct': 'Dictionnaire',
            'explanation': 'Le dictionnaire est une structure de données qui associe des clés à des valeurs.'
        },
        {
            'question': 'Quelle est la complexité temporelle de la recherche dichotomique ?',
            'options': ['O(n)', 'O(n²)', 'O(log n)', 'O(n log n)'],
            'correct': 'O(log n)',
            'explanation': 'La recherche dichotomique a une complexité logarithmique car elle divise l\'espace de recherche par 2 à chaque étape.'
        },
        {
            'question': 'Quel est le résultat de l\'expression booléenne (True and False) or (not False) ?',
            'options': ['True', 'False', 'None', 'Error'],
            'correct': 'True',
            'explanation': '(True and False) donne False, (not False) donne True, et False or True donne True.'
        },
        {
            'question': 'Quelle méthode algorithmique consiste à choisir à chaque étape la solution qui semble la meilleure ?',
            'options': ['Diviser pour régner', 'Programmation dynamique', 'Algorithme glouton', 'Backtracking'],
            'correct': 'Algorithme glouton',
            'explanation': 'Les algorithmes gloutons font des choix localement optimaux à chaque étape.'
        },
        {
            'question': 'Quel est le modèle d\'architecture séquentielle classique des ordinateurs ?',
            'options': ['Modèle client-serveur', 'Modèle OSI', 'Modèle de von Neumann', 'Modèle TCP/IP'],
            'correct': 'Modèle de von Neumann',
            'explanation': 'Le modèle de von Neumann est caractérisé par une unité de traitement, une unité de contrôle, une mémoire et des dispositifs d\'entrée/sortie.'
        },
        {
            'question': 'Quelle est la fonction principale d\'un système d\'exploitation ?',
            'options': ['Exécuter des applications web', 'Gérer les ressources matérielles', 'Créer des documents', 'Naviguer sur internet'],
            'correct': 'Gérer les ressources matérielles',
            'explanation': 'Le système d\'exploitation gère les ressources matérielles et fournit des services aux programmes.'
        },
        {
            'question': 'Quel protocole est utilisé pour la transmission de données sur le Web ?',
            'options': ['FTP', 'SMTP', 'HTTP', 'SSH'],
            'correct': 'HTTP',
            'explanation': 'HTTP (HyperText Transfer Protocol) est le protocole utilisé pour transférer les pages web.'
        },
        {
            'question': 'Quelle méthode de tri a une complexité moyenne de O(n log n) ?',
            'options': ['Tri à bulles', 'Tri par insertion', 'Tri par sélection', 'Tri fusion'],
            'correct': 'Tri fusion',
            'explanation': 'Le tri fusion divise récursivement le tableau en deux, trie chaque moitié, puis fusionne les résultats.'
        },
        {
            'question': 'Quelle structure de données fonctionne selon le principe "dernier entré, premier sorti" (LIFO) ?',
            'options': ['File', 'Pile', 'Liste chaînée', 'Arbre binaire'],
            'correct': 'Pile',
            'explanation': 'Une pile (stack) suit le principe LIFO : le dernier élément ajouté est le premier à être retiré.'
        },
        {
            'question': 'Quel est le langage de programmation recommandé dans le programme de NSI ?',
            'options': ['Java', 'C++', 'Python', 'JavaScript'],
            'correct': 'Python',
            'explanation': 'Python est recommandé pour sa simplicité et sa lisibilité, facilitant l\'apprentissage des concepts informatiques.'
        },
        {
            'question': 'Quelle est la différence entre = et == en Python ?',
            'options': ['Aucune différence', '= est l\'affectation, == est la comparaison', '= est la comparaison, == est l\'affectation', '= est pour les nombres, == pour les chaînes'],
            'correct': '= est l\'affectation, == est la comparaison',
            'explanation': 'L\'opérateur = assigne une valeur à une variable, tandis que == teste l\'égalité entre deux valeurs.'
        }
    ]
    
    # Questions pour NSI Terminale
    terminale_questions = [
        {
            'question': 'Quelle structure de données utilise des nœuds contenant des références vers d\'autres nœuds ?',
            'options': ['Tableau', 'Liste chaînée', 'Dictionnaire', 'Ensemble'],
            'correct': 'Liste chaînée',
            'explanation': 'Une liste chaînée est composée de nœuds contenant une valeur et une référence au nœud suivant.'
        },
        {
            'question': 'Quelle méthode de parcours d\'arbre visite d\'abord tous les nœuds d\'un niveau avant de passer au niveau suivant ?',
            'options': ['Parcours en profondeur', 'Parcours en largeur', 'Parcours préfixe', 'Parcours infixe'],
            'correct': 'Parcours en largeur',
            'explanation': 'Le parcours en largeur (BFS) explore tous les nœuds d\'un niveau avant de passer au niveau suivant.'
        },
        {
            'question': 'Quelle est la complexité temporelle de l\'algorithme de Dijkstra avec une implémentation par tas binaire ?',
            'options': ['O(n)', 'O(n²)', 'O(n log n)', 'O(2^n)'],
            'correct': 'O(n log n)',
            'explanation': 'Avec une implémentation par tas binaire, l\'algorithme de Dijkstra a une complexité de O((V+E)log V), soit O(n log n) dans le cas général.'
        },
        {
            'question': 'Quel concept de programmation permet à une fonction de s\'appeler elle-même ?',
            'options': ['Itération', 'Récursivité', 'Héritage', 'Polymorphisme'],
            'correct': 'Récursivité',
            'explanation': 'La récursivité est un concept où une fonction s\'appelle elle-même pour résoudre un problème.'
        },
        {
            'question': 'Quelle structure de données est optimisée pour les opérations de recherche, d\'insertion et de suppression en O(log n) ?',
            'options': ['Liste chaînée', 'Tableau', 'Arbre binaire de recherche équilibré', 'File de priorité'],
            'correct': 'Arbre binaire de recherche équilibré',
            'explanation': 'Un arbre binaire de recherche équilibré (comme l\'AVL ou le rouge-noir) maintient une hauteur logarithmique.'
        },
        {
            'question': 'Quel algorithme permet de trouver le plus court chemin entre tous les couples de sommets d\'un graphe ?',
            'options': ['Dijkstra', 'Bellman-Ford', 'Floyd-Warshall', 'Kruskal'],
            'correct': 'Floyd-Warshall',
            'explanation': 'L\'algorithme de Floyd-Warshall calcule les plus courts chemins entre toutes les paires de sommets d\'un graphe.'
        },
        {
            'question': 'Quelle technique consiste à stocker les résultats intermédiaires pour éviter de recalculer les mêmes sous-problèmes ?',
            'options': ['Programmation dynamique', 'Algorithme glouton', 'Diviser pour régner', 'Backtracking'],
            'correct': 'Programmation dynamique',
            'explanation': 'La programmation dynamique résout des problèmes en combinant les solutions de sous-problèmes et en mémorisant les résultats.'
        },
        {
            'question': 'Quelle structure de données est utilisée pour implémenter une file de priorité efficace ?',
            'options': ['Liste chaînée', 'Tableau trié', 'Tas (heap)', 'Arbre AVL'],
            'correct': 'Tas (heap)',
            'explanation': 'Un tas (heap) est une structure arborescente qui permet d\'accéder efficacement à l\'élément de plus haute priorité.'
        },
        {
            'question': 'Quelle est la différence entre un algorithme de tri stable et instable ?',
            'options': ['La complexité temporelle', 'La complexité spatiale', 'La préservation de l\'ordre relatif des éléments égaux', 'La capacité à trier des types de données différents'],
            'correct': 'La préservation de l\'ordre relatif des éléments égaux',
            'explanation': 'Un tri stable préserve l\'ordre relatif des éléments égaux, tandis qu\'un tri instable peut les réorganiser.'
        },
        {
            'question': 'Quelle est la complexité spatiale de l\'algorithme de tri fusion (merge sort) ?',
            'options': ['O(1)', 'O(log n)', 'O(n)', 'O(n²)'],
            'correct': 'O(n)',
            'explanation': 'Le tri fusion nécessite un espace supplémentaire proportionnel à la taille du tableau à trier.'
        },
        {
            'question': 'Quel concept de programmation orientée objet permet à une classe d\'acquérir les propriétés d\'une autre classe ?',
            'options': ['Encapsulation', 'Polymorphisme', 'Héritage', 'Abstraction'],
            'correct': 'Héritage',
            'explanation': 'L\'héritage permet à une classe (sous-classe) d\'hériter des attributs et méthodes d\'une autre classe (superclasse).'
        },
        {
            'question': 'Quelle structure de données est la plus adaptée pour vérifier si un élément appartient à un ensemble avec une complexité moyenne de O(1) ?',
            'options': ['Liste', 'Arbre binaire de recherche', 'Table de hachage', 'Tableau trié'],
            'correct': 'Table de hachage',
            'explanation': 'Une table de hachage (dictionnaire en Python) offre un accès en temps constant en moyenne pour la recherche d\'éléments.'
        }
    ]
    
    # Questions pour SNT
    snt_questions = [
        {
            'question': 'Quelle est l\'unité de base de l\'information en informatique ?',
            'options': ['Octet', 'Bit', 'Pixel', 'Hertz'],
            'correct': 'Bit',
            'explanation': 'Le bit (binary digit) est l\'unité de base de l\'information, pouvant prendre la valeur 0 ou 1.'
        },
        {
            'question': 'Quel composant d\'un ordinateur est responsable de l\'exécution des instructions ?',
            'options': ['Disque dur', 'Mémoire RAM', 'Processeur (CPU)', 'Carte graphique'],
            'correct': 'Processeur (CPU)',
            'explanation': 'Le processeur (CPU) est le composant qui exécute les instructions des programmes.'
        },
        {
            'question': 'Qu\'est-ce qu\'un algorithme ?',
            'options': ['Un langage de programmation', 'Une suite d\'instructions pour résoudre un problème', 'Un type de virus informatique', 'Un composant matériel'],
            'correct': 'Une suite d\'instructions pour résoudre un problème',
            'explanation': 'Un algorithme est une séquence d\'instructions précises permettant de résoudre un problème.'
        },
        {
            'question': 'Quel est le rôle principal d\'un système d\'exploitation ?',
            'options': ['Créer des documents', 'Naviguer sur internet', 'Gérer les ressources de l\'ordinateur', 'Éditer des images'],
            'correct': 'Gérer les ressources de l\'ordinateur',
            'explanation': 'Le système d\'exploitation gère les ressources matérielles et logicielles de l\'ordinateur.'
        },
        {
            'question': 'Qu\'est-ce qu\'une adresse IP ?',
            'options': ['Un code postal numérique', 'Un identifiant unique pour chaque appareil sur un réseau', 'Un mot de passe', 'Un nom de domaine'],
            'correct': 'Un identifiant unique pour chaque appareil sur un réseau',
            'explanation': 'Une adresse IP est un numéro d\'identification attribué à chaque appareil connecté à un réseau.'
        },
        {
            'question': 'Quelle est la différence entre un logiciel libre et un logiciel propriétaire ?',
            'options': ['Le prix', 'La qualité', 'L\'accès au code source', 'La popularité'],
            'correct': 'L\'accès au code source',
            'explanation': 'Un logiciel libre donne accès à son code source et permet sa modification et redistribution.'
        },
        {
            'question': 'Qu\'est-ce qu\'un cookie web ?',
            'options': ['Un virus informatique', 'Un petit fichier stocké sur l\'ordinateur par un site web', 'Un type de connexion internet', 'Un langage de programmation'],
            'correct': 'Un petit fichier stocké sur l\'ordinateur par un site web',
            'explanation': 'Un cookie est un petit fichier texte qu\'un site web stocke sur l\'ordinateur de l\'utilisateur pour suivre ses préférences ou son activité.'
        },
        {
            'question': 'Qu\'est-ce que le phishing ?',
            'options': ['Une technique de pêche virtuelle', 'Une technique d\'optimisation de site web', 'Une technique de piratage par usurpation d\'identité', 'Un type de réseau social'],
            'correct': 'Une technique de piratage par usurpation d\'identité',
            'explanation': 'Le phishing est une technique frauduleuse visant à obtenir des informations personnelles en se faisant passer pour une entité de confiance.'
        },
        {
            'question': 'Quel est le langage de base utilisé pour créer des pages web ?',
            'options': ['Java', 'Python', 'HTML', 'C++'],
            'correct': 'HTML',
            'explanation': 'HTML (HyperText Markup Language) est le langage standard pour créer la structure des pages web.'
        },
        {
            'question': 'Qu\'est-ce que le cloud computing ?',
            'options': ['La météo informatique', 'L\'utilisation de ressources informatiques distantes via internet', 'Un type de virus', 'Un système de refroidissement pour ordinateurs'],
            'correct': 'L\'utilisation de ressources informatiques distantes via internet',
            'explanation': 'Le cloud computing permet d\'utiliser des ressources informatiques (stockage, calcul) hébergées sur des serveurs distants via internet.'
        },
        {
            'question': 'Qu\'est-ce que les données personnelles ?',
            'options': ['Des informations secrètes', 'Des informations qui permettent d\'identifier une personne', 'Des fichiers stockés sur un ordinateur', 'Des statistiques'],
            'correct': 'Des informations qui permettent d\'identifier une personne',
            'explanation': 'Les données personnelles sont toutes les informations qui permettent d\'identifier directement ou indirectement une personne physique.'
        },
        {
            'question': 'Qu\'est-ce que le RGPD ?',
            'options': ['Un virus informatique', 'Un langage de programmation', 'Une réglementation sur la protection des données personnelles', 'Un système d\'exploitation'],
            'correct': 'Une réglementation sur la protection des données personnelles',
            'explanation': 'Le Règlement Général sur la Protection des Données est un cadre juridique européen qui encadre le traitement des données personnelles.'
        }
    ]
    
    # Questions pour Troisième
    troisieme_questions = [
        {
            'question': 'Quelle instruction Python permet d\'afficher du texte à l\'écran ?',
            'options': ['input()', 'print()', 'display()', 'show()'],
            'correct': 'print()',
            'explanation': 'La fonction print() permet d\'afficher du texte ou des variables à l\'écran.'
        },
        {
            'question': 'Comment déclare-t-on une variable en Python ?',
            'options': ['var nom = valeur', 'nom := valeur', 'nom = valeur', 'variable nom = valeur'],
            'correct': 'nom = valeur',
            'explanation': 'En Python, on déclare une variable simplement en lui assignant une valeur avec l\'opérateur =.'
        },
        {
            'question': 'Quel est le résultat de 10 % 3 en Python ?',
            'options': ['1', '3.33', '3', '0'],
            'correct': '1',
            'explanation': 'L\'opérateur % calcule le reste de la division euclidienne. 10 divisé par 3 donne 3 avec un reste de 1.'
        },
        {
            'question': 'Quelle structure permet de répéter une action un nombre défini de fois ?',
            'options': ['Boucle if', 'Boucle for', 'Boucle when', 'Boucle repeat'],
            'correct': 'Boucle for',
            'explanation': 'La boucle for permet d\'itérer un nombre défini de fois, par exemple: for i in range(10):'
        },
        {
            'question': 'Comment vérifie-t-on si deux valeurs sont égales en Python ?',
            'options': ['a = b', 'a == b', 'a === b', 'a.equals(b)'],
            'correct': 'a == b',
            'explanation': 'L\'opérateur == teste l\'égalité entre deux valeurs, tandis que = est utilisé pour l\'affectation.'
        },
        {
            'question': 'Quel est le type de la valeur "42" en Python ?',
            'options': ['int', 'float', 'str', 'bool'],
            'correct': 'str',
            'explanation': 'Les guillemets indiquent que "42" est une chaîne de caractères (string), pas un nombre.'
        },
        {
            'question': 'Comment créer une liste vide en Python ?',
            'options': ['list()', '[]', 'new List()', '{}'],
            'correct': '[]',
            'explanation': 'On peut créer une liste vide avec la syntaxe [] ou avec list().'
        },
        {
            'question': 'Quelle fonction permet de connaître la longueur d\'une liste ?',
            'options': ['count()', 'size()', 'length()', 'len()'],
            'correct': 'len()',
            'explanation': 'La fonction len() retourne le nombre d\'éléments dans une séquence comme une liste, une chaîne, etc.'
        },
        {
            'question': 'Comment accède-t-on au premier élément d\'une liste en Python ?',
            'options': ['liste[0]', 'liste[1]', 'liste.first()', 'liste.get(0)'],
            'correct': 'liste[0]',
            'explanation': 'En Python, l\'indexation commence à 0, donc le premier élément est à l\'index 0.'
        },
        {
            'question': 'Quelle instruction permet de lire une entrée utilisateur ?',
            'options': ['read()', 'input()', 'get()', 'scan()'],
            'correct': 'input()',
            'explanation': 'La fonction input() permet de lire une entrée utilisateur depuis le clavier.'
        },
        {
            'question': 'Comment convertir une chaîne en nombre entier ?',
            'options': ['int(chaine)', 'Integer.parse(chaine)', 'to_int(chaine)', 'chaine.toInteger()'],
            'correct': 'int(chaine)',
            'explanation': 'La fonction int() convertit son argument en un entier si possible.'
        },
        {
            'question': 'Quelle est la valeur de 3 ** 2 en Python ?',
            'options': ['6', '9', '5', '8'],
            'correct': '9',
            'explanation': 'L\'opérateur ** représente l\'exponentiation. 3 ** 2 signifie 3 au carré, soit 9.'
        }
    ]
    
    # Questions pour Prépa NSI
    prepa_questions = [
        {
            'question': 'Quelle est la différence entre une liste et un tuple en Python ?',
            'options': ['Aucune différence', 'Les listes sont indexées, pas les tuples', 'Les tuples sont immuables, les listes sont modifiables', 'Les tuples peuvent contenir différents types, pas les listes'],
            'correct': 'Les tuples sont immuables, les listes sont modifiables',
            'explanation': 'Les tuples sont immuables (on ne peut pas les modifier après création) contrairement aux listes.'
        },
        {
            'question': 'Comment définit-on une fonction en Python ?',
            'options': ['function nom():', 'def nom():', 'define nom():', 'func nom():'],
            'correct': 'def nom():',
            'explanation': 'Le mot-clé def est utilisé pour définir une fonction en Python.'
        },
        {
            'question': 'Quelle méthode permet d\'ajouter un élément à la fin d\'une liste ?',
            'options': ['list.add()', 'list.append()', 'list.insert()', 'list.push()'],
            'correct': 'list.append()',
            'explanation': 'La méthode append() ajoute un élément à la fin d\'une liste.'
        },
        {
            'question': 'Comment accéder à un élément d\'un dictionnaire ?',
            'options': ['dict(key)', 'dict.get(key)', 'dict[key]', 'dict.key'],
            'correct': 'dict[key]',
            'explanation': 'On accède à un élément d\'un dictionnaire en utilisant la syntaxe dict[key].'
        },
        {
            'question': 'Quelle structure conditionnelle permet d\'exécuter un bloc de code si une condition est vraie ?',
            'options': ['for', 'while', 'if', 'switch'],
            'correct': 'if',
            'explanation': 'La structure if permet d\'exécuter un bloc de code si une condition est vraie.'
        },
        {
            'question': 'Comment importer un module en Python ?',
            'options': ['include module', 'import module', 'require module', 'using module'],
            'correct': 'import module',
            'explanation': 'La syntaxe import module permet d\'importer un module en Python.'
        }
    ]
    
    # Sélectionner les questions en fonction du niveau
    if level == 'Première Générale':
        questions = random.sample(premiere_questions, min(count, len(premiere_questions)))
    elif level == 'Terminale Générale':
        questions = random.sample(terminale_questions, min(count, len(terminale_questions)))
    elif level == 'SNT':
        questions = random.sample(snt_questions, min(count, len(snt_questions)))
    elif level == 'Troisième':
        questions = random.sample(troisieme_questions, min(count, len(troisieme_questions)))
    elif level == 'Prépa NSI':
        questions = random.sample(prepa_questions, min(count, len(prepa_questions)))
    else:
        # Par défaut, utiliser les questions de Première
        questions = random.sample(premiere_questions, min(count, len(premiere_questions)))
    
    # Mélanger les options pour chaque question
    for question in questions:
        options = question['options']
        correct = question['correct']
        random.shuffle(options)
        # Mettre à jour l'index de la bonne réponse
        question['correct_index'] = options.index(correct)
    
    return questions

def generate_questions_from_data(data, level, count):
    """
    Génère des questions QCM basées sur les données des exercices.
    
    Args:
        data: Les données des exercices
        level: Le niveau scolaire
        count: Le nombre de questions à générer
    
    Returns:
        Une liste de questions QCM
    """
    # Récupérer les thèmes et descriptions pour le niveau
    level_data = data.get(level, [])
    
    if not level_data:
        # Utiliser les questions prédéfinies si aucune donnée n'est disponible
        return generate_questions_from_pdf(None, level, count)
    
    questions = []
    themes = []
    
    # Collecter tous les thèmes et descriptions
    for theme_data in level_data:
        theme = theme_data.get('thème', '')
        themes.append(theme)
        
        for niveau_data in theme_data.get('niveaux', []):
            description = niveau_data.get('description', '')
            niveau = niveau_data.get('niveau', 1)
            
            # Générer une question basée sur la description
            question = {
                'question': f'Quel est le niveau de difficulté de l\'exercice "{description}" ?',
                'options': ['Facile (niveau 1)', 'Moyen (niveau 2-3)', 'Difficile (niveau 4-5)', 'Expert (niveau 6+)'],
                'correct': get_difficulty_label(niveau),
                'explanation': f'Cet exercice est classé au niveau {niveau} dans le thème "{theme}".'
            }
            
            questions.append(question)
    
    # Générer des questions sur les thèmes
    for theme in themes:
        question = {
            'question': f'Quel niveau scolaire est associé au thème "{theme}" ?',
            'options': ['Troisième', 'SNT', 'Prépa NSI', 'Première Générale', 'Terminale Générale'],
            'correct': level,
            'explanation': f'Le thème "{theme}" fait partie du programme de {level}.'
        }
        
        questions.append(question)
    
    # Sélectionner aléatoirement le nombre de questions demandé
    if questions:
        selected_questions = random.sample(questions, min(count, len(questions)))
        
        # Mélanger les options pour chaque question
        for question in selected_questions:
            options = question['options']
            correct = question['correct']
            random.shuffle(options)
            # Mettre à jour l'index de la bonne réponse
            question['correct_index'] = options.index(correct)
        
        return selected_questions
    else:
        # Utiliser les questions prédéfinies si aucune question n'a pu être générée
        return generate_questions_from_pdf(None, level, count)

def get_difficulty_label(niveau):
    """
    Retourne le libellé de difficulté correspondant au niveau.
    
    Args:
        niveau: Le niveau de difficulté (1-5)
    
    Returns:
        Le libellé de difficulté
    """
    if niveau == 1:
        return 'Facile (niveau 1)'
    elif niveau in [2, 3]:
        return 'Moyen (niveau 2-3)'
    elif niveau in [4, 5]:
        return 'Difficile (niveau 4-5)'
    else:
        return 'Expert (niveau 6+)'

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
