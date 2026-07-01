from __future__ import annotations

import time
import random
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.game_logic import TIME_LIMIT_SECONDS, score_answer, winner_label
from utils.question_generator import build_battle_questions, load_vocabulary


APP_DIR = Path(__file__).parent
VOCAB_PATH = APP_DIR / "data" / "vocabulary.csv"
LEVELS = ["Beginner", "Intermediate", "Advanced", "Mixed"]
TOTAL_QUESTIONS = 20
BONUS_START_QUESTION = 15


st.set_page_config(page_title="Vocabulary Master", layout="wide")


@st.cache_data
def get_vocabulary() -> pd.DataFrame:
    return load_vocabulary(VOCAB_PATH)


def initialize_battle(player_1: str, player_2: str, level: str) -> None:
    seed = int(time.time())
    questions = build_battle_questions(get_vocabulary(), level, seed=seed)
    first_player_index = random.Random(seed).choice([0, 1])
    st.session_state.battle = {
        "players": [player_1, player_2],
        "level": level,
        "total_rounds": len(questions),
        "questions": questions,
        "current_round": 0,
        "first_player_index": first_player_index,
        "scores": {player_1: 0, player_2: 0},
        "streaks": {player_1: 0, player_2: 0},
        "last_points": {player_1: 0, player_2: 0},
        "last_feedback": {player_1: "Belum menjawab", player_2: "Belum menjawab"},
        "answers": [],
        "round_started_at": time.time(),
        "finished": False,
    }


def reset_battle() -> None:
    st.session_state.pop("battle", None)


def submit_answer(answer: str | None) -> None:
    battle = st.session_state.battle
    active_player_index = (battle["first_player_index"] + battle["current_round"]) % 2
    player = battle["players"][active_player_index]
    question = battle["questions"][battle["current_round"]]
    seconds_used = time.time() - battle["round_started_at"]
    result = score_answer(answer, question["correct"], battle["streaks"][player], seconds_used, question["is_bonus"])

    battle["scores"][player] += result.points
    battle["streaks"][player] = result.new_streak
    battle["last_points"][player] = result.points
    battle["last_feedback"][player] = result.feedback
    battle["answers"].append(
        {
            "Soal": question["round"],
            "Pemain": player,
            "Fase": "Bonus" if question["is_bonus"] else "Normal",
            "Mode": question["type"],
            "Pertanyaan": question["prompt"],
            "Jawaban": answer if answer is not None else "Lewat waktu",
            "Jawaban Benar": question["correct"],
            "Benar": "Ya" if result.correct else "Tidak",
            "Waktu": f"{min(seconds_used, TIME_LIMIT_SECONDS):.1f} detik",
            "Poin": result.points,
            "Vocabulary": question["word"],
            "Arti": question["meaning"],
            "Contoh": question["example"],
        }
    )
    st.toast(result.feedback)

    battle["current_round"] += 1
    battle["round_started_at"] = time.time()
    battle["finished"] = battle["current_round"] >= battle["total_rounds"]


st.title("Vocabulary Master")
st.caption("Battle vocabulary 2 pemain: 20 soal bergantian, timer 10 detik, dan 6 soal terakhir sebagai bonus round.")

if "battle" not in st.session_state:
    vocab = get_vocabulary()
    with st.container(border=True):
        st.subheader("Buat Battle")
        col_a, col_b = st.columns(2)
        with col_a:
            player_1 = st.text_input("Nama Player 1", value="Player 1")
            level = st.selectbox("Level", LEVELS, index=0)
        with col_b:
            player_2 = st.text_input("Nama Player 2", value="Player 2")
            st.metric("Total soal", TOTAL_QUESTIONS)

        st.info(f"Bank vocabulary tersedia: {len(vocab)} kata. Soal {BONUS_START_QUESTION}-{TOTAL_QUESTIONS} adalah bonus round.")
        if st.button("Mulai Battle", type="primary", use_container_width=True):
            if player_1.strip().casefold() == player_2.strip().casefold():
                st.error("Nama kedua pemain harus berbeda.")
            else:
                initialize_battle(player_1.strip(), player_2.strip(), level)
                st.rerun()
else:
    battle = st.session_state.battle
    players = battle["players"]

    score_cols = st.columns(2)
    for index, player in enumerate(players):
        with score_cols[index]:
            st.metric(
                player,
                battle["scores"][player],
                delta=f"+{battle['last_points'][player]} poin terakhir | Streak {battle['streaks'][player]}",
            )
            st.caption(battle["last_feedback"][player])

    if battle["finished"]:
        winner = winner_label(battle["scores"])
        st.success(f"Pemenang: {winner}")
        answers = pd.DataFrame(battle["answers"])

        st.subheader("Review Battle")
        st.dataframe(answers, use_container_width=True, hide_index=True)

        wrong_answers = answers[answers["Benar"] == "Tidak"]
        if not wrong_answers.empty:
            st.subheader("Vocabulary yang perlu diulang")
            st.dataframe(
                wrong_answers[["Pemain", "Vocabulary", "Arti", "Contoh"]],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.balloons()
            st.write("Kedua pemain menjawab semuanya dengan benar.")

        if st.button("Battle Baru", type="primary"):
            reset_battle()
            st.rerun()
    else:
        question = battle["questions"][battle["current_round"]]
        active_player_index = (battle["first_player_index"] + battle["current_round"]) % 2
        active_player = players[active_player_index]
        progress = (battle["current_round"] + 1) / battle["total_rounds"]
        seconds_used = time.time() - battle["round_started_at"]
        seconds_left = max(0, TIME_LIMIT_SECONDS - int(seconds_used))
        is_timeout = seconds_used > TIME_LIMIT_SECONDS

        st.progress(progress, text=f"Soal {question['round']} dari {battle['total_rounds']}")
        with st.container(border=True):
            phase = "Bonus Round" if question["is_bonus"] else "Normal Round"
            st.caption(f"Gilirannya {active_player} | {phase}")
            timer_cols = st.columns(3)
            timer_cols[0].metric("Sisa waktu", f"{seconds_left} detik")
            timer_cols[1].metric("Nilai dasar", 200 if question["is_bonus"] else 100)
            timer_cols[2].metric("Soal bonus mulai", f"{BONUS_START_QUESTION}/{TOTAL_QUESTIONS}")
            st.subheader(question["type"])
            st.write(question["instruction"])
            st.markdown(f"### {question['prompt']}")
            answer = st.radio("Pilih jawaban", question["options"], index=None, disabled=is_timeout)

            col_submit, col_reset = st.columns([3, 1])
            with col_submit:
                if is_timeout:
                    if st.button("Waktu Habis - Lanjut", type="primary", use_container_width=True):
                        submit_answer(None)
                        st.rerun()
                elif st.button("Kunci Jawaban", type="primary", use_container_width=True, disabled=answer is None):
                    submit_answer(answer)
                    st.rerun()
            with col_reset:
                if st.button("Reset", use_container_width=True):
                    reset_battle()
                    st.rerun()
