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
        "attitude": "태도, 사고방식",
        "attract": "끌어들이다, 매혹하다",
        "attribute": "속성, ~의 덕분으로 돌리다",
        "audience": "청중, 관객",
        "author": "작가, 저자",
        "authority": "권위, 당국",
        "available": "이용 가능한, 시간이 있는",
        "average": "평균의",
        "avoid": "피하다",
        "award": "상, 수여하다",
        "aware": "알고 있는, 의식하는",
        "awful": "끔찍한, 지독한",
        "awkward": "어색한, 서투른",
        "balance": "균형, 잔고",
        "ban": "금지하다",
        "barely": "간신히, 거의 ~않다",
        "barrier": "장벽, 장애물",
        "base": "기초, 토대",
        "behalf": "이익, 지지",
        "behave": "행동하다",
        "belief": "믿음, 신념",
        "belong": "~에 속하다",
        "benefit": "이익, 혜택",
        "betray": "배신하다, 드러내다",
        "bewildered": "당혹해 하는",
        "bias": "편견, 선입견",
        "bid": "입찰하다, 시도하다",
        "bind": "묶다, 결속시키다",
        "biography": "전기, 일대기",
        "blame": "비난하다, ~의 탓으로 돌리다",
        "blend": "섞다, 혼합하다",
        "bless": "축복하다",
        "block": "차단하다, 구역",
        "bloom": "꽃이 피다",
        "boast": "자랑하다",
        "bond": "유대, 결속",
        "border": "국경, 경계",
        "boredom": "지루함",
        "borrow": "빌리다",
        "bother": "괴롭히다, 신경 쓰다",
        "boundary": "경계(선)",
        "brake": "브레이크, 제동을 걸다",
        "branch": "나뭇가지, 지점",
        "brave": "용감한",
        "breakthrough": "돌파구, 비약적 발전",
        "breathe": "숨을 쉬다",
        "brief": "잠시의, 간결한",
        "brilliant": "훌륭한, 빛나는",
        "broad": "넓은, 광범위한",
        "broadcast": "방송하다",
        "browse": "둘러보다, 훑어보다",
        "brutal": "잔혹한, 야만적인",
        "budget": "예산",
        "burden": "짐, 부담",
        "burst": "터지다, 폭발하다",
        "bury": "묻다, 매장하다",
        "calculate": "계산하다",
        "campaign": "캠페인, 운동",
        "candidate": "후보자",
        "capable": "~할 수 있는, 유능한",
        "capacity": "용량, 능력",
        "capital": "자본, 수도, 대문자",
        "capture": "포획하다, 붙잡다",
        "career": "경력, 직업",
        "careful": "조심스러운",
        "category": "범주, 카테고리",
        "cause": "원인, 일으키다",
        "caution": "주의, 경고",
        "cease": "중단하다, 그치다",
        "celebrate": "축하하다",
        "cell": "세포, 칸",
        "century": "세기, 100년",
        "certain": "확실한, 특정한",
        "certificate": "증명서, 자격증",
        "challenge": "도전, 난제",
        "chamber": "방, 회의실",
        "chaos": "혼란, 무질서",
        "character": "성격, 특징, 등장인물",
        "charge": "요금, 책임, 충전하다",
        "charity": "자선(단체)",
        "charm": "매력",
        "chase": "추격하다",
        "chat": "수다를 떨다",
        "cheap": "저렴한",
        "check": "확인하다, 억제하다",
        "cheerful": "쾌활한",
        "cherish": "소중히 여기다",
        "chew": "씹다",
        "chief": "주요한, 우두머리",
        "chill": "냉기, 한기",
        "choice": "선택",
        "choir": "합창단",
        "chronic": "만성적인",
        "circumstance": "상황, 환경",
        "cite": "인용하다",
        "citizen": "시민",
        "civil": "시민의, 민간의",
        "claim": "주장하다, 요구하다",
        "clarify": "명확하게 하다",
        "classic": "전형적인, 고전의",
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
