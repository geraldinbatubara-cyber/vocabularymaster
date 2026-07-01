from __future__ import annotations

from dataclasses import dataclass


TIME_LIMIT_SECONDS = 10
NORMAL_BASE_POINTS = 100
BONUS_BASE_POINTS = 200
NORMAL_STREAK_BONUS = 25
BONUS_STREAK_BONUS = 50


@dataclass(frozen=True)
class ScoreResult:
    points: int
    new_streak: int
    correct: bool
    timed_out: bool
    feedback: str


def score_answer(
    answer: str | None,
    correct_answer: str,
    current_streak: int,
    seconds_used: float,
    is_bonus: bool = False,
) -> ScoreResult:
    if answer is None or seconds_used > TIME_LIMIT_SECONDS:
        return ScoreResult(
            points=0,
            new_streak=0,
            correct=False,
            timed_out=True,
            feedback=f"Waktu habis. Jawaban benar: {correct_answer}",
        )

    is_correct = answer.strip().casefold() == correct_answer.strip().casefold()
    if not is_correct:
        return ScoreResult(
            points=0,
            new_streak=0,
            correct=False,
            timed_out=False,
            feedback=f"Kurang tepat. Jawaban benar: {correct_answer}",
        )

    new_streak = current_streak + 1
    base_points = BONUS_BASE_POINTS if is_bonus else NORMAL_BASE_POINTS
    streak_bonus = BONUS_STREAK_BONUS if is_bonus else NORMAL_STREAK_BONUS
    streak_points = streak_bonus if new_streak >= 3 else 0
    speed_points = speed_bonus(seconds_used, is_bonus)
    total = base_points + streak_points + speed_points

    bonuses = []
    if speed_points:
        bonuses.append(f"bonus cepat +{speed_points}")
    if streak_points:
        bonuses.append(f"bonus streak +{streak_points}")
    bonus_text = f" ({', '.join(bonuses)})" if bonuses else ""

    return ScoreResult(
        points=total,
        new_streak=new_streak,
        correct=True,
        timed_out=False,
        feedback=f"Benar! +{total} poin{bonus_text}",
    )


def speed_bonus(seconds_used: float, is_bonus: bool = False) -> int:
    if seconds_used <= 3:
        return 100 if is_bonus else 50
    if seconds_used <= 6:
        return 60 if is_bonus else 30
    if seconds_used <= TIME_LIMIT_SECONDS:
        return 20 if is_bonus else 10
    return 0


def winner_label(player_scores: dict[str, int]) -> str:
    if not player_scores:
        return "Belum ada pemenang"

    sorted_scores = sorted(player_scores.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[0][1] == sorted_scores[1][1]:
        return "Seri"

    return sorted_scores[0][0]
