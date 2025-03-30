@echo off
echo ===================================================
echo Installation du Generateur d'Exercices Python
echo ===================================================
echo.

REM Vérifier si Python est installé
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe ou n'est pas dans le PATH.
    echo Veuillez installer Python 3.8 ou superieur depuis https://www.python.org/downloads/
    echo Assurez-vous de cocher l'option "Add Python to PATH" lors de l'installation.
    pause
    exit /b 1
)

REM Vérifier la version de Python
for /f "tokens=2" %%I in ('python --version 2^>^&1') do set PYTHON_VERSION=%%I
echo Version de Python detectee: %PYTHON_VERSION%

REM Créer un environnement virtuel
echo.
echo Creation de l'environnement virtuel...
if exist .venv (
    echo L'environnement virtuel existe deja.
) else (
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo Erreur lors de la creation de l'environnement virtuel.
        pause
        exit /b 1
    )
    echo Environnement virtuel cree avec succes.
)

REM Activer l'environnement virtuel
echo.
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate
if %errorlevel% neq 0 (
    echo Erreur lors de l'activation de l'environnement virtuel.
    pause
    exit /b 1
)
echo Environnement virtuel active avec succes.

REM Installer les dépendances
echo.
echo Installation des dependances...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b 1
)
echo Dependances installees avec succes.

REM Créer le fichier .env s'il n'existe pas
echo.
if exist .env (
    echo Le fichier .env existe deja.
) else (
    echo Creation du fichier .env...
    echo FLASK_SECRET_KEY=dev_key_123 > .env
    echo GEMINI_API_KEY=votre_cle_gemini >> .env
    echo MISTRAL_API_KEY=votre_cle_mistral >> .env
    echo Fichier .env cree avec succes.
    echo N'oubliez pas de remplacer les cles API par vos propres cles dans le fichier .env.
)

REM Créer le dossier uploads s'il n'existe pas
echo.
if exist uploads (
    echo Le dossier uploads existe deja.
) else (
    echo Creation du dossier uploads...
    mkdir uploads
    echo Dossier uploads cree avec succes.
)

REM Initialiser la base de données
echo.
echo Initialisation de la base de donnees...
flask init-db
if %errorlevel% neq 0 (
    echo Erreur lors de l'initialisation de la base de donnees.
    pause
    exit /b 1
)
echo Base de donnees initialisee avec succes.

echo.
echo ===================================================
echo Installation terminee avec succes !
echo.
echo Pour demarrer l'application, executez:
echo python app.py
echo.
echo Puis ouvrez votre navigateur a l'adresse:
echo http://127.0.0.1:5000
echo ===================================================
echo.

pause
