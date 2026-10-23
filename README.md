# 🎮 Game Glitch Detective: The Impossible Guess

## 🎯 Game Goal

Game Glitch Investigator is a number guessing game built with Streamlit. The game chooses a secret number from a range based on the difficulty level:

| Difficulty | Range | Guesses |
|------------|-------|---------|
| Easy | 1–20 | 6 |
| Normal | 1–100 | 8 |
| Hard | 1–200 | 5 |

The player has a set number of guesses to figure it out, using "Go HIGHER" or "Go LOWER" clues. Fewer guesses = a higher score.

The first version of the code was written by AI, and it was full of bugs. My job was to find the bugs, figure out why they happened, fix them, and then verify the fixes by running tests.

## 🛠️ Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest
```

## 🐞 Bugs Found

The original game trace is in [`bug_trace_before.txt`](bug_trace_before.txt). Section 1 of [`reflection.md`](reflection.md) has a reproduction table and full details.

1. **Backwards hints:** when you guessed too high, you were told to "Go HIGHER" (`check_guess()`).
2. **Secret turned into a string:** on even attempts, the secret was converted to a string, so `"9"` was treated as greater than `"50"` (submit block in `app.py`).
3. **New Game didn't reset the game:** win or lose, the game stayed on the "You already won" screen.
4. **Off-by-one attempts:** `attempts` started at 1, so Normal gave 7 guesses instead of 8, and the "Attempts left" banner lagged one guess behind.
5. **Wrong guesses were rewarded:** "Too High" guesses earned +5 points on even tries (`update_score()`).
6. **Wrong difficulty ranges:** Hard (1–50) was *easier* than Normal (1–100), and the banner always showed 1–100.
7. **Invalid input wasted a guess:** typing `"abc"` used up an attempt.

## 🔧 Fixes Implemented

- **Refactor:** I moved all game logic out of `app.py` into `logic_utils.py` so it can be tested without Streamlit. Now `app.py` only handles the UI and session state.
- **`check_guess()`** always compares integers and only returns the outcome. A new **`get_hint_message()`** function matches each outcome with its correct direction (e.g., `"📉 Too high! Go LOWER."`).
- **Removed** the code that converted the secret to a string on even attempts.
- **`start_new_game()`** is a new function that resets the secret, attempts, score, status and history, using the range for the current difficulty. It runs on the first load, when you click New Game, and when the difficulty is changed.
- **Attempts** start at 0 and only count valid guesses. The banner is drawn last, so "Attempts left" is always up to date.
- **`update_score()`**: winning on the first try gives you 100 points, and each wrong guess costs 5 points (but the score can never go below 0):

  ```python
  if outcome in ("Too High", "Too Low"):
      return max(0, current_score - 5)
  ```

- **Difficulty:** Hard is now 1–200, and the banner shows the real range for each difficulty.
- **`parse_guess()`** rejects empty input, non-numbers, decimals (instead of silently truncating them) and out-of-range numbers.

Each fix is marked with a `# FIX:` comment in the code.

## 📸 Demo Walkthrough

A sample game on Normal (range 1–100, 8 attempts) with the secret number 50:

