from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import streamlit as st

from utils.game_logic import score_answer, winner_label
from utils.question_generator import build_battle_questions, load_vocabulary


APP_DIR = Path(__file__).parent
VOCAB_PATH = APP_DIR / "data" / "vocabulary.csv"
LEVELS = ["Beginner", "Intermediate", "Advanced", "Mixed"]
ROUND_OPTIONS = [5, 10, 15]


st.set_page_config(page_title="Vocabulary Master", layout="wide")


@st.cache_data
def get_vocabulary() -> pd.DataFrame:
    return load_vocabulary(VOCAB_PATH)


def initialize_battle(player_1: str, player_2: str, level: str, total_rounds: int) -> None:
    seed = int(time.time())
    questions = build_battle_questions(get_vocabulary(), level, total_rounds, seed=seed)
    st.session_state.battle = {
        "players": [player_1, player_2],
        "level": level,
        "total_rounds": len(questions),
        "questions": questions,
        "current_round": 0,
        "active_player_index": 0,
        "scores": {player_1: 0, player_2: 0},
        "streaks": {player_1: 0, player_2: 0},
        "answers": [],
        "round_started_at": time.time(),
        "finished": False,
    }


def reset_battle() -> None:
    st.session_state.pop("battle", None)


def submit_answer(answer: str) -> None:
    battle = st.session_state.battle
    player = battle["players"][battle["active_player_index"]]
    question = battle["questions"][battle["current_round"]]
    seconds_used = time.time() - battle["round_started_at"]
    result = score_answer(answer, question["correct"], battle["streaks"][player], seconds_used)

    battle["scores"][player] += result.points
    battle["streaks"][player] = result.new_streak
    battle["answers"].append(
        {
            "Ronde": question["round"],
            "Pemain": player,
            "Mode": question["type"],
            "Pertanyaan": question["prompt"],
            "Jawaban": answer,
            "Jawaban Benar": question["correct"],
            "Benar": "Ya" if result.correct else "Tidak",
            "Poin": result.points,
            "Vocabulary": question["word"],
            "Arti": question["meaning"],
            "Contoh": question["example"],
        }
    )
    st.toast(result.feedback)

    if battle["active_player_index"] == 0:
        battle["active_player_index"] = 1
    else:
        battle["active_player_index"] = 0
        battle["current_round"] += 1

    battle["round_started_at"] = time.time()
    battle["finished"] = battle["current_round"] >= battle["total_rounds"]


st.title("Vocabulary Master")
st.caption("Battle vocabulary 2 pemain dengan skor, streak, bonus cepat, dan review setelah duel.")

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
            total_rounds = st.selectbox("Jumlah ronde", ROUND_OPTIONS, index=1)

        st.info(f"Bank vocabulary tersedia: {len(vocab)} kata.")
        if st.button("Mulai Battle", type="primary", use_container_width=True):
            if player_1.strip().casefold() == player_2.strip().casefold():
                st.error("Nama kedua pemain harus berbeda.")
            else:
                initialize_battle(player_1.strip(), player_2.strip(), level, total_rounds)
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
                delta=f"Streak {battle['streaks'][player]}",
            )

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
        active_player = players[battle["active_player_index"]]
        progress = (battle["current_round"] + 1) / battle["total_rounds"]

        st.progress(progress, text=f"Ronde {question['round']} dari {battle['total_rounds']}")
        with st.container(border=True):
            st.caption(f"Gilirannya {active_player}")
            st.subheader(question["type"])
            st.write(question["instruction"])
            st.markdown(f"### {question['prompt']}")
            answer = st.radio("Pilih jawaban", question["options"], index=None)

            col_submit, col_reset = st.columns([3, 1])
            with col_submit:
                if st.button("Kunci Jawaban", type="primary", use_container_width=True, disabled=answer is None):
                    submit_answer(answer)
                    st.rerun()
            with col_reset:
                if st.button("Reset", use_container_width=True):
                    reset_battle()
                    st.rerun()
