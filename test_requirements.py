import pytest
from datetime import datetime, timedelta

from fitness_logic import (
    escape_markdown_v2,
    calc_bmr, calc_tdee, adjust_tdee_for_goal, calc_macros,
    level_by_age, parse_time_hhmm, ensure_future
)

def test_escape_markdown_none_and_empty():
    assert escape_markdown_v2(None) is None
    assert escape_markdown_v2("") == ""

@pytest.mark.parametrize("raw, expected_substrings", [
    ("a_b", [r"a\_b"]),
    ("(hi)!", [r"\(hi\)\!"]),
    ("2+2=4.", [r"2\+2\=4\."]),
])
def test_escape_markdown_special_chars(raw, expected_substrings):
    out = escape_markdown_v2(raw)
    for s in expected_substrings:
        assert s in out

def test_calorie_requirements_bmr_tdee_goal_adjustment():
    bmr = calc_bmr(sex="Ч", height_cm=180, weight_kg=80, age=25)
    tdee = calc_tdee(bmr, 1.55)

    cut = adjust_tdee_for_goal(tdee, "Схуднення")
    bulk = adjust_tdee_for_goal(tdee, "Набір маси")
    keep = adjust_tdee_for_goal(tdee, "Підтримання")

    assert cut == pytest.approx(tdee * 0.85)
    assert bulk == pytest.approx(tdee * 1.15)
    assert keep == pytest.approx(tdee)

def test_calorie_requirements_invalid_inputs_raise():
    with pytest.raises(ValueError):
        calc_bmr("Ч", 0, 80, 25)
    with pytest.raises(ValueError):
        calc_bmr("Ч", 180, -1, 25)
    with pytest.raises(ValueError):
        calc_bmr("Ч", 180, 80, 0)

def test_macros_requirements():
    m = calc_macros(2000)
    assert m.protein_g == int((0.3 * 2000) / 4)
    assert m.fat_g == int((0.25 * 2000) / 9)
    assert m.carbs_g == int((0.45 * 2000) / 4)

@pytest.mark.parametrize("age, expected", [
    (18, "початковий"),
    (25, "середній"),
    (39, "середній"),
    (40, "помірний"),
])
def test_level_by_age(age, expected):
    assert level_by_age(age) == expected

@pytest.mark.parametrize("txt, exp", [
    ("07:30", (7, 30)),
    ("0:00", (0, 0)),
    ("23:59", (23, 59)),
])
def test_parse_time_ok(txt, exp):
    assert parse_time_hhmm(txt) == exp

@pytest.mark.parametrize("bad", ["0730", "24:00", "12:60", "12:", ":10", "aa:bb", "12:30:40"])
def test_parse_time_bad(bad):
    with pytest.raises(ValueError):
        parse_time_hhmm(bad)

def test_ensure_future_requirement():
    now = datetime.now()
    future = now + timedelta(minutes=1)
    past = now - timedelta(minutes=1)

    ensure_future(future, now)  # ok
    with pytest.raises(ValueError):
        ensure_future(past, now)
    with pytest.raises(ValueError):
        ensure_future(now, now)
