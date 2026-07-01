from __future__ import annotations

import random
from pathlib import Path

import pandas as pd


QUESTION_TYPES = {
    "Meaning Match": "Pilih arti bahasa Indonesia yang tepat untuk kata berikut.",
    "Reverse Meaning": "Pilih vocabulary bahasa Inggris yang tepat untuk arti berikut.",
    "Synonym Duel": "Pilih sinonim yang paling dekat.",
    "Antonym Duel": "Pilih antonim yang paling tepat.",
    "Fill the Blank": "Lengkapi kalimat dengan vocabulary yang tepat.",
}


def load_vocabulary(path: str | Path) -> pd.DataFrame:
    vocab = pd.read_csv(path)
    required = {"word", "meaning", "level", "synonym", "antonym", "example"}
    missing = required.difference(vocab.columns)
    if missing:
        raise ValueError(f"Kolom vocabulary belum lengkap: {', '.join(sorted(missing))}")
    return vocab.dropna(subset=list(required)).reset_index(drop=True)


def build_battle_questions(vocab: pd.DataFrame, level: str, total_rounds: int, seed: int | None = None) -> list[dict]:
    rng = random.Random(seed)
    pool = vocab if level == "Mixed" else vocab[vocab["level"] == level]
    if pool.empty:
        pool = vocab

    rows = pool.sample(n=min(total_rounds, len(pool)), random_state=seed).to_dict("records")
    questions = []
    for round_index, row in enumerate(rows, start=1):
        question_type = rng.choice(list(QUESTION_TYPES))
        questions.append(_make_question(row, vocab, question_type, round_index, rng))
    return questions


def _make_question(row: dict, vocab: pd.DataFrame, question_type: str, round_index: int, rng: random.Random) -> dict:
    if question_type == "Meaning Match":
        prompt = row["word"]
        correct = row["meaning"]
        options = _options(vocab["meaning"].tolist(), correct, rng)
    elif question_type == "Reverse Meaning":
        prompt = row["meaning"]
        correct = row["word"]
        options = _options(vocab["word"].tolist(), correct, rng)
    elif question_type == "Synonym Duel":
        prompt = row["word"]
        correct = row["synonym"]
        options = _options(vocab["synonym"].tolist(), correct, rng)
    elif question_type == "Antonym Duel":
        prompt = row["word"]
        correct = row["antonym"]
        options = _options(vocab["antonym"].tolist(), correct, rng)
    else:
        prompt = row["example"].replace(row["word"], "____")
        correct = row["word"]
        options = _options(vocab["word"].tolist(), correct, rng)

    return {
        "round": round_index,
        "type": question_type,
        "instruction": QUESTION_TYPES[question_type],
        "prompt": prompt,
        "correct": correct,
        "options": options,
        "word": row["word"],
        "meaning": row["meaning"],
        "example": row["example"],
    }


def _options(values: list[str], correct: str, rng: random.Random) -> list[str]:
    distractors = [value for value in sorted(set(values)) if value != correct]
    selected = rng.sample(distractors, k=min(3, len(distractors)))
    options = selected + [correct]
    rng.shuffle(options)
    return options
