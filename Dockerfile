# Utilisation d'une image Python officielle
FROM python:3.9-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copie des fichiers nécessaires
COPY requirements.txt .
COPY . .

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Création des répertoires nécessaires
RUN mkdir -p /app/uploads \
    && mkdir -p /app/logs \
    && mkdir -p /app/instance

# Exposition du port
EXPOSE 5000

# Commande de démarrage
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
