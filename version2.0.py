from socketIO_client import SocketIO
import random

server_url = "http://192.168.1.104"
server_port = 4000

socketIO = SocketIO(server_url, server_port)

def on_connect():
    print("Connected to server")
    socketIO.emit('signin', {
        'user_name': "Pablish",
        'tournament_id': 142857,
        'user_role': 'player'
    })

def on_ok_signin():
    print("Login")

def on_finish(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    winner_turn_id = data['winner_turn_id']
    board = data['board']
    
    # Your cleaning board logic here
    
    print("Winner:", winner_turn_id)
    # print_board(board)
    socketIO.emit('player_ready', {
        'tournament_id': 142857,
        'player_turn_id': player_turn_id,
        'game_id': game_id
    })

def on_ready(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    board = data['board']
    print("I'm player:", player_turn_id)
    # print_board(board)
    
    # Your logic / user input here
    move = get_best_move(board, player_turn_id)
    print("Move in:", move)
    socketIO.emit('play', {
        'tournament_id': 142857,
        'player_turn_id': player_turn_id,
        'game_id': game_id,
        'movement': move
    })

def get_best_move(board, player_turn_id):
    valid_moves = get_valid_moves(board)
    best_score = float('-inf')
    best_move = random.choice(valid_moves)
    alpha = float('-inf')
    beta = float('inf')
    depth = 6  # Adjust the depth according to your needs
    
    for move in valid_moves:
        new_board = make_move(board, move, player_turn_id)
        score = minimax(new_board, depth-1, alpha, beta, False, player_turn_id)
        
        if score > best_score:
            best_score = score
            best_move = move
        
        alpha = max(alpha, best_score)
        if alpha >= beta:
            break
    
    return best_move

def minimax(board, depth, alpha, beta, is_maximizing_player, player_turn_id):
    if depth == 0 or is_game_over(board):
        return evaluate(board, player_turn_id)
    
    if is_maximizing_player:
        max_eval = float('-inf')
        valid_moves = get_valid_moves(board)
        
        for move in valid_moves:
            new_board = make_move(board, move, player_turn_id)
            eval = minimax(new_board, depth-1, alpha, beta, False, player_turn_id)
            max_eval = max(max_eval, eval)
            alpha = max(alpha, max_eval)
            if alpha >= beta:
                break
        
        return max_eval
    else:
        min_eval = float('inf')
        opponent = get_opponent(player_turn_id)
        valid_moves = get_valid_moves(board)
        
        for move in valid_moves:
            new_board = make_move(board, move, opponent)
            eval = minimax(new_board, depth-1, alpha, beta, True, player_turn_id)
            min_eval = min(min_eval, eval)
            beta = min(beta, min_eval)
            if alpha >= beta:
                break
        
        return min_eval

def get_valid_moves(board):
    valid_moves = []
    for col in range(7):
        if board[0][col] == 0:
            valid_moves.append(col)
    return valid_moves

def make_move(board, move, player_turn_id):
    new_board = [row[:] for row in board]
    for row in range(5, -1, -1):
        if new_board[row][move] == 0:
            new_board[row][move] = player_turn_id
            break
    return new_board

def is_game_over(board):
    return is_board_full(board) or is_winner(board, 1) or is_winner(board, 2)

def is_board_full(board):
    for row in range(6):
        for col in range(7):
            if board[row][col] == 0:
                return False
    return True

def is_winner(board, player):
    # Check rows
    for row in range(6):
        for col in range(4):
            if board[row][col] == player and board[row][col+1] == player and board[row][col+2] == player and board[row][col+3] == player:
                return True
    
    # Check columns
    for row in range(3):
        for col in range(7):
            if board[row][col] == player and board[row+1][col] == player and board[row+2][col] == player and board[row+3][col] == player:
                return True
    
    # Check diagonals (top left to bottom right)
    for row in range(3):
        for col in range(4):
            if board[row][col] == player and board[row+1][col+1] == player and board[row+2][col+2] == player and board[row+3][col+3] == player:
                return True
    
    # Check diagonals (top right to bottom left)
    for row in range(3):
        for col in range(3, 7):
            if board[row][col] == player and board[row+1][col-1] == player and board[row+2][col-2] == player and board[row+3][col-3] == player:
                return True
    
    return False

def evaluate(board, player_turn_id):
    score = 0
    
    # Evaluate rows
    for row in range(6):
        row_list = board[row]
        for col in range(4):
            window = row_list[col:col+4]
            score += evaluate_window(window, player_turn_id)
    
    # Evaluate columns
    for col in range(7):
        col_list = [board[row][col] for row in range(6)]
        for row in range(3):
            window = col_list[row:row+4]
            score += evaluate_window(window, player_turn_id)
    
    # Evaluate diagonals (top left to bottom right)
    for row in range(3):
        for col in range(4):
            window = [board[row+i][col+i] for i in range(4)]
            score += evaluate_window(window, player_turn_id)
    
    # Evaluate diagonals (top right to bottom left)
    for row in range(3):
        for col in range(3, 7):
            window = [board[row+i][col-i] for i in range(4)]
            score += evaluate_window(window, player_turn_id)
    
    return score

def evaluate_window(window, player_turn_id):
    score = 0
    opponent = get_opponent(player_turn_id)

    if player_turn_id == 1:
        score = offence(window, player_turn_id)
    else:
        score = defence(window, player_turn_id)

    return score

def offence(window, piece):
    # Heurística ofensiva
    score = 0
    opp_piece = get_opponent(piece)

    if window.count(piece) == 4:
        score += 1000  # Aumentamos el valor para una línea de 4 fichas propias
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 100  # Aumentamos el valor para una línea de 3 fichas propias con un espacio vacío
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 10  # Aumentamos el valor para una línea de 2 fichas propias con dos espacios vacíos

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 100  # Reducimos el valor para una línea de 3 fichas del oponente con un espacio vacío

    return score


def defence(window, piece):
    # Heurística defensiva
    score = 0
    opp_piece = get_opponent(piece)

    if window.count(piece) == 4:
        score += 1000  # Aumentamos el valor para una línea de 4 fichas propias
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 100  # Aumentamos el valor para una línea de 3 fichas propias con un espacio vacío
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 10  # Aumentamos el valor para una línea de 2 fichas propias con dos espacios vacíos

    if window.count(opp_piece) == 4:
        score -= 1000  # Reducimos el valor para una línea de 4 fichas del oponente
    elif window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 100  # Reducimos el valor para una línea de 3 fichas del oponente con un espacio vacío
    elif window.count(opp_piece) == 2 and window.count(0) == 2:
        score -= 10  # Reducimos el valor para una línea de 2 fichas del oponente con dos espacios vacíos

    return score


def get_opponent(player_turn_id):
    return 1 if player_turn_id == 2 else 2

def print_board(board):
    for row in board:
        for cell in row:
            if cell == 0:
                print("⚪", end=" ")  # Espacio en blanco
            elif cell == 1:
                print("🔴", end=" ")  # Ficha del jugador 1
            elif cell == 2:
                print("🔵", end=" ")  # Ficha del jugador 2
        print()

socketIO.on('connect', on_connect)
socketIO.on('ok_signin', on_ok_signin)
socketIO.on('finish', on_finish)
socketIO.on('ready', on_ready)
socketIO.on('finish', on_finish)

socketIO.wait()
