"""Automated tests. Run with:  python -m unittest -v"""

import random
import unittest

import tictactoe as t


def board_from(text):
    """Make a board from 9 characters, using '.' for empty squares."""
    return [" " if char == "." else char for char in text]


def scripted(answers):
    iterator = iter(answers)
    return lambda prompt="": next(iterator)


HUMAN = {"name": "Human", "controller": "human"}


class BoardTests(unittest.TestCase):
    def test_every_winning_line(self):
        for line in t.WIN_LINES:
            board = t.new_board()
            for index in line:
                board[index] = "O"
            self.assertEqual(t.winner(board), "O")
            self.assertEqual(t.winning_line(board), line)

    def test_no_winner_yet(self):
        self.assertIsNone(t.winner(board_from("XO.......")))
        self.assertIsNone(t.winner(t.new_board()))

    def test_draw_board(self):
        board = board_from("XOXXOOOXX")
        self.assertIsNone(t.winner(board))
        self.assertTrue(t.is_full(board))
        self.assertTrue(t.game_over(board))

    def test_available_moves(self):
        self.assertEqual(t.available_moves(board_from("XO.......")), [2, 3, 4, 5, 6, 7, 8])

    def test_render_shows_numbers_for_empty_squares(self):
        text = t.render(board_from("XO..X...O"))
        self.assertIn(" X | O | 3 ", text)
        self.assertIn(" 4 | X | 6 ", text)
        self.assertIn(" 7 | 8 | O ", text)

    def test_parse_move(self):
        board = board_from("X........")
        self.assertEqual(t.parse_move("5", board), 4)
        self.assertEqual(t.parse_move(" 9 ", board), 8)
        for bad in ["", "0", "10", "abc", "-1", "1.5", "1"]:
            with self.assertRaises(t.MoveError, msg=bad):
                t.parse_move(bad, board)


class ComputerTests(unittest.TestCase):
    def test_easy_only_plays_empty_squares(self):
        rng = random.Random(1)
        board = board_from("XOXOXO...")
        for _ in range(100):
            self.assertIn(t.easy_move(board, rng), [6, 7, 8])

    def test_medium_takes_a_win(self):
        board = board_from("OO.XX....")
        self.assertEqual(t.medium_move(board, "O", random.Random(2)), 2)

    def test_medium_blocks(self):
        board = board_from("XX.O.....")
        self.assertEqual(t.medium_move(board, "O", random.Random(2)), 2)

    def test_medium_prefers_winning_over_blocking(self):
        board = board_from("XX.OO....")
        self.assertEqual(t.medium_move(board, "O", random.Random(2)), 5)

    def test_medium_takes_centre(self):
        self.assertEqual(t.medium_move(board_from("X........"), "O", random.Random(2)), 4)

    def test_hard_takes_win_and_blocks(self):
        self.assertEqual(t.hard_move(board_from("OO.XX...."), "O", random.Random(3)), 2)
        self.assertEqual(t.hard_move(board_from("XX.O....."), "O", random.Random(3)), 2)

    def test_hard_never_changes_the_board(self):
        board = board_from("X...O....")
        before = board[:]
        t.hard_move(board, "X", random.Random(4))
        self.assertEqual(board, before)

    def test_hard_vs_hard_is_always_a_draw(self):
        players = {s: {"name": s, "controller": "hard"} for s in "XO"}
        for seed in range(15):
            result = t.play_game(players, random.Random(seed), show=lambda text: None)
            self.assertIsNone(result["winner"], seed)
            self.assertTrue(t.is_full(result["board"]))

    def test_hard_never_loses_against_any_opponent(self):
        """Try EVERY possible sequence of human moves against the hard computer."""
        rng = random.Random(5)

        def explore(board, turn, computer_symbol):
            """Return how many complete games were checked below this position."""
            self.assertNotEqual(t.winner(board), t.other(computer_symbol), "hard computer lost!")
            if t.game_over(board):
                return 1
            if turn == computer_symbol:
                trial = board[:]
                trial[t.hard_move(trial, turn, rng)] = turn
                return explore(trial, t.other(turn), computer_symbol)
            total = 0
            for index in t.available_moves(board):
                trial = board[:]
                trial[index] = turn
                total += explore(trial, t.other(turn), computer_symbol)
            return total

        games_as_x = explore(t.new_board(), "X", "X")
        games_as_o = explore(t.new_board(), "X", "O")
        self.assertGreater(games_as_x, 50)
        self.assertGreater(games_as_o, 50)


