# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game it looked fine: a title, a difficulty selector in the sidebar, a text box and Submit / New Game buttons. Once I started guessing with the Developer Debug Info open (secret = 50), it was clearly broken. The hints pointed the wrong way, the game ignored the difficulty in its instructions, and after winning, clicking "New Game" did nothing because the game stayed stuck on "You already won." I also noticed I got fewer guesses than the sidebar promised.

**Bugs I found (input → expected vs. actual → code-level cause):**

1. **Hints are backwards.** Guessing 60 when the secret is 50 should say "Go LOWER", but it says "📈 Go HIGHER!". Guessing 40 says "Go LOWER" instead of "Go HIGHER". *Cause:* `check_guess()` in `app.py` pairs the "Too High" outcome with the "Go HIGHER!" message (and "Too Low" with "Go LOWER!").
2. **The secret turns into a string on every even attempt.** On attempts 2, 4, 6…, the submit block runs `secret = str(st.session_state.secret)`. `check_guess()` then hits a `TypeError` and falls back to comparing text, so `check_guess(9, "50")` returns "Too High" because the text "9" sorts after "50". Expected: 9 is "Too Low". *Cause:* the `attempts % 2 == 0` block in the submit section of `app.py`, plus the `except TypeError` fallback in `check_guess()`.
3. **New Game doesn't actually start a new game.** After winning, clicking "New Game 🔁" should reset the game. Actually: the page still says "You already won. Start a new game to play again." and the old score and history remain. *Cause:* the `if new_game:` block only resets `attempts` and `secret`. It never resets `status`, `score` or `history`, and it always picks a secret from 1–100, ignoring the difficulty.
4. **Off-by-one attempts.** On Normal (8 attempts allowed), the game should show "Attempts left: 8" at the start. Actually it shows 7, because `attempts` starts at 1 in session state. The "Attempts left" banner is also drawn before the guess is counted, so it lags one guess behind.
5. **Score rewards wrong guesses.** A "Too High" guess on an even attempt adds +5 points (`update_score(0, "Too High", 2)` returns 5) instead of subtracting. *Cause:* the `attempt_number % 2 == 0` branch in `update_score()`.
6. **Difficulty ranges are wrong.** "Hard" uses a range of 1–50, which is easier than Normal's 1–100, and the main banner always says "Guess a number between 1 and 100" even on Easy (1–20). *Cause:* `get_range_for_difficulty()` and the hardcoded text in `st.info(...)`.
7. **Invalid input costs an attempt.** Typing "abc" shows "That is not a number." but still uses up a guess. *Cause:* `st.session_state.attempts += 1` runs before `parse_guess()` checks the input.

**Bug Reproduction Log**

Full trace: [`bug_trace_before.txt`](bug_trace_before.txt) (played with a fixed secret of 50).

| Input | Expected Behavior | Actual Behavior | Console Output / Error | Suspected Code Location |
|-------|-------------------|-----------------|------------------------|-------------------------|
| Guess 60, secret 50 (attempt 1) | Hint "Go LOWER" | Hint "📈 Go HIGHER!" | none (no crash) | `app.py`, `check_guess()` messages |
| Guess 40, secret 50 | Hint "Go HIGHER" | Hint "📉 Go LOWER!" | none | `app.py`, `check_guess()` messages |
| Guess 9 on attempt 4, secret 50 | Outcome "Too Low" | Outcome "Too High" (text "9" > "50") | `check_guess(9, '50') -> ('Too High', ...)` | `app.py`, submit block `str(secret)` + `except TypeError` in `check_guess()` |
| Win, then click "New Game" | Fresh game: status playing, score 0, empty history | "You already won. Start a new game to play again." Score 65 and history [60, 50] kept | `status=won attempts=0 score=65` | `app.py`, `if new_game:` block |
| Start a Normal game | "Attempts left: 8" | "Attempts left: 7" | `attempts=1` at start | `app.py`, `st.session_state.attempts = 1` |
| Wrong guess 60 on attempt 2 | Score goes down (−5) | Score goes up to 5 | `update_score(0, 'Too High', 2) -> 5` | `app.py`, `update_score()` even-attempt branch |
| Select "Hard" | Harder (wider) range than Normal, banner shows Hard's range | Range 1–50; banner says "between 1 and 100" | `Range: 1 to 50` | `app.py`, `get_range_for_difficulty()` and `st.info(...)` |
| Guess "abc" | Error message, no attempt used | "That is not a number." and attempts goes 1 → 2 | `attempts=2` | `app.py`, `attempts += 1` before `parse_guess()` |

