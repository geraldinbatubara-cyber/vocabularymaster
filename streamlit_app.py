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
QUESTION_OPTIONS = [20, 30, 40, 50]
BONUS_QUESTION_RATIO = 0.3
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


def open_lobby() -> None:
    st.session_state.show_lobby = True


def render_landing_page() -> None:
    st.markdown(
        """
        <style>
        .vm-shell { background:#ffffff; border-radius:8px; padding:22px 8px 0; overflow:hidden; }
        .vm-nav { display:flex; align-items:center; justify-content:space-between; max-width:1220px; margin:0 auto 52px; padding:0 18px; }
        .vm-brand { display:flex; align-items:center; gap:10px; color:#0757d9; font-size:24px; font-weight:900; }
        .vm-brand-mark { width:44px; height:28px; background:#ffb703; border-radius:8px 8px 3px 3px; transform:skew(-16deg); box-shadow:14px 0 0 #ffd166; }
        .vm-nav-links { display:flex; gap:34px; color:#1f2937; font-weight:800; font-size:16px; }
        .vm-nav-pill { background:#ffb703; color:#063b7a; border-radius:8px; padding:14px 24px; font-weight:900; box-shadow:0 10px 22px rgba(255,183,3,0.28); }
        .vm-hero { max-width:1220px; min-height:640px; margin:0 auto; display:grid; grid-template-columns:0.92fr 1.08fr; gap:28px; align-items:center; padding:0 18px 34px; }
        .vm-copy h1 { color:#0757d9; font-size:58px; line-height:1.02; letter-spacing:0; margin:0; font-weight:900; }
        .vm-copy h2 { color:#0757d9; font-size:30px; line-height:1.1; margin:18px 0 12px; font-weight:900; }
        .vm-copy p { color:#4b5563; font-size:19px; line-height:1.55; margin:0; max-width:620px; font-weight:650; }
        .vm-proof { display:flex; gap:10px; flex-wrap:wrap; margin-top:26px; }
        .vm-proof span { background:#f3f8ff; color:#0757d9; border:1px solid #dbeafe; border-radius:8px; padding:10px 14px; font-weight:900; }
        .vm-stage { min-height:520px; position:relative; overflow:hidden; border-radius:72px 0 0 72px; background:linear-gradient(135deg,#35a9ff 0%,#006be6 58%,#0051b8 100%); box-shadow:0 24px 50px rgba(0,92,184,0.24); }
        .vm-stage:after { content:""; position:absolute; right:-42px; bottom:-70px; width:116%; height:150px; background:#ffb703; transform:rotate(-10deg); }
        .vm-dotfield { position:absolute; right:34px; top:30px; width:250px; height:160px; background-image:radial-gradient(rgba(255,255,255,0.55) 3px,transparent 4px); background-size:24px 24px; opacity:0.8; }
        .vm-float { position:absolute; width:72px; height:72px; border-radius:999px; background:#eaf6ff; display:flex; align-items:center; justify-content:center; color:#0877e8; font-size:30px; font-weight:900; box-shadow:0 16px 30px rgba(15,23,42,0.18); }
        .vm-float.small { width:56px; height:56px; font-size:24px; }
        .vm-phone { position:absolute; width:210px; min-height:360px; background:#0f172a; border-radius:34px; padding:12px; box-shadow:0 24px 42px rgba(0,0,0,0.28); }
        .vm-phone.one { left:210px; top:155px; transform:rotate(-2deg); }
        .vm-phone.two { left:345px; top:102px; transform:rotate(2deg); }
        .vm-screen { background:#f8fbff; border-radius:25px; min-height:336px; padding:14px; }
        .vm-screen-top { background:#0ea5e9; border-radius:18px; color:white; padding:14px; font-weight:900; }
        .vm-score-row { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-top:10px; }
        .vm-score { background:white; border-radius:8px; padding:10px; color:#0f172a; font-size:13px; font-weight:900; }
        .vm-timer { background:#ffb703; color:#063b7a; border-radius:999px; width:82px; height:82px; margin:16px auto 12px; display:flex; align-items:center; justify-content:center; font-size:38px; font-weight:900; }
        .vm-answer { background:#e0f2fe; color:#0757d9; border-radius:8px; padding:11px; margin-top:8px; text-align:center; font-weight:900; }
        .vm-answer.alt { background:#dcfce7; color:#166534; }
        .vm-answer.hot { background:#ffe4e6; color:#be123c; }
        .st-key-landing_start button { background:#ffb703 !important; color:#063b7a !important; border:2px solid #f59e0b !important; min-height:58px !important; font-size:20px !important; font-weight:900 !important; border-radius:999px !important; box-shadow:0 14px 24px rgba(255,183,3,0.30) !important; }
        .st-key-landing_vocab button { background:#ffffff !important; color:#0757d9 !important; border:2px solid #bfdbfe !important; min-height:58px !important; font-size:18px !important; font-weight:900 !important; border-radius:999px !important; }
        @media (max-width: 900px) {
            .vm-nav-links { display:none; }
            .vm-hero { grid-template-columns:1fr; min-height:auto; }
            .vm-copy h1 { font-size:44px; }
            .vm-stage { min-height:430px; border-radius:40px; }
            .vm-phone.one { left:60px; top:120px; }
            .vm-phone.two { left:190px; top:80px; }
        }
        </style>
        <section class="vm-shell">
            <div class="vm-nav">
                <div class="vm-brand"><span class="vm-brand-mark"></span><span>Vocabulary Master</span></div>
                <div class="vm-nav-links"><span>Battle</span><span>Vocabulary</span><span>Bonus Round</span><span>Review</span></div>
                <div class="vm-nav-pill">Play Now</div>
            </div>
            <div class="vm-hero">
                <div class="vm-copy">
                    <h1>Vocabulary Master</h1>
                    <h2>#BattleYourWords</h2>
                    <p>Web app belajar bahasa Inggris dengan duel vocabulary 2 pemain, countdown cepat, bonus round, dan bank soal yang bisa kamu update kapan saja.</p>
                    <div class="vm-proof">
                        <span>2 Player Battle</span>
                        <span>10s Countdown</span>
                        <span>CSV Vocabulary</span>
                    </div>
                </div>
                <div class="vm-stage">
                    <div class="vm-dotfield"></div>
                    <div class="vm-float" style="left:70px;top:125px;">A+</div>
                    <div class="vm-float small" style="left:178px;top:190px;">10</div>
                    <div class="vm-float small" style="right:205px;top:105px;">VS</div>
                    <div class="vm-float" style="right:110px;top:190px;">TOP</div>
                    <div class="vm-float small" style="right:55px;top:320px;">CSV</div>
                    <div class="vm-phone one">
                        <div class="vm-screen">
                            <div class="vm-screen-top">Player A<br><span style="font-size:12px;">Streak 3</span></div>
                            <div class="vm-score-row"><div class="vm-score">Score<br>450</div><div class="vm-score">Bonus<br>120</div></div>
                            <div class="vm-timer">7</div>
                            <div class="vm-answer">curious</div>
                            <div class="vm-answer alt">honest</div>
                            <div class="vm-answer hot">rare</div>
                        </div>
                    </div>
                    <div class="vm-phone two">
                        <div class="vm-screen">
                            <div class="vm-screen-top">Vocabulary Battle<br><span style="font-size:12px;">Bonus Round</span></div>
                            <div class="vm-score-row"><div class="vm-score">Ayu<br>680</div><div class="vm-score">Bima<br>640</div></div>
                            <div class="vm-timer">3</div>
                            <div class="vm-answer">resilient</div>
                            <div class="vm-answer alt">achieve</div>
                            <div class="vm-answer hot">damage</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    cta_cols = st.columns([1, 1.1, 1.1, 1])
    with cta_cols[1]:
        if st.button("Mulai Battle", key="landing_start", use_container_width=True):
            open_lobby()
            st.rerun()
    with cta_cols[2]:
        if st.button("Kelola Bank Vocabulary", key="landing_vocab", use_container_width=True):
            open_lobby()
            st.rerun()

    feature_cols = st.columns(4)
    features = [
        ("Duel 2 Pemain", "Bergantian menjawab vocabulary dengan skor dan streak."),
        ("Countdown 10 Detik", "Setiap soal terasa cepat, fokus, dan menantang."),
        ("Bonus Round", "Bagian akhir match punya nilai lebih besar."),
        ("CSV Fleksibel", "Upload dan kelola bank vocabulary kapan saja."),
    ]
    colors = ["#ecfeff", "#f0fdf4", "#fff7ed", "#fdf2f8"]
    for col, (title, body), color in zip(feature_cols, features, colors):
        with col:
            st.markdown(
                f"""
                <div class="vm-mini-card" style="background:{color};">
                    <strong>{html.escape(title)}</strong>
                    <span>{html.escape(body)}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )


