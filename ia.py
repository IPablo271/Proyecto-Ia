import numpy as np
import colorama
from colorama import Fore, Style

# Constantes para el tablero
EMPTY = 0
PLAYER = 1
AI = 2

# Heurísticas para evaluar el tablero
WIN_SCORE = 100000
DRAW_SCORE = 0

def evaluate_window(window, player):
    score = 0
    opponent = PLAYER if player == AI else AI

    if window.count(player) == 4:
        score += WIN_SCORE
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        score += 100
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        score += 10

    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 80

    return score

def evaluate_board(board, player):
    score = 0

    # Evaluación horizontal
    for r in range(6):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(4):
            window = row_array[c:c+4]
            score += evaluate_window(window, player)

    # Evaluación vertical
    for c in range(7):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(3):
            window = col_array[r:r+4]
            score += evaluate_window(window, player)

    # Evaluación en diagonal /
    for r in range(3):
        for c in range(4):
            window = [board[r+i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    # Evaluación en diagonal \
    for r in range(3):
        for c in range(4):
            window = [board[r+3-i][c+i] for i in range(4)]
            score += evaluate_window(window, player)

    return score

def is_terminal_node(board):
    return (len(get_valid_locations(board)) == 0) or (check_win(board, PLAYER)) or (check_win(board, AI))

def get_valid_locations(board):
    valid_locations = []
    for col in range(7):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def is_valid_location(board, col):
    return board[5][col] == 0

def make_move(board, col, player):
    row = get_next_open_row(board, col)
    board[row][col] = player

def get_next_open_row(board, col):
    for r in range(6):
        if board[r][col] == 0:
            return r

def check_win(board, player):
    # Verificar victoria en filas
    for r in range(6):
        for c in range(4):
            if board[r][c] == player and board[r][c+1] == player and board[r][c+2] == player and board[r][c+3] == player:
                return True

    # Verificar victoria en columnas
    for c in range(7):
        for r in range(3):
            if board[r][c] == player and board[r+1][c] == player and board[r+2][c] == player and board[r+3][c] == player:
                return True

    # Verificar victoria en diagonales /
    for r in range(3):
        for c in range(4):
            if board[r][c] == player and board[r+1][c+1] == player and board[r+2][c+2] == player and board[r+3][c+3] == player:
                return True

    # Verificar victoria en diagonales \
    for r in range(3):
        for c in range(4):
            if board[r+3][c] == player and board[r+2][c+1] == player and board[r+1][c+2] == player and board[r][c+3] == player:
                return True

    return False

def minimax(board, depth, alpha, beta, maximizing_player):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if check_win(board, AI):
                return (None, WIN_SCORE)
            elif check_win(board, PLAYER):
                return (None, -WIN_SCORE)
            else:
                return (None, DRAW_SCORE)
        else:
            return (None, evaluate_board(board, AI))

    if maximizing_player:
        value = -float('inf')
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            make_move(temp_board, col, AI)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value

    else:  # Minimizing player
        value = float('inf')
        column = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            make_move(temp_board, col, PLAYER)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def print_board(board):
    colorama.init()  # Inicializar colorama
    print("\n")
    for row in range(6):
        for col in range(7):
            if board[row][col] == PLAYER:
                print(Fore.YELLOW + "O ", end="")
            elif board[row][col] == AI:
                print(Fore.RED + "X ", end="")
            else:
                print(Fore.WHITE + "- ", end="")
        print()

    for col in range(7):
        print(Fore.WHITE + str(col) + " ", end="")
    print()
    print(Style.RESET_ALL)  # Restablecer el estilo por defecto  # Restablecer el estilo por defecto

def play_connect4():
    board = np.zeros((6, 7), dtype=int)
    game_over = False
    turn = np.random.choice([PLAYER, AI])

    while not game_over:
        if turn == PLAYER:
            col = int(input("Elige una columna (0-6): "))
            if is_valid_location(board, col):
                make_move(board, col, PLAYER)
                if check_win(board, PLAYER):
                    print("¡Has ganado!")
                    game_over = True
                turn = AI

        else:
            col, _ = minimax(board, 6, -float('inf'), float('inf'), True)
            if is_valid_location(board, col):
                make_move(board, col, AI)
                if check_win(board, AI):
                    print("¡Has perdido!")
                    game_over = True
                turn = PLAYER

        print_board(board)

        if is_terminal_node(board):
            print("¡Empate!")
            game_over = True

play_connect4()
