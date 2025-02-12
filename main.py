import sys
import socket

def main():
    hostname_serveur = sys.argv[1]
    port_serveur = 2910
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((hostname_serveur, port_serveur))

    while True:
        data = client.recv(1024).decode()
        print(data)  

        if "a gagné" in data or "Match nul" in data or "Vous avez perdu" in data:
            # Affichage du score actuel
            print(data)

            replay = input("Voulez-vous jouer une nouvelle partie ? (oui/non): ").strip().lower()
            if replay != 'oui':
                break 
            else:
                client.send("oui".encode())  
                continue  
        if "Entrez votre coup" in data or "Votre tour" in data:
            shot = -1
            while shot < 0 or shot >= 9:
                try:
                    shot = int(input("Entrez votre coup (0-8): "))
                except ValueError:
                    print("Veuillez entrer un nombre valide entre 0 et 8.")
            client.send(str(shot).encode())

    client.close()

if __name__ == "__main__":
    main()
