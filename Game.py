import random
import math

#for the GUI
import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
import random

#metadata
DEPTH = 2
BOARD_SIZE = 9
NO_ADJACENT_CELLS_FOR_WIN = 5

#for the GUI
CELL_SIZE = 50
STONE_RADIUS = 14

#Board Tokens
EMPTY = '.'
PLAYER_BLACK = 'B'
PLAYER_WHITE = 'W'

def create_board():
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def print_board(board):
    print('  ' + ' '.join(f'{i:2}' for i in range(BOARD_SIZE)))
    for idx, row in enumerate(board):
        print(f'{idx:2} ' + '  '.join(row))


def is_valid_move(board, row, col):
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE and board[row][col] == EMPTY


def make_move(board, row, col, player):
    board[row][col] = player


def check_winner(board, player):
    # horizontal, vertical, diagonal, anti-diagonal
    directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                for d_row, d_col in directions:
                    count = 1
                    next_row, next_col = row + d_row, col + d_col
                    for _ in range(NO_ADJACENT_CELLS_FOR_WIN - 1):  # Need four more to complete 5
                        if 0 <= next_row < BOARD_SIZE and 0 <= next_col < BOARD_SIZE and board[next_row][next_col] == player:
                            count += 1
                            next_row += d_row
                            next_col += d_col
                        else:
                            break
                    if count == NO_ADJACENT_CELLS_FOR_WIN:
                        return True
    return False



# Only consider vacancies within the radius of any occupied cell
def get_available_moves(board, radius=2):
    # 1) Gather all occupied cells
    occupied = [
        (r, c)
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
        if board[r][c] != EMPTY
    ]

    # 2) If none are occupied yet (which happens at first move only), return every empty cell
    if not occupied:
        return [
            (r, c)
            for r in range(BOARD_SIZE)
            for c in range(BOARD_SIZE)
            if board[r][c] == EMPTY
        ]

    # 3) Otherwise, only return empties within the radius of every occupied cell
    candidates = set()
    for (r0, c0) in occupied:
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r, c = r0 + dr, c0 + dc
                if (
                    0 <= r < BOARD_SIZE and
                    0 <= c < BOARD_SIZE and
                    board[r][c] == EMPTY
                ):
                    candidates.add((r, c))
    return list(candidates)




# Basic 5-cell pattern weight
PATTERN_WEIGHTS = {
    'XXXXX': 100000,
    '.XXXX':  5000,    
    'XXXX.':  5000,
    '.XXX.':  1000,   
    'XXX.X':  2000,     
    'XX.XX':  2000,     
    '.XX.X':   200,     
    '.X.XX':   200,
    '.XX..':    50,
    '..XX.':    50,
}
DIRECTIONS = [(0,1), (1,0), (1,1), (1,-1)]


def pattern_score(board, player):
    opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
    total = 0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            for dr, dc in DIRECTIONS:
                window = []
                for i in range(NO_ADJACENT_CELLS_FOR_WIN):
                    rr, cc = r + dr*i, c + dc*i
                    if 0 <= rr < BOARD_SIZE and 0 <= cc < BOARD_SIZE:
                        cell = board[rr][cc]
                        if   cell == player:   window.append('X')
                        elif cell == EMPTY:    window.append('.')
                        else:                  window.append('O')
                    else:
                        window.append('O')  # off-board = blocked
                pattern = ''.join(window)
                if 'O' not in pattern:
                    total += PATTERN_WEIGHTS.get(pattern, 0)
    return total


def evaluate_board(board, player):
    opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK

    # immediate win/loss
    if check_winner(board, player):
        return 1000000
    if check_winner(board, opponent):
        return -1000000

    my_score  = pattern_score(board, player)
    opp_score = pattern_score(board, opponent)
    return my_score - opp_score * 1.5


# Minimax Algorithm
def minimax(board, depth, is_maximizing, player):
    score = evaluate_board(board, player)
    if abs(score) == 10000 or depth == 0 or not get_available_moves(board):
        return score

    if is_maximizing:
        best_score = -math.inf
        for row, col in get_available_moves(board):
            board[row][col] = player
            best_score = max(best_score, minimax(
                board, depth - 1, False, player))
            board[row][col] = EMPTY
        return best_score
    else:
        best_score = math.inf
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        for row, col in get_available_moves(board):
            board[row][col] = opponent
            best_score = min(best_score, minimax(
                board, depth - 1, True, player))
            board[row][col] = EMPTY
        return best_score


