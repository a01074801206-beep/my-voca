import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import json
import random
import pandas as pd

st.set_page_config(page_title="VOCA MASTER PRO", layout="wide")

# ---------------------------------------------------------
# [기능 1] 구글 시트 연결 및 데이터 로드 (멀티 탭 지원)
# ---------------------------------------------------------
def init_gspread():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    service_account_info = json.loads(st.secrets["gcp_service_account"])
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    return gspread.authorize(creds)

def load_tab_data(tab_name):
    """지정한 탭의 단어 데이터를 로드"""
    try:
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        sheet = spreadsheet.worksheet(tab_name)
        rows = sheet.get_all_values()
        return {row[0].strip(): row[1].strip() for row in rows if row[0] and row[0] not in ["단어", "word"]}
    except:
        return {}

def load_stats():
    """학습 기록 로드"""
    try:
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        stats_sheet = spreadsheet.worksheet("stats")
        rows = stats_sheet.get_all_records()
        return {row['단어']: {"solved": int(row['맞춘횟수']), "unlocked": str(row['해금여부']).upper() == 'TRUE'} for row in rows}
    except:
        return {}

def save_stats_to_sheet(word, solved, unlocked):
    try:
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        stats_sheet = spreadsheet.worksheet("stats")
        cell = stats_sheet.find(word)
        if cell:
            stats_sheet.update_cell(cell.row, 2, solved)
            stats_sheet.update_cell(cell.row, 3, "TRUE" if unlocked else "FALSE")
        else:
            stats_sheet.append_row([word, solved, "TRUE" if unlocked else "FALSE"])
    except: pass

# ---------------------------------------------------------
# 2. 세션 상태 관리
# ---------------------------------------------------------
if 'stats' not in st.session_state:
    st.session_state.stats = load_stats()

# 사이드바에서 데이터셋 선택
with st.sidebar:
    st.header("📚 데이터셋 선택")
    selected_tab = st.selectbox("공부할 단어장", ["words_all", "words_verb"], help="구글 시트의 탭 이름과 일치해야 합니다.")
    
    if st.button("🔄 선택한 단어장 로드"):
        st.session_state.word_dict = load_tab_data(selected_tab)
        st.session_state.current_quiz = random.choice(list(st.session_state.word_dict.keys())) if st.session_state.word_dict else None
        st.rerun()

# 최초 로드
if 'word_dict' not in st.session_state:
    st.session_state.word_dict = load_tab_data(selected_tab)

if 'wrong_words' not in st.session_state: st.session_state.wrong_words = set()
if 'show_hint' not in st.session_state: st.session_state.show_hint = False

# ---------------------------------------------------------
# 3. 메인 화면 구성
# ---------------------------------------------------------
st.title(f"📚 VOCA MASTER PRO ({selected_tab})")

# 진척도 (현재 로드된 단어장 기준)
if st.session_state.word_dict:
    current_pool = set(st.session_state.word_dict.keys())
    unlocked_count = sum(1 for w, s in st.session_state.stats.items() if w in current_pool and s["unlocked"])
    total_count = len(current_pool)
    progress = unlocked_count / total_count if total_count > 0 else 0
    st.progress(progress)
    st.caption(f"🏆 {selected_tab} 해금률: {progress*100:.1f}% ({unlocked_count}/{total_count})")

tab1, tab2, tab3, tab4 = st.tabs(["🎯 퀴즈", "📖 도감", "❌ 오답노트", "⚙️ 설정"])

# --- [Tab 1: 퀴즈] ---
with tab1:
    mode = st.radio("모드", ["전체 랜덤", "오답 집중"], horizontal=True)
    
    # 퀴즈 풀 생성
    pool = list(st.session_state.word_dict.keys())
    if mode == "오답 집중" and st.session_state.wrong_words:
        pool = [w for w in pool if w in st.session_state.wrong_words]
    
    if not pool:
        st.warning("조건에 맞는 단어가 없습니다.")
    else:
        if 'current_quiz' not in st.session_state or st.session_state.current_quiz not in pool:
            st.session_state.current_quiz = random.choice(pool)
            
        q_word = st.session_state.current_quiz
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
                    st.success("정답!")
                    # 통계 업데이트 및 저장
                    if q_word not in st.session_state.stats:
                        st.session_state.stats[q_word] = {"solved": 0, "unlocked": False}
                    st.session_state.stats[q_word]["solved"] += 1
                    st.session_state.stats[q_word]["unlocked"] = True
                    save_stats_to_sheet(q_word, st.session_state.stats[q_word]["solved"], True)
                else:
                    st.error(f"오답! 정답: {answer}")
                    st.session_state.wrong_words.add(q_word)
            if cols[1].form_submit_button("힌트 보기", use_container_width=True):
                st.session_state.show_hint = True
                st.rerun()

        if st.button("다음 단어 ➡️", use_container_width=True):
            st.session_state.current_quiz = random.choice(pool)
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

# --- [Tab 3: 오답노트] ---
with tab3:
    if not st.session_state.wrong_words:
        st.write("오답이 없습니다!")
    else:
        for ww in list(st.session_state.wrong_words):
            if ww in st.session_state.word_dict:
                with st.expander(f"📌 {ww}"):
                    st.write(f"뜻: {st.session_state.word_dict[ww]}")
                    if st.button(f"삭제", key=f"del_{ww}"):
                        st.session_state.wrong_words.remove(ww)
                        st.rerun()
import json

# [추가] JSON 파일을 읽어서 시트로 전송하는 함수
def sync_verbs_from_json():
    try:
        # 1. JSON 파일 읽기
        with open('verbs.json', 'r', encoding='utf-8') as f:
            verbs_payload = json.load(f)
        
        # 2. 구글 시트 연결
        client = init_gspread()
        spreadsheet = client.open("voka_master")
        
        # 3. 'words_verb' 탭 초기화 및 업로드
        try:
            worksheet = spreadsheet.worksheet("words_verb")
            worksheet.clear()
        except:
            worksheet = spreadsheet.add_worksheet(title="words_verb", rows="1500", cols="2")
        
        worksheet.append_row(["단어", "뜻"])
        worksheet.append_rows(verbs_payload)
        return True, len(verbs_payload)
    except Exception as e:
        return False, str(e)

# --- [Tab 4: 설정] 화면에 버튼 배치 ---
with tab4:
    st.subheader("📦 데이터 동기화")
    st.info("verbs.json 파일에 있는 단어들을 구글 시트 'words_verb' 탭으로 전송합니다.")
    
    if st.button("🚀 JSON 데이터 시트로 전송하기", use_container_width=True):
        with st.spinner('시트 업데이트 중...'):
            success, result = sync_verbs_from_json()
            if success:
                st.success(f"성공! {result}개의 단어가 업로드되었습니다.")
                st.balloons()
            else:
                st.error(f"오류 발생: {result}")
