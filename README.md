# 🎮 Game Glitch Investigator: The Impossible Guesser

## 🎯 Game Purpose

Game Glitch Investigator is a number guessing game built with Streamlit. The game picks a secret number in a range set by the difficulty (Easy 1–20, Normal 1–100, Hard 1–200). The player guesses until they find it, using "Go HIGHER" / "Go LOWER" hints, within a limited number of attempts. Fewer guesses means a higher score.

The starter code was written by an AI and was full of glitches. My job was to find the bugs, understand their causes, fix them, and prove the fixes with tests.

## 🛠️ Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m streamlit run app.py
python -m pytest
```

## 🐞 Bugs Found

Full details and a reproduction table are in [`reflection.md`](reflection.md) section 1. A trace of the original game is in [`bug_trace_before.txt`](bug_trace_before.txt).

1. **Backwards hints:** guessing too high told you to "Go HIGHER" (`check_guess`).
2. **Secret became a string on even attempts,** so `"9"` was treated as higher than `"50"` (submit block in `app.py`).
3. **New Game didn't reset the game:** after winning or losing, the game stayed stuck on "You already won".
4. **Off-by-one attempts:** `attempts` started at 1, so Normal gave 7 guesses instead of 8, and the "Attempts left" banner lagged behind.
5. **Scoring rewarded wrong guesses:** "Too High" guesses earned +5 on even attempts (`update_score`).
6. **Difficulty ranges were wrong:** Hard (1–50) was easier than Normal (1–100), and the banner always said 1–100.
7. **Invalid input used up an attempt:** typing "abc" still counted as a guess.

## 🔧 Fixes Applied

- **Refactored** all game logic out of `app.py` into `logic_utils.py`, so it can be tested without Streamlit. `app.py` now only handles the UI and session state.
- **`check_guess()`** always compares integers and returns just the outcome. A new **`get_hint_message()`** maps each outcome to the correct direction ("Too high! Go LOWER.").
- **Removed** the code that converted the secret to a string on even attempts.
- **New `start_new_game()`** resets secret, attempts, score, status and history, using the current difficulty's range. It runs on first load, on New Game and when the difficulty changes.
- **Attempts** start at 0 and are only counted for valid guesses. The banner is drawn last so "Attempts left" is always current.
- **`update_score()`**: every wrong guess costs 5 points (but the score never drops below 0), and a first-try win is worth 100.
- **Difficulty**: Hard is now 1–200, and the banner shows the real range.
- **`parse_guess()`** rejects empty input, non-numbers, decimals (instead of silently truncating) and out-of-range numbers.

Each fix is marked with a `# FIX:` comment in the code.

## 📸 Demo Walkthrough

A sample game on Normal (range 1–100, 8 attempts), with the secret number 50:

1. The game starts and shows "Guess a number between 1 and 100. Attempts left: 8" and a score of 0.
2. User enters a guess of **60**. The game shows "📉 Too high! Go LOWER." The score stays at 0 (it can't go below 0) and attempts left drops to 7.
3. User enters **abc**. The game shows "That is not a whole number." No attempt is used (still 7 left).
4. User enters **40**. The game shows "📈 Too low! Go HIGHER." Score is still 0, attempts left is 6.
5. User enters **9**, which the old code wrongly called "too high". The game correctly shows "📈 Too low! Go HIGHER." Attempts left is 5.
6. User enters **50**. Balloons appear and the game shows "You won! The secret was 50. Final score: 70." (A win on attempt 4 earns 100 − 30 = 70 points.)
7. User clicks **New Game 🔁**. The score resets to 0, history clears, "Attempts left" goes back to 8, and a new secret is picked from 1–100.
8. User switches to **Hard**. A new game starts automatically and the banner reads "Guess a number between 1 and 200. Attempts left: 5".

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

`tests/test_game_logic.py` has 23 tests: the 3 starter tests, tests targeting each fixed bug, and edge-case tests for `parse_guess()`. Output is also saved in [`test_results.txt`](test_results.txt).

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

- [x] **Challenge 1: Advanced Edge-Case Testing.** Tests cover empty and whitespace-only input, non-numeric strings, decimals, negative numbers, numbers above the range, exact range boundaries and surrounding whitespace. Prompts and rationale are in [`ai_interactions.md`](ai_interactions.md).
