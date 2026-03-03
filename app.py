import streamlit as st
import random

# 1. 단어 데이터 (본인이 외우고 싶은 단어로 수정하세요!)
# 형식: {"단어": "뜻", ...}
if 'voca_db' not in st.session_state:
    st.session_state.voca_db = {
        "apple": "사과", "banana": "바나나", "cherry": "체리", 
        "determine": "결정하다", "effort": "노력", "feature": "특징",
        "generous": "관대한", "habit": "습관", "identify": "확인하다",
        "judgment": "판단", "knowledge": "지식", "limit": "제한",
        "maintain": "유지하다", "notice": "알아차리다", "opportunity": "기회",
        "provide": "제공하다", "quality": "품질", "respect": "존중",
        "source": "원천", "tough": "힘든"
    }

# 2. 앱 상태 초기화 (처음 실행 시 20개 추출)
if 'quiz_list' not in st.session_state:
    all_words = list(st.session_state.voca_db.items())
    # 데이터가 20개보다 적을 경우를 대비해 처리
    sample_count = min(len(all_words), 20)
    st.session_state.quiz_list = random.sample(all_words, sample_count)
    st.session_state.total_count = sample_count

# 앱 UI 구성
st.title("🎯 20문제 완전 학습기")
st.write(f"현재 남은 문제: **{len(st.session_state.quiz_list)}** / {st.session_state.total_count}")

# 모든 문제를 다 맞혔을 때
if not st.session_state.quiz_list:
    st.balloons()
    st.success("🎉 축하합니다! 20문제를 모두 마스터하셨습니다.")
    if st.button("새로운 20문제 시작하기"):
        del st.session_state.quiz_list
        st.rerun()
else:
    # 현재 풀어야 할 문제 (리스트의 첫 번째)
    current_word, current_mean = st.session_state.quiz_list[0]
    
    st.divider()
    st.subheader(f"뜻: {current_mean}")
    
    # 정답 입력창 (엔터를 치면 바로 제출되도록 설정)
    user_input = st.text_input("영단어를 입력하세요:", key="input_field").strip().lower()

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("정답 확인", use_container_width=True):
            if user_input == current_word.lower():
                st.success("✅ 정답!")
                # 맞히면 리스트에서 제거
                st.session_state.quiz_list.pop(0)
                st.rerun()
            else:
                st.error(f"❌ 틀렸습니다! 정답은 [{current_word}] 입니다.")
                # 틀리면 맨 뒤로 보내거나 섞기 (여기서는 맨 뒤로 보냄)
                wrong_item = st.session_state.quiz_list.pop(0)
                st.session_state.quiz_list.append(wrong_item)
                # 틀렸을 때 리스트를 다시 한번 섞어주면 더 효과적입니다.
                random.shuffle(st.session_state.quiz_list)
    
    with col2:
        if st.button("패스 (뒤로 넘기기)", use_container_width=True):
            passed_item = st.session_state.quiz_list.pop(0)
            st.session_state.quiz_list.append(passed_item)
            st.rerun()
