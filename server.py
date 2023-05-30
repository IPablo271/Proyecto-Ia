from socketIO_client import SocketIO
import random

server_url = "http://192.168.1.134"
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
    # Your logic for handling 'finish' event here

def on_ready(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    board = data['board']
    print("I'm player:", player_turn_id)
    print(board)
    
    # Your logic / user input here
    move = minimax(board, player_turn_id)
    print("Move in:", move)
    socketIO.emit('play', {
        'tournament_id': 142857,
        'player_turn_id': player_turn_id,
        'game_id': game_id,
        'movement': move
    })

def on_finish(data):
    game_id = data['game_id']
    player_turn_id = data['player_turn_id']
    winner_turn_id = data['winner_turn_id']
    board = data['board']
    
    # Your cleaning board logic here
    
    print("Winner:", winner_turn_id)
    print(board)
    socketIO.emit('player_ready', {
        'tournament_id': 142857,
        'player_turn_id': player_turn_id,
        'game_id': game_id
    })

def minimax(board, player_turn_id):
    # Define the maximum depth for the search
    max_depth = 6

    def evaluate(board, player):
        # Heuristic 1: Count the number of player's pieces in each possible winning line
        score = 0
        lines = get_winning_lines()
        for line in lines:
            count = sum([1 for position in line if board[position] == player])
            if count == 4:
                score += 1000
            elif count == 3:
                score += 10
            elif count == 2:
                score += 1
        return score

    def get_winning_lines():
        # Define all possible winning lines in Connect 4
        lines = []
        # Horizontal lines
        for row in range(6):
            for col in range(4):
                lines.append([(row, col), (row, col + 1), (row, col + 2), (row, col + 3)])
        # Vertical lines
        for row in range(3):
            for col in range(7):
                lines.append([(row, col), (row + 1, col), (row + 2, col), (row + 3, col)])
        # Diagonal lines (top-left to bottom-right)
        for row in range(3):
            for col in range(4):
                lines.append([(row, col), (row + 1, col + 1), (row + 2, col + 2), (row + 3, col + 3)])
        # Diagonal lines (top-right to bottom-left)
        for row in range(3):
            for col in range(3, 7):
                lines.append([(row, col), (row + 1, col - 1), (row + 2, col - 2), (row + 3, col - 3)])
        return lines

    def get_valid_moves(board):
        # Return a list of valid moves (columns with empty spaces)
        valid_moves = []
        for col in range(7):
            if board[col] == 0:
                valid_moves.append(col)
        return valid_moves

    def is_terminal_node(board):
        # Check if the game is over (board is full or a player has won)
        if 0 not in board:
            return True
        lines = get_winning_lines()
        for line in lines:
            line_values = [board[position] for position in line]
            if line_values.count(1) == 4 or line_values.count(2) == 4:
                return True
        return False

    def min_value(board, alpha, beta, depth):
        if is_terminal_node(board) or depth == max_depth:
            return evaluate(board, player_turn_id)
        value = float('inf')
        for move in get_valid_moves(board):
            new_board = board[:]
            new_board[move] = 2 if player_turn_id == 1 else 1
            value = min(value, max_value(new_board, alpha, beta, depth + 1))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def max_value(board, alpha, beta, depth):
        if is_terminal_node(board) or depth == max_depth:
            return evaluate(board, player_turn_id)
        value = float('-inf')
        for move in get_valid_moves(board):
            new_board = board[:]
            new_board[move] = player_turn_id
            value = max(value, min_value(new_board, alpha, beta, depth + 1))
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    # Main minimax algorithm with alpha-beta pruning
    best_move = random.choice(get_valid_moves(board))
    best_score = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    for move in get_valid_moves(board):
        new_board = board[:]
        new_board[move] = player_turn_id
        score = min_value(new_board, alpha, beta, 1)
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)
    return best_move

socketIO.on('connect', on_connect)
socketIO.on('ok_signin', on_ok_signin)
socketIO.on('finish', on_finish)
socketIO.on('ready', on_ready)
socketIO.on('finish', on_finish)

socketIO.wait()
