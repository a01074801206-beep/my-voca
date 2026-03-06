import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import random

# 1. 페이지 설정
st.set_page_config(page_title="VOCA MASTER", layout="wide")

# ---------------------------------------------------------
# [기능 1] 구글 시트 연결 및 데이터 로드
# ---------------------------------------------------------
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

# 사이드바 데이터 새로고침
if st.sidebar.button("🔄 데이터 강제 새로고침"):
    st.session_state.word_dict = load_data()
    new_stats = {w: {"solved": 0, "unlocked": False} for w in st.session_state.word_dict}
    if 'stats' in st.session_state:
        new_stats.update(st.session_state.stats)
    st.session_state.stats = new_stats
    st.rerun()

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

if not st.session_state.word_dict:
    st.error("⚠️ 시트 데이터를 불러오지 못했습니다. 설정을 확인해주세요.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🔥 영-한 퀘스트", "📖 단어 도감", "❌ 오답 노트", "⚙️ 설정"])

# --- [Tab 1: 영-한 타이핑 퀘스트] ---
with tab1:
    st.subheader("영어 단어를 보고 한글 뜻을 입력하세요!")
    q_word = st.session_state.get('current_quiz')
    
    if q_word:
        # 단어 표시 영역
        st.markdown(f"""
            <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;">
                <h1 style="color: #0e1117; font-size: 60px; margin: 0;">{q_word}</h1>
            </div>
        """, unsafe_allow_html=True)
        
        answer_mean = st.session_state.word_dict[q_word]
        
        with st.form(key="quiz_form", clear_on_submit=True):
            user_input = st.text_input("이 단어의 뜻은? (시트와 똑같이 입력하세요)").strip()
            submit = st.form_submit_button("정답 확인", use_container_width=True)
            
            if submit:
                if user_input == answer_mean:
                    st.balloons()
                    st.success(f"정답입니다! 🎉 뜻: {answer_mean}")
                    st.session_state.stats[q_word]["solved"] += 1
                    st.session_state.stats[q_word]["unlocked"] = True
                    if q_word in st.session_state.wrong_words:
                        st.session_state.wrong_words.remove(q_word)
                else:
                    st.error(f"오답입니다! 정답은 '{answer_mean}' 입니다.")
                    st.session_state.wrong_words.add(q_word)
        
        if st.button("다음 단어 ➡️", use_container_width=True):
            st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
            st.rerun()

# --- [Tab 2: 단어 도감 (해금 방식)] ---
with tab2:
    st.subheader("📖 단어 도감")
    search = st.text_input("도감 내 검색 (단어 입력):", placeholder="검색어를 입력하세요...")
    
    display_data = []
    if 'stats' in st.session_state:
        for w, m in st.session_state.word_dict.items():
            if search.lower() in w.lower():
                stat = st.session_state.stats.get(w, {"solved": 0, "unlocked": False})
                status = "✅ 해금" if stat["unlocked"] else "🔒 미해금"
                display_data.append({
                    "상태": status,
                    "단어": w,
                    "뜻": m if stat["unlocked"] else "??? (정답을 맞춰 해금하세요)",
                    "맞춘 횟수": stat["solved"]
                })
        
        st.dataframe(display_data, use_container_width=True)

# --- [Tab 3: 오답 노트] ---
with tab3:
    st.subheader("❌ 오답 노트")
    if not st.session_state.get('wrong_words'):
        st.write("틀린 단어가 없습니다! 아주 훌륭해요.")
    else:
        for ww in list(st.session_state.wrong_words):
            with st.expander(f"📌 {ww}"):
                st.write(f"정답(뜻): **{st.session_state.word_dict[ww]}**")
                if st.button(f"'{ww}' 복습 완료", key=f"del_{ww}"):
                    st.session_state.wrong_words.remove(ww)
                    st.rerun()

# --- [Tab 4: 설정] ---
with tab4:
    st.subheader("⚙️ 관리")
    if st.button("모든 학습 기록(통계/오답) 초기화"):
        st.session_state.clear()
        st.rerun()
