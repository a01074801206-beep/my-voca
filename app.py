import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import random
import pandas as pd

# 1. 페이지 설정
st.set_page_config(page_title="VOCA MASTER PRO", layout="wide")

# ---------------------------------------------------------
# [기능 1] 구글 시트 연결 및 데이터 로드
# ---------------------------------------------------------
def init_gspread():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    return gspread.authorize(creds)

def load_all_data():
    try:
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        
        # 1. 단어장 로드 (첫 번째 탭)
        word_sheet = spreadsheet.get_worksheet(0)
        word_rows = word_sheet.get_all_values()
        word_dict = {row[0].strip(): row[1].strip() for row in word_rows if row[0] and row[0] not in ["단어", "word"]}
        
        # 2. 학습 통계 로드 (stats 탭)
        try:
            stats_sheet = spreadsheet.worksheet("stats")
            stats_rows = stats_sheet.get_all_records()
            stats_dict = {row['단어']: {"solved": int(row['맞춘횟수']), "unlocked": str(row['해금여부']).upper() == 'TRUE'} for row in stats_rows}
        except:
            # stats 탭이 없거나 비어있을 경우 초기화
            stats_dict = {w: {"solved": 0, "unlocked": False} for w in word_dict}
            
        return word_dict, stats_dict
    except Exception as e:
        st.sidebar.error(f"연결 에러: {e}")
        return {}, {}

def save_stats_to_sheet(word, solved, unlocked):
    """정답을 맞췄을 때 시트에 즉시 기록"""
    try:
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        stats_sheet = spreadsheet.worksheet("stats")
        
        # 기존 기록 확인
        cell = stats_sheet.find(word)
        if cell:
            stats_sheet.update_cell(cell.row, 2, solved)
            stats_sheet.update_cell(cell.row, 3, "TRUE" if unlocked else "FALSE")
        else:
            stats_sheet.append_row([word, solved, "TRUE" if unlocked else "FALSE"])
    except:
        pass

# ---------------------------------------------------------
# 2. 데이터 초기화
# ---------------------------------------------------------
if 'word_dict' not in st.session_state:
    with st.spinner('클라우드에서 학습 기록을 불러오는 중...'):
        w_dict, s_dict = load_all_data()
        st.session_state.word_dict = w_dict
        st.session_state.stats = s_dict

if 'wrong_words' not in st.session_state:
    st.session_state.wrong_words = set()

if 'current_quiz' not in st.session_state and st.session_state.word_dict:
    st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))

if 'show_hint' not in st.session_state:
    st.session_state.show_hint = False

# ---------------------------------------------------------
# 3. 메인 화면 및 진척도 표시
# ---------------------------------------------------------
st.title("📚 VOCA MASTER PRO")

if st.session_state.word_dict:
    unlocked_count = sum(1 for s in st.session_state.stats.values() if s.get("unlocked"))
    total_count = len(st.session_state.word_dict)
    progress = unlocked_count / total_count if total_count > 0 else 0
    
    col_prog, col_text = st.columns([4, 1])
    col_prog.progress(progress)
    col_text.write(f"🏆 **{progress*100:.1f}%** 해금됨")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 퀴즈", "📖 도감", "❌ 오답노트", "⚙️ 설정"])

# --- [Tab 1: 퀴즈] ---
with tab1:
    mode = st.radio("모드", ["전체 랜덤", "오답 집중 복습"], horizontal=True)
    q_word = st.session_state.get('current_quiz')
    
    if q_word:
        st.markdown(f"<div style='background-color:#f0f2f6;padding:30px;border-radius:15px;text-align:center;'><h1 style='font-size:60px;'>{q_word}</h1></div>", unsafe_allow_html=True)
        
        answer = st.session_state.word_dict[q_word]
        if st.session_state.show_hint:
            st.caption(f"💡 힌트: {answer[0]} " + "_ " * (len(answer)-1))

        with st.form(key="q_form", clear_on_submit=True):
            user_in = st.text_input("뜻을 입력하세요:")
            cols = st.columns(2)
            if cols[0].form_submit_button("정답 확인", use_container_width=True):
                if user_in == answer:
                    st.balloons()
                    st.success("정답입니다!")
                    st.session_state.stats[q_word]["solved"] += 1
                    st.session_state.stats[q_word]["unlocked"] = True
                    # [핵심] 시트에 저장
                    save_stats_to_sheet(q_word, st.session_state.stats[q_word]["solved"], True)
                else:
                    st.error(f"오답! 정답은: {answer}")
                    st.session_state.wrong_words.add(q_word)
            
            if cols[1].form_submit_button("힌트 보기", use_container_width=True):
                st.session_state.show_hint = True
                st.rerun()

        if st.button("다음 단어 ➡️", use_container_width=True):
            if mode == "오답 집중 복습" and st.session_state.wrong_words:
                st.session_state.current_quiz = random.choice(list(st.session_state.wrong_words))
            else:
                st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys()))
            st.session_state.show_hint = False
            st.rerun()

# --- [Tab 2: 도감] ---
with tab2:
    search = st.text_input("도감 검색:")
    df_list = []
    for w, m in st.session_state.word_dict.items():
        if search.lower() in w.lower():
            s = st.session_state.stats.get(w, {"solved": 0, "unlocked": False})
            df_list.append({
                "상태": "✅ 해금" if s["unlocked"] else "🔒 미해금",
                "단어": w,
                "뜻": m if s["unlocked"] else "???",
                "회수": s["solved"]
            })
    st.dataframe(pd.DataFrame(df_list), use_container_width=True)

# --- 나머지 탭 생략 (기존 기능 유지) ---
