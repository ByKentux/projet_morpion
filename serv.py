# serv.py

import socket
from grid import *  

def get_masked_grid(grid, player, reveal_opponent=False):
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

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    hostname = socket.gethostname()
    s.bind((socket.gethostbyname(hostname), 2910)) 
    s.listen(2)  
    
    print("Serveur en attente de connexions...")
    clients = []

    while len(clients) < 2:
        client_socket, client_address = s.accept()
        clients.append(client_socket)
        print(f"Connexion acceptée de {client_address}")

    print("Les deux joueurs sont connectés. Le jeu commence !")
    
    while True:
        current_player = 0  
        game_grid = grid()  
        
        while True:
            player = current_player + 1
            client = clients[current_player]
            
            while True:
                masked_grid = get_masked_grid(game_grid, player, False)
                client.send(f"Votre tour !\n{masked_grid}".encode())
                
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
                else:
                    result_message = "Vous avez perdu !"
                
                for i, c in enumerate(clients):
                    final_grid = get_masked_grid(game_grid, i + 1, True)
                    if game_grid.gameOver() == i + 1:
                        c.send(f"{result_message}\nVoici la grille finale :\n{final_grid}".encode())
                    else:
                        c.send(f"Vous avez perdu !\nVoici la grille finale :\n{final_grid}".encode())
                
                for c in clients:
                    c.send("Voulez-vous jouer une autre partie ? (oui/non)".encode())
                
                responses = [c.recv(1024).decode().strip().lower() for c in clients]
                if all(response == "oui" for response in responses):
                    game_grid.reset()
                    continue
                else:
                    break 

            current_player = 1 - current_player  

        print("Une des parties est terminée, les joueurs ne veulent plus continuer.")
        break
    
    for client in clients:
        client.close()

if __name__ == "__main__":
    main()
