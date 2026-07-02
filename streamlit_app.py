from __future__ import annotations

import html
import time
import random
from pathlib import Path

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from utils.game_logic import TIME_LIMIT_SECONDS, score_answer
from utils.question_generator import build_battle_questions, load_vocabulary, normalize_vocabulary


APP_DIR = Path(__file__).parent
VOCAB_PATH = APP_DIR / "data" / "vocabulary.csv"
LEVELS = ["Beginner", "Intermediate", "Advanced", "Mixed"]
TOTAL_QUESTIONS = 20
BONUS_START_QUESTION = 15
TEMPLATE_COLUMNS = ["word", "meaning", "level", "synonym", "antonym", "example", "category"]


st.set_page_config(page_title="Vocabulary Master", layout="wide")


@st.cache_data
def get_vocabulary() -> pd.DataFrame:
    return load_vocabulary(VOCAB_PATH)


def active_vocabulary() -> pd.DataFrame:
    return normalize_vocabulary(st.session_state.get("uploaded_vocabulary", get_vocabulary()))


def template_csv() -> bytes:
    template = pd.DataFrame(
        [
            {
                "word": "borrow",
                "meaning": "meminjam",
                "level": "Beginner",
                "synonym": "take",
                "antonym": "lend",
                "example": "Can I borrow your pencil?",
                "category": "daily_life",
            },
            {
                "word": "consider",
                "meaning": "mempertimbangkan",
                "level": "Intermediate",
                "synonym": "think",
                "antonym": "ignore",
                "example": "Please consider the second option.",
                "category": "work",
            },
            {
                "word": "resilient",
                "meaning": "tangguh",
                "level": "Advanced",
                "synonym": "strong",
                "antonym": "fragile",
                "example": "A resilient learner keeps practicing.",
                "category": "academic",
            },
        ],
        columns=TEMPLATE_COLUMNS,
    )
    return template.to_csv(index=False).encode("utf-8")


