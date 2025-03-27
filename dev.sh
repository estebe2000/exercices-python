#!/bin/bash

# Script de démarrage pour l'application Générateur d'Exercices Python en mode développement

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python 3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si pip est installé
if ! command -v pip3 &> /dev/null; then
    echo "pip3 n'est pas installé. Veuillez l'installer avant de continuer."
    exit 1
fi

# Vérifier si l'environnement virtuel existe, sinon le créer
if [ ! -d ".venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv .venv
fi

# Activer l'environnement virtuel
source .venv/bin/activate

# Installer ou mettre à jour les dépendances
echo "Installation des dépendances..."
pip install -r requirements.txt

# Vérifier si le fichier .env existe, sinon le créer à partir de .env.example
if [ ! -f ".env" ]; then
    echo "Création du fichier .env à partir de .env.example..."
    cp .env.example .env
    echo "Veuillez éditer le fichier .env pour configurer les variables d'environnement."
fi

# Démarrer l'application en mode développement
echo "Démarrage de l'application en mode développement..."
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