1. The game begins by saying "Guess a number between 1 and 100. Attempts left: 8." The score is 0.
2. The user types in a guess of **60**. The game says "📉 Too high! Go LOWER." The score stays at 0 (it can't go below 0), and the attempts left drop to 7.
3. The user types **abc**. The game displays "That is not a whole number." No attempt is used; there are still 7 left.
4. The user enters **40**. The game says "📈 Too low! Go HIGHER." The score is still 0, with 6 tries left.
5. The user enters **9**. The old code wrongly called 9 "too high," but now the game shows the right message: "📈 Too low! Go HIGHER." There are 5 attempts left.
6. The user enters **50**. The game says "You won!" and balloons go off. The secret was 50, and the final score is 70 (100 − 30 = 70 points for a win on the fourth try).
7. The user clicks **New Game 🔁**. The history is cleared, the score resets to 0, "Attempts left" goes back to 8, and a new secret is chosen from 1–100.
8. The user switches to **Hard**. A new game starts automatically, and the banner says "Guess a number between 1 and 200. Attempts left: 5."

Terminal trace of the fixed game (same inputs as the original bug trace), also saved in [`game_trace_after.txt`](game_trace_after.txt):

```
Game Glitch Investigator: trace of the FIXED game (same inputs as bug_trace_before.txt)
(Streamlit strips emoji from messages in this trace.)

Game 1: Normal, secret=50
  start: Guess a number between 1 and 100. Attempts left: 8
  guess=  60 -> ['Too high! Go LOWER.']  | attempts=1 score=0 status=playing | Guess a number between 1 and 100. Attempts left: 7
  guess=  40 -> ['Too low! Go HIGHER.']  | attempts=2 score=0 status=playing | Guess a number between 1 and 100. Attempts left: 6
  guess=   9 -> ['Too low! Go HIGHER.']  | attempts=3 score=0 status=playing | Guess a number between 1 and 100. Attempts left: 5
  guess=  50 -> ['Correct!', 'You won! The secret was 50. Final score: 70. Click New Game to play again.']  | attempts=4 score=70 status=won | Guess a number between 1 and 100. Attempts left: 4
Game 2: Normal, secret=50, win on 2nd guess
  guess=  60 -> ['Too high! Go LOWER.']  | attempts=1 score=0 status=playing | Guess a number between 1 and 100. Attempts left: 7
  guess=  50 -> ['Correct!', 'You won! The secret was 50. Final score: 90. Click New Game to play again.']  | attempts=2 score=90 status=won | Guess a number between 1 and 100. Attempts left: 6
  click New Game ->
  after New Game: status=playing attempts=0 score=0 history=[]
  messages: []
Game 3: invalid input
  guess= abc -> ['That is not a whole number.']  | attempts=0 score=0 status=playing | Guess a number between 1 and 100. Attempts left: 8
Game 4: Hard difficulty range
  sidebar: ['Range: 1 to 200', 'Attempts allowed: 5'] | main: Guess a number between 1 and 200. Attempts left: 5
```

## 🧪 Test Results

There are 23 tests in [`tests/test_game_logic.py`](tests/test_game_logic.py): the 3 starter tests, tests for each fixed bug, and edge-case tests for `parse_guess()`. The output is also saved in [`test_results.txt`](test_results.txt).

```
============================= test session starts ==============================
platform linux -- Python 3.13.17, pytest-9.1.1, pluggy-1.7.0
cachedir: .pytest_cache
rootdir: C:\Users\saith\ai110-module1show-gameglitchinvestigator-starter
plugins: platformdirs-4.12.4, anyio-4.15.1
collecting ... collected 23 items

tests/test_game_logic.py::test_winning_guess PASSED                      [  4%]
tests/test_game_logic.py::test_guess_too_high PASSED                     [  8%]
tests/test_game_logic.py::test_guess_too_low PASSED                      [ 13%]
tests/test_game_logic.py::test_too_high_hint_tells_player_to_go_lower PASSED [ 17%]
tests/test_game_logic.py::test_too_low_hint_tells_player_to_go_higher PASSED [ 21%]
tests/test_game_logic.py::test_single_digit_guess_is_too_low_not_text_compared PASSED [ 26%]
tests/test_game_logic.py::test_string_secret_is_compared_as_a_number PASSED [ 30%]
tests/test_game_logic.py::test_wrong_guess_always_loses_points PASSED    [ 34%]
tests/test_game_logic.py::test_score_never_goes_below_zero PASSED        [ 39%]
tests/test_game_logic.py::test_first_try_win_is_worth_100 PASSED         [ 43%]
tests/test_game_logic.py::test_win_points_never_drop_below_10 PASSED     [ 47%]
tests/test_game_logic.py::test_hard_range_is_wider_than_normal PASSED    [ 52%]
tests/test_game_logic.py::test_empty_input_is_rejected[] PASSED          [ 56%]
tests/test_game_logic.py::test_empty_input_is_rejected[   ] PASSED       [ 60%]
tests/test_game_logic.py::test_empty_input_is_rejected[None] PASSED      [ 65%]
tests/test_game_logic.py::test_non_numeric_input_is_rejected[abc] PASSED [ 69%]
tests/test_game_logic.py::test_non_numeric_input_is_rejected[12abc] PASSED [ 73%]
tests/test_game_logic.py::test_non_numeric_input_is_rejected[ten] PASSED [ 78%]
tests/test_game_logic.py::test_decimal_input_is_rejected_not_truncated PASSED [ 82%]
tests/test_game_logic.py::test_negative_number_is_out_of_range PASSED    [ 86%]
tests/test_game_logic.py::test_number_above_range_is_rejected PASSED     [ 91%]
tests/test_game_logic.py::test_range_boundaries_are_accepted PASSED      [ 95%]
tests/test_game_logic.py::test_surrounding_whitespace_is_ignored PASSED  [100%]

============================== 23 passed in 0.04s ==============================
```

## 🚀 Stretch Features

- [x] **Challenge 1: Advanced Edge-Case Testing.** These tests cover empty and whitespace-only input, non-numeric strings, decimals, negative numbers, numbers above the range, exact range boundaries and surrounding whitespace. The prompts and rationale are in [`ai_interactions.md`](ai_interactions.md).
