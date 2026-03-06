import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import random

# 1. 페이지 설정
st.set_page_config(page_title="VOCA MASTER PRO", layout="wide")

# ---------------------------------------------------------
# [기능 1] 구글 시트 연결 및 데이터 로드
# ---------------------------------------------------------
@st.cache_data(ttl=600) # 10분간 캐시 유지
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        service_account_info = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        
        spreadsheet = client.open("voka_master")
        sheet = spreadsheet.get_worksheet(0) 
        rows = sheet.get_all_values()
        
        if not rows: return {}

        word_dict = {}
        for row in rows:
            if len(row) >= 2:
                w, m = str(row[0]).strip(), str(row[1]).strip()
                if w and w not in ["단어", "word"]:
                    word_dict[w] = m
        return word_dict
    except Exception as e:
        st.sidebar.error(f"연결 에러: {e}")
        return {}

# ---------------------------------------------------------
# 2. 세션 상태 및 학습 데이터 초기화
# ---------------------------------------------------------
if 'word_dict' not in st.session_state:
    st.session_state.word_dict = load_data()

if 'stats' not in st.session_state and st.session_state.word_dict:
    st.session_state.stats = {w: {"solved": 0, "unlocked": False} for w in st.session_state.word_dict}

if 'wrong_words' not in st.session_state:
    st.session_state.wrong_words = set()

if 'current_quiz' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))

if 'show_hint' not in st.session_state:
    st.session_state.show_hint = False

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER PRO")

# [추천 2] 진척도 대시보드
if st.session_state.word_dict:
    unlocked_count = sum(1 for s in st.session_state.stats.values() if s["unlocked"])
    total_count = len(st.session_state.word_dict)
    progress = unlocked_count / total_count
    
    col_stat1, col_stat2 = st.columns([4, 1])
    with col_stat1:
        st.progress(progress)
    with col_stat2:
        st.write(f"📊 **{progress*100:.1f}%** ({unlocked_count}/{total_count})")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 퀴즈", "📖 도감", "❌ 오답노트", "⚙️ 설정"])

# --- [Tab 1: 퀴즈 (복습 모드 & 힌트 포함)] ---
with tab1:
    # [추천 3] 복습 모드 선택
    mode = st.radio("모드 선택", ["전체 랜덤", "오답 집중 복습"], horizontal=True)
    
    st.divider()
    
    q_word = st.session_state.get('current_quiz')
    if q_word:
        # 단어 표시
        st.markdown(f"<div style='background-color: #f0f2f6; padding: 30px; border-radius: 15px; text-align: center;'><h1 style='font-size: 60px;'>{q_word}</h1></div>", unsafe_allow_html=True)
        
        answer_mean = st.session_state.word_dict[q_word]
        
        # [추천 1] 힌트 기능
        if st.session_state.show_hint:
            hint_text = answer_mean[0] + " _ " * (len(answer_mean) - 1)
            st.caption(f"💡 힌트: {hint_text} ({len(answer_mean)}글자)")

        with st.form(key="quiz_form", clear_on_submit=True):
            user_input = st.text_input("뜻을 입력하세요:").strip()
            cols = st.columns(2)
            submit = cols[0].form_submit_button("정답 확인", use_container_width=True)
            hint_btn = cols[1].form_submit_button("힌트 보기", use_container_width=True)
            
            if hint_btn:
                st.session_state.show_hint = True
                st.rerun()

            if submit:
                if user_input == answer_mean:
                    st.balloons()
                    st.success(f"정답! 🎉 : {answer_mean}")
                    st.session_state.stats[q_word]["solved"] += 1
                    st.session_state.stats[q_word]["unlocked"] = True
                    if q_word in st.session_state.wrong_words:
                        st.session_state.wrong_words.remove(q_word)
                else:
                    st.error(f"오답! 정답은 '{answer_mean}'")
                    st.session_state.wrong_words.add(q_word)

        if st.button("다음 단어 ➡️", use_container_width=True):
            if mode == "오답 집중 복습" and st.session_state.wrong_words:
                st.session_state.current_quiz = random.choice(list(st.session_state.wrong_words))
            else:
                st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
            st.session_state.show_hint = False
            st.rerun()

# --- [Tab 2: 도감] ---
with tab2:
    search = st.text_input("검색:", placeholder="단어 검색...")
    display_data = []
    for w, m in st.session_state.word_dict.items():
        if search.lower() in w.lower():
            stat = st.session_state.stats.get(w, {"solved": 0, "unlocked": False})
            display_data.append({
                "상태": "✅ 해금" if stat["unlocked"] else "🔒 미해금",
                "단어": w,
                "뜻": m if stat["unlocked"] else "???",
                "횟수": stat["solved"]
            })
    st.dataframe(display_data, use_container_width=True)

# --- [Tab 3: 오답노트] ---
with tab3:
    if not st.session_state.wrong_words:
        st.write("깨끗합니다! ✨")
    else:
        for ww in list(st.session_state.wrong_words):
            with st.expander(f"📌 {ww}"):
                st.write(f"뜻: {st.session_state.word_dict[ww]}")
                if st.button(f"삭제", key=f"del_{ww}"):
                    st.session_state.wrong_words.remove(ww)
                    st.rerun()

# --- [Tab 4: 설정] ---
with tab4:
    if st.sidebar.button("🔄 시트 강제 동기화"):
        st.cache_data.clear()
        st.session_state.word_dict = load_data()
        st.rerun()
    if st.button("기록 초기화"):
        st.session_state.clear()
        st.rerun()
