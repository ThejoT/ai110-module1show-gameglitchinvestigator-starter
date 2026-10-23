import random

import streamlit as st

# FIX: Logic moved into logic_utils.py (refactored with Claude) so it can be tested.
from logic_utils import (
    ATTEMPT_LIMITS,
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)

st.set_page_config(page_title="Glitchy Guesser", page_icon="🎮")

st.title("🎮 Game Glitch Investigator")
st.caption("An AI-generated guessing game. Something is off.")

st.sidebar.header("Settings")

difficulty = st.sidebar.selectbox(
    "Difficulty",
    ["Easy", "Normal", "Hard"],
    index=1,
)

attempt_limit = ATTEMPT_LIMITS[difficulty]
low, high = get_range_for_difficulty(difficulty)

st.sidebar.caption(f"Range: {low} to {high}")
st.sidebar.caption(f"Attempts allowed: {attempt_limit}")


def start_new_game():
    """Reset every piece of game state for a fresh game at the current difficulty."""
    # FIX: New Game used to reset only attempts and secret, so status stayed "won"/"lost"
    # and the game was stuck. It also ignored the difficulty range. Now everything resets.
    st.session_state.secret = random.randint(low, high)
    st.session_state.attempts = 0  # FIX: was 1, which cost the player a guess
    st.session_state.score = 0
    st.session_state.status = "playing"
    st.session_state.history = []
    st.session_state.difficulty = difficulty


# FIX: start a new game on first load, or when the difficulty changes, so the secret
# always comes from the selected difficulty's range.
if "secret" not in st.session_state or st.session_state.get("difficulty") != difficulty:
    start_new_game()

st.subheader("Make a guess")

# FIX: the banner used to be hardcoded to "1 and 100" and drawn before the guess was
# counted. A placeholder lets us fill it in at the end with up-to-date numbers.
status_banner = st.empty()

debug_panel = st.expander("Developer Debug Info")

raw_guess = st.text_input(
    "Enter your guess:",
    key=f"guess_input_{difficulty}"
)

col1, col2, col3 = st.columns(3)
with col1:
    submit = st.button("Submit Guess 🚀")
with col2:
    new_game = st.button("New Game 🔁")
with col3:
    show_hint = st.checkbox("Show hint", value=True)

if new_game:
    start_new_game()
    st.success("New game started.")
    st.rerun()

if submit and st.session_state.status == "playing":
    ok, guess_int, err = parse_guess(raw_guess, low, high)

    if not ok:
        # FIX: invalid input no longer uses up an attempt.
        st.error(err)
    else:
        st.session_state.attempts += 1
        st.session_state.history.append(guess_int)

        # FIX: removed the code that turned the secret into a string on even attempts.
        # check_guess now always compares two integers.
        outcome = check_guess(guess_int, st.session_state.secret)

        if show_hint:
            st.warning(get_hint_message(outcome))

        st.session_state.score = update_score(
            current_score=st.session_state.score,
            outcome=outcome,
            attempt_number=st.session_state.attempts,
        )

        if outcome == "Win":
            st.balloons()
            st.session_state.status = "won"
        elif st.session_state.attempts >= attempt_limit:
            st.session_state.status = "lost"

if st.session_state.status == "won":
    st.success(
        f"You won! The secret was {st.session_state.secret}. "
        f"Final score: {st.session_state.score}. Click New Game to play again."
    )
elif st.session_state.status == "lost":
    st.error(
        f"Out of attempts! The secret was {st.session_state.secret}. "
        f"Score: {st.session_state.score}. Click New Game to try again."
    )

# Filled in last so the debug values reflect the guess that was just made.
with debug_panel:
    st.write("Secret:", st.session_state.secret)
    st.write("Attempts:", st.session_state.attempts)
    st.write("Score:", st.session_state.score)
    st.write("Difficulty:", difficulty)
    st.write("History:", st.session_state.history)

status_banner.info(
    f"Guess a number between {low} and {high}. "
    f"Attempts left: {attempt_limit - st.session_state.attempts}"
)

st.divider()
st.caption("Built by an AI that claims this code is production-ready.")
