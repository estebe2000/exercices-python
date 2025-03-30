"""
Module centralisant tous les prompts utilisés par les différents fournisseurs d'IA.
"""

import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis .env
load_dotenv()

# Paramètres par défaut (utiliser les valeurs de .env si disponibles)
DEFAULT_MAX_TOKENS = int(os.getenv("DEFAULT_MAX_TOKENS", 1500))
DEFAULT_TEMPERATURE = float(os.getenv("DEFAULT_TEMPERATURE", 0.7))
DEFAULT_RETRY_COUNT = int(os.getenv("DEFAULT_RETRY_COUNT", 2))
DEFAULT_RETRY_DELAY = int(os.getenv("DEFAULT_RETRY_DELAY", 1))

# Instructions de formatage HTML communes
HTML_FORMATTING_INSTRUCTIONS = """
Utilise uniquement des balises HTML standard pour le formatage:
- <h1>, <h2>, <h3> pour les titres
- <p> pour les paragraphes
- <ul> et <li> pour les listes
- <pre><code class="language-python">...</code></pre> pour les blocs de code
- <strong> pour le texte en gras
- <em> pour le texte en italique
- <span class="text-success">✅ Texte</span> pour les messages de succès
- <span class="text-danger">❌ Texte</span> pour les messages d'erreur
- <span class="text-info">💡 Texte</span> pour les suggestions
- <span class="text-primary">🚀 Texte</span> pour les conseils d'amélioration

Ne mélange pas HTML et Markdown. Utilise uniquement du HTML pur.
"""

# Message système principal
SYSTEM_MESSAGE = f"""Tu es un expert en programmation Python et en pédagogie. 
Tu aides à créer des exercices de programmation pour des élèves de lycée et à évaluer leur code.

IMPORTANT: Tu dois formater tes réponses en HTML pur pour un affichage correct dans un navigateur.

Quand tu crées des exercices:
1. Utilise une structure claire avec des titres et sous-titres bien formatés (<h1>, <h2>, <h3>)
2. Fournis un squelette de code avec plusieurs zones à compléter (3-5 minimum) marquées par "# À COMPLÉTER" ou "# VOTRE CODE ICI"
3. Ne fournis jamais d'exercice déjà complet - il doit toujours y avoir plusieurs parties à implémenter
4. Pour les niveaux Première et Terminale uniquement, inclus 2 tests maximum avec des messages de réussite (✅) ou d'échec (❌)
5. Pour les autres niveaux, ne fournis aucun test
6. Adapte la difficulté au niveau de l'élève (Première ou Terminale)
7. Sois précis dans tes explications et tes attentes

Quand tu évalues du code:
1. Vérifie si le code répond correctement à l'énoncé
2. Identifie les erreurs potentielles (syntaxe, logique, etc.)
3. Suggère des améliorations (optimisation, lisibilité, etc.)
4. Donne des conseils pour aller plus loin
5. Sois encourageant et constructif dans tes retours

{HTML_FORMATTING_INSTRUCTIONS}
"""

def get_evaluation_prompt(code: str, enonce: str) -> str:
    """
    Génère le prompt pour l'évaluation de code.
    
    Args:
        code: Le code Python à évaluer
        enonce: L'énoncé de l'exercice
        
    Returns:
        Le prompt formaté pour l'évaluation
    """
    return f"""
    Évalue le code Python suivant par rapport à l'énoncé donné:
    
    Énoncé:
    {enonce}
    
    Code soumis:
    ```python
    {code}
    ```
    
    IMPORTANT: Ton évaluation doit être formatée en HTML pur pour un affichage correct dans un navigateur.
    
    Ton évaluation doit toujours inclure:
    1. Un titre principal avec <h1>Évaluation du code</h1>
    2. Une section sur la conformité à l'énoncé avec <h2>Conformité à l'énoncé</h2>
    3. Une section sur les erreurs potentielles avec <h2>Erreurs potentielles</h2>
    4. Une section sur les suggestions d'amélioration avec <h2>Suggestions d'amélioration</h2>:
       - Si le code ne fonctionne pas: fournir UNE seule suggestion principale
       - Si le code fonctionne: fournir 3 suggestions maximum
    
    IMPORTANT: La section "Pour aller plus loin" avec <h2>Pour aller plus loin</h2> ne doit être incluse QUE si le code fonctionne correctement et répond à l'énoncé. Si le code contient des erreurs ou ne répond pas à l'énoncé, n'inclus PAS cette section.
    
    Utilise des émojis et des classes pour rendre ton évaluation plus visuelle:
    - <span class="text-success">✅ Texte</span> pour les points positifs
    - <span class="text-danger">❌ Texte</span> pour les erreurs ou problèmes
    - <span class="text-info">💡 Texte</span> pour les suggestions
    - <span class="text-primary">🚀 Texte</span> pour les conseils d'amélioration
    
    TRÈS IMPORTANT:
    - NE DONNE JAMAIS LA SOLUTION COMPLÈTE à l'exercice
    - Fournis uniquement des notions de cours et des pistes de réflexion
    - Si tu dois donner un exemple de code, utilise un exemple différent de l'exercice ou montre seulement une petite partie de la solution
    - Guide l'élève vers la bonne direction sans faire le travail à sa place
    - Sois encourageant et constructif dans tes retours
    
    {HTML_FORMATTING_INSTRUCTIONS}
    """


