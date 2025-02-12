import sys
import socket

def main():
    # Vérification de l'argument passé pour l'adresse du serveur
    if len(sys.argv) < 2:
        print("Erreur : Veuillez spécifier l'adresse du serveur.")
        sys.exit(1)

    hostname_serveur = sys.argv[1]  # Adresse du serveur passée en argument
    port_serveur = 2910
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect((hostname_serveur, port_serveur))
        print(f"Connecté au serveur {hostname_serveur} sur le port {port_serveur}")
    except (socket.error, socket.gaierror) as e:
        print(f"Erreur de connexion : {e}")
        sys.exit(1)
    
    while True:
        # Recevoir les données envoyées par le serveur
        data = client.recv(1024).decode()
        print(data)  # Affiche la grille ou un message final du serveur
        
        # Vérification si la partie est terminée
        if "a gagné" in data or "Match nul" in data or "Vous avez perdu" in data:
            # Demander si le joueur veut rejouer
            replay = input("Voulez-vous jouer une nouvelle partie ? (oui/non): ").strip().lower()
            if replay != 'oui':
                break  # Si l'utilisateur ne veut pas rejouer, on quitte le programme
            else:
                # Demander au serveur de démarrer une nouvelle partie
                client.send("oui".encode())  # Message pour le serveur
                continue  # Revenir au début pour jouer une nouvelle partie
        
        # Si le message contient "coup", demander au joueur de jouer
        if "Entrez votre coup" in data or "Votre tour" in data:
            shot = -1
            while shot < 0 or shot >= 9:
                try:
                    shot = int(input("Entrez votre coup (0-8): "))
                except ValueError:
                    print("Veuillez entrer un nombre valide entre 0 et 8.")
            
            # Envoyer le coup au serveur
            client.send(str(shot).encode())
    
    client.close()

if __name__ == "__main__":
    main()
