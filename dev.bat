@echo off
REM Script de démarrage pour l'application Générateur d'Exercices Python en mode développement (Windows)

REM Vérifier si Python est installé
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH. Veuillez l'installer avant de continuer.
    exit /b 1
)

REM Vérifier si pip est installé
pip --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo pip n'est pas installé ou n'est pas dans le PATH. Veuillez l'installer avant de continuer.
    exit /b 1
)

REM Vérifier si l'environnement virtuel existe, sinon le créer
if not exist .venv (
    echo Création de l'environnement virtuel...
    python -m venv .venv
)

REM Activer l'environnement virtuel
call .venv\Scripts\activate.bat

REM Installer ou mettre à jour les dépendances
echo Installation des dépendances...
pip install -r requirements.txt

REM Vérifier si le fichier .env existe, sinon le créer à partir de .env.example
if not exist .env (
    echo Création du fichier .env à partir de .env.example...
    copy .env.example .env
    echo Veuillez éditer le fichier .env pour configurer les variables d'environnement.
)

REM Démarrer l'application en mode développement
echo Démarrage de l'application en mode développement...
set FLASK_ENV=development
set FLASK_DEBUG=1
python app.py
