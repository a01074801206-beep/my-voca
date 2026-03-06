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
    """구글 시트 API 연결 설정"""
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Secrets에서 JSON 열쇠 가져오기
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    # ※ 본인의 구글 시트 이름을 정확히 입력하세요!
    return client.open("보카마스터_데이터베이스").sheet1

def load_data():
    """구글 시트에서 데이터를 더 확실하게 읽어오기"""
    try:
        sheet = init_connection()
        
        # [수정] 첫 번째 탭의 모든 값을 가져옵니다.
        all_values = sheet.get_all_values()
        
        if not all_values or len(all_values) <= 1:
            # 데이터가 제목줄밖에 없거나 아예 없는 경우
            return {}

        word_dict = {}
        # 첫 번째 줄(제목)을 제외하고 반복
        for row in all_values[1:]:
            # 행에 최소 2개의 칸이 있고, '단어' 칸(row[0])이 비어있지 않은 경우
            if len(row) >= 2:
                word = str(row[0]).strip()
                mean = str(row[1]).strip()
                if word: # 단어가 존재할 때만 추가
                    word_dict[word] = mean
        
        return word_dict
        
    except Exception as e:
        # 응답 200인데 에러가 난다면 데이터 파싱 문제일 가능성이 큼
        st.error(f"❌ 상세 에러: {e}")
        return {}

# ---------------------------------------------------------
# 2. 데이터 및 세션 상태 초기화
# ---------------------------------------------------------
# 처음 실행하거나 '새로고침' 버튼 누를 때만 시트에서 읽어옴
if 'word_dict' not in st.session_state or st.sidebar.button("🔄 데이터 새로고침"):
    with st.spinner('구글 시트에서 단어장을 동기화 중...'):
        st.session_state.word_dict = load_data()
        # 데이터 로드 후 퀴즈 초기화
        if st.session_state.word_dict:
            st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
            st.session_state.show_mean = False

# 퀴즈 상태 변수 (첫 실행 시 방어 코드)
if 'current_word' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
if 'show_mean' not in st.session_state:
    st.session_state.show_mean = False

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title("📚 VOCA MASTER")

# 상단 정보바
if st.session_state.word_dict:
    st.write(f"✅ 구글 시트에서 **{len(st.session_state.word_dict)}개**의 단어를 성공적으로 가져왔습니다.")
else:
    st.warning("⚠️ 구글 시트가 비어있거나 연결에 문제가 있습니다. 시트에 단어를 추가해주세요.")

st.divider()

# ---------------------------------------------------------
# 4. 단어 학습 기능 (메인)
# ---------------------------------------------------------
if st.session_state.word_dict:
    word = st.session_state.current_word
    
    # 단어 카드 스타일 표시
    st.markdown(f"""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: #0e1117;">{word}</h1>
    </div>
    """, unsafe_content_id=True)

    # 버튼 레이아웃
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("👁️ 뜻 보기", use_container_width=True):
            st.session_state.show_mean = True

    with col2:
        if st.button("➡️ 다음 단어", use_container_width=True):
            st.session_state.current_word = random.choice(list(st.session_state.word_dict.keys()))
            st.session_state.show_mean = False
            st.rerun()

    # 뜻 표시 (성공 박스 스타일)
    if st.session_state.show_mean:
        st.success(f"**뜻:** {st.session_state.word_dict[word]}")

st.divider()

# ---------------------------------------------------------
# 5. 하단 관리용 메뉴 (Expander)
# ---------------------------------------------------------
with st.expander("🛠️ 시스템 정보"):
    st.caption("구글 시트 연동 시스템 작동 중")
    if st.button("로그아웃/세션 초기화"):
        st.session_state.clear()
        st.rerun()
