# Générateur d'Exercices Python avec IA et GED

Une application web interactive pour générer des exercices de programmation Python personnalisés pour les élèves de lycée (Première et Terminale), avec évaluation automatique du code par intelligence artificielle et gestion électronique de documents (GED).

![Logo du projet](static/logo.jpg)

## Fonctionnalités

### Générateur d'exercices
- **Génération d'exercices personnalisés** : Création d'énoncés adaptés au niveau des élèves (Première, Terminale ou SNT)
- **Thèmes variés** : Couvre différents concepts de programmation Python selon le programme scolaire
- **Niveaux de difficulté** : Exercices adaptables selon les compétences des élèves
- **Mode débutant** : Option pour générer des exercices sans fonctions ni classes, adaptés aux débutants
- **Éditeur de code intégré** : Interface conviviale avec coloration syntaxique
- **Exécution de code en temps réel** : Test immédiat des solutions proposées
- **Évaluation automatique** : Analyse du code et suggestions d'amélioration par IA
- **Double moteur d'IA** : Compatible avec LocalAI (Mistral) et Google Gemini

### Gestion Électronique de Documents (GED)
- **Upload de fichiers** : Possibilité d'uploader des documents de différents formats
- **Gestion par tags** : Organisation des documents avec un système de tags
- **Recherche avancée** : Recherche de documents par nom ou par tag
- **Modification des métadonnées** : Édition du nom et des tags des documents
- **Visualisation intégrée** : Affichage des documents directement dans le navigateur

## Prérequis

- Python 3.8 ou supérieur
- LocalAI installé et configuré (pour le mode local) ou une clé API Gemini (pour le mode cloud)
- Navigateur web moderne

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/generateur-exercices-python.git
   cd generateur-exercices-python
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

Au lieu d'utiliser un fichier `.env`, vous devez modifier le fichier `ai_provider.py` pour configurer votre fournisseur d'IA préféré.

Ouvrez `ai_provider.py` et modifiez les paramètres suivants :

```python
# Configuration pour LocalAI
LOCALAI_URL = "http://127.0.0.1:8080/v1/chat/completions"
LOCALAI_MODEL = "mistral-7b-instruct-v0.3"

# Configuration pour Gemini
GEMINI_API_KEY = "YOUR_API_KEY"  # Remplacez par votre clé API Gemini
GEMINI_MODEL = "gemini-2.0-flash"
```

### Recommandations de Configuration

#### Pour LocalAI :
- Assurez-vous que votre instance LocalAI est correctement configurée et accessible
- Vérifiez que l'URL pointe vers le bon endpoint de votre serveur LocalAI
- Utilisez le modèle Mistral approprié à votre installation

#### Pour Gemini :
- **IMPORTANT** : Remplacez `"YOUR_API_KEY"` par votre véritable clé API Gemini
- La clé API doit être gardée confidentielle
- Ne commitez jamais votre clé API dans le dépôt Git

Options de configuration :
- Sélectionnez le fournisseur d'IA en modifiant la variable `AI_PROVIDER` dans `ai_provider.py`
  - `AI_PROVIDER = 'localai'` pour utiliser LocalAI
  - `AI_PROVIDER = 'gemini'` pour utiliser Google Gemini

## Utilisation

1. Démarrez l'application :
   ```bash
   python app.py
   ```

2. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

### Générateur d'exercices

1. Accédez à l'onglet "Générateur d'exercices" (page d'accueil)

2. Sélectionnez le niveau scolaire, le thème et la difficulté pour générer un exercice
   - Pour les débutants, choisissez un exercice marqué comme "Débutant" (SNT par exemple)

3. Écrivez votre code dans l'éditeur intégré

4. Exécutez et évaluez votre code directement dans l'interface

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
  "Niveau": [
    {
      "thème": "Nom du thème",
      "niveaux": [
        {
          "niveau": 1,
          "description": "Description de l'exercice",
          "debutant": true  // Optionnel, true pour les exercices sans fonctions/classes
        }
      ]
    }
  ]
}
```

Vous pouvez enrichir ce fichier avec de nouveaux thèmes et exercices en respectant cette structure.

### Structure de la base de données GED

La GED utilise une base de données SQLite avec les tables suivantes :

1. **documents** : Stocke les métadonnées des documents
   - `id` : Identifiant unique du document (UUID)
   - `name` : Nom du document
   - `upload_date` : Date d'upload du document
   - `file_path` : Chemin vers le fichier physique

2. **tags** : Stocke les tags disponibles
   - `id` : Identifiant unique du tag
   - `name` : Nom du tag

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

## Licence

Ce projet est sous licence [MIT](LICENSE).

## Crédits

- Développé pour l'Éducation Nationale
- Utilise [LocalAI](https://github.com/go-skynet/LocalAI) et [Gemini API](https://ai.google.dev/)
- Interface basée sur Bootstrap et CodeMirror
