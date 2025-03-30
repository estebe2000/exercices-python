"""
Script pour ajouter la colonne est_cours à la table document dans la base de données.
"""

import os
import sqlite3

# Chemin vers la base de données
DB_PATH = 'instance/ged.db'

def add_est_cours_column():
    """Ajoute la colonne est_cours à la table document."""
    # Vérifier si le fichier de base de données existe
    if not os.path.exists(DB_PATH):
        print(f"Erreur: Le fichier de base de données {DB_PATH} n'existe pas.")
        return False
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(document)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'est_cours' in columns:
            print("La colonne est_cours existe déjà dans la table document.")
            conn.close()
            return True
        
        # Ajouter la colonne est_cours avec une valeur par défaut de 0 (False)
        cursor.execute("ALTER TABLE document ADD COLUMN est_cours BOOLEAN DEFAULT 0")
        
        # Valider les modifications
        conn.commit()
        print("La colonne est_cours a été ajoutée avec succès à la table document.")
        
        # Fermer la connexion
        conn.close()
        return True
    
    except sqlite3.Error as e:
        print(f"Erreur SQLite: {e}")
        return False
    except Exception as e:
        print(f"Erreur: {e}")
        return False

if __name__ == "__main__":
    add_est_cours_column()
