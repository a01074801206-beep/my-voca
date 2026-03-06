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
def init_connection():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    # ※ 본인의 시트 이름을 정확히 입력하세요!
    return client.open("보카마스터_데이터베이스").sheet1

def load_data():
    try:
        sheet = init_connection()
        # [수정] 제목줄 무시하고 모든 값을 리스트로 가져옴
        rows = sheet.get_all_values()
        
        if not rows or len(rows) < 1:
            return {}

        word_dict = {}
        # 첫 번째 줄이 '단어/뜻' 제목이든 실제 데이터든 상관없이 싹 다 읽음
        for row in rows:
            if len(row) >= 2:
                w = str(row[0]).strip()
                m = str(row[1]).strip()
                # '단어'라는 제목줄은 제외하고 실제 내용만 담기
                if w and w != "단어":
                    word_dict[w] = m
        return word_dict
    except Exception as e:
        # Response 200 에러가 나더라도 무시하고 빈 딕셔너리 반환 방지
        st.sidebar.error(f"연결 상태: {e}")
        return {}

# ---------------------------------------------------------
# 2. 데이터 초기화
# ---------------------------------------------------------
if 'word_dict' not in st.session_state or st.sidebar.button("🔄 데이터 강제 새로고침"):
    st.session_state.word_dict = load_data()

# 퀴즈 상태 관리
if 'current_word' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
if 'show_mean' not in st.session_state:
    st.session_state.show_mean = False

# ---------------------------------------------------------
# 3. 메인 화면
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

if not st.session_state.word_dict:
    st.error("⚠️ 시트에서 데이터를 가져오지 못했습니다.")
    st.info("💡 해결방법: 스마트폰 구글 시트 앱을 열어 A열에 단어, B열에 뜻이 적혀있는지 확인하세요!")
    if st.button("다시 시도"):
        st.rerun()
else:
    st.success(f"✅ {len(st.session_state.word_dict)}개의 단어를 불러왔습니다.")
    
    st.divider()

    # 단어 학습 카드
    word = st.session_state.current_word
    st.markdown(f"""
        <div style="background-color: #f0f2f6; padding: 30px; border-radius: 15px; text-align: center;">
            <h1 style="margin: 0;">{word}</h1>
        </div>
    """, unsafe_content_id=True)

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