def best_move_minimax(board, player, depth=2):
    best_score = -math.inf
    move = None
    for row, col in get_available_moves(board):
        board[row][col] = player
        score = minimax(board, depth - 1, False, player)
        board[row][col] = EMPTY
        if score > best_score:
            best_score = score
            move = (row, col)
    return move


# Alpha-Beta Pruning Algorithm
def alphabeta(board, depth, alpha, beta, is_maximizing, player):
    score = evaluate_board(board, player)
    if abs(score) == 10000 or depth == 0 or not get_available_moves(board):
        return score

    if is_maximizing:
        best_score = -math.inf
        for row, col in get_available_moves(board):
            board[row][col] = player
            best_score = max(best_score, alphabeta(
                board, depth - 1, alpha, beta, False, player))
            board[row][col] = EMPTY
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break
        return best_score
    else:
        best_score = math.inf
        opponent = PLAYER_WHITE if player == PLAYER_BLACK else PLAYER_BLACK
        for row, col in get_available_moves(board):
            board[row][col] = opponent
            best_score = min(best_score, alphabeta(
                board, depth - 1, alpha, beta, True, player))
            board[row][col] = EMPTY
            beta = min(beta, best_score)
            if beta <= alpha:
                break
        return best_score


def best_move_alphabeta(board, player, depth=2):
    best_score = -math.inf
    move = None
    for row, col in get_available_moves(board):
        board[row][col] = player
        score = alphabeta(board, depth - 1, -math.inf, math.inf, False, player)
        board[row][col] = EMPTY
        if score > best_score:
            best_score = score
            move = (row, col)
    return move

def ai_vs_ai():
    board = create_board()
    print("AI vs AI battle: Minimax (B) vs Alpha-Beta (W)")
    print_board(board)

    # First move is random
    first_move = random.choice(get_available_moves(board))
    make_move(board, first_move[0], first_move[1], PLAYER_BLACK)
    print(f"First move (B): {first_move[0]} {first_move[1]}")
    print_board(board)

    turn = PLAYER_WHITE  # The second move is always for the white player
    while True:
        #check for tie
        if not get_available_moves(board):
            print("It's a tie!")
            return
        
        if turn == PLAYER_BLACK:
            row, col = best_move_minimax(board, PLAYER_BLACK, DEPTH)
        else:
            try:
                row, col = best_move_alphabeta(board, PLAYER_WHITE, DEPTH)
            except:
                print("It's a Tie!")
                return

        make_move(board, row, col, turn)
        print(f"{turn} chooses: {row} {col}")
        print_board(board)

        if check_winner(board, turn):
            print(f"{turn} wins!")
            break

        #toggle the turn
        turn = PLAYER_WHITE if turn == PLAYER_BLACK else PLAYER_BLACK


def human_vs_ai():
    board = create_board()
    print("Welcome to Gomoku! You are 'B'. AI is 'W'.")
    print_board(board)

    while True:
        # Human turn
        try:
            row, col = map(int, input("Enter your move (row col): ").split())
        except:
            print("Invalid format. Try again.")
            continue
        while not is_valid_move(board, row, col):
            print("Invalid move. Try again.")
            row, col = map(int, input("Enter your move (row col): ").split())
        make_move(board, row, col, PLAYER_BLACK)
        print_board(board)

        if check_winner(board, PLAYER_BLACK):
            print("You win!")
            break


        # AI turn
        #check for tie
        if not get_available_moves(board):
            print("It's a Tie!")
            return
        
        print("AI is thinking...")

        ai_row, ai_col = best_move_minimax(board, PLAYER_WHITE, DEPTH)
        make_move(board, ai_row, ai_col, PLAYER_WHITE)

        print(f"AI chooses: {ai_row} {ai_col}")
        print_board(board)

        if check_winner(board, PLAYER_WHITE):
            print("AI wins!")
            break









