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

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.
