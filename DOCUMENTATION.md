# Documentation Technique - Générateur d'Exercices Python avec IA et GED

Ce document fournit une documentation technique détaillée du projet "Générateur d'Exercices Python avec IA et GED". Il complète le [README.md](README.md) en apportant des informations approfondies sur les aspects techniques et fonctionnels.

## Table des matières

1. [Fonctionnalités détaillées](#fonctionnalités-détaillées)
2. [Architecture technique](#architecture-technique)
3. [Sécurité et sandbox Python](#sécurité-et-sandbox-python)
4. [Modèles d'IA et configuration](#modèles-dia-et-configuration)
5. [Structure des données](#structure-des-données)
6. [Base de données GED](#base-de-données-ged)
7. [Utilisation avancée](#utilisation-avancée)
8. [Déploiement](#déploiement)
9. [Sécurité et confidentialité](#sécurité-et-confidentialité)

## Fonctionnalités détaillées

### Interface utilisateur
- **Fenêtre de bienvenue** : Popup d'accueil présentant les fonctionnalités de l'application aux nouveaux utilisateurs
- **Interface intuitive** : Navigation simple et claire avec barre de menu et tooltips
- **Aide contextuelle** : Guide d'utilisation détaillé accessible à tout moment via le menu d'aide
- **Expérience personnalisée** : Option "Ne plus afficher" pour la fenêtre de bienvenue
- **Design responsive** : Interface adaptée à différentes tailles d'écran
- **Bac à sable Python** : Environnement d'expérimentation libre avec éditeur de code et console de sortie
- **Sélecteur de rôle** : Possibilité de basculer entre les vues Admin, Professeur et Étudiant pour tester différentes interfaces
- **Thème clair/sombre** : Option de basculement entre thème clair et sombre avec détection automatique des préférences système

### Système de rôles
- **Vue Admin** : Accès complet à toutes les fonctionnalités, y compris la GED, l'éditeur d'exercices et la configuration
- **Vue Professeur** : Accès à la GED et aux fonctionnalités d'enseignement, sans les options d'administration
- **Vue Étudiant** : Accès uniquement aux fonctionnalités d'apprentissage (exercices, cours, bac à sable)
- **Persistance des préférences** : Mémorisation du rôle sélectionné entre les sessions grâce au stockage local
- **Interface adaptative** : Affichage des éléments de menu et des fonctionnalités selon le rôle sélectionné

### Générateur d'exercices
- **Génération d'exercices personnalisés** : Création d'énoncés adaptés au niveau des élèves (Troisième, SNT, Prépa NSI, Première, Terminale)
- **Thèmes variés** : Couvre différents concepts de programmation Python selon le programme scolaire
- **Niveaux de difficulté** : Exercices adaptables selon les compétences des élèves (5 niveaux de difficulté)
- **Mode débutant** : Exercices sans fonctions ni classes pour les niveaux Troisième, SNT et Prépa NSI, adaptés aux débutants
- **Squelettes de code à compléter** : Structure de code avec parties à remplir par l'élève (zones "# À COMPLÉTER"), garantissant une approche pédagogique progressive
- **Éditeur de code intégré** : Interface conviviale avec coloration syntaxique et indentation automatique
- **Exécution de code en temps réel** : Test immédiat des solutions proposées
- **Support de la fonction input()** : Possibilité d'exécuter du code interactif avec saisie utilisateur
- **Évaluation automatique** : Analyse du code et suggestions d'amélioration par IA
- **Triple moteur d'IA** : Compatible avec LocalAI (Mistral), Google Gemini et Mistral Codestral
- **Export en notebook Jupyter** : Téléchargement des exercices au format .ipynb pour une utilisation hors ligne

### Gestion Électronique de Documents (GED)
- **Upload de fichiers** : Possibilité d'uploader des documents de différents formats
- **Gestion par tags** : Organisation des documents avec un système de tags
- **Recherche avancée** : Recherche de documents par nom ou par tag
- **Modification des métadonnées** : Édition du nom et des tags des documents
- **Visualisation intégrée** : Affichage des documents directement dans le navigateur
- **Marquage de cours** : Possibilité de marquer des documents comme cours pour les afficher dans l'onglet Cours

### Bibliothèque de Cours
- **Affichage en style bibliothèque** : Présentation visuelle des documents marqués comme cours
- **Mode lecture** : Consultation facile des documents de cours directement dans le navigateur
- **Filtrage par tags** : Organisation des cours par thématiques
- **Recherche de cours** : Recherche par nom dans la bibliothèque de cours
- **Interface visuelle** : Présentation des cours sous forme de cartes avec nom, description et tags

## Architecture technique

L'application est construite avec les technologies suivantes :

- **Backend** : Flask (Python)
- **Frontend** : HTML, CSS, JavaScript, Bootstrap 5
- **Base de données** : SQLite (pour la GED)
- **Éditeur de code** : CodeMirror
- **IA** : LocalAI (Mistral), Google Gemini API, Mistral API

### Structure des fichiers

```
exercices-python/
├── app.py                  # Point d'entrée de l'application
├── ai_providers.py         # Gestion des fournisseurs d'IA
├── code_execution.py       # Exécution sécurisée de code Python
├── code_sandbox.py         # Sandbox pour l'exécution sécurisée
├── models.py               # Modèles de données
├── utils.py                # Fonctions utilitaires
├── prompts.py              # Templates de prompts pour l'IA
├── notebook_generator.py   # Génération de notebooks Jupyter
├── requirements.txt        # Dépendances Python
├── .env                    # Variables d'environnement (non versionné)
├── static/                 # Fichiers statiques (CSS, JS, images)
├── templates/              # Templates HTML (Jinja2)
├── routes/                 # Routes Flask organisées par fonctionnalité
├── instance/               # Données d'instance (base de données)
├── uploads/                # Fichiers uploadés pour la GED
├── logs/                   # Logs de l'application
└── exercices/              # Données des exercices
    └── data.json           # Définition des exercices
```

## Sécurité et sandbox Python

L'application utilise un système de sandbox pour exécuter le code Python de manière sécurisée. Ce système est implémenté dans les fichiers `code_sandbox.py` et `code_execution.py`.

### Fonctionnalités de sécurité

- **Limitation du temps d'exécution** : Timeout de 60 secondes pour éviter les boucles infinies
- **Limitation de la mémoire** : Restriction de l'utilisation de la mémoire (100 Mo par défaut)
- **Limitation des instructions** : Maximum de 1 000 000 instructions pour éviter les codes trop complexes
- **Analyse statique du code** : Détection des appels dangereux, imports non autorisés et boucles potentiellement infinies
- **Environnement d'exécution restreint** : Accès limité aux fonctions et modules Python
- **Exécution dans un thread séparé** : Isolation du code exécuté

### Support de la fonction input()

L'application prend en charge la fonction `input()` de deux manières :

1. **Mode synchrone** : Pour les codes simples sans `input()`, exécution directe dans le sandbox
2. **Mode asynchrone** : Pour les codes utilisant `input()`, utilisation de la classe `AsyncCodeExecutor` qui :
   - Exécute le code dans un thread séparé
   - Détecte les appels à `input()`
   - Affiche une boîte de dialogue pour permettre à l'utilisateur de saisir une valeur
   - Reprend l'exécution avec la valeur fournie

### Modules préchargés

Le bac à sable Python inclut plusieurs bibliothèques préchargées :

- **Calcul scientifique** : numpy (np), pandas (pd), scipy, sympy (sp), matplotlib (plt)
- **Traitement de texte** : re, string, nltk, textblob
- **Bibliothèque standard** : math, random, statistics

Ces modules sont disponibles sans avoir à les importer explicitement, ce qui simplifie l'écriture de code pour les débutants.

## Modèles d'IA et configuration

L'application propose trois modèles d'IA différents, chacun avec ses avantages :

### 1. LocalAI (Mistral)

- **Description** : Modèle hébergé localement sur votre machine
- **Avantages** : Fonctionne sans connexion internet, pas de coût d'API
- **Configuration** : Nécessite une installation de LocalAI sur votre machine
- **Recommandé pour** : Utilisation en classe sans connexion internet fiable

### 2. Google Gemini

- **Description** : Modèle en ligne de Google
- **Avantages** : Excellentes performances pour la génération d'exercices
- **Configuration** : Nécessite une clé API Gemini
- **Recommandé pour** : Génération d'exercices complexes et variés

### 3. Mistral Codestral

- **Description** : Modèle spécialisé pour le code via l'API Mistral
- **Avantages** : Particulièrement efficace pour l'évaluation de code Python
- **Configuration** : Nécessite une clé API Mistral
- **Recommandé pour** : Évaluation précise du code des élèves

### Configuration des modèles d'IA

La configuration des modèles d'IA se fait via le fichier `.env` :

```
GEMINI_API_KEY=votre_cle_gemini
MISTRAL_API_KEY=votre_cle_mistral
```

Le choix du modèle se fait via l'interface de configuration de l'application ou en modifiant la variable `AI_PROVIDER` dans `ai_provider.py` :

```python
AI_PROVIDER = 'localai'  # ou 'gemini' ou 'mistral'
```

### Améliorations des prompts

Les prompts utilisés pour communiquer avec l'IA sont définis dans le fichier `prompts.py`. Ils sont optimisés pour :

- **Génération d'exercices** : Création d'énoncés clairs avec 3-5 zones à compléter
- **Évaluation de code** : Analyse du code et suggestions d'amélioration
- **Structure HTML standardisée** : Utilisation de balises spécifiques pour les succès, erreurs, suggestions et améliorations

## Structure des données

### Exercices (data.json)

Les exercices sont définis dans le fichier `exercices/data.json` avec la structure suivante :

```json
{
  "Niveau Scolaire": [
    {
      "thème": "Nom du thème",
      "niveaux": [
        {
          "niveau": 1,
          "description": "Description de l'exercice",
          "debutant": true  // true pour les exercices sans fonctions/classes
        }
      ]
    }
  ]
}
```

L'application prend en charge les niveaux scolaires suivants, organisés du plus avancé au plus débutant:

1. **Terminale Générale** (`"debutant": false`) - Exercices avancés pour les élèves de Terminale
2. **Première Générale** (`"debutant": false`) - Exercices intermédiaires pour les élèves de Première
3. **Prépa NSI** (`"debutant": true`) - Exercices de préparation à la NSI
4. **SNT** (`"debutant": true`) - Exercices de Sciences Numériques et Technologie
5. **Troisième** (`"debutant": true`) - Exercices d'initiation pour les élèves de Troisième

### Génération de squelettes de code

L'application génère automatiquement des squelettes de code à compléter pour chaque exercice. Ces squelettes sont conçus pour:

- Fournir une structure de base que l'élève doit compléter
- Inclure des commentaires explicatifs indiquant les parties à remplir
- Contenir des tests pour vérifier la solution

Exemple de squelette de code généré:

```python
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
    print("Forme non reconnue")

# Tests - NE PAS SÉPARER DU CODE CI-DESSUS
try:
    assert aire == 15  # Test pour le rectangle
    print('✅ Test 1 réussi: aire du rectangle == 15')
except AssertionError:
    print('❌ Test 1 échoué: aire du rectangle devrait être 15')
```

## Base de données GED

La GED utilise une base de données SQLite avec les tables suivantes :

### 1. documents

Stocke les métadonnées des documents :
- `id` : Identifiant unique du document (UUID)
- `nom_fichier` : Nom du document
- `nom_unique` : Identifiant unique pour le fichier physique
- `date_upload` : Date d'upload du document
- `taille_fichier` : Taille du fichier en octets
- `type_mime` : Type MIME du fichier
- `description` : Description optionnelle du document
- `user_id` : Identifiant de l'utilisateur (pour usage futur)
- `est_cours` : Booléen indiquant si le document est un cours

### 2. tags

Stocke les tags disponibles :
- `id` : Identifiant unique du tag
- `nom` : Nom du tag

### 3. document_tags

Table de relation many-to-many entre documents et tags :
- `document_id` : Référence à un document
- `tag_id` : Référence à un tag

Les fichiers physiques sont stockés dans le dossier `uploads/` avec leur UUID comme nom de fichier.

## Utilisation avancée

### Utilisation de la fonction input()

L'application prend en charge la fonction `input()` pour créer des exercices interactifs :

1. Écrivez du code qui utilise la fonction `input()` pour demander des entrées à l'utilisateur
2. Cliquez sur le bouton "Exécuter le code"
3. L'application détecte automatiquement l'utilisation de `input()` et affiche une boîte de dialogue
4. Saisissez votre réponse et cliquez sur "Soumettre"
5. L'exécution du code reprend avec la valeur que vous avez fournie

Exemple de code utilisant `input()` :
```python
# Demander le nom de l'utilisateur
nom = input("Entrez votre nom : ")

# Saluer l'utilisateur
print(f"Bonjour, {nom} !")

# Demander l'âge de l'utilisateur
age_str = input("Entrez votre âge : ")

# Convertir l'âge en entier
try:
    age = int(age_str)
    
    # Afficher un message différent selon l'âge
    if age < 18:
        print("Vous êtes mineur.")
    else:
        print("Vous êtes majeur.")
except ValueError:
    print("L'âge que vous avez entré n'est pas un nombre valide.")
```

### Notebooks Jupyter

L'application permet de télécharger les exercices générés au format notebook Jupyter (.ipynb) :

1. Après avoir généré un exercice, cliquez sur le bouton "Télécharger en notebook Jupyter"
2. Donnez un titre à votre notebook
3. Cliquez sur "Télécharger"
4. Le notebook sera téléchargé sur votre ordinateur au format .ipynb

Les notebooks générés contiennent :
- L'énoncé de l'exercice formaté en Markdown
- Le squelette de code à compléter
- Les tests pour vérifier la solution

### Raccourcis clavier

Le bac à sable Python prend en charge plusieurs raccourcis clavier :
- **Ctrl+Enter** : Exécuter le code
- **Ctrl+S** : Télécharger le code
- **Ctrl+O** : Ouvrir un fichier

## Déploiement

### Déploiement sur la Forge Éducation

Pour déployer cette application sur la Forge Éducation :

1. Assurez-vous que tous les fichiers nécessaires sont présents :
   - Code source de l'application
   - Fichier `requirements.txt`
   - Fichier `ai_provider.py` avec la configuration appropriée
   - Dossier `exercices` avec le fichier `data.json`

2. Configurez les paramètres dans `ai_provider.py` selon l'environnement de la Forge Éducation

3. Suivez les instructions spécifiques de déploiement de la Forge Éducation

### Déploiement sur un serveur web

Pour déployer l'application sur un serveur web standard :

1. Clonez le dépôt sur votre serveur
2. Installez les dépendances avec `pip install -r requirements.txt`
3. Configurez un serveur WSGI (Gunicorn, uWSGI, etc.) pour servir l'application Flask
4. Configurez un serveur web (Nginx, Apache, etc.) comme proxy inverse
5. Configurez les variables d'environnement dans le fichier `.env`
6. Initialisez la base de données avec `flask init-db`
7. Créez le dossier `uploads` avec les permissions appropriées

Exemple de configuration Nginx :
```nginx
server {
    listen 80;
    server_name votre-domaine.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

Exemple de lancement avec Gunicorn :
```bash
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

## Sécurité et confidentialité

### Sécurité des clés API

- Ne partagez jamais vos clés API publiquement
- Utilisez des variables d'environnement ou des mécanismes sécurisés pour stocker les clés sensibles
- Rotez régulièrement vos clés API

### Sécurité de l'exécution de code

L'application utilise plusieurs mécanismes pour sécuriser l'exécution de code Python :

1. **Analyse statique** : Détection des appels dangereux, imports non autorisés et boucles potentiellement infinies
2. **Environnement restreint** : Accès limité aux fonctions et modules Python
3. **Limitation des ressources** : Restriction du temps d'exécution, de la mémoire et du nombre d'instructions
4. **Exécution isolée** : Exécution du code dans un thread séparé

Ces mécanismes permettent d'exécuter du code Python de manière sécurisée, tout en offrant une expérience utilisateur fluide.

### Confidentialité des données

L'application ne collecte pas de données personnelles. Les fichiers uploadés dans la GED sont stockés localement sur le serveur et ne sont pas partagés avec des tiers.

Si vous déployez l'application dans un environnement de production, assurez-vous de :
- Configurer HTTPS pour chiffrer les communications
- Mettre en place une politique de sauvegarde pour les données importantes
- Limiter l'accès à l'application aux utilisateurs autorisés