def bonus_start_question(total_questions: int) -> int:
    bonus_count = max(1, round(total_questions * BONUS_QUESTION_RATIO))
    return total_questions - bonus_count + 1


def initialize_battle(player_1: str, player_2: str, level: str, category: str, total_questions: int) -> None:
    seed = int(time.time())
    questions = build_battle_questions(
        active_vocabulary(),
        level,
        category=category,
        total_questions=total_questions,
        seed=seed,
    )
    first_player_index = random.Random(seed).choice([0, 1])
    st.session_state.battle = {
        "players": [player_1, player_2],
        "level": level,
        "category": category,
        "selected_total_questions": total_questions,
        "bonus_start_question": bonus_start_question(total_questions),
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
        "battle_started": False,
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
    battle["finished"] = battle["current_round"] >= battle["total_rounds"]
    if not battle["finished"]:
        battle["round_started_at"] = time.time()


def start_battle_clock() -> None:
    st.session_state.battle["round_started_at"] = time.time()
    st.session_state.battle["battle_started"] = True


def render_player_card(player: str, battle: dict, is_active: bool = False) -> None:
    status = "Giliranmu" if is_active else "Menunggu"
    background = "#eff6ff" if is_active else "#f9fafb"
    border = "#2563eb" if is_active else "#e5e7eb"
    status_color = "#1d4ed8" if is_active else "#6b7280"
    shadow = "0 0 0 3px rgba(37,99,235,0.12)" if is_active else "none"
    st.markdown(
        f"""
        <div style="background:{background};border:2px solid {border};border-radius:8px;padding:12px 14px;box-shadow:{shadow};">
            <div style="color:{status_color};font-size:12px;font-weight:800;text-transform:uppercase;">{status}</div>
            <div style="color:#111827;font-size:22px;font-weight:900;margin-top:2px;">{html.escape(player)}</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px;">
                <div>
                    <div style="color:#6b7280;font-size:11px;font-weight:700;">Skor</div>
                    <div style="color:#111827;font-size:22px;font-weight:900;line-height:1;">{battle['scores'][player]}</div>
                </div>
                <div>
                    <div style="color:#6b7280;font-size:11px;font-weight:700;">Streak</div>
                    <div style="color:#111827;font-size:22px;font-weight:900;line-height:1;">{battle['streaks'][player]}</div>
                </div>
            </div>
            <div style="margin-top:8px;color:#374151;font-size:13px;font-weight:700;">
                +{battle['last_points'][player]} poin terakhir
            </div>
            <div style="margin-top:2px;color:#6b7280;font-size:12px;">{html.escape(battle['last_feedback'][player])}</div>
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
        <div style="display:flex;justify-content:center;margin:0;">
            <div style="width:100%;background:{background};border:2px solid {color};border-radius:8px;padding:14px 18px;text-align:center;box-shadow:0 12px 26px rgba(17,24,39,0.10);">
                <div style="color:{color};font-size:12px;font-weight:900;text-transform:uppercase;">Countdown</div>
                <div style="color:{color};font-size:82px;font-weight:900;line-height:0.9;">{seconds_left}</div>
                <div style="color:{color};font-size:13px;font-weight:900;">detik</div>
                <div style="color:{color};font-size:12px;font-weight:800;margin-top:4px;">{html.escape(label)} | {phase}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_side_info(label: str, value: str | int) -> None:
    st.markdown(
        f"""
        <div style="height:100%;min-height:148px;padding:18px 10px;text-align:center;display:flex;flex-direction:column;justify-content:center;">
            <div style="color:#9ca3af;font-size:12px;font-weight:900;text-transform:uppercase;">{html.escape(label)}</div>
            <div style="color:#374151;font-size:30px;font-weight:900;line-height:1;margin-top:10px;">{html.escape(str(value))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_start_gate(active_player: str, question: dict) -> None:
    phase = "Bonus Round" if question["is_bonus"] else "Normal Round"
    st.markdown(
        f"""
        <div style="text-align:center;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:28px;margin:14px 0;">
            <div style="color:#4b5563;font-size:13px;font-weight:900;text-transform:uppercase;">{phase}</div>
            <div style="color:#111827;font-size:28px;font-weight:900;margin-top:6px;">Giliran {html.escape(active_player)}</div>
            <div style="color:#6b7280;font-size:15px;font-weight:700;margin-top:8px;">Tekan START sekali untuk mulai match. Setelah itu giliran berjalan otomatis.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <style>
        .st-key-start_round button {
            background:#16a34a !important;
            border:2px solid #15803d !important;
            color:white !important;
            font-size:24px !important;
            font-weight:900 !important;
            padding:1rem 2rem !important;
            min-height:70px !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    left, center, right = st.columns([1, 1.2, 1])
    with center:
        if st.button("START", key="start_round", use_container_width=True):
            start_battle_clock()
            st.rerun()


def render_answer_cards(options: list[str], is_timeout: bool, round_index: int) -> None:
    colors = [
        ("#eff6ff", "#2563eb", "#1e3a8a"),
        ("#f0fdf4", "#16a34a", "#14532d"),
        ("#fff7ed", "#ea580c", "#7c2d12"),
        ("#fdf2f8", "#db2777", "#831843"),
    ]
    css_rules = []
    for index, (background, border, text_color) in enumerate(colors):
        css_rules.append(
            f"""
            .st-key-answer_card_{index}_{round_index} button {{
                min-height:108px !important;
                background:{background} !important;
                border:2px solid {border} !important;
                border-radius:8px !important;
                color:{text_color} !important;
                font-size:22px !important;
                font-weight:900 !important;
                white-space:normal !important;
                line-height:1.25 !important;
                padding:12px !important;
            }}
            .st-key-answer_card_{index}_{round_index} button:hover {{
                box-shadow:0 0 0 3px {border}33 !important;
                transform:translateY(-1px);
            }}
            """
        )
    st.markdown(f"<style>{''.join(css_rules)}</style>", unsafe_allow_html=True)
    option_cols = st.columns(4)
    for index, option in enumerate(options):
        with option_cols[index]:
            if st.button(
                option,
                key=f"answer_card_{index}_{round_index}",
                use_container_width=True,
                disabled=is_timeout,
            ):
                submit_answer(option)
                st.rerun()


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


if "battle" not in st.session_state and not st.session_state.get("show_lobby", False):
    render_landing_page()
    st.stop()


st.title("Vocabulary Master")
st.caption("Battle vocabulary 2 pemain: pilih 20-50 soal, timer 10 detik, dan 30% soal terakhir sebagai bonus round.")

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
            total_questions = st.selectbox("Jumlah soal", QUESTION_OPTIONS, index=0)

        vocab = normalize_vocabulary(vocab)
        categories = ["All Categories"] + sorted(vocab["category"].dropna().unique().tolist())
        category = st.selectbox("Kategori vocabulary", categories, index=0)
        bonus_start = bonus_start_question(total_questions)
        st.info(f"Bank vocabulary tersedia: {len(vocab)} kata. Soal {bonus_start}-{total_questions} adalah bonus round.")
        st.markdown(
            """
            <style>
            .st-key-create_battle button {
                background:#16a34a !important;
                border:2px solid #15803d !important;
                color:white !important;
                font-size:22px !important;
                font-weight:900 !important;
                min-height:64px !important;
                box-shadow:0 12px 28px rgba(22,163,74,0.20) !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        left, center, right = st.columns([1, 1.35, 1])
        with center:
            if st.button("Mulai Battle", key="create_battle", use_container_width=True):
                if player_1.strip().casefold() == player_2.strip().casefold():
                    st.error("Nama kedua pemain harus berbeda.")
                else:
                    initialize_battle(player_1.strip(), player_2.strip(), level, category, total_questions)
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
        question = battle["questions"][battle["current_round"]]
        progress = (battle["current_round"] + 1) / battle["total_rounds"]

        st.progress(progress, text=f"Soal {question['round']} dari {battle['total_rounds']}")
        with st.container(border=True):
            phase = "Bonus Round" if question["is_bonus"] else "Normal Round"
            st.caption(f"Gilirannya {active_player} | {phase}")
            if not battle.get("battle_started", False):
                render_start_gate(active_player, question)
                center_reset = st.columns([1.2, 1, 1.2])[1]
                with center_reset:
                    if st.button("Reset", use_container_width=True):
                        reset_battle()
                        st.rerun()
                st.stop()

            st_autorefresh(interval=1000, key="battle_countdown")
            seconds_used = time.time() - battle["round_started_at"]
            seconds_left = max(0, TIME_LIMIT_SECONDS - int(seconds_used))
            is_timeout = seconds_left == 0
            spotlight_cols = st.columns([0.9, 1.35, 0.9])
            with spotlight_cols[0]:
                render_side_info("Nilai dasar", 200 if question["is_bonus"] else 100)
            with spotlight_cols[1]:
                render_timer_card(seconds_left, question["is_bonus"])
            with spotlight_cols[2]:
                render_side_info("Jenis soal", "Bonus" if question["is_bonus"] else "Biasa")
            if is_timeout:
                st.error("Waktu Habis")
            st.markdown(
                f"""
                <div style="margin:8px 0 10px;text-align:center;">
                    <div style="color:#4b5563;font-size:14px;font-weight:900;text-transform:uppercase;">{html.escape(question['type'])}</div>
                    <div style="color:#6b7280;font-size:14px;font-weight:700;">{html.escape(question['instruction'])}</div>
                    <div style="color:#111827;font-size:28px;font-weight:900;line-height:1.2;margin-top:6px;">{html.escape(question['prompt'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_answer_cards(question["options"], is_timeout, battle["current_round"])

            if is_timeout:
                left, center, right = st.columns([1.15, 1, 1.15])
                with center:
                    if st.button("Waktu Habis - Lanjut", type="primary", use_container_width=True):
                        submit_answer(None)
                        st.rerun()
                    if st.button("Reset", use_container_width=True):
                        reset_battle()
                        st.rerun()
            else:
                left, center, right = st.columns([1.15, 1, 1.15])
                with center:
                    if st.button("Reset", use_container_width=True):
                        reset_battle()
                        st.rerun()
