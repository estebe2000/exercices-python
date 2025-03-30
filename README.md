# Générateur d'Exercices Python avec IA et GED

Une application web interactive pour générer des exercices de programmation Python personnalisés pour les élèves de collège et lycée (Troisième, SNT, Prépa NSI, Première et Terminale), avec évaluation automatique du code par intelligence artificielle et gestion électronique de documents (GED).

![Logo du projet](static/logo.jpg)

## Démonstration en ligne

Une version de démonstration de l'application est disponible ici : [https://exercices-python.onrender.com/](https://exercices-python.onrender.com/)

## Fonctionnalités

### Interface utilisateur
- **Fenêtre de bienvenue** : Popup d'accueil présentant les fonctionnalités de l'application aux nouveaux utilisateurs
- **Interface intuitive** : Navigation simple et claire avec barre de menu et tooltips
- **Aide contextuelle** : Guide d'utilisation détaillé accessible à tout moment via le menu d'aide
- **Expérience personnalisée** : Option "Ne plus afficher" pour la fenêtre de bienvenue
- **Design responsive** : Interface adaptée à différentes tailles d'écran

### Générateur d'exercices
- **Génération d'exercices personnalisés** : Création d'énoncés adaptés au niveau des élèves (Troisième, SNT, Prépa NSI, Première, Terminale)
- **Thèmes variés** : Couvre différents concepts de programmation Python selon le programme scolaire
- **Niveaux de difficulté** : Exercices adaptables selon les compétences des élèves (5 niveaux de difficulté)
- **Mode débutant** : Exercices sans fonctions ni classes pour les niveaux Troisième, SNT et Prépa NSI, adaptés aux débutants
- **Squelettes de code à compléter** : Structure de code avec parties à remplir par l'élève (zones "# À COMPLÉTER"), garantissant une approche pédagogique progressive
- **Éditeur de code intégré** : Interface conviviale avec coloration syntaxique et indentation automatique
- **Exécution de code en temps réel** : Test immédiat des solutions proposées
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

## Prérequis

- Python 3.8 ou supérieur
- LocalAI installé et configuré (pour le mode local) ou une clé API Gemini (pour le mode cloud)
- Navigateur web moderne

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/estebe2000/exercices-python.git
   cd exercices-python
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv .venv
   # Sur Windows
   .venv\Scripts\activate
   # Sur macOS/Linux
   source .venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Initialisez la base de données pour la GED :
   ```bash
   flask init-db
   ```

5. Créez le dossier pour les uploads s'il n'existe pas :
   ```bash
   mkdir -p uploads
   ```

## Configuration du Fournisseur d'IA

L'application utilise un fichier `.env` pour stocker les clés API. Créez/modifiez le fichier `.env` avec les variables suivantes :

```
GEMINI_API_KEY=votre_cle_gemini
MISTRAL_API_KEY=votre_cle_mistral
```

### Choix du modèle d'IA

L'application propose trois modèles d'IA différents, chacun avec ses avantages :

1. **LocalAI (Mistral)** : Modèle hébergé localement sur votre machine
   - Avantages : Fonctionne sans connexion internet, pas de coût d'API
   - Configuration : Nécessite une installation de LocalAI sur votre machine

2. **Google Gemini** : Modèle en ligne de Google
   - Avantages : Excellentes performances pour la génération d'exercices
   - Configuration : Nécessite une clé API Gemini

3. **Mistral Codestral** : Modèle spécialisé pour le code via l'API Mistral
   - Avantages : Particulièrement efficace pour l'évaluation de code Python
   - Configuration : Nécessite une clé API Mistral

Vous pouvez changer de modèle à tout moment via l'interface de configuration de l'application.

### Améliorations des prompts

