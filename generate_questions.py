"""
Script pour générer des questions QCM pour tous les niveaux.

Ce script utilise le module qcm_generator pour générer des questions QCM
pour tous les niveaux et les ajouter au fichier JSON.
"""

import sys
from qcm_generator import add_questions_to_level, THEMES

def main():
    """Fonction principale du script."""
    # Générer des questions pour chaque niveau
    for level in THEMES.keys():
        print(f"Génération de questions pour {level}...")
        count = add_questions_to_level(level, count=10)
        print(f"  {count} questions ajoutées.")

if __name__ == "__main__":
    main()
