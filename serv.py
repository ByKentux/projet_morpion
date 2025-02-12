import socket
from grid import *

def get_masked_grid(grid, player):
    """Renvoie la grille masquée pour un joueur. Le joueur voit ses propres coups et les cases vides."""
    masked_cells = [
        cell if cell == player or cell == EMPTY else EMPTY
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

def get_full_grid(grid):
    """Renvoie la grille complète (pour l'observateur)."""
    grid_state = "\n".join([
        " -------------",
        f" | {symbols[grid.cells[0]]} | {symbols[grid.cells[1]]} | {symbols[grid.cells[2]]} | ",
        " -------------",
        f" | {symbols[grid.cells[3]]} | {symbols[grid.cells[4]]} | {symbols[grid.cells[5]]} | ",
        " -------------",
        f" | {symbols[grid.cells[6]]} | {symbols[grid.cells[7]]} | {symbols[grid.cells[8]]} | ",
        " -------------"
    ])
    return grid_state

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    hostname = socket.gethostname()
    s.bind((socket.gethostbyname(hostname), 2910)) 
    s.listen(3)  # Permet d'accepter jusqu'à 3 connexions (2 joueurs + 1 observateur)

    print("Serveur en attente de connexions...")
    clients = []

    # Initialisation des scores
    scores = {1: 0, 2: 0}

    while len(clients) < 2:
        client_socket, client_address = s.accept()
        clients.append(client_socket)
        print(f"Connexion acceptée de {client_address}")

    print("Les deux joueurs sont connectés. Le jeu commence !")

    # Acceptation de l'observateur
    observer = None
    if len(clients) == 2:
        print("Attente d'un observateur...")
        observer_socket, observer_address = s.accept()
        observer = observer_socket
        clients.append(observer)
        print(f"Observateur connecté depuis {observer_address}")

    while True:
        current_player = 0  
        game_grid = grid()  

        while True:
            player = current_player + 1
            client = clients[current_player]

            while True:
                # Envoi de la grille masquée pour le joueur
                masked_grid = get_masked_grid(game_grid, player)
                client.send(f"Votre tour !\n{masked_grid}".encode())

                # Envoi de la grille complète à l'observateur
                if observer:
                    full_grid = get_full_grid(game_grid)
                    observer.send(f"Grille mise à jour :\n{full_grid}".encode())

                data = client.recv(1024).decode()
                if not data:
                    break

                shot = int(data.strip())
                if game_grid.cells[shot] == EMPTY:
                    game_grid.play(player, shot)
                    break  
                else:
                    client.send(f"Cette case ({shot}) est déjà occupée !\n{masked_grid}".encode())

            if game_grid.gameOver() != -1:
                result_message = ""
                if game_grid.gameOver() == 0:
                    result_message = "Match nul !"
                elif game_grid.gameOver() == player:
                    result_message = "Vous avez gagné !"
                    scores[player] += 1  # Met à jour le score du joueur gagnant
                else:
                    result_message = "Vous avez perdu !"

                # Envoi du message de résultat et de la grille finale aux deux joueurs
                for i, c in enumerate(clients[:2]):  # Envoi aux joueurs uniquement
                    final_grid = get_masked_grid(game_grid, i + 1)  # Envoi de la grille masquée
                    if game_grid.gameOver() == i + 1:
                        c.send(f"{result_message}\nVoici la grille finale :\n{final_grid}".encode())
                    else:
                        c.send(f"Vous avez perdu !\nVoici la grille finale :\n{final_grid}".encode())

                # Affichage du score actuel
                for c in clients[:2]:
                    c.send(f"Score actuel: Joueur 1: {scores[1]}, Joueur 2: {scores[2]}\n".encode())

                # Envoi des informations à l'observateur
                if observer:
                    observer.send(f"Résultat final : {result_message}\nGrille finale :\n{get_full_grid(game_grid)}".encode())

                for c in clients[:2]:
                    c.send("Voulez-vous jouer une autre partie ? (oui/non)".encode())

                responses = [c.recv(1024).decode().strip().lower() for c in clients[:2]]
                if all(response == "oui" for response in responses):
                    game_grid.reset()
                    continue
                else:
                    break 

            current_player = 1 - current_player  

        print("Une des parties est terminée, les joueurs ne veulent plus continuer.")
        break

    # Affiche le score final à la fin de toutes les parties
    for c in clients[:2]:
        c.send(f"Score final: Joueur 1: {scores[1]}, Joueur 2: {scores[2]}\n".encode())

    for client in clients:
        client.close()

if __name__ == "__main__":
    main()
