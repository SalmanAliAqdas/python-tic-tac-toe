"""Tic-Tac-Toe in the terminal.

Play against the computer (easy, medium or unbeatable hard level)
or against a friend on the same keyboard.
"""

import random

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),   # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),   # columns
    (0, 4, 8), (2, 4, 6),              # diagonals
]
LEVELS = {"1": "easy", "2": "medium", "3": "hard"}


class MoveError(Exception):
    """Input that is not a usable move (it does not use up a turn)."""


# ---------- Board rules (pure functions, easy to test) ----------

def new_board():
    return [" "] * 9


def other(symbol):
    return "O" if symbol == "X" else "X"


def winner(board):
    """Return 'X', 'O' or None."""
    for a, b, c in WIN_LINES:
        if board[a] != " " and board[a] == board[b] == board[c]:
            return board[a]
    return None


def winning_line(board):
    for line in WIN_LINES:
        a, b, c = line
        if board[a] != " " and board[a] == board[b] == board[c]:
            return line
    return None


def available_moves(board):
    return [index for index, cell in enumerate(board) if cell == " "]


def is_full(board):
    return " " not in board


def game_over(board):
    return winner(board) is not None or is_full(board)


def render(board):
    """Draw the board. Empty squares show their number (1-9)."""
    cells = [cell if cell != " " else str(index + 1) for index, cell in enumerate(board)]
    rows = [f" {cells[i]} | {cells[i + 1]} | {cells[i + 2]} " for i in (0, 3, 6)]
    return "\n---+---+---\n".join(rows)


def parse_move(text, board):
    """Turn '5' into board index 4. Raises MoveError for anything unusable."""
    text = text.strip()
    if not text.isdigit() or not 1 <= int(text) <= 9:
        raise MoveError("Please type a square number from 1 to 9, or 'q' to quit.")
    index = int(text) - 1
    if board[index] != " ":
        raise MoveError("That square is already taken.")
    return index


# ---------- Computer players ----------

def easy_move(board, rng=random):
    return rng.choice(available_moves(board))


def find_winning_move(board, symbol):
    """A square that would win the game for `symbol` right now, or None."""
    for index in available_moves(board):
        trial = board[:]
        trial[index] = symbol
        if winner(trial) == symbol:
            return index
    return None


def medium_move(board, me, rng=random):
    """Win if possible, otherwise block, otherwise centre, otherwise random."""
    move = find_winning_move(board, me)
    if move is None:
        move = find_winning_move(board, other(me))
    if move is None and board[4] == " ":
        move = 4
    if move is None:
        move = rng.choice(available_moves(board))
    return move


_memory = {}


def minimax(board, turn, me):
    """Score a position for `me` assuming both sides play perfectly.

    Positive = good for me (faster wins score higher), negative = bad, 0 = draw.
    """
    key = (tuple(board), turn, me)
    if key in _memory:
        return _memory[key]

    champion = winner(board)
    spaces = len(available_moves(board))
    if champion == me:
        score = 1 + spaces
    elif champion is not None:
        score = -(1 + spaces)
    elif spaces == 0:
        score = 0
    else:
        scores = []
        for index in available_moves(board):
            board[index] = turn
            scores.append(minimax(board, other(turn), me))
            board[index] = " "
        score = max(scores) if turn == me else min(scores)

    _memory[key] = score
    return score


def hard_move(board, me, rng=random):
    """Unbeatable: tries every move and assumes the opponent also plays perfectly."""
    best_score, best_moves = None, []
    for index in available_moves(board):
        board[index] = me
        score = minimax(board, other(me), me)
        board[index] = " "
        if best_score is None or score > best_score:
            best_score, best_moves = score, [index]
        elif score == best_score:
            best_moves.append(index)
    return rng.choice(best_moves)


def computer_move(board, me, level, rng=random):
    if level == "easy":
        return easy_move(board, rng)
    if level == "medium":
        return medium_move(board, me, rng)
    return hard_move(board, me, rng)


# ---------- Playing one game ----------

