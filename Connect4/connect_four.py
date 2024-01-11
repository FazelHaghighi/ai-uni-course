import numpy as np
import pygame
import sys
import math
import random

BLUE = (87, 137, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 71)
YELLOW = (255, 242, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7


def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


def drop_piece(board, row, col, piece):
    board[row][col] = piece


def is_valid_location(board, col):
    return board[ROW_COUNT - 1][col] == 0


def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r


def print_board(board):
    print(np.flip(board, 0))


def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True


def draw_board(board, player_color, computer_color):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(
                screen,
                BLUE,
                (c * SQUARESIZE, r * SQUARESIZE + SQUARESIZE, SQUARESIZE, SQUARESIZE),
            )
            center = (
                int(c * SQUARESIZE + SQUARESIZE / 2),
                int(r * SQUARESIZE + SQUARESIZE + SQUARESIZE / 2),
            )
            pygame.draw.circle(screen, BLACK, center, RADIUS)

    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            center = (
                int(c * SQUARESIZE + SQUARESIZE / 2),
                height - int(r * SQUARESIZE + SQUARESIZE / 2),
            )
            if board[r][c] == 1:
                pygame.draw.circle(screen, player_color, center, RADIUS)
            elif board[r][c] == 2:
                pygame.draw.circle(screen, computer_color, center, RADIUS)

    pygame.display.update()


def display_winner(player):
    label = myfont.render(f"Player {player} wins!!", 1, RED if player == 1 else YELLOW)
    screen.blit(label, (40, 10))
    pygame.display.update()
    pygame.time.wait(3000)


def is_board_full(board):
    return all(board[ROW_COUNT - 1][col] != 0 for col in range(COLUMN_COUNT))


def evaluate_window(window, piece):
    score = 0
    opp_piece = 1 if piece == 2 else 2

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(0) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(0) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(0) == 1:
        score -= 4

    return score


def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [board[r][COLUMN_COUNT // 2] for r in range(ROW_COUNT)]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c : c + 4]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r : r + 4]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    # Score negatively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(4)]
            score += evaluate_window(window, piece)

    return score


def is_terminal_node(board):
    return winning_move(board, 1) or winning_move(board, 2) or is_board_full(board)


def minimax(board, depth, maximizing_player):
    """
    Implements the minimax algorithm to determine the best move for a player in Connect Four.

    Args:
        board (list): The current state of the game board.
        depth (int): The depth of the search tree.
        maximizing_player (bool): Indicates whether the current player is maximizing or minimizing.

    Returns:
        tuple: The column and the corresponding score of the best move.
    """
    valid_locations = [
        col for col in range(COLUMN_COUNT) if is_valid_location(board, col)
    ]
    is_terminal = is_terminal_node(board)

    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, 2):
                return (None, 100000000000000)
            elif winning_move(board, 1):
                return (None, -100000000000000)
            else:  # Game is a draw
                return (None, 0)
        else:  # Depth is zero
            return (None, score_position(board, 2))

    if maximizing_player:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 2)
            new_score = minimax(temp_board, depth - 1, False)[1]
            if new_score > value:
                value = new_score
                column = col
        return column, value

    else:  # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, 1)
            new_score = minimax(temp_board, depth - 1, True)[1]
            if new_score < value:
                value = new_score
                column = col
        return column, value


def choose_color():
    while True:
        color_choice = input("Choose your color (R for Red, Y for Yellow): ").upper()
        if color_choice in ["R", "Y"]:
            return RED if color_choice == "R" else YELLOW
        else:
            print("Invalid choice. Please enter 'R' or 'Y'.")


def choose_difficulty():
    while True:
        difficulty_choice = input(
            "Choose difficulty (E for Easy, M for Medium, H for Hard): "
        ).upper()
        if difficulty_choice in ["E", "M", "H"]:
            if difficulty_choice == "E":
                return 2
            elif difficulty_choice == "M":
                return 4
            elif difficulty_choice == "H":
                return 6
        else:
            print("Invalid choice. Please enter 'E', 'M', or 'H'.")


# Main game loop
chosen_color = choose_color()
difficulty = choose_difficulty()

# Set player and computer colors based on user's choice
player_color = YELLOW if chosen_color == "Y" else RED
computer_color = RED if player_color == YELLOW else YELLOW

board = create_board()
print_board(board)
game_over = False
turn = 0

pygame.init()

SQUARESIZE = 80
width = COLUMN_COUNT * SQUARESIZE
height = (ROW_COUNT + 1) * SQUARESIZE
size = (width, height)
RADIUS = int(SQUARESIZE / 2 - 5)

screen = pygame.display.set_mode(size)
draw_board(board, player_color, computer_color)
pygame.display.update()

myfont = pygame.font.SysFont("monospace", 50)

# Adjust initial turn based on chosen color
turn = 0 if chosen_color == RED else 1

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEMOTION and turn == 0:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            pygame.draw.circle(
                screen, player_color, (posx, int(SQUARESIZE / 2)), RADIUS
            )
            pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN and turn == 0:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARESIZE))
            posx = event.pos[0]
            col = int(math.floor(posx / SQUARESIZE))

            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 1)

                if winning_move(board, 1):
                    display_winner(1)
                    game_over = True

                print_board(board)
                draw_board(board, player_color, computer_color)
                turn += 1
                turn %= 2

        # Computer's turn
        if turn == 1 and not game_over:
            col, _ = minimax(board, difficulty, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, 2)

                if winning_move(board, 2):
                    display_winner(2)
                    game_over = True

                print_board(board)
                draw_board(board, player_color, computer_color)
                turn += 1
                turn %= 2

            pygame.time.wait(500)  # Add a delay for better visualization

        if game_over:
            pygame.time.wait(3000)
