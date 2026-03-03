import streamlit as st
import random

# --- 1. 수능 단어 데이터베이스 (직접 삽입) ---
# 아래 괄호 { } 사이에 '단어': '뜻' 형태로 2,000개를 넣으시면 됩니다.
if 'voca_db' not in st.session_state:
    st.session_state.voca_db = {
        "abandon": "버리다, 포기하다",
        "ability": "능력",
        "absorb": "흡수하다",
        "abstract": "추상적인",
        "academic": "학업의, 학교의",
        "accent": "강세, 말투",
        "accept": "받아들이다",
        "access": "접근, 이용",
        "accompany": "동행하다",
        "account": "계좌, 설명",
        # ... 여기에 나머지 1,990개를 복사해서 넣으세요!
        "zone": "구역, 지역"
    }

# --- 2. 앱 로직 설정 ---
if 'quiz_list' not in st.session_state:
    all_words = list(st.session_state.voca_db.items())
    # 전체 중 무작위 20개 추출
    sample_count = min(len(all_words), 20)
    st.session_state.quiz_list = random.sample(all_words, sample_count)
    st.session_state.total_count = sample_count

# --- 3. UI 화면 구성 ---
st.title("🎓 수능 영단어 지옥 훈련")
st.write(f"오늘의 목표: **{st.session_state.total_count}문제 완벽 암기**")

# 진행률 바
progress = (st.session_state.total_count - len(st.session_state.quiz_list)) / st.session_state.total_count
st.progress(progress)
st.write(f"남은 단어: **{len(st.session_state.quiz_list)}**개")

if not st.session_state.quiz_list:
    st.balloons()
    st.success("🎉 대단합니다! 20문제를 모두 마스터하셨습니다.")
    if st.button("다음 20문제 도전하기"):
        del st.session_state.quiz_list
        st.rerun()
else:
    # 현재 문제 추출
    word, mean = st.session_state.quiz_list[0]
    
    st.divider()
    st.markdown(f"<h1 style='text-align: center; color: #2E86C1;'>{word}</h1>", unsafe_allow_html=True)
    
    # 정답 입력창
    user_ans = st.text_input("뜻을 입력하세요 (예: 사과)", key="input_box").strip()

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("정답 확인", use_container_width=True):
            if user_ans == mean:
                st.success("✅ 정답!")
                st.session_state.quiz_list.pop(0) # 리스트에서 제거
                st.rerun()
            else:
                st.error(f"❌ 틀렸습니다! 정답은 [{mean}] 입니다.")
                # 틀리면 리스트 맨 뒤로 보내고 다시 섞기
                wrong_item = st.session_state.quiz_list.pop(0)
                st.session_state.quiz_list.append(wrong_item)
                random.shuffle(st.session_state.quiz_list)
                # 틀린 정보를 확인하게 하기 위해 리런은 버튼 클릭 시에만 발생
                if st.button("다음 문제로"):
                    st.rerun()

    with col2:
        if st.button("모르겠어요 (패스)", use_container_width=True):
            st.info(f"정답은 **{mean}** 입니다. 외워질 때까지 계속 나옵니다!")
            passed_item = st.session_state.quiz_list.pop(0)
            st.session_state.quiz_list.append(passed_item)
            random.shuffle(st.session_state.quiz_list)
            if st.button("알겠습니다"):
                st.rerun()
