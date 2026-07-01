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

NORMAL_QUESTION_TYPES = ["Meaning Match", "Reverse Meaning", "Fill the Blank"]
BONUS_QUESTION_TYPES = ["Synonym Duel", "Antonym Duel", "Fill the Blank"]
NORMAL_QUESTION_COUNT = 14
TOTAL_QUESTION_COUNT = 20


def load_vocabulary(path: str | Path) -> pd.DataFrame:
    vocab = pd.read_csv(path)
    return normalize_vocabulary(vocab)


def normalize_vocabulary(vocab: pd.DataFrame) -> pd.DataFrame:
    required = {"word", "meaning", "level", "synonym", "antonym", "example"}
    missing = required.difference(vocab.columns)
    if missing:
        raise ValueError(f"Kolom vocabulary belum lengkap: {', '.join(sorted(missing))}")
    if "category" not in vocab.columns:
        vocab = vocab.assign(category="general")
    vocab["category"] = vocab["category"].fillna("general").astype(str).str.strip().replace("", "general")
    return vocab.dropna(subset=list(required)).reset_index(drop=True)


def build_battle_questions(
    vocab: pd.DataFrame,
    level: str,
    category: str = "All Categories",
    seed: int | None = None,
) -> list[dict]:
    rng = random.Random(seed)
    vocab = _category_pool(vocab, category)
    normal_pool = _level_pool(vocab, level)
    bonus_pool = _bonus_pool(vocab, level)

    normal_rows = _sample_rows(normal_pool, NORMAL_QUESTION_COUNT, seed)
    bonus_rows = _sample_rows(bonus_pool, TOTAL_QUESTION_COUNT - NORMAL_QUESTION_COUNT, None if seed is None else seed + 1)

    questions = []
    for question_index, row in enumerate(normal_rows, start=1):
        question_type = rng.choice(NORMAL_QUESTION_TYPES)
        questions.append(_make_question(row, vocab, question_type, question_index, rng, is_bonus=False))

    for question_index, row in enumerate(bonus_rows, start=NORMAL_QUESTION_COUNT + 1):
        question_type = rng.choice(BONUS_QUESTION_TYPES)
        questions.append(_make_question(row, vocab, question_type, question_index, rng, is_bonus=True))
    return questions


def _category_pool(vocab: pd.DataFrame, category: str) -> pd.DataFrame:
    if category == "All Categories" or "category" not in vocab.columns:
        return vocab
    pool = vocab[vocab["category"] == category]
    return vocab if pool.empty else pool


def _level_pool(vocab: pd.DataFrame, level: str) -> pd.DataFrame:
    if level == "Mixed":
        return vocab
    pool = vocab[vocab["level"] == level]
    return vocab if pool.empty else pool


def _bonus_pool(vocab: pd.DataFrame, level: str) -> pd.DataFrame:
    if level == "Advanced":
        return _level_pool(vocab, "Advanced")
    if level == "Intermediate":
        pool = vocab[vocab["level"].isin(["Intermediate", "Advanced"])]
    else:
        pool = vocab[vocab["level"].isin(["Intermediate", "Advanced"])]
    return vocab if pool.empty else pool


def _sample_rows(pool: pd.DataFrame, count: int, seed: int | None) -> list[dict]:
    return pool.sample(n=count, replace=len(pool) < count, random_state=seed).to_dict("records")


def _make_question(
    row: dict,
    vocab: pd.DataFrame,
    question_type: str,
    question_index: int,
    rng: random.Random,
    is_bonus: bool,
) -> dict:
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
        "round": question_index,
        "type": question_type,
        "instruction": QUESTION_TYPES[question_type],
        "prompt": prompt,
        "correct": correct,
        "options": options,
        "is_bonus": is_bonus,
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
