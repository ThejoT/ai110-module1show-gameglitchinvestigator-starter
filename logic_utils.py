"""Game logic for Game Glitch Investigator, kept separate from the Streamlit UI."""

# FIX: Refactored all game logic out of app.py into this file with Claude's help,
# so it can be unit tested without running Streamlit.

DIFFICULTY_RANGES = {
    "Easy": (1, 20),
    "Normal": (1, 100),
    # FIX: Hard used to be 1-50 (easier than Normal). Widened it so Hard is hardest.
    "Hard": (1, 200),
}

ATTEMPT_LIMITS = {
    "Easy": 6,
    "Normal": 8,
    "Hard": 5,
}

# FIX: Hint messages were backwards ("Too High" said "Go HIGHER"). Each outcome now
# maps to the direction the player should actually move.
HINT_MESSAGES = {
    "Win": "🎉 Correct!",
    "Too High": "📉 Too high! Go LOWER.",
    "Too Low": "📈 Too low! Go HIGHER.",
}


def get_range_for_difficulty(difficulty: str):
    """Return the (low, high) inclusive range for a difficulty, defaulting to Normal."""
    return DIFFICULTY_RANGES.get(difficulty, DIFFICULTY_RANGES["Normal"])


def parse_guess(raw: str, low: int = None, high: int = None):
    """
    Parse user input into an int guess.

    Returns: (ok: bool, guess_int: int | None, error_message: str | None)
    If low/high are given, guesses outside that range are rejected.
    """
    if raw is None or raw.strip() == "":
        return False, None, "Enter a guess."

    raw = raw.strip()
    try:
        value = int(raw)
    except ValueError:
        # FIX: "12.7" used to be silently truncated to 12. Whole numbers only now.
        return False, None, "That is not a whole number."

    if low is not None and high is not None and not (low <= value <= high):
        return False, None, f"Enter a number between {low} and {high}."

    return True, value, None


def check_guess(guess: int, secret: int) -> str:
    """
    Compare guess to secret and return the outcome: "Win", "Too High" or "Too Low".

    FIX: Both values are always compared as integers. The old version fell back to
    comparing strings, which made "9" count as higher than "50".
    """
    guess, secret = int(guess), int(secret)
    if guess == secret:
        return "Win"
    if guess > secret:
        return "Too High"
    return "Too Low"


def get_hint_message(outcome: str) -> str:
    """Return the player-facing hint message for an outcome."""
    return HINT_MESSAGES[outcome]


def update_score(current_score: int, outcome: str, attempt_number: int) -> int:
    """
    Update score based on outcome and which attempt this was (1 = first guess).

    A win is worth 100 on the first try, minus 10 per extra attempt (minimum 10).
    Every wrong guess costs 5 points.
    """
    if outcome == "Win":
        # FIX: was 100 - 10 * (attempt_number + 1), which docked points twice.
        points = max(10, 100 - 10 * (attempt_number - 1))
        return current_score + points

    # FIX: wrong "Too High" guesses used to *earn* +5 on even attempts.
    if outcome in ("Too High", "Too Low"):
        return current_score - 5

    return current_score
