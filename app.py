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
# 2. 세션 상태 및 데이터 초기화
# ---------------------------------------------------------
if 'word_dict' not in st.session_state or st.sidebar.button("🔄 시트 데이터 새로고침"):
    st.session_state.word_dict = load_data()
    if st.session_state.word_dict:
        st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
        st.session_state.quiz_options = random.sample(list(st.session_state.word_dict.values()), 3)
        if st.session_state.word_dict[st.session_state.current_quiz] not in st.session_state.quiz_options:
            st.session_state.quiz_options[0] = st.session_state.word_dict[st.session_state.current_quiz]
        random.shuffle(st.session_state.quiz_options)

# ---------------------------------------------------------
# 3. 메인 화면 구성 (탭 활용)
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

if not st.session_state.word_dict:
    st.error("⚠️ 시트 데이터를 불러오지 못했습니다. 설정을 확인해주세요.")
    st.stop()

# 탭 메뉴 구성
tab1, tab2, tab3 = st.tabs(["🔥 일일 퀘스트", "📖 단어 도감", "⚙️ 관리"])

# --- [Tab 1: 일일 퀘스트 (정답 맞히기)] ---
with tab1:
    st.subheader("오늘의 도전! 정답을 맞혀보세요.")
    q_word = st.session_state.get('current_quiz')
    
    if q_word:
        st.info(f"## {q_word}")
        answer = st.session_state.word_dict[q_word]
        
        # 사지선다형 퀴즈
        user_choice = st.radio("알맞은 뜻을 고르세요:", st.session_state.quiz_options, index=None)
        
        if st.button("정답 확인"):
            if user_choice == answer:
                st.balloons()
                st.success("정답입니다! 완벽해요! 🎉")
            else:
                st.error(f"아쉽네요! 정답은 '{answer}' 입니다.")
        
        if st.button("다음 문제 ➡️"):
            st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
            # 오답 후보 생성
            all_means = list(st.session_state.word_dict.values())
            st.session_state.quiz_options = random.sample(all_means, 3)
            if st.session_state.word_dict[st.session_state.current_quiz] not in st.session_state.quiz_options:
                st.session_state.quiz_options[0] = st.session_state.word_dict[st.session_state.current_quiz]
            random.shuffle(st.session_state.quiz_options)
            st.rerun()

# --- [Tab 2: 단어 도감 (리스트 보기)] ---
with tab2:
    st.subheader("나만의 단어 도감")
    search_query = st.text_input("단어 검색:", placeholder="찾고 싶은 단어를 입력하세요...")
    
    # 검색 필터링
    filtered_dict = {w: m for w, m in st.session_state.word_dict.items() if search_query.lower() in w.lower()}
    
    st.write(f"총 **{len(filtered_dict)}**개의 단어가 있습니다.")
    
    # 도감 스타일 테이블
    st.table([{"단어": w, "뜻": m} for w, m in list(filtered_dict.items())[:100]]) # 상위 100개만 표시
    if len(filtered_dict) > 100:
        st.caption("※ 단어가 너무 많아 상위 100개만 표시됩니다. 검색 기능을 활용하세요!")

# --- [Tab 3: 관리 및 정보] ---
with tab3:
    st.write(f"현재 연결된 시트: **voka_master**")
    st.write(f"로드된 단어 수: **{len(st.session_state.word_dict)}개**")
    if st.button("전체 세션 초기화"):
        st.session_state.clear()
        st.rerun()
