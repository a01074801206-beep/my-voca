import streamlit as st
import random

# --- 1. 단어 데이터 (여기에 제가 드린 단어들을 넣으세요) ---
if 'voca_db' not in st.session_state:
    # 중복 제거를 위해 dict로 정의
    raw_data = {
        "banana": "바나나, 바나나들", 
        "happy": "해피, 행복", 
          # 예시
        # ... (이전 대화에서 드린 단어들을 여기에 쭉 붙여넣으세요)
    }
    st.session_state.voca_db = raw_data

# --- 2. 퀴즈 세션 초기화 ---
if 'quiz_list' not in st.session_state:
    st.session_state.quiz_list = []
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

st.title("🚀 수능 영단어 2400 마스터")

# 시작 버튼
if st.button("테스트 시작 (20문제)"):
    all_words = list(st.session_state.voca_db.items())
    st.session_state.quiz_list = random.sample(all_words, 20)
    st.session_state.show_answer = False

# --- 3. 퀴즈 진행 로직 ---
if st.session_state.quiz_list:
    word, mean = st.session_state.quiz_list[0]
    
    st.subheader(f"단어: **{word}**")
    st.write(f"남은 문제: {len(st.session_state.quiz_list)}개")
    
    user_input = st.text_input("뜻을 입력하세요:", key=f"input_{word}").strip()

    if st.button("확인"):
        # [핵심 수정 부분] 쉼표로 분리하여 하나라도 맞으면 정답 처리
        ans_list = [a.strip() for a in mean.split(",")]
        
        if user_input in ans_list or user_input == mean:
            st.success(f"✅ 정답입니다! 뜻: {mean}")
            st.session_state.quiz_list.pop(0)
            st.rerun()
        else:
            st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.error(f"❌ 틀렸습니다! 정답은: **{mean}**")
        if st.button("외웠어요! 다음 문제 ➡️"):
            # 틀린 단어를 맨 뒤로 보냄
            wrong_item = st.session_state.quiz_list.pop(0)
            st.session_state.quiz_list.append(wrong_item)
            st.session_state.show_answer = False
            st.rerun()
