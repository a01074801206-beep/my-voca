import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import random

# 1. 페이지 설정
st.set_page_config(page_title="VOCA MASTER", layout="centered")

# ---------------------------------------------------------
# [기능 1] 구글 시트 연결 및 데이터 로드 함수
# ---------------------------------------------------------
def load_data():
    try:
        scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        service_account_info = json.loads(st.secrets["gcp_service_account"])
        creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
        client = gspread.authorize(creds)
        
        # [수정] 파일명을 voka_master로 변경하고 첫 번째 워크시트를 엽니다.
        spreadsheet = client.open("voka_master")
        sheet = spreadsheet.get_worksheet(0) 
        
        # 모든 데이터를 리스트로 가져옵니다.
        rows = sheet.get_all_values()
        
        if not rows or len(rows) < 1:
            return {}

        word_dict = {}
        for row in rows:
            if len(row) >= 2:
                w = str(row[0]).strip()
                m = str(row[1]).strip()
                # 제목줄('단어')이거나 빈 칸이면 제외
                if w and w != "단어" and w != "word":
                    word_dict[w] = m
        return word_dict
    except Exception as e:
        # 에러 메시지를 사이드바에 작게 표시하여 디버깅을 돕습니다.
        st.sidebar.error(f"연결 상태 확인: {e}")
        return {}

# ---------------------------------------------------------
# 2. 데이터 초기화
# ---------------------------------------------------------
if 'word_dict' not in st.session_state or st.sidebar.button("🔄 데이터 강제 새로고침"):
    st.session_state.word_dict = load_data()

# 퀴즈 상태 초기화
if 'current_word' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
if 'show_mean' not in st.session_state:
    st.session_state.show_mean = False

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

if not st.session_state.word_dict:
    st.error("⚠️ 데이터를 가져오지 못했습니다.")
    st.info("💡 확인사항: 1. 구글 시트 파일명이 'voka_master'가 맞나요? 2. 시트 2행부터 단어가 들어있나요?")
    if st.button("다시 연결 시도"):
        st.rerun()
else:
    st.success(f"✅ {len(st.session_state.word_dict)}개의 단어를 불러왔습니다.")
    st.divider()

    # 단어 카드
    word = st.session_state.current_word
    st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #dee2e6;">
            <h1 style="margin: 0; color: #1a1a1a;">{word}</h1>
        </div>
    """, unsafe_content_id=True)

    st.write("") # 간격 조절
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👁️ 뜻 보기", use_container_width=True):
            st.session_state.show_mean = True
    with col2:
        if st.button("➡️ 다음 단어", use_container_width=True):
            st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
            st.session_state.show_mean = False
            st.rerun()

    if st.session_state.show_mean:
        st.info(f"**뜻:** {st.session_state.word_dict[word]}")