def get_exercise_prompt(niveau: str, theme: str, difficulte: int, description: str, debutant: bool = False) -> str:
    """
    Génère le prompt pour la création d'un énoncé d'exercice.
    
    Args:
        niveau: Niveau scolaire
        theme: Thème de l'exercice
        difficulte: Niveau de difficulté
        description: Description de l'exercice
        debutant: Si True, l'exercice est pour débutant (sans fonctions, classes, etc.)
        
    Returns:
        Prompt formaté pour l'IA
    """
    # Ajouter des instructions spécifiques pour les exercices débutants
    niveau_python = ""
    if debutant:
        niveau_python = """
        IMPORTANT: Cet exercice est destiné à des débutants en Python. 
        N'utilise PAS de fonctions, de classes, d'objets ou d'autres concepts avancés dans le squelette de code.
        Utilise uniquement des variables, des opérations de base, des conditions (if/else) et des boucles (for/while).
        Le code doit être simple et direct, sans abstractions avancées.
        """
    else:
        niveau_python = """
        Cet exercice peut utiliser des fonctions, des classes et d'autres concepts avancés de Python si nécessaire.
        """
    
    # Instructions pour les exemples de code
    code_examples = """
    Exemple de format CORRECT pour le code et les tests (dans un SEUL bloc):
    
    <pre><code class="language-python">
    def fonction(a, b):
        # À COMPLÉTER: Additionner les deux nombres
        pass
        
    # Tests - NE PAS SÉPARER DU CODE CI-DESSUS
    try:
        assert fonction(1, 2) == 3
        print("✅ Test 1 réussi: fonction(1, 2) == 3")
    except AssertionError:
        print("❌ Test 1 échoué: fonction(1, 2) devrait retourner 3")
    </code></pre>
    
    Exemple de squelette de code INCORRECT (car déjà complet et fonctionnel):
    
    <pre><code class="language-python">
    def est_palindrome(chaine):
        # À COMPLÉTER: Normaliser la chaîne (ignorer les espaces et la casse)
        chaine_normalisee = chaine.replace(" ", "").lower()
    
        # À COMPLÉTER: Vérifier si la chaîne normalisée est un palindrome
        if chaine_normalisee == chaine_normalisee[::-1]:
            return True
        else:
            return False
    </code></pre>
    
    Exemple de squelette de code CORRECT (avec parties à compléter, non fonctionnel):
    
    <pre><code class="language-python">
    def est_palindrome(chaine):
        # À COMPLÉTER: Normaliser la chaîne (ignorer les espaces et la casse)
        # VOTRE CODE ICI
        
        # À COMPLÉTER: Vérifier si la chaîne normalisée est un palindrome
        # VOTRE CODE ICI
        
        # À COMPLÉTER: Retourner le résultat (True ou False)
        pass
    </code></pre>
    
    Autre exemple de squelette de code CORRECT (avec parties à compléter, non fonctionnel):
    
    <pre><code class="language-python">
    # Calcul de l'aire en fonction de la forme choisie
    if forme == "rectangle":
        # À COMPLÉTER: Calculer l'aire du rectangle
        pass
    elif forme == "cercle":
        # À COMPLÉTER: Calculer l'aire du cercle
        pass
    elif forme == "triangle":
        # À COMPLÉTER: Calculer l'aire du triangle
        pass
    else:
        # À COMPLÉTER: Gérer le cas d'une forme non reconnue
        pass
    </code></pre>
    """
    
    return f"""
    Génère un énoncé d'exercice Python pour un élève de {niveau} avec les caractéristiques suivantes:
    - Thème: {theme}
    - Niveau de difficulté: {difficulte}
    - Description: {description}
    
    {niveau_python}
    
    IMPORTANT: Ton énoncé doit être formaté en HTML pur pour un affichage correct dans un navigateur.
    
    L'énoncé doit inclure:
    1. Un titre principal avec <h1>Titre de l'exercice</h1>
    2. Une description détaillée du problème avec des sous-titres <h2>Section</h2>
    3. Des exemples d'entrées/sorties si nécessaire
    4. Des contraintes ou indications si nécessaire
    
    IMPORTANT: Inclus également:
    5. Un squelette de code à trous que l'élève devra compléter, SUIVI IMMÉDIATEMENT des tests dans le MÊME bloc de code.
    
    RÈGLES IMPORTANTES POUR LE CODE:
    - Le squelette de code et les tests DOIVENT être dans un SEUL bloc de code <pre><code class="language-python">...</code></pre>
    - NE PAS séparer le squelette de code et les tests en plusieurs blocs
    - Les exemples d'entrées/sorties doivent être en dehors du bloc de code principal
    - Utilise des commentaires comme "# À COMPLÉTER" ou "# VOTRE CODE ICI" pour indiquer les parties à remplir
    - NE PAS utiliser la fonction input() dans les exercices, car elle ne fonctionne pas correctement dans l'éditeur
    - Si des données d'entrée sont nécessaires, les fournir directement dans le code (par exemple, sous forme de variables prédéfinies)
    
    RÈGLES CRUCIALES POUR LE SQUELETTE DE CODE:
    - Le squelette de code DOIT OBLIGATOIREMENT contenir ENTRE 3 ET 5 parties à compléter par l'élève
    - NE JAMAIS fournir un code déjà complet ou fonctionnel
    - SUPPRIMER SYSTÉMATIQUEMENT les implémentations et les remplacer par des commentaires "# À COMPLÉTER" ou "# VOTRE CODE ICI"
    - MÊME pour les opérations simples (comme aire = longueur * largeur), TOUJOURS remplacer par "# À COMPLÉTER: Calculer l'aire du rectangle" et PAS de code fonctionnel
    - Pour les structures conditionnelles, laisser la structure mais VIDER COMPLÈTEMENT le contenu des blocs
    - Pour les boucles, laisser la structure mais VIDER COMPLÈTEMENT le contenu des blocs
    - Pour les fonctions, laisser la signature mais remplacer le corps par "# À COMPLÉTER" et "pass"
    - VÉRIFIER ATTENTIVEMENT que le code fourni n'est PAS fonctionnel tel quel et nécessite des modifications pour fonctionner
    
    RÈGLES CRUCIALES POUR LES TESTS:
    - Les tests NE DOIVENT JAMAIS contenir la solution complète ou partielle
    - Les tests doivent utiliser des assertions ou des vérifications indirectes
    - NE JAMAIS inclure le code de la solution dans les tests
    - Utiliser des variables pour stocker les résultats attendus plutôt que de montrer comment les calculer
    - Pour les exercices avec affichage (print), vérifier le résultat avec des assertions sur des variables, pas en répétant le code de la solution
    
    {code_examples}
    
    {HTML_FORMATTING_INSTRUCTIONS}
    """

