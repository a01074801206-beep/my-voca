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
if 'word_dict' not in st.session_state or st.sidebar.button("🔄 데이터 새로고침"):
    st.session_state.word_dict = load_data()
    # 학습 통계 초기화 (최초 1회만)
    if 'stats' not in st.session_state:
        st.session_state.stats = {w: {"solved": 0, "unlocked": False} for w in st.session_state.word_dict}
    if 'wrong_words' not in st.session_state:
        st.session_state.wrong_words = set()

# 퀴즈용 상태 초기화
if 'current_quiz' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

tab1, tab2, tab3, tab4 = st.tabs(["🔥 타이핑 퀘스트", "📖 단어 도감", "❌ 오답 노트", "⚙️ 설정"])

# --- [Tab 1: 타이핑 퀘스트] ---
with tab1:
    st.subheader("뜻을 보고 단어를 직접 타이핑하세요!")
    q_word = st.session_state.current_quiz
    if q_word:
        q_mean = st.session_state.word_dict[q_word]
        st.info(f"### 💡 뜻: {q_mean}")
        
        user_answer = st.text_input("정답 단어를 입력하세요:", key="quiz_input").strip()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("정답 확인", use_container_width=True):
                if user_answer.lower() == q_word.lower():
                    st.balloons()
                    st.success(f"정답입니다! 🎉 ({q_word})")
                    # 통계 업데이트
                    st.session_state.stats[q_word]["solved"] += 1
                    st.session_state.stats[q_word]["unlocked"] = True
                    if q_word in st.session_state.wrong_words:
                        st.session_state.wrong_words.remove(q_word)
                else:
                    st.error(f"틀렸습니다! 정답은 '{q_word}' 입니다.")
                    st.session_state.wrong_words.add(q_word)
        
        with col2:
            if st.button("다음 문제 ➡️", use_container_width=True):
                st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
                st.rerun()

# --- [Tab 2: 단어 도감 (해금/미해금)] ---
with tab2:
    st.subheader("📖 단어 도감")
    search = st.text_input("도감 내 검색:", placeholder="단어를 입력하세요...")
    
    display_data = []
    for w, m in st.session_state.word_dict.items():
        if search.lower() in w.lower():
            stat = st.session_state.stats.get(w, {"solved": 0, "unlocked": False})
            status = "✅ 해금" if stat["unlocked"] else "🔒 미해금"
            display_data.append({
                "상태": status,
                "단어": w if stat["unlocked"] else "???",
                "뜻": m,
                "맞춘 횟수": stat["solved"]
            })
    
    st.dataframe(display_data, use_container_width=True)

# --- [Tab 3: 오답 노트] ---
with tab4: # 관리 탭
    st.write(f"현재 로드된 단어: {len(st.session_state.word_dict)}개")
    if st.button("모든 학습 데이터 초기화"):
        st.session_state.clear()
        st.rerun()

with tab3:
    st.subheader("❌ 오답 노트")
    if not st.session_state.wrong_words:
        st.write("틀린 단어가 없습니다. 완벽해요!")
    else:
        st.write(f"복습이 필요한 단어가 **{len(st.session_state.wrong_words)}**개 있습니다.")
        for ww in list(st.session_state.wrong_words):
            with st.expander(f"📌 {st.session_state.word_dict[ww]}"):
                st.write(f"정답: **{ww}**")
                if st.button(f"'{ww}' 복습 완료", key=f"del_{ww}"):
                    st.session_state.wrong_words.remove(ww)
                    st.rerun()
