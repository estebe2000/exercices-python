# Exemple d'utilisation de la fonction input()

# Demander le nom de l'utilisateur
nom = input("Entrez votre nom : ")

# Saluer l'utilisateur
print(f"Bonjour, {nom} !")

# Demander l'âge de l'utilisateur
age_str = input("Entrez votre âge : ")

# Convertir l'âge en entier
try:
    age = int(age_str)
    
    # Afficher un message différent selon l'âge
    if age < 18:
        print("Vous êtes mineur.")
    else:
        print("Vous êtes majeur.")
        
    # Calculer l'année de naissance approximative
    import datetime
    annee_actuelle = datetime.datetime.now().year
    annee_naissance = annee_actuelle - age
    
    print(f"Vous êtes né(e) aux alentours de {annee_naissance}.")
    
except ValueError:
    print("L'âge que vous avez entré n'est pas un nombre valide.")

# Jeu de devinette simple
print("\nJouons à un jeu de devinette !")
nombre_secret = 42
essai = input("Devinez un nombre entre 1 et 100 : ")

try:
    essai = int(essai)
    
    if essai == nombre_secret:
        print("Bravo ! Vous avez deviné le nombre secret !")
    elif essai < nombre_secret:
        print("Trop petit ! Le nombre secret est plus grand.")
    else:
        print("Trop grand ! Le nombre secret est plus petit.")
        
except ValueError:
    print("Ce n'est pas un nombre valide.")

print("\nMerci d'avoir testé cet exemple d'utilisation de input() !")
