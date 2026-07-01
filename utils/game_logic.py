from __future__ import annotations

from dataclasses import dataclass


BASE_POINTS = 100
STREAK_BONUS = 25
FAST_BONUS = 20


@dataclass(frozen=True)
class ScoreResult:
    points: int
    new_streak: int
    correct: bool
    feedback: str


def score_answer(answer: str, correct_answer: str, current_streak: int, seconds_used: float) -> ScoreResult:
    is_correct = answer.strip().casefold() == correct_answer.strip().casefold()
    if not is_correct:
        return ScoreResult(
            points=0,
            new_streak=0,
            correct=False,
            feedback=f"Kurang tepat. Jawaban benar: {correct_answer}",
        )

    new_streak = current_streak + 1
    streak_points = STREAK_BONUS if new_streak >= 3 else 0
    speed_points = FAST_BONUS if seconds_used <= 5 else 0
    total = BASE_POINTS + streak_points + speed_points

    bonuses = []
    if speed_points:
        bonuses.append("bonus cepat")
    if streak_points:
        bonuses.append("bonus streak")
    bonus_text = f" ({', '.join(bonuses)})" if bonuses else ""

    return ScoreResult(
        points=total,
        new_streak=new_streak,
        correct=True,
        feedback=f"Benar! +{total} poin{bonus_text}",
    )


def winner_label(player_scores: dict[str, int]) -> str:
    if not player_scores:
        return "Belum ada pemenang"

    sorted_scores = sorted(player_scores.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[0][1] == sorted_scores[1][1]:
        return "Seri"

    return sorted_scores[0][0]
