# fitness_logic.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

ESCAPE_CHARS = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']

def escape_markdown_v2(text: str | None) -> str | None:
    if not text:
        return text
    for ch in ESCAPE_CHARS:
        text = text.replace(ch, f"\\{ch}")
    return text

def calc_bmr(sex: str, height_cm: float, weight_kg: float, age: int) -> float:
    if height_cm <= 0 or weight_kg <= 0 or age <= 0:
        raise ValueError("height/weight/age must be positive")
    s = sex.strip().upper()
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if s == "Ч" else -161)

def calc_tdee(bmr: float, activity_factor: float = 1.55) -> float:
    if bmr <= 0 or activity_factor <= 0:
        raise ValueError("bmr/activity_factor must be positive")
    return bmr * activity_factor

def adjust_tdee_for_goal(tdee: float, goal: str) -> float:
    if tdee <= 0:
        raise ValueError("tdee must be positive")
    g = goal.strip()
    if g == "Схуднення":
        return tdee * 0.85
    if g == "Набір маси":
        return tdee * 1.15
    return tdee  # "Підтримання" або інше значення за замовчуванням

@dataclass(frozen=True)
class Macros:
    protein_g: int
    fat_g: int
    carbs_g: int

def calc_macros(kcal: int) -> Macros:
    if kcal <= 0:
        raise ValueError("kcal must be positive")
    protein = int((0.3 * kcal) / 4)
    fat = int((0.25 * kcal) / 9)
    carbs = int((0.45 * kcal) / 4)
    return Macros(protein, fat, carbs)

def level_by_age(age: int) -> str:
    if age <= 0:
        raise ValueError("age must be positive")
    if age < 25:
        return "початковий"
    if age < 40:
        return "середній"
    return "помірний"

def parse_time_hhmm(text: str) -> tuple[int, int]:
    t = text.strip()
    if ":" not in t:
        raise ValueError("missing ':'")
    parts = t.split(":")
    if len(parts) != 2:
        raise ValueError("bad time split")
    hour, minute = map(int, parts)
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError("out of range")
    return hour, minute

def ensure_future(when: datetime, now: datetime) -> None:
    if when <= now:
        raise ValueError("time is in the past")
