"""
Script de test pour vérifier le fonctionnement de la fonction input() dans le sandbox.

Ce script teste l'utilisation de la fonction input() dans le sandbox.
"""

from code_sandbox import execute_python_code_safely

# Code à tester
code_with_input = """
# Demander à l'utilisateur d'entrer son nom
nom = input("Entrez votre nom : ")
print(f"Bonjour, {nom} !")

# Demander à l'utilisateur d'entrer son âge
age = input("Entrez votre âge : ")
try:
    age = int(age)
    print(f"Dans 10 ans, vous aurez {age + 10} ans.")
except ValueError:
    print("L'âge doit être un nombre entier.")
"""

print("Test de la fonction input() dans le sandbox")
print("Veuillez répondre aux questions qui vont s'afficher...")
print("-" * 50)

# Exécuter le code avec input()
result = execute_python_code_safely(code_with_input)

print("-" * 50)
if result['error']:
    print(f"ERREUR: {result['error']}")
else:
    print(f"SORTIE: {result['output']}")