class GameTests(unittest.TestCase):
    def two_humans(self):
        return {"X": dict(HUMAN, name="A"), "O": dict(HUMAN, name="B")}

    def play(self, answers):
        output = []
        result = t.play_game(self.two_humans(), random.Random(0), scripted(answers), output.append)
        return result, "\n".join(output)

    def test_x_wins_top_row(self):
        result, text = self.play(["1", "4", "2", "5", "3"])
        self.assertEqual(result["winner"], "X")
        self.assertIn("A (X) wins!", text)

    def test_o_wins(self):
        result, text = self.play(["1", "3", "2", "5", "9", "7"])
        self.assertEqual(result["winner"], "O")

    def test_draw(self):
        result, text = self.play(["1", "2", "3", "5", "4", "6", "8", "7", "9"])
        self.assertIsNone(result["winner"])
        self.assertFalse(result["quit"])
        self.assertIn("draw", text)

    def test_bad_input_and_taken_squares_do_not_use_a_turn(self):
        result, text = self.play(["abc", "0", "10", "1", "1", "4", "2", "5", "3"])
        self.assertEqual(result["winner"], "X")
        self.assertIn("already taken", text)

    def test_quit(self):
        result, text = self.play(["q"])
        self.assertTrue(result["quit"])

    def test_human_vs_computer_game_completes(self):
        players = {"X": dict(HUMAN, name="You"), "O": {"name": "Computer", "controller": "medium"}}
        answers = [str(n) for n in range(1, 10)] * 3
        result = t.play_game(players, random.Random(7), scripted(answers[:40]), lambda text: None)
        self.assertTrue(t.game_over(result["board"]))


class StatsAndMenuTests(unittest.TestCase):
    def test_stats(self):
        players = {"X": {"name": "You", "controller": "human"},
                   "O": {"name": "Computer", "controller": "hard"}}
        stats = t.new_stats()
        t.update_stats(stats, players, {"winner": "X", "quit": False})
        t.update_stats(stats, players, {"winner": "O", "quit": False})
        t.update_stats(stats, players, {"winner": None, "quit": False})
        t.update_stats(stats, players, {"winner": "X", "quit": True})   # abandoned: ignored
        self.assertEqual(stats, {"games": 3, "draws": 1, "wins": {"You": 1, "Computer": 1}})
        self.assertIn("Games played: 3", t.format_stats(stats))

    def test_empty_stats(self):
        self.assertEqual(t.format_stats(t.new_stats()), "No finished games yet.")

    def test_setup_one_player_as_x_and_as_o(self):
        players = t.setup_one_player(scripted(["3", "1"]), lambda text: None)
        self.assertEqual(players["X"]["controller"], "human")
        self.assertEqual(players["O"]["controller"], "hard")
        players = t.setup_one_player(scripted(["x", "1", "2"]), lambda text: None)
        self.assertEqual(players["O"]["controller"], "human")
        self.assertEqual(players["X"]["controller"], "easy")

    def test_play_again_loop(self):
        players = {"X": dict(HUMAN, name="A"), "O": dict(HUMAN, name="B")}
        stats = t.new_stats()
        answers = ["1", "4", "2", "5", "3", "y",     # game 1: X wins, play again
                   "1", "4", "2", "5", "3", "n"]     # game 2: X wins, stop
        t.play_session(players, stats, random.Random(0), scripted(answers), lambda text: None)
        self.assertEqual(stats["wins"], {"A": 2})


if __name__ == "__main__":
    unittest.main()