class GomokuGUI:
    def __init__(self, root):
        self.root = root

        self.canvas = tk.Canvas(root, width=BOARD_SIZE * CELL_SIZE, height=BOARD_SIZE * CELL_SIZE + 50, bg='#DEB887')
        self.canvas.pack()

        self.board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.turn = PLAYER_BLACK

        self.draw_grid()

        self.ask_game_mode()


    def ask_game_mode(self):
        mode = simpledialog.askstring("Game Mode", "Enter game mode:\n1 for AI vs AI\n2 for Human vs AI")

        if mode is None:
            self.root.destroy()
            return

        if mode == "1":
            self.root.title("Gomoku AI vs AI")
            self.root.after(700, self.ai_vs_ai_aux)
        elif mode == "2":
            self.root.title("Gomoku Human vs AI")
            self.root.after(700, self.human_vs_ai)
        else:
            messagebox.showerror("Invalid Input", "Please enter '1' or '2'")
            self.ask_game_mode()


    def draw_grid(self):
        for i in range(BOARD_SIZE):
            #form the lines of the grid with the proper spacings
            x = y = CELL_SIZE // 2 + i * CELL_SIZE
            self.canvas.create_line(CELL_SIZE // 2, y, CELL_SIZE * (BOARD_SIZE - 1) + CELL_SIZE // 2, y)
            self.canvas.create_line(x, CELL_SIZE // 2, x, CELL_SIZE * (BOARD_SIZE - 1) + CELL_SIZE // 2)


    def draw_stone(self, row, col, color):
        x = col * CELL_SIZE + CELL_SIZE // 2
        y = row * CELL_SIZE + CELL_SIZE // 2
        self.canvas.create_oval(x - STONE_RADIUS, y - STONE_RADIUS,
                                x + STONE_RADIUS, y + STONE_RADIUS,
                                fill='black' if color == PLAYER_BLACK else 'white', outline='')


    def draw_game_over(self, isTie, is_AI_VS_AI):
        text = (
            "It's a Tie!" if isTie
            else "Black Wins!" if is_AI_VS_AI and self.turn == PLAYER_BLACK
            else "White Wins!" if is_AI_VS_AI and self.turn == PLAYER_WHITE
            else "You win!" if self.turn == PLAYER_BLACK
            else "AI wins!"
        )

        self.canvas.create_text(
            BOARD_SIZE * CELL_SIZE // 2,
            BOARD_SIZE * CELL_SIZE + 15,
            text=text,
            font=('Helvetica', 20, 'bold'),
            fill='blue'
        )

    def ai_vs_ai_aux(self):
        # First move is random
        row, col = random.choice(get_available_moves(self.board))
        make_move(self.board, row, col, PLAYER_BLACK)
        self.draw_stone(row, col, self.turn)

        self.turn = PLAYER_WHITE

        self.root.after(300, self.ai_vs_ai)


    def ai_vs_ai(self):
        # if there are no more available moves, then it's a tie
        if not get_available_moves(self.board):
            self.draw_game_over(True, True)
            return
        
        if self.turn == PLAYER_BLACK:
            row, col = best_move_minimax(self.board, PLAYER_BLACK, DEPTH)
        else:
            row, col = best_move_alphabeta(self.board, PLAYER_WHITE, DEPTH)

        make_move(self.board, row, col, self.turn)
        self.draw_stone(row, col, self.turn)

        if check_winner(self.board, self.turn):
            self.draw_game_over(False, True)
            return

        #toggle the turn
        self.turn = PLAYER_WHITE if self.turn == PLAYER_BLACK else PLAYER_BLACK
        
        self.root.after(300, self.ai_vs_ai)


    def human_vs_ai(self):
        # if there are no more available moves, then it's a tie
        if not get_available_moves(self.board):
            self.draw_game_over(True, False)
            return
        
        # Human turn
        if self.turn == PLAYER_BLACK:
            dialogHeader = "Your Turn"
            while True:
                try:
                    row, col = map(int, simpledialog.askstring(dialogHeader, "Enter your move (row col): ").split())
                except:
                    dialogHeader = "Invalid format. Try again."
                    continue
                if is_valid_move(self.board, row, col):
                    break
                else:
                    dialogHeader = "Invalid move. Try again."

        #AI turn
        else:
            row, col = best_move_minimax(self.board, PLAYER_WHITE, DEPTH)

        make_move(self.board, row, col, self.turn)
        self.draw_stone(row, col, self.turn)

        if check_winner(self.board, self.turn):
            self.draw_game_over(False, False)
            return
        
        #toggle the turn
        self.turn = PLAYER_WHITE if self.turn == PLAYER_BLACK else PLAYER_BLACK

        self.root.after(300, self.human_vs_ai)







if __name__ == "__main__":
    print("1. Play in console")
    print("2. Play in GUI")
    choice = input("Enter choice: ")

    if choice == '1':
        print("1. Watch AI vs AI battle")
        print("2. Play Human vs AI")
        choice = input("Enter choice: ")

        if choice == '1':
            ai_vs_ai()
        elif choice == '2':
            human_vs_ai()
        else:
            print("Invalid choice.")
    elif choice == '2':
        root = tk.Tk()
        app = GomokuGUI(root)
        root.mainloop()
    else:
        print("Invalid choice.")
