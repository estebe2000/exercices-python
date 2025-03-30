# Générateur d'Exercices Python avec IA et GED

Une application web interactive pour générer des exercices de programmation Python personnalisés pour les élèves de collège et lycée, avec évaluation automatique du code par intelligence artificielle et gestion électronique de documents (GED).

![Logo du projet](static/logo.jpg)

## Présentation

Cette application permet aux enseignants et aux élèves de :
- Générer des exercices Python adaptés à différents niveaux scolaires (Troisième à Terminale)
- Exécuter et évaluer du code Python directement dans le navigateur
- Gérer des documents pédagogiques avec un système de GED
- Consulter une bibliothèque de cours organisée par thèmes
- Expérimenter avec un bac à sable Python incluant des bibliothèques scientifiques

Pour plus de détails sur les fonctionnalités et les aspects techniques, consultez la [documentation complète](DOCUMENTATION.md).

## Installation

### Installation automatique (recommandée)

#### Windows
```bash
git clone https://github.com/estebe2000/exercices-python.git
cd exercices-python
install_windows.bat
```

#### Linux/macOS
```bash
git clone https://github.com/estebe2000/exercices-python.git
cd exercices-python
chmod +x install_linux.sh
./install_linux.sh
```

### Installation manuelle

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

4. Créez un fichier `.env` avec les variables suivantes :
   ```
   FLASK_SECRET_KEY=dev_key_123
   GEMINI_API_KEY=votre_cle_gemini
   MISTRAL_API_KEY=votre_cle_mistral
   ```

5. Initialisez la base de données pour la GED :
   ```bash
   flask init-db
   ```

6. Créez le dossier pour les uploads s'il n'existe pas :
   ```bash
   mkdir -p uploads
   ```

7. Démarrez l'application :
   ```bash
   python app.py
   ```

8. Ouvrez votre navigateur à l'adresse : http://127.0.0.1:5000

## Dépannage

### Erreur "Internal Server Error" dans la GED

Si vous rencontrez une erreur lors de l'accès à la GED :

1. Assurez-vous que la base de données a été initialisée :
   ```bash
   flask init-db
   ```

2. Vérifiez que le dossier `uploads` existe :
   ```bash
   mkdir -p uploads
   ```

3. Vérifiez les permissions des dossiers `instance` et `uploads`.

### Problèmes avec les modèles d'IA

1. Pour LocalAI : vérifiez que votre instance LocalAI est en cours d'exécution.

2. Pour Gemini/Mistral : vérifiez que vos clés API sont correctement configurées dans le fichier `.env`.

3. Consultez les logs dans le dossier `logs/` pour plus de détails sur les erreurs.

## TODO

### Prochaines fonctionnalités
- [ ] Authentification et gestion des utilisateurs
- [ ] Système de suivi de progression pour les élèves
- [ ] Intégration avec les ENT (Environnements Numériques de Travail)
- [ ] Support de p5.js pour les exercices graphiques
- [ ] Support de Turtle pour l'apprentissage visuel
- [ ] RAG (Retrieval Augmented Generation) pour la génération de cours

### Améliorations techniques
- [ ] Optimisation des performances pour les grands fichiers
- [ ] Tests unitaires et d'intégration
- [ ] Documentation API pour les développeurs
- [ ] Support Docker pour faciliter le déploiement

## Crédits

- D'après une idée originale de [David Roche](https://www.linkedin.com/in/david-roche-34b9a024a/)
- Développé pour l'Éducation Nationale
- Utilise [LocalAI](https://localai.io/), [Gemini API](https://ai.google.dev/) et [Mistral API](https://mistral.ai/)
- Interface basée sur Bootstrap et CodeMirror

## Licence

Ce projet est sous licence [MIT](LICENSE).
