# Générateur d'Exercices Python avec IA

Une application web permettant de générer des exercices de programmation Python personnalisés pour les élèves de lycée (Première et Terminale) et d'évaluer leur code.

## Fonctionnalités

- Génération d'exercices Python adaptés au niveau des élèves (Première ou Terminale)
- Sélection de thèmes spécifiques au programme scolaire
- Choix du niveau de difficulté
- Éditeur de code intégré avec coloration syntaxique
- Exécution du code directement dans l'application
- Évaluation automatique du code avec retours personnalisés
- Support de deux modèles d'IA : LocalAI (Mistral) et Google Gemini

## Prérequis

- Python 3.8 ou supérieur
- LocalAI installé et configuré avec le modèle mistral-7b-instruct-v0.3 (pour le mode LocalAI)
- Une clé API Google Gemini (pour le mode Gemini)

## Installation

1. Clonez ce dépôt :
   ```bash
   git clone [URL_DU_DEPOT]
   cd exercices-python
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv .venv
   # Sur Windows
   .venv\Scripts\activate
   # Sur Linux/macOS
   source .venv/bin/activate
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez les variables d'environnement (optionnel) :
   Créez un fichier `.env` à la racine du projet avec les variables suivantes :
   ```
   LOCALAI_URL=http://127.0.0.1:8080/v1/chat/completions
   LOCALAI_MODEL=mistral-7b-instruct-v0.3
   GEMINI_API_KEY=votre_clé_api_gemini
   FLASK_SECRET_KEY=une_clé_secrète_pour_flask
   ```

## Utilisation

1. Assurez-vous que LocalAI est en cours d'exécution (si vous utilisez le mode LocalAI) :
   ```bash
   # Exemple de commande pour démarrer LocalAI (à adapter selon votre installation)
   localai
   ```

2. Lancez l'application :
   ```bash
   python app.py
   ```

3. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

## Déploiement en production

Pour un déploiement en production, il est recommandé d'utiliser Gunicorn :

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

## Structure du projet

- `app.py` : Point d'entrée de l'application Flask
- `ai_providers.py` : Classes pour interagir avec les différents modèles d'IA
- `exercices/data.json` : Données des exercices par niveau et thème
- `static/` : Fichiers statiques (CSS, JavaScript, images)
- `templates/` : Templates HTML pour l'interface utilisateur

## Configuration des modèles d'IA

### LocalAI

L'application est configurée par défaut pour utiliser LocalAI avec le modèle mistral-7b-instruct-v0.3. Assurez-vous que LocalAI est correctement installé et configuré avec ce modèle.

### Google Gemini

Pour utiliser Google Gemini, vous devez obtenir une clé API et la configurer dans le fichier `ai_providers.py` ou via une variable d'environnement.

## Personnalisation des exercices

Les exercices disponibles sont définis dans le fichier `exercices/data.json`. Vous pouvez modifier ce fichier pour ajouter, supprimer ou modifier des thèmes et des niveaux de difficulté.

## Licence

[Insérer les informations de licence ici]

## Contact

[Insérer les informations de contact ici]
