import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env s'il existe
load_dotenv()

class Config:
    """Configuration de base pour l'application."""
    # Configuration Flask
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'exercices_python_secret_key')
    DEBUG = False
    TESTING = False
    
    # Configuration LocalAI
    LOCALAI_URL = os.environ.get('LOCALAI_URL', 'http://127.0.0.1:8080/v1/chat/completions')
    LOCALAI_MODEL = os.environ.get('LOCALAI_MODEL', 'mistral-7b-instruct-v0.3')
    
    # Configuration Gemini
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-2.0-flash')

class DevelopmentConfig(Config):
    """Configuration pour l'environnement de développement."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuration pour l'environnement de production."""
    # En production, assurez-vous que SECRET_KEY est défini dans les variables d'environnement
    pass

class TestingConfig(Config):
    """Configuration pour les tests."""
    TESTING = True
    DEBUG = True

# Dictionnaire des configurations disponibles
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

# Fonction pour obtenir la configuration en fonction de l'environnement
def get_config():
    """Retourne la configuration appropriée en fonction de l'environnement."""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