def play_game(players, rng=random, ask=input, show=print):
    """Play one game.

    `players` maps 'X' and 'O' to a name and a controller, for example:
        {"X": {"name": "You", "controller": "human"},
         "O": {"name": "Computer", "controller": "hard"}}
    X always goes first. Returns {'winner': 'X'/'O'/None, 'quit': bool, 'board': board}.
    """
    board = new_board()
    turn = "X"

    while not game_over(board):
        show("\n" + render(board))
        player = players[turn]

        if player["controller"] == "human":
            while True:
                text = ask(f"\n{player['name']} ({turn}), choose a square (1-9): ").strip().lower()
                if text in ("q", "quit"):
                    show("Game abandoned.")
                    return {"winner": None, "quit": True, "board": board}
                try:
                    move = parse_move(text, board)
                    break
                except MoveError as error:
                    show(f"{error} (Try again.)")
        else:
            move = computer_move(board, turn, player["controller"], rng)
            show(f"\n{player['name']} ({turn}) plays square {move + 1}.")

        board[move] = turn
        turn = other(turn)

    show("\n" + render(board))
    champion = winner(board)
    if champion:
        show(f"\n{players[champion]['name']} ({champion}) wins!")
    else:
        show("\nIt's a draw.")
    return {"winner": champion, "quit": False, "board": board}


# ---------- Statistics and menus ----------

def new_stats():
    return {"games": 0, "draws": 0, "wins": {}}


def update_stats(stats, players, result):
    if result["quit"]:
        return
    stats["games"] += 1
    if result["winner"] is None:
        stats["draws"] += 1
    else:
        name = players[result["winner"]]["name"]
        stats["wins"][name] = stats["wins"].get(name, 0) + 1


def format_stats(stats):
    if stats["games"] == 0:
        return "No finished games yet."
    lines = [f"Games played: {stats['games']}"]
    for name, count in stats["wins"].items():
        lines.append(f"  {name}: {count} win(s)")
    lines.append(f"  Draws: {stats['draws']}")
    return "\n".join(lines)


def choose_option(title, options, ask=input, show=print):
    show(title)
    for key, label in options.items():
        show(f"  {key}. {label}")
    while True:
        choice = ask("Your choice: ").strip()
        if choice in options:
            return choice
        show("Please type one of the numbers shown.")


def setup_one_player(ask=input, show=print):
    level_key = choose_option("\nDifficulty:", {
        "1": "Easy (plays randomly)",
        "2": "Medium (wins and blocks when it can)",
        "3": "Hard (unbeatable, the best you can get is a draw)",
    }, ask, show)
    side_key = choose_option("\nWhich side?", {
        "1": "X (you go first)",
        "2": "O (computer goes first)",
    }, ask, show)
    human, computer = ("X", "O") if side_key == "1" else ("O", "X")
    return {
        human: {"name": "You", "controller": "human"},
        computer: {"name": "Computer", "controller": LEVELS[level_key]},
    }


def setup_two_players():
    return {
        "X": {"name": "Player X", "controller": "human"},
        "O": {"name": "Player O", "controller": "human"},
    }


def play_session(players, stats, rng=random, ask=input, show=print):
    """Play repeatedly with the same players until they stop."""
    while True:
        result = play_game(players, rng, ask, show)
        update_stats(stats, players, result)
        if result["quit"]:
            return
        again = ask("\nPlay again with the same settings? (y/n): ").strip().lower()
        if again != "y":
            return


def main():
    stats = new_stats()
    while True:
        print()
        print("Tic-Tac-Toe")
        print("  1. One player (against the computer)")
        print("  2. Two players")
        print("  3. Statistics")
        print("  q. Quit")
        choice = input("Your choice: ").strip().lower()

        if choice == "1":
            play_session(setup_one_player(), stats)
        elif choice == "2":
            play_session(setup_two_players(), stats)
        elif choice == "3":
            print()
            print(format_stats(stats))
            input("\nPress Enter to go back to the menu...")
        elif choice in ("q", "quit", "exit"):
            print()
            print(format_stats(stats))
            print("Thanks for playing. Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3 or q.")


if __name__ == "__main__":
    main()
