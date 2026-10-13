# Tic-Tac-Toe

A command-line Tic-Tac-Toe game written in Python. Play against the computer at three difficulty levels, or against a friend on the same keyboard.

## Features
- **One player** against the computer:
  - Easy: plays randomly
  - Medium: wins when it can, blocks your winning move, otherwise takes the centre or a random square
  - Hard: unbeatable. It uses the minimax algorithm, so the best you can do is a draw
- **Two players** on the same keyboard
- Choose to play as X (go first) or O (go second)
- Squares are numbered 1 to 9 on the board, so moves are easy to type
- Mistakes never cost a turn: letters, numbers outside 1 to 9 and taken squares just ask again
- Play again with the same settings, or leave a game with `q`
- Session statistics for wins and draws
- Automated tests (25), including a test that tries **every possible sequence of human moves** to prove the hard computer never loses

## Requirements
- Python 3 installed
- No extra packages needed

## How to run
```
python tictactoe.py
```
If `python` is not recognized on Windows, use `py tictactoe.py`.

## How to play
Empty squares show their number. Type the number of the square you want and press Enter:

```
 1 | 2 | 3
---+---+---
 4 | 5 | 6
---+---+---
 7 | 8 | 9
```

Get three of your symbols in a row (across, down or diagonally) to win. X always goes first. Type `q` during a game to leave it.

Example:
```
 X | 2 | O
---+---+---
 4 | X | 6
---+---+---
 7 | 8 | O

You (X), choose a square (1-9): 9
That square is already taken. (Try again.)
```

## Tips
- Taking the centre (square 5) first is a strong opening.
- Against Hard, you cannot win. Try to draw every game.
- Try Hard as O (the computer goes first). It is the toughest setup.

## Running the tests
```
python -m unittest -v
```

## How it works
- The board is a list of 9 squares, and `WIN_LINES` lists the 8 winning combinations.
- `easy_move`, `medium_move` and `hard_move` are the three computer players.
- `minimax` looks at every possible future game and picks the move with the best guaranteed result. Results are remembered so it runs instantly.
- Game rules are separate from keyboard input, so everything can be tested automatically.

## Project structure
- `tictactoe.py`: the game
- `test_tictactoe.py`: automated tests
- `.gitignore`: files Git should ignore
- `readme.md`: this file

## Possible future improvements
- Larger boards (4x4)
- Save statistics to a file
- A graphical or web version
