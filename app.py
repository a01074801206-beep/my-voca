import streamlit as st
import random

# --- 1. 단어 데이터 (301~400번대 추가용) ---
if 'voca_db' not in st.session_state:
    st.session_state.voca_db = {
        # 앞서 드린 단어들을 여기에 쭉 붙여넣으세요!
        "convenience": "편의, 편리",
        "convert": "전환하다, 바꾸다",
        "convey": "전달하다, 운반하다",
        "convince": "확신시키다, 설득하다",
        "cooperate": "협력하다",
        "coordinate": "조정하다, 통합하다",
        "cope": "대처하다, 맞서다",
        "core": "핵심, 핵심의",
        "corporate": "기업의, 법인의",
        "correspond": "일치하다, 서신을 주고받다",
        "corrupt": "부패한, 타락시키다",
        "costly": "비싼, 대가가 큰",
        "council": "의회, 자문위원회",
        "counsel": "상담, 조언하다",
        "counter": "계산대, 반대하다",
        "counterpart": "대응 관계에 있는 사람/사물",
        "countless": "무수한",
        "courage": "용기",
        "courtesy": "예의, 공손",
        "coward": "겁쟁이",
        # ... 추가 단어들
    }

# --- 2. 상태 초기화 ---
if 'quiz_list' not in st.session_state:
    all_words = list(st.session_state.voca_db.items())
    sample_count = min(len(all_words), 20)
    st.session_state.quiz_list = random.sample(all_words, sample_count)
    st.session_state.total_count = sample_count
    st.session_state.show_answer = False  # 정답 공개 여부 상태 추가

st.title("🎯 수능 단어 완전 정복")
st.write(f"남은 문제: **{len(st.session_state.quiz_list)}**개")

if not st.session_state.quiz_list:
    st.balloons()
    st.success("🎉 오늘 목표 달성!")
    if st.button("새로운 20문제 시작"):
        del st.session_state.quiz_list
        st.rerun()
else:
    word, mean = st.session_state.quiz_list[0]
    
    st.divider()
    st.markdown(f"<h1 style='text-align: center;'>{word}</h1>", unsafe_allow_html=True)

    # 정답을 확인 중인 상태가 아닐 때만 입력창을 보여줌
    if not st.session_state.show_answer:
        user_ans = st.text_input("뜻을 입력하세요", key="input_box").strip()
        
        if st.button("정답 확인", use_container_width=True):
            if user_ans == mean:
                st.success("✅ 정답입니다!")
                st.session_state.quiz_list.pop(0)
                st.rerun()
            else:
                st.session_state.show_answer = True # 정답 공개 상태로 전환
                st.rerun()
                
        if st.button("모르겠어요 (패스)", use_container_width=True):
            st.session_state.show_answer = True
            st.rerun()

    # 틀렸거나 패스해서 정답을 보여줘야 하는 상태
    else:
        st.error(f"❌ 정답은: **{mean}**")
        st.info("단어를 외운 후 아래 버튼을 눌러주세요.")
        
        if st.button("다음 문제로 넘어가기 ➡️", use_container_width=True):
            # 틀린 단어를 맨 뒤로 보내고 다시 섞기
            wrong_item = st.session_state.quiz_list.pop(0)
            st.session_state.quiz_list.append(wrong_item)
            random.shuffle(st.session_state.quiz_list)
            
            # 다시 문제 모드로 전환
            st.session_state.show_answer = False
            st.rerun()
