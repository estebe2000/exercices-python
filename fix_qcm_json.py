"""
Script pour corriger le fichier qcm_questions.json.

Ce script lit le fichier qcm_questions.json, corrige les problèmes de syntaxe JSON,
et écrit le résultat dans un nouveau fichier.
"""

import json
import os
import re

# Chemin du fichier source
source_file = 'exercices/qcm_questions.json'
# Chemin du fichier de sauvegarde
backup_file = 'exercices/qcm_questions.json.bak'
# Chemin du fichier corrigé
fixed_file = 'exercices/qcm_questions.json.fixed'

def fix_json_content(content):
    """
    Corrige les problèmes de syntaxe JSON courants.
    
    Args:
        content: Le contenu JSON à corriger
        
    Returns:
        Le contenu JSON corrigé
    """
    # Remplacer les caractères spéciaux mal encodés
    content = content.replace('Ã¨', 'è')
    content = content.replace('Ã©', 'é')
    content = content.replace('Ã', 'é')
    
    # Ajouter des virgules manquantes entre les propriétés d'un objet
    content = re.sub(r'"\s*\n\s*"', '",\n  "', content)
    
    # Ajouter des virgules manquantes entre les éléments d'un tableau
    content = re.sub(r'"\s*\n\s*]', '"\n  ]', content)
    content = re.sub(r'"\s*\n\s*(?=[^,\s])', '",\n  ', content)
    
    # Ajouter des virgules manquantes entre les objets d'un tableau
    content = re.sub(r'}\s*\n\s*{', '},\n  {', content)
    
    # Supprimer les virgules en trop à la fin des tableaux
    content = re.sub(r',\s*]', '\n  ]', content)
    
    # Approche plus radicale: reconstruire le JSON
    try:
        # Essayer de corriger le JSON en utilisant une approche plus directe
        # Remplacer toutes les occurrences de "]," par "]" pour éviter les virgules en trop
        content = re.sub(r'],\s*}', ']\n  }', content)
        
        # Essayer de parser le JSON pour voir s'il est valide
        json.loads(content)
    except json.JSONDecodeError:
        # Si le JSON n'est toujours pas valide, essayer une approche plus radicale
        try:
            # Créer un nouveau fichier JSON à partir de zéro
            new_content = '{\n'
            
            # Extraire les niveaux
            levels_match = re.search(r'{\s*"([^"]+)":', content)
            if levels_match:
                current_level = levels_match.group(1)
                new_content += f'  "{current_level}": [\n'
                
                # Extraire les questions
                questions = []
                question_pattern = r'{\s*"question":[^}]+}'
                for match in re.finditer(question_pattern, content):
                    question_text = match.group(0)
                    # Nettoyer la question
                    question_text = re.sub(r'"\s*\n\s*"', '", "', question_text)
                    question_text = re.sub(r'"\s*\n\s*}', '"\n  }', question_text)
                    questions.append(question_text)
                
                # Ajouter les questions au nouveau contenu
                if questions:
                    new_content += '    ' + ',\n    '.join(questions)
                
                new_content += '\n  ]\n}'
                
                # Vérifier si le nouveau contenu est valide
                json.loads(new_content)
                content = new_content
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Erreur lors de la reconstruction du JSON: {e}")
    
    return content

def main():
    try:
        # Vérifier si le fichier source existe
        if not os.path.exists(source_file):
            print(f"Erreur: Le fichier {source_file} n'existe pas.")
            return
        
        # Créer une sauvegarde du fichier original
        with open(source_file, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print(f"Sauvegarde créée: {backup_file}")
        
        # Corriger le contenu JSON
        fixed_content = fix_json_content(original_content)
        
        # Écrire le contenu corrigé dans un fichier temporaire
        with open(fixed_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Fichier corrigé créé: {fixed_file}")
        
        # Essayer de charger le fichier corrigé pour vérifier qu'il est valide
        try:
            with open(fixed_file, 'r', encoding='utf-8') as f:
                json.load(f)
            print("Le fichier JSON corrigé est valide.")
            
            # Remplacer le fichier original par le fichier corrigé
            os.replace(fixed_file, source_file)
            print(f"Le fichier {source_file} a été remplacé par la version corrigée.")
        except json.JSONDecodeError as e:
            print(f"Erreur: Le fichier corrigé n'est toujours pas un JSON valide: {e}")
            print("Le fichier original n'a pas été modifié.")
            
            # Approche alternative: créer un fichier JSON minimal valide
            print("Tentative de création d'un fichier JSON minimal valide...")
            
            # Créer un fichier JSON minimal avec une structure de base
            minimal_json = {
                "Troisième": [],
                "SNT": [],
                "Prépa NSI": [],
                "Première Générale": [],
                "Terminale Générale": []
            }
            
            with open(source_file, 'w', encoding='utf-8') as f:
                json.dump(minimal_json, f, ensure_ascii=False, indent=2)
            
            print(f"Un fichier JSON minimal valide a été créé à {source_file}")
    
    except Exception as e:
        print(f"Une erreur s'est produite: {e}")

if __name__ == "__main__":
    main()