def initialize_battle(player_1: str, player_2: str, level: str, category: str) -> None:
    seed = int(time.time())
    questions = build_battle_questions(active_vocabulary(), level, category=category, seed=seed)
    first_player_index = random.Random(seed).choice([0, 1])
    st.session_state.battle = {
        "players": [player_1, player_2],
        "level": level,
        "category": category,
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


def render_player_card(player: str, battle: dict, is_active: bool = False) -> None:
    status = "Giliranmu" if is_active else "Menunggu"
    background = "#eff6ff" if is_active else "#f9fafb"
    border = "#2563eb" if is_active else "#e5e7eb"
    status_color = "#1d4ed8" if is_active else "#6b7280"
    shadow = "0 0 0 3px rgba(37,99,235,0.12)" if is_active else "none"
    st.markdown(
        f"""
        <div style="background:{background};border:2px solid {border};border-radius:8px;padding:18px;box-shadow:{shadow};">
            <div style="color:{status_color};font-size:13px;font-weight:800;text-transform:uppercase;">{status}</div>
            <div style="color:#111827;font-size:26px;font-weight:900;margin-top:4px;">{html.escape(player)}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px;">
                <div>
                    <div style="color:#6b7280;font-size:12px;font-weight:700;">Skor</div>
                    <div style="color:#111827;font-size:24px;font-weight:900;">{battle['scores'][player]}</div>
                </div>
                <div>
                    <div style="color:#6b7280;font-size:12px;font-weight:700;">Streak</div>
                    <div style="color:#111827;font-size:24px;font-weight:900;">{battle['streaks'][player]}</div>
                </div>
            </div>
            <div style="margin-top:12px;color:#374151;font-size:14px;font-weight:700;">
                +{battle['last_points'][player]} poin terakhir
            </div>
            <div style="margin-top:4px;color:#6b7280;font-size:13px;">{html.escape(battle['last_feedback'][player])}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_timer_card(seconds_left: int, is_bonus: bool) -> None:
    if seconds_left <= 3:
        color = "#dc2626"
        background = "#fee2e2"
        label = "Cepat jawab"
    elif seconds_left <= 6:
        color = "#a16207"
        background = "#fef3c7"
        label = "Tetap fokus"
    else:
        color = "#15803d"
        background = "#dcfce7"
        label = "Masih aman"

    phase = "Bonus Round" if is_bonus else "Normal Round"
    st.markdown(
        f"""
        <div style="background:{background};border:1px solid {color};border-radius:8px;padding:18px;text-align:center;">
            <div style="color:{color};font-size:13px;font-weight:800;text-transform:uppercase;">{html.escape(label)} | {phase}</div>
            <div style="color:{color};font-size:54px;font-weight:900;line-height:1;">{seconds_left}</div>
            <div style="color:{color};font-size:14px;font-weight:800;">detik</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def answer_seconds(value: str) -> float:
    try:
        return float(str(value).replace(" detik", ""))
    except ValueError:
        return 0.0


def render_match_summary(answers: pd.DataFrame, player_scores: dict[str, int]) -> None:
    rows = []
    for player, score in player_scores.items():
        player_answers = answers[answers["Pemain"] == player]
        correct_count = int((player_answers["Benar"] == "Ya").sum())
        total_count = len(player_answers)
        accuracy = (correct_count / total_count * 100) if total_count else 0
        bonus_points = int(player_answers[player_answers["Fase"] == "Bonus"]["Poin"].sum())
        fastest = player_answers[player_answers["Benar"] == "Ya"]["Waktu"].map(answer_seconds).min()
        rows.append(
            {
                "Pemain": player,
                "Skor": score,
                "Benar": correct_count,
                "Akurasi": f"{accuracy:.0f}%",
                "Poin Bonus": bonus_points,
                "Jawaban Tercepat": "-" if pd.isna(fastest) else f"{fastest:.1f} detik",
            }
        )

    st.subheader("Match Summary")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_final_result(player_scores: dict[str, int]) -> None:
    sorted_scores = sorted(player_scores.items(), key=lambda item: item[1], reverse=True)
    if len(sorted_scores) >= 2 and sorted_scores[0][1] == sorted_scores[1][1]:
        st.info("Hasil seri")
        tie_cols = st.columns(len(sorted_scores))
        for col, (player, score) in zip(tie_cols, sorted_scores):
            with col:
                st.markdown(
                    f"""
                    <div style="background:#f3f4f6;border:1px solid #d1d5db;border-radius:8px;padding:18px;">
                        <div style="color:#374151;font-size:14px;font-weight:700;">SERI</div>
                        <div style="color:#111827;font-size:24px;font-weight:800;">{html.escape(player)}</div>
                        <div style="color:#374151;font-size:18px;font-weight:700;">{score} poin</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        return

    winner, winner_score = sorted_scores[0]
    loser, loser_score = sorted_scores[-1]
    result_cols = st.columns(2)
    with result_cols[0]:
        st.markdown(
            f"""
            <div style="background:#dcfce7;border:2px solid #16a34a;border-radius:8px;padding:20px;box-shadow:0 0 0 3px rgba(22,163,74,0.12);">
                <div style="color:#166534;font-size:14px;font-weight:800;">PEMENANG</div>
                <div style="color:#14532d;font-size:30px;font-weight:900;">{html.escape(winner)}</div>
                <div style="color:#166534;font-size:22px;font-weight:800;">{winner_score} poin</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with result_cols[1]:
        st.markdown(
            f"""
            <div style="background:#e5e7eb;border:1px solid #9ca3af;border-radius:8px;padding:20px;opacity:0.88;">
                <div style="color:#4b5563;font-size:14px;font-weight:700;">KALAH</div>
                <div style="color:#374151;font-size:26px;font-weight:800;">{html.escape(loser)}</div>
                <div style="color:#4b5563;font-size:20px;font-weight:700;">{loser_score} poin</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


st.title("Vocabulary Master")
st.caption("Battle vocabulary 2 pemain: 20 soal bergantian, timer 10 detik, dan 6 soal terakhir sebagai bonus round.")

if "battle" not in st.session_state:
    vocab = active_vocabulary()
    with st.container(border=True):
        st.subheader("Kelola Bank Vocabulary")
        upload = st.file_uploader("Upload CSV bank vocabulary", type=["csv"])
        if upload is not None:
            try:
                vocab = normalize_vocabulary(pd.read_csv(upload))
                st.session_state.uploaded_vocabulary = vocab
                st.success(f"Bank vocabulary aktif diganti dari file upload: {len(vocab)} kata.")
                st.dataframe(vocab.head(10), use_container_width=True, hide_index=True)
            except Exception as exc:
                st.error(f"CSV belum valid: {exc}")

        st.download_button(
            "Unduh Template CSV Bank Vocabulary",
            data=template_csv(),
            file_name="template_bank_vocabulary.csv",
            mime="text/csv",
            use_container_width=True,
        )

    with st.container(border=True):
        st.subheader("Buat Battle")
        col_a, col_b = st.columns(2)
        with col_a:
            player_1 = st.text_input("Nama Player 1", value="Player 1")
            level = st.selectbox("Level", LEVELS, index=0)
        with col_b:
            player_2 = st.text_input("Nama Player 2", value="Player 2")
            st.metric("Total soal", TOTAL_QUESTIONS)

        vocab = normalize_vocabulary(vocab)
        categories = ["All Categories"] + sorted(vocab["category"].dropna().unique().tolist())
        category = st.selectbox("Kategori vocabulary", categories, index=0)
        st.info(f"Bank vocabulary tersedia: {len(vocab)} kata. Soal {BONUS_START_QUESTION}-{TOTAL_QUESTIONS} adalah bonus round.")
        if st.button("Mulai Battle", type="primary", use_container_width=True):
            if player_1.strip().casefold() == player_2.strip().casefold():
                st.error("Nama kedua pemain harus berbeda.")
            else:
                initialize_battle(player_1.strip(), player_2.strip(), level, category)
                st.rerun()
else:
    battle = st.session_state.battle
    players = battle["players"]
    active_player = None
    if not battle["finished"]:
        active_player_index = (battle["first_player_index"] + battle["current_round"]) % 2
        active_player = players[active_player_index]

    score_cols = st.columns(2)
    for index, player in enumerate(players):
        with score_cols[index]:
            render_player_card(player, battle, is_active=player == active_player)

    if battle["finished"]:
        render_final_result(battle["scores"])
        answers = pd.DataFrame(battle["answers"])
        render_match_summary(answers, battle["scores"])

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
        st_autorefresh(interval=1000, key="battle_countdown")
        question = battle["questions"][battle["current_round"]]
        progress = (battle["current_round"] + 1) / battle["total_rounds"]
        seconds_used = time.time() - battle["round_started_at"]
        seconds_left = max(0, TIME_LIMIT_SECONDS - int(seconds_used))
        is_timeout = seconds_left == 0

        st.progress(progress, text=f"Soal {question['round']} dari {battle['total_rounds']}")
        with st.container(border=True):
            phase = "Bonus Round" if question["is_bonus"] else "Normal Round"
            st.caption(f"Gilirannya {active_player} | {phase}")
            timer_cols = st.columns([1.2, 1, 1])
            with timer_cols[0]:
                render_timer_card(seconds_left, question["is_bonus"])
            timer_cols[1].metric("Nilai dasar", 200 if question["is_bonus"] else 100)
            timer_cols[2].metric("Soal bonus mulai", f"{BONUS_START_QUESTION}/{TOTAL_QUESTIONS}")
            if is_timeout:
                st.error("Waktu Habis")
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
