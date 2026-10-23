# AI Interactions Log

> Stretch feature attempted: **Challenge 1: Advanced Edge-Case Testing (SF7)**. Other stretch sections were not attempted and have been removed.

---

## Test Generation (SF7)

I used Claude to help generate edge-case tests for `parse_guess()` and `check_guess()` in `logic_utils.py`. All tests are in `tests/test_game_logic.py`, and all 23 tests pass (see `test_results.txt` and the README).

**Prompt used:** I gave Claude the full project instructions and grading rubric and asked it to complete the project. For tests, the rubric's Challenge 1 requirement acted as the prompt:

```
At least three pytest cases targeting complex edge cases (e.g., handling
non-numeric strings, negative numbers, or empty inputs) are implemented.
```

Claude expanded that into the cases below, plus one test aimed at the even-attempt string-comparison bug.

| Edge Case | Prompt / Source | AI-Suggested Test | Did It Pass? | Your Reasoning |
|-----------|-------------|-------------------|--------------|----------------|
| Empty or whitespace-only input (`""`, `"   "`, `None`) | Challenge 1 rubric | `test_empty_input_is_rejected` (parametrized) | ✅ Yes | Clicking Submit with an empty box is the most common accidental input. It should show "Enter a guess." and not crash or use an attempt. |
| Non-numeric strings (`"abc"`, `"12abc"`, `"ten"`) | Challenge 1 rubric | `test_non_numeric_input_is_rejected` (parametrized) | ✅ Yes | Players may type words or mistype digits. `"12abc"` checks that partially numeric text is rejected, not partly parsed. |
| Decimal input (`"12.7"`) | Challenge 1 rubric | `test_decimal_input_is_rejected_not_truncated` | ✅ Yes (after fix) | The original code silently truncated 12.7 to 12, which hides a mistake from the player. The game only uses whole numbers, so decimals are now rejected. |
| Negative numbers (`"-5"` with range 1–100) | Challenge 1 rubric | `test_negative_number_is_out_of_range` | ✅ Yes | A negative guess can never be correct, so it shouldn't waste an attempt. The error message should tell the player the valid range. |
| Above the range (`"101"` with range 1–100) | Challenge 1 rubric | `test_number_above_range_is_rejected` | ✅ Yes | Same reasoning as negatives: guesses outside the difficulty's range are rejected. |
| Exact boundaries (`"1"` and `"100"`) | Challenge 1 rubric | `test_range_boundaries_are_accepted` | ✅ Yes | Off-by-one mistakes happen at the edges. The range is inclusive, so 1 and 100 must be accepted. |
| Single-digit vs two-digit compare (`check_guess(9, "50")`) | Bug 2 (even-attempt bug) | `test_string_secret_is_compared_as_a_number` | ✅ Yes (after fix) | This is the even-attempt bug: as text, "9" > "50". The test would fail on the original code and proves numbers are now compared as numbers. |

**Design decision behind the decimal test:** the original `parse_guess()` silently truncated `"12.7"` to 12. While fixing the code, `parse_guess()` was changed to reject decimals instead, so the player is told about the mistake rather than having their guess quietly changed. The decimal test locks in that behavior.
