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
        
        # 파일명 'voka_master' 확인
        spreadsheet = client.open("voka_master")
        sheet = spreadsheet.get_worksheet(0) 
        
        rows = sheet.get_all_values()
        
        if not rows or len(rows) < 1:
            return {}

        word_dict = {}
        for row in rows:
            if len(row) >= 2:
                w = str(row[0]).strip()
                m = str(row[1]).strip()
                # 제목줄 제외 로직
                if w and w not in ["단어", "word", ""]:
                    word_dict[w] = m
        return word_dict
    except Exception as e:
        st.sidebar.error(f"연결 상태 확인: {e}")
        return {}

# ---------------------------------------------------------
# 2. 데이터 초기화
# ---------------------------------------------------------
# 세션 상태 초기화
if 'word_dict' not in st.session_state:
    st.session_state.word_dict = {}
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'show_mean' not in st.session_state:
    st.session_state.show_mean = False

# 데이터 로드 (최초 실행 혹은 새로고침 버튼)
if not st.session_state.word_dict or st.sidebar.button("🔄 데이터 강제 새로고침"):
    with st.spinner('시트 동기화 중...'):
        loaded_data = load_data()
        if loaded_data:
            st.session_state.word_dict = loaded_data
            st.session_state.current_word = random.choice(list(loaded_data.keys()))
            st.session_state.show_mean = False
            st.rerun()

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

if not st.session_state.word_dict:
    st.error("⚠️ 데이터를 가져오지 못했습니다.")
    st.info("💡 확인사항:\n1. 구글 시트 파일명이 **voka_master** 인가요?\n2. 시트 2행부터 단어가 들어있나요?\n3. 서비스 계정 이메일이 시트에 '편집자'로 초대되었나요?")
else:
    st.success(f"✅ {len(st.session_state.word_dict)}개의 단어를 불러왔습니다.")
    st.divider()

    # 단어 카드 표시 영역
    word = st.session_state.current_word
    if word:
        # [수정] unsafe_allow_html=True 로 오타 수정
        st.markdown(f"""
            <div style="background-color: #f8f9fa; padding: 40px; border-radius: 20px; text-align: center; border: 1px solid #dee2e6;">
                <h1 style="margin: 0; color: #1a1a1a;">{word}</h1>
            </div>
        """, unsafe_allow_html=True)

        st.write("") 
        
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
    else:
        st.warning("단어를 선택할 수 없습니다. 시트 내용을 확인해주세요.")

# ---------------------------------------------------------
# 4. 하단 관리 (사이드바)
# ---------------------------------------------------------
with st.sidebar:
    st.header("설정")
    if st.button("세션 초기화"):
        st.session_state.clear()
        st.rerun()
