# Configuration Gunicorn pour l'application

# Nombre de workers (processus)
# Une bonne pratique est de définir 2-4 x nombre de cœurs CPU
workers = 4

# Nombre de threads par worker
threads = 2

# Adresse et port d'écoute
bind = "0.0.0.0:8000"

# Timeout en secondes
timeout = 120

# Activer le rechargement automatique en développement
reload = False

# Niveau de journalisation
loglevel = "info"

# Fichier de journalisation
accesslog = "logs/access.log"
errorlog = "logs/error.log"

# Classe de worker
worker_class = "sync"

# Nombre maximum de requêtes qu'un worker traitera avant d'être redémarré
max_requests = 1000
max_requests_jitter = 50

# Préchargement de l'application pour de meilleures performances
preload_app = True