def get_qcm_prompt(level, theme):
    """
    Génère un prompt pour la création de questions QCM.
    
    Args:
        level: Le niveau scolaire
        theme: Le thème des questions
    
    Returns:
        Le prompt pour l'IA
    """
    return f"""
    Tu es un expert en programmation Python et en pédagogie. Tu dois créer des questions à choix multiples (QCM) pour des élèves de niveau {level} sur le thème "{theme}".

    Génère 3 questions QCM de difficulté variée (facile, moyenne, difficile) sur ce thème.

    Pour chaque question:
    1. Formule une question claire et précise
    2. Propose 4 options de réponse dont une seule est correcte
    3. Indique clairement la réponse correcte
    4. Fournis une explication détaillée de la réponse correcte

    Format de réponse attendu (JSON):
    [
        {{
            "question": "Texte de la question 1",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": "Option correcte (doit être l'une des options)",
            "explanation": "Explication détaillée de la réponse correcte"
        }},
        {{
            "question": "Texte de la question 2",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": "Option correcte (doit être l'une des options)",
            "explanation": "Explication détaillée de la réponse correcte"
        }},
        {{
            "question": "Texte de la question 3",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct": "Option correcte (doit être l'une des options)",
            "explanation": "Explication détaillée de la réponse correcte"
        }}
    ]

    IMPORTANT:
    - Les questions doivent être adaptées au niveau {level}
    - Les questions doivent porter sur le thème "{theme}"
    - Les options doivent être plausibles mais une seule doit être correcte
    - L'explication doit être pédagogique et aider à comprendre pourquoi la réponse est correcte
    - Respecte strictement le format JSON demandé
    """
