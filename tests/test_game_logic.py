import os
import sys

import pytest

# Make logic_utils importable when running pytest from the repo root.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from logic_utils import (  # noqa: E402
    check_guess,
    get_hint_message,
    get_range_for_difficulty,
    parse_guess,
    update_score,
)


# ----- Starter tests -------------------------------------------------------- #
def test_winning_guess():
    # If the secret is 50 and guess is 50, it should be a win
    result = check_guess(50, 50)
    assert result == "Win"


def test_guess_too_high():
    # If secret is 50 and guess is 60, hint should be "Too High"
    result = check_guess(60, 50)
    assert result == "Too High"


def test_guess_too_low():
    # If secret is 50 and guess is 40, hint should be "Too Low"
    result = check_guess(40, 50)
    assert result == "Too Low"


# ----- Bug 1: backwards hints ----------------------------------------------- #
def test_too_high_hint_tells_player_to_go_lower():
    assert "LOWER" in get_hint_message(check_guess(60, 50))


def test_too_low_hint_tells_player_to_go_higher():
    assert "HIGHER" in get_hint_message(check_guess(40, 50))


# ----- Bug 2: string comparison on even attempts ---------------------------- #
def test_single_digit_guess_is_too_low_not_text_compared():
    # As text, "9" > "50". As numbers, 9 < 50.
    assert check_guess(9, 50) == "Too Low"


def test_string_secret_is_compared_as_a_number():
    assert check_guess(9, "50") == "Too Low"
    assert check_guess(100, "50") == "Too High"


# ----- Bug 5: scoring ------------------------------------------------------- #
def test_wrong_guess_always_loses_points():
    for attempt in range(1, 9):
        assert update_score(50, "Too High", attempt) == 45
        assert update_score(50, "Too Low", attempt) == 45


def test_score_never_goes_below_zero():
    assert update_score(0, "Too High", 1) == 0
    assert update_score(3, "Too Low", 2) == 0


def test_first_try_win_is_worth_100():
    assert update_score(0, "Win", 1) == 100


def test_win_points_never_drop_below_10():
    assert update_score(0, "Win", 50) == 10


# ----- Bug 6: difficulty ranges --------------------------------------------- #
def test_hard_range_is_wider_than_normal():
    _, normal_high = get_range_for_difficulty("Normal")
    _, hard_high = get_range_for_difficulty("Hard")
    assert hard_high > normal_high


# ----- Edge cases: parse_guess (Challenge 1) ------------------------------- #
@pytest.mark.parametrize("raw", ["", "   ", None])
def test_empty_input_is_rejected(raw):
    ok, value, err = parse_guess(raw)
    assert ok is False and value is None and err == "Enter a guess."


@pytest.mark.parametrize("raw", ["abc", "12abc", "ten"])
def test_non_numeric_input_is_rejected(raw):
    ok, value, _ = parse_guess(raw)
    assert ok is False and value is None


def test_decimal_input_is_rejected_not_truncated():
    ok, value, _ = parse_guess("12.7")
    assert ok is False and value is None


def test_negative_number_is_out_of_range():
    ok, _, err = parse_guess("-5", 1, 100)
    assert ok is False and "between 1 and 100" in err


def test_number_above_range_is_rejected():
    ok, _, _ = parse_guess("101", 1, 100)
    assert ok is False


def test_range_boundaries_are_accepted():
    assert parse_guess("1", 1, 100) == (True, 1, None)
    assert parse_guess("100", 1, 100) == (True, 100, None)


def test_surrounding_whitespace_is_ignored():
    assert parse_guess("  42 ") == (True, 42, None)