-------|-------------------|-----------------|------------------------|
| | | | |
| | | | |
| | | | |

---

## 2. How did you use AI as a teammate?

I used Claude as my AI coding assistant for this project. I gave it the project instructions and my repo, and used it to explain the buggy logic, refactor the code into `logic_utils.py`, apply the fixes and write the tests. I checked its work by reading the changes, running `pytest` and replaying the game.

**AI explanation of a bug:** Claude explained why guessing 9 sometimes said "Too High" when the secret was 50: on every even attempt, the submit block runs `secret = str(st.session_state.secret)`. Comparing the integer 9 with the string "50" raises a `TypeError`, so `check_guess()` falls into its `except TypeError` branch and converts the guess to a string too. Strings are compared character by character, and "9" comes after "5", so "9" > "50" is `True` and the game calls 9 "Too High".

**A correct AI suggestion:** Claude suggested deleting the even-attempt `str()` conversion completely and making `check_guess()` convert both values with `int()` before comparing, instead of keeping the `try/except` fallback. This was correct because the bug came from comparing text, and comparing numbers removes it at the source. I verified it with `test_single_digit_guess_is_too_low_not_text_compared` (`check_guess(9, 50) == "Too Low"`) and `test_string_secret_is_compared_as_a_number`. I also replayed the game: guessing 9 on attempt 3 now correctly shows "Too low! Go HIGHER." (see `game_trace_after.txt`).

**An AI suggestion I did not accept as written:** The original `check_guess()` returned a tuple `(outcome, message)`, but the three starter tests expect only the outcome (`check_guess(50, 50) == "Win"`). One option was to keep the tuple and rewrite the starter tests to unpack it. I rejected that because the starter tests describe the intended behavior, and changing tests just to make them pass hides problems instead of fixing them. Instead, I had `check_guess()` return only the outcome and moved the messages into a separate `get_hint_message()` function. This also made the backwards-hint bug easier to fix and test on its own. I verified it by running all 3 starter tests unchanged alongside my new ones: 22 passed.

---

## 3. Debugging and testing your fixes

I decided a bug was really fixed only when two things were true: a pytest test targeting that exact bug passed, and the live game behaved correctly for the same input that broke it before. For the second part, I replayed the game with the secret fixed at 50, using the same inputs as my original bug trace, and compared [`bug_trace_before.txt`](bug_trace_before.txt) to [`game_trace_after.txt`](game_trace_after.txt). For example, guessing 60 used to say "Go HIGHER!" and now says "Too high! Go LOWER.", and clicking New Game after a win used to leave the game stuck, while now it resets to status "playing" with 0 attempts and a score of 0.

One test that taught me something was `test_wrong_guess_always_loses_points`. It loops through attempts 1 to 8 and checks that every wrong guess costs exactly 5 points. Testing a single attempt would have missed the bug, because the old code only gave +5 on *even* attempts. This showed me that some bugs only appear on certain inputs, so a test should cover a range of values.

AI helped me design the tests by suggesting edge cases I hadn't thought of, such as decimals like "12.7" (which the old code silently truncated to 12), whitespace-only input and the exact range boundaries 1 and 100. The final run:

```
22 passed in 0.05s
```

Full output is in [`test_results.txt`](test_results.txt) and in the README.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the whole script from top to bottom every time the user clicks a button or changes an input. That means a normal variable is created fresh on every click and forgets its old value. `st.session_state` is like a dictionary that survives those reruns, so the secret number, attempts, score and game status have to live there. This project showed me why resetting state carefully matters: the New Game bug happened because only some of the values in `st.session_state` were reset, so the old "won" status survived the rerun and blocked the new game.

---

## 5. Looking ahead: your developer habits

One habit I want to reuse is reproducing a bug with a specific input *before* fixing it, and then writing a test for that exact input. Having the before and after traces made it obvious whether each fix worked.

Next time I work with AI on a coding task, I would ask it to fix one bug at a time and review each change before moving on, instead of accepting a large set of changes at once. That would make it easier to see exactly what each change did.

This project showed me that AI-generated code can look clean and still be wrong in subtle ways, like comparing strings instead of numbers. I now treat AI code as a draft that needs testing, not as finished work.