**Pour la génération d'exercices :**
- Toujours inclure 3-5 zones à compléter (# À COMPLÉTER ou # VOTRE CODE ICI)
- Ne jamais fournir d'exercice déjà complet
- Pour Première/Terminale : 2 tests maximum
- Pour autres niveaux : pas de tests

**Pour l'évaluation de code :**
- Si le code ne fonctionne pas : 1 seule suggestion principale
- Si le code fonctionne : 3 suggestions maximum
- Structure HTML standardisée avec balises spécifiques :
  - ✅ pour les succès
  - ❌ pour les erreurs
  - 💡 pour les suggestions
  - 🚀 pour les améliorations

### Recommandations de Configuration

#### Pour LocalAI :
- Assurez-vous que votre instance LocalAI est correctement configurée et accessible
- Vérifiez que l'URL pointe vers le bon endpoint de votre serveur LocalAI
- Utilisez le modèle Codestral pour de meilleures performances avec le code Python

#### Pour Gemini :
- **IMPORTANT** : Remplacez `"YOUR_API_KEY"` par votre véritable clé API Gemini
- La clé API doit être gardée confidentielle
- Ne commitez jamais votre clé API dans le dépôt Git

Options de configuration :
- Sélectionnez le fournisseur d'IA en modifiant la variable `AI_PROVIDER` dans `ai_provider.py`
  - `AI_PROVIDER = 'localai'` pour utiliser LocalAI (recommandé avec Codestral)
  - `AI_PROVIDER = 'gemini'` pour utiliser Google Gemini
  - `AI_PROVIDER = 'mistral'` pour utiliser Mistral Codestral

## Utilisation

1. Démarrez l'application :
   ```bash
   python app.py
   ```

2. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

### Générateur d'exercices

1. Accédez à l'onglet "Générateur d'exercices" (page d'accueil)

2. Sélectionnez le niveau scolaire, le thème et la difficulté pour générer un exercice
   - Pour les débutants, choisissez un exercice marqué comme "Débutant" (Troisième, SNT ou Prépa NSI)

3. Écrivez votre code dans l'éditeur intégré

4. Exécutez et évaluez votre code directement dans l'interface

5. Téléchargez l'exercice au format notebook Jupyter si vous souhaitez y travailler hors ligne

### Éditeur de données d'exercices

1. Accédez à l'onglet "Éditeur de données"

2. Vous pouvez ajouter, modifier ou supprimer des niveaux scolaires, des thèmes et des exercices
   - Pour marquer un exercice comme "débutant", cochez la case correspondante lors de la création ou de la modification

### Gestion Électronique de Documents (GED)

1. Accédez à l'onglet "GED"

2. Pour ajouter un document :
   - Cliquez sur "Ajouter un document"
   - Sélectionnez un fichier à uploader
   - Ajoutez des tags pour organiser votre document
   - Cliquez sur "Enregistrer"

3. Pour rechercher des documents :
   - Utilisez la barre de recherche pour filtrer par nom
   - Cliquez sur un tag pour filtrer les documents par tag

4. Pour modifier un document :
   - Cliquez sur "Modifier" à côté du document
   - Modifiez le nom et/ou les tags
   - Cliquez sur "Enregistrer"

5. Pour supprimer un document :
   - Cliquez sur "Supprimer" à côté du document
   - Confirmez la suppression

6. Pour marquer un document comme cours :
   - Cliquez sur le bouton avec l'icône de livre à côté du document
   - Le bouton devient vert plein lorsque le document est marqué comme cours
   - Cliquez à nouveau pour retirer le document des cours

### Bibliothèque de Cours

1. Accédez à l'onglet "Cours"

2. Consultez les documents marqués comme cours, présentés en style bibliothèque
   - Les documents sont affichés sous forme de cartes avec leur nom, description et tags
   - Seuls les documents marqués comme cours dans l'onglet GED sont visibles ici

3. Pour rechercher des cours :
   - Utilisez la barre de recherche pour filtrer par nom
   - Utilisez le sélecteur de tags pour filtrer par tag

4. Pour consulter un cours :
   - Cliquez sur le bouton "Consulter" de la carte du document
   - Le document s'ouvrira dans un nouvel onglet du navigateur

### Notebooks Jupyter

1. Après avoir généré un exercice, cliquez sur le bouton "Télécharger en notebook Jupyter"

2. Donnez un titre à votre notebook

3. Cliquez sur "Télécharger"

4. Le notebook sera téléchargé sur votre ordinateur au format .ipynb

5. Ouvrez le notebook avec Jupyter Notebook, JupyterLab, Google Colab ou tout autre environnement compatible

## Déploiement sur la Forge Éducation

Pour déployer cette application sur la Forge Éducation :

1. Assurez-vous que tous les fichiers nécessaires sont présents :
   - Code source de l'application
   - Fichier `requirements.txt`
   - Fichier `ai_provider.py` avec la configuration appropriée
   - Dossier `exercices` avec le fichier `data.json`

2. Configurez les paramètres dans `ai_provider.py` selon l'environnement de la Forge Éducation

3. Suivez les instructions spécifiques de déploiement de la Forge Éducation

## Sécurité et Confidentialité

- Ne partagez jamais vos clés API publiquement
- Utilisez des variables d'environnement ou des mécanismes sécurisés pour stocker les clés sensibles
- Rotez régulièrement vos clés API

## Structure des données

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

Chaque niveau scolaire contient plusieurs thèmes, et chaque thème contient plusieurs exercices avec différents niveaux de difficulté (de 1 à 5).

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

Vous pouvez enrichir le fichier `data.json` avec de nouveaux thèmes et exercices en respectant la structure existante.

### Structure de la base de données GED

La GED utilise une base de données SQLite avec les tables suivantes :

1. **documents** : Stocke les métadonnées des documents
   - `id` : Identifiant unique du document (UUID)
   - `nom_fichier` : Nom du document
   - `nom_unique` : Identifiant unique pour le fichier physique
   - `date_upload` : Date d'upload du document
   - `taille_fichier` : Taille du fichier en octets
   - `type_mime` : Type MIME du fichier
   - `description` : Description optionnelle du document
   - `user_id` : Identifiant de l'utilisateur (pour usage futur)
   - `est_cours` : Booléen indiquant si le document est un cours

2. **tags** : Stocke les tags disponibles
   - `id` : Identifiant unique du tag
   - `nom` : Nom du tag

3. **document_tags** : Table de relation many-to-many entre documents et tags
   - `document_id` : Référence à un document
   - `tag_id` : Référence à un tag

Les fichiers physiques sont stockés dans le dossier `uploads/` avec leur UUID comme nom de fichier.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

## Dépannage

### Erreur "Internal Server Error" dans la GED

Si vous rencontrez une erreur "Internal Server Error" lors de l'accès à la GED, cela peut être dû à une base de données non initialisée ou corrompue. Pour résoudre ce problème:

1. Assurez-vous que la base de données a été initialisée:
   ```bash
   flask init-db
   ```
   Vous devriez voir le message "Base de données initialisée avec succès".

2. Vérifiez que le dossier `uploads` existe:
   ```bash
   mkdir -p uploads
   ```

3. Si vous réinitialisez la base de données, notez que les métadonnées des documents précédemment téléchargés (noms, tags, descriptions) seront perdues. Les fichiers physiques resteront dans le dossier `uploads`, mais ils ne seront plus référencés dans la base de données.

4. Pour éviter les problèmes de base de données:
   - Effectuez des sauvegardes régulières du fichier `instance/ged.db`
   - N'initialisez la base de données qu'une seule fois lors de l'installation initiale
   - Si vous déployez l'application sur un nouveau serveur, n'oubliez pas d'initialiser la base de données

### Limite de taille des fichiers

Par défaut, la taille maximale des fichiers pouvant être téléchargés est limitée à 16 Mo. Si vous avez besoin de télécharger des fichiers plus volumineux, vous pouvez modifier la valeur de `MAX_CONTENT_LENGTH` dans le fichier `app.py`.

## Roadmap et TODO

### Fonctionnalités déjà implémentées ✅
- Interface utilisateur avec fenêtre de bienvenue
- Générateur d'exercices Python avec différents niveaux de difficulté
- Éditeur de code intégré avec coloration syntaxique
- Exécution de code en temps réel
- Évaluation automatique par IA
- Gestion Électronique de Documents (GED)
- Support pour trois moteurs d'IA (LocalAI, Gemini, Mistral)
- Squelettes de code à compléter avec tests
- Export des exercices au format notebook Jupyter

### Fonctionnalités à venir 🚀
- **Authentification et autorisations**
  - Protection par login
  - Gestion des rôles (élève ou professeur)
  - Différents niveaux d'accès selon le rôle

- **Amélioration de l'IA**
  - RAG (Retrieval Augmented Generation) pour la génération de cours basés sur les documents fournis par l'enseignant
  - Système de scoring basé sur la qualité du code

- **Fonctionnalités pédagogiques avancées**
  - Support de la fonction `input()` pour les exercices interactifs
  - Intégration de p5.js pour les exercices graphiques
  - Support de Turtle pour l'apprentissage visuel
  - Envoi et récupération de fichiers
  - Profils élèves pour le suivi des progressions
  - Intégration avec les ENT (Environnements Numériques de Travail)

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Crédits

- D'après une idée originale de [David Roche](https://www.linkedin.com/in/david-roche-34b9a024a/)
- Développé pour l'Éducation Nationale
- Utilise [LocalAI](https://localai.io/) ([GitHub](https://github.com/mudler/LocalAI)) et [Gemini API](https://ai.google.dev/)
- Interface basée sur Bootstrap et CodeMirror
