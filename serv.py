import socket
import random
from grid import *  # Importation de la classe grid

def get_masked_grid(grid, player, reveal_opponent=False):
    """Retourne une version de la grille masquée ou complète."""
    masked_cells = [
        cell if cell == player or cell == EMPTY or reveal_opponent else EMPTY
        for cell in grid.cells
    ]
    grid_state = "\n".join([ 
        " -------------", 
        f" | {symbols[masked_cells[0]]} | {symbols[masked_cells[1]]} | {symbols[masked_cells[2]]} | ", 
        " -------------", 
        f" | {symbols[masked_cells[3]]} | {symbols[masked_cells[4]]} | {symbols[masked_cells[5]]} | ", 
        " -------------", 
        f" | {symbols[masked_cells[6]]} | {symbols[masked_cells[7]]} | {symbols[masked_cells[8]]} | ", 
        " -------------" 
    ]) 
    return grid_state

def get_random_shot(game_grid):
    """Retourne un coup aléatoire sur une case vide."""
    available_shots = [i for i, cell in enumerate(game_grid.cells) if cell == EMPTY]
    return random.choice(available_shots) if available_shots else -1

def main():
    # Initialisation des scores
    scores = [0, 0]  # Score pour joueur 1 et joueur 2

    # Création de la socket serveur
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    hostname = socket.gethostname()
    s.bind((socket.gethostbyname(hostname), 2910))  # Écoute sur le port 2910
    s.listen(3)  # Écoute pour 3 connexions (2 joueurs + 1 observateur)
    
    print("Serveur en attente de connexions...")
    clients = []

    # Acceptation des connexions des joueurs et observateurs
    while len(clients) < 3:
        client_socket, client_address = s.accept()
        clients.append(client_socket)
        print(f"Connexion acceptée de {client_address}")
    
    # Les 2 premiers clients sont des joueurs, le troisième est un observateur
    joueurs = clients[:2]
    observateur = clients[2]
    
    print("Jeu commencé avec un observateur connecté.")
    
    while True:
        current_player = 0  # Joueur 1 commence
        game_grid = grid()  # Créer une nouvelle grille

        while True:
            player = current_player + 1  # Joueur courant (1 ou 2)
            client = joueurs[current_player]
            
            while True:
                masked_grid = get_masked_grid(game_grid, player, False)
                client.send(f"Votre tour !\n{masked_grid}".encode())
                observateur.send(f"Tour de Joueur {player} :\n{masked_grid}".encode())
                data = client.recv(1024).decode()

                # Si c'est un robot, on joue un coup aléatoire
                if player == 2:  # Si c'est le tour du robot
                    shot = get_random_shot(game_grid)
                    print(f"Le robot joue le coup {shot}")
                    game_grid.play(player, shot)
                    break
                else:
                    # Traitement normal du coup pour un joueur humain
                    shot = int(data.strip())
                    if game_grid.cells[shot] == EMPTY:
                        game_grid.play(player, shot)
                        break
                    else:
                        client.send(f"Cette case est déjà occupée !\n{masked_grid}".encode())

            # Vérification de la fin du jeu
            if game_grid.gameOver() != -1:
                result_message = ""
                if game_grid.gameOver() == 0:
                    result_message = "Match nul !"
                elif game_grid.gameOver() == player:
                    result_message = "Vous avez gagné !"
                    scores[current_player] += 1  # Augmenter le score du joueur gagnant
                else:
                    result_message = "Vous avez perdu !"

                # Informer les joueurs et l'observateur
                for i, c in enumerate(joueurs):
                    final_grid = get_masked_grid(game_grid, i + 1, True)
                    c.send(f"{result_message}\nVoici la grille finale :\n{final_grid}".encode())
                
                # L'observateur voit aussi la fin du jeu
                observateur.send(f"Fin de partie. Résultat : {result_message}\n{final_grid}".encode())

                # Affichage des scores
                for i, c in enumerate(joueurs):
                    c.send(f"Scores actuels : Joueur 1: {scores[0]}, Joueur 2: {scores[1]}".encode())

                for c in joueurs:
                    c.send("Voulez-vous jouer une autre partie ? (oui/non)".encode())

                responses = [c.recv(1024).decode().strip().lower() for c in joueurs]
                if all(response == "oui" for response in responses):
                    # Réinitialiser la grille et continuer à jouer
                    game_grid.reset()
                    continue
                else:
                    break  # Quitter la boucle principale du jeu

            current_player = 1 - current_player  # Alterner entre joueurs

        break  # Si les joueurs ne veulent plus continuer, sortir de la boucle

    # Fermer les connexions
    for client in clients:
        client.close()

if __name__ == "__main__":
    main()
