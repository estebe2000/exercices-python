#!/bin/bash

echo "==================================================="
echo "Installation du Générateur d'Exercices Python"
echo "==================================================="
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "Python n'est pas installé ou n'est pas dans le PATH."
    echo "Veuillez installer Python 3.8 ou supérieur."
    echo "Sur Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "Sur Fedora: sudo dnf install python3 python3-pip"
    echo "Sur Arch: sudo pacman -S python python-pip"
    exit 1
fi

# Vérifier la version de Python
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "Version de Python détectée: $PYTHON_VERSION"

# Créer un environnement virtuel
echo ""
echo "Création de l'environnement virtuel..."
if [ -d ".venv" ]; then
    echo "L'environnement virtuel existe déjà."
else
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "Erreur lors de la création de l'environnement virtuel."
        exit 1
    fi
    echo "Environnement virtuel créé avec succès."
fi

# Activer l'environnement virtuel
echo ""
echo "Activation de l'environnement virtuel..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Erreur lors de l'activation de l'environnement virtuel."
    exit 1
fi
echo "Environnement virtuel activé avec succès."

# Installer les dépendances
echo ""
echo "Installation des dépendances..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Erreur lors de l'installation des dépendances."
    exit 1
fi
echo "Dépendances installées avec succès."

# Créer le fichier .env s'il n'existe pas
echo ""
if [ -f ".env" ]; then
    echo "Le fichier .env existe déjà."
else
    echo "Création du fichier .env..."
    cat > .env << EOF
FLASK_SECRET_KEY=dev_key_123
GEMINI_API_KEY=votre_cle_gemini
MISTRAL_API_KEY=votre_cle_mistral
EOF
    echo "Fichier .env créé avec succès."
    echo "N'oubliez pas de remplacer les clés API par vos propres clés dans le fichier .env."
fi

# Créer le dossier uploads s'il n'existe pas
echo ""
if [ -d "uploads" ]; then
    echo "Le dossier uploads existe déjà."
else
    echo "Création du dossier uploads..."
    mkdir -p uploads
    echo "Dossier uploads créé avec succès."
fi

# Initialiser la base de données
echo ""
echo "Initialisation de la base de données..."
flask init-db
if [ $? -ne 0 ]; then
    echo "Erreur lors de l'initialisation de la base de données."
    exit 1
fi
echo "Base de données initialisée avec succès."

echo ""
echo "==================================================="
echo "Installation terminée avec succès !"
echo ""
echo "Pour démarrer l'application, exécutez:"
echo "source .venv/bin/activate && python app.py"
echo ""
echo "Puis ouvrez votre navigateur à l'adresse:"
echo "http://127.0.0.1:5000"
echo "==================================================="
echo ""

# Rendre le script exécutable
chmod +x install_linux.sh
