"""
Script de test pour vérifier le fonctionnement du sandbox de code.

Ce script teste différents scénarios pour s'assurer que le sandbox protège
correctement contre les boucles infinies, les appels dangereux, etc.
"""

from code_sandbox import execute_python_code_safely

# Fichier de sortie pour les résultats
output_file = "test_results.txt"

def run_test(name, code):
    """Exécute un test et écrit le résultat dans un fichier."""
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"\n=== Test: {name} ===\n")
        f.write(f"Code à exécuter:\n{code}\n\n")
        
        result = execute_python_code_safely(code)
        
        if result['error']:
            f.write(f"ERREUR: {result['error']}\n")
            print(f"Test '{name}': ERREUR DÉTECTÉE ✓")
        else:
            f.write(f"SORTIE: {result['output']}\n")
            print(f"Test '{name}': Exécuté avec succès")
        
        f.write("=" * 50 + "\n")

# Initialiser le fichier de sortie
with open(output_file, "w", encoding="utf-8") as f:
    f.write("RÉSULTATS DES TESTS DE SÉCURITÉ DU SANDBOX\n")
    f.write("=" * 50 + "\n")

print("Exécution des tests de sécurité du sandbox...")

# Test 1: Code normal
run_test("Code normal", """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)

result = factorial(5)
print(f"Factorielle de 5 = {result}")
""")

# Test 2: Boucle infinie avec while True
run_test("Boucle infinie (while True)", """
while True:
    print("Ceci est une boucle infinie")
""")

# Test 3: Boucle avec un très grand nombre d'itérations
run_test("Boucle avec grand nombre d'itérations", """
for i in range(100000000):
    print(i)
""")

# Test 4: Appel à une fonction dangereuse (eval)
run_test("Appel à eval()", """
code = "print('Ceci est exécuté via eval()')"
eval(code)
""")

# Test 5: Tentative d'accès au système de fichiers
run_test("Accès au système de fichiers", """
with open('test.txt', 'w') as f:
    f.write('Ceci est un test')
""")

# Test 6: Tentative d'import d'un module non autorisé
run_test("Import non autorisé", """
import os
os.system('echo "Commande système exécutée"')
""")

# Test 7: Utilisation excessive de mémoire
run_test("Utilisation excessive de mémoire", """
# Tenter de créer une liste très grande
big_list = [i for i in range(50000000)]
print(len(big_list))
""")

# Test 8: Code avec une syntaxe invalide
run_test("Syntaxe invalide", """
if True
    print("Syntaxe incorrecte")
""")

# Test 9: Code qui fonctionne normalement avec numpy
run_test("Utilisation de numpy", """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
print(f"Moyenne: {np.mean(arr)}")
print(f"Écart-type: {np.std(arr)}")
""")

print("\nTous les tests ont été exécutés. Résultats détaillés dans le fichier:", output_file)
