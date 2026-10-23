# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

The first time I ran the game it looked fine: a title, a difficulty selector in the sidebar, a text box and Submit / New Game buttons. Once I started guessing with the Developer Debug Info open (secret = 50), it was clearly broken. The hints pointed the wrong way, the game ignored the difficulty in its instructions, and after winning, clicking "New Game" did nothing because the game stayed stuck on "You already won." I also noticed I got fewer guesses than the sidebar promised.

The first two bugs I noticed were in the hints. Guessing 60 when the secret was 50 should have said "Go LOWER," but it said "📈 Go HIGHER!", and guessing 40 said "Go LOWER" instead of "Go HIGHER." The cause was in `check_guess()` in `app.py`, which paired the "Too High" outcome with the "Go HIGHER!" message and "Too Low" with "Go LOWER!" Worse, on every even attempt the submit block ran `secret = str(st.session_state.secret)`, which turned the secret into text. That made `check_guess()` hit a `TypeError` and fall back to comparing strings, so `check_guess(9, "50")` returned "Too High" because the text "9" sorts after "50," even though 9 is actually too low.

The game's state and scoring were also broken. After winning, clicking "New Game 🔁" should have started a fresh game, but the page stayed stuck on "You already won," and the old score and history remained, because the `if new_game:` block only reset `attempts` and `secret` and never reset `status`, `score` or `history`. The `attempts` counter started at 1 instead of 0, so Normal showed "Attempts left: 7" instead of 8, and the banner was drawn before each guess was counted, so it lagged behind. In `update_score()`, a wrong "Too High" guess on an even attempt added 5 points instead of subtracting them (`update_score(0, "Too High", 2)` returned 5).

Finally, there were problems with difficulty and input. `get_range_for_difficulty()` gave Hard a range of 1–50, which made it easier than Normal's 1–100, and the main banner always said "Guess a number between 1 and 100," even on Easy (1–20). Typing something invalid like "abc" showed "That is not a number." but still used up an attempt, because `st.session_state.attempts += 1` ran before `parse_guess()` checked the input.

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

**An AI suggestion I did not accept as written:** Claude's fixed `update_score()` subtracted 5 points for every wrong guess with no lower limit, so a player who lost a game on Easy could end with a score of −30. The math was correct, but I didn't like the result: a negative score feels like a punishment in a casual guessing game, and it was confusing to see a win on the fourth guess show "Final score: 55" because of the earlier penalties. I changed it to `max(0, current_score - 5)` so the score never drops below 0, and marked the change with a `# FIX (my change)` comment. I verified it by updating `test_wrong_guess_always_loses_points` to start from 50, adding `test_score_never_goes_below_zero`, and replaying the game: wrong guesses now leave the score at 0, and winning on the fourth guess shows "Final score: 70." All 23 tests pass.

---

## 3. Debugging and testing your fixes

I tested iteratively, checking each fix as soon as it was made instead of waiting until the end. I decided a bug was really fixed only when two things were true: a pytest test targeting that exact bug passed, and the live game behaved correctly for the same input that broke it before. For the second part, I replayed the game with the secret fixed at 50, using the same inputs as my original bug trace, and compared [`bug_trace_before.txt`](bug_trace_before.txt) to [`game_trace_after.txt`](game_trace_after.txt). For example, guessing 60 used to say "Go HIGHER!" and now says "Too high! Go LOWER.", and clicking New Game after a win used to leave the game stuck, while now it resets to status "playing" with 0 attempts and a score of 0.

One test that taught me something was `test_wrong_guess_always_loses_points`. It loops through attempts 1 to 8 and checks that every wrong guess costs exactly 5 points (starting from a score of 50). Testing a single attempt would have missed the bug, because the old code only gave +5 on *even* attempts. This showed me that some bugs only appear on certain inputs, so a test should cover a range of values.

AI helped me design the tests by suggesting edge cases I hadn't thought of, such as decimals like "12.7" (which the old code silently truncated to 12), whitespace-only input and the exact range boundaries 1 and 100. The final run:

```
23 passed in 0.04s
```

Full output is in [`test_results.txt`](test_results.txt) and in the README.

---

## 4. What did you learn about Streamlit and state?

Streamlit reruns the whole script from top to bottom every time the user clicks a button or changes an input. That means a normal variable is created fresh on every click and forgets its old value. `st.session_state` is like a dictionary that survives those reruns, so the secret number, attempts, score and game status have to live there. This project showed me why resetting state carefully matters: the New Game bug happened because only some of the values in `st.session_state` were reset, so the old "won" status survived the rerun and blocked the new game.

---

## 5. Looking ahead: your developer habits

The habit I want to reuse most is iterative improvement. Instead of trying to fix everything at once, I worked in small rounds: reproduce a bug with a specific input, make one fix, run the tests and replay the game, then move on to the next bug. Each round built on the last one, which is why my commit history goes from logging the bugs, to fixing them, to documenting the results. This also made mistakes easy to catch, because if something broke, I knew it came from the most recent change.

Next time I work with AI on a coding task, I would apply that same iterative approach to the AI itself. I would ask it to fix one bug at a time and review each change before moving on, instead of accepting a large set of changes at once. Smaller steps would make it easier to understand exactly what each change did and to push back on anything I didn't agree with.

This project changed how I think about AI-generated code: it can look clean and still be wrong in subtle ways, like comparing strings instead of numbers. I now treat AI code as a first draft that gets better through testing and repeated improvement, not as finished work.
