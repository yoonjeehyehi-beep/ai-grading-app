import streamlit as st

st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

# --- 채점 핵심 로직 함수 정의 ---
def evaluate_set1_q1(ans_a, ans_b, ans_c):
    """1세트 문항1 채점 로직"""
    score = [0, 0, 0]
    feedback = ["", "", ""]
    
    # ㉠ 채점 (쉬운 과제 관련)
    keywords_a = ["쉬운", "친숙한", "노력이 적게", "단순한"]
    if any(k in ans_a for k in keywords_a):
        score[0] = 2
        feedback[0] = "정답입니다. 과제의 특성을 잘 찾아냈습니다."
    else:
        feedback[0] = "오답입니다. '쉬운 과제' 또는 '친숙한 과목'의 특성이 포함되어야 합니다."
        
    # ㉡ 채점 (혼자 집중 관련)
    keywords_b = ["혼자", "스스로", "타인의 시선이 없는", "독서실", "방에서"]
    if any(k in ans_b for k in keywords_b) and ("집중" in ans_b or "몰입" in ans_b):
        score[1] = 2
        feedback[1] = "정답입니다. 효율적인 환경 및 태도를 정확히 정리했습니다."
    else:
        feedback[1] = "오답입니다. '혼자 차분하게 집중한다'는 의미가 명확해야 합니다."
        
    # ㉢ 채점 (심리 현상 명칭 - 용어 필수)
    if "사회적 억제" in ans_c.replace(" ", ""):
        score[2] = 2
        feedback[2] = "정답입니다. 정확한 학술 용어를 제시했습니다."
    else:
        feedback[2] = "오답입니다. 정확한 용어는 '사회적 억제'입니다."
        
    return score, feedback


def evaluate_set3_q2(user_ans):
    """3세트 문항2 채점 로직 (설명문 작성)"""
    score = 0
    feedback = []
    
    # 1. 괄호 안 설명 방법 추출
    method = ""
    if "(비교)" in user_ans:
        method = "비교"
    elif "(인과)" in user_ans:
        method = "인과"
    else:
        return 0, ["문장 끝에 사용할 설명 방법인 '(비교)' 또는 '(인과)'를 괄호 안에 표기해야 합니다."]

    # 공통 예외: 지문에 없는 외부 배경지식 사용 차단
    external_blocks = ["스마트폰", "게임", "유튜브", "돈", "성공"]
    if any(b in user_ans for b in external_blocks):
        return 0, ["오답(지문 외 지식 활용 불가): 지문에 없는 외부 개념을 사용하여 문장을 구성했습니다."]

    if method == "비교":
        # 필수 의미: 음식과 삶의 공통 속성 (맛을 다르게 느낌 = 경험을 다르게 받아들임, 혹은 천천히 음미해야 함)
        pass_keywords = ["음식", "맛", "살아가는", "삶", "경험", "비슷"]
        misconcept_blocks = ["차이", "다르다", "반면"] # 대조의 특성을 쓰면 오답
        
        if any(mis in user_ans for mis in misconcept_blocks):
            feedback.append("오답(오개념): '비교'를 선택했으나 차이점을 부각하는 대조의 특성을 사용했습니다.")
        elif any(k in user_ans for k in pass_keywords):
            score = 4
            feedback.append("정답입니다! 음식과 세상을 살아가는 일의 공통성을 바탕으로 '비교'의 문장을 잘 구성했습니다.")
        else:
            feedback.append("오답(키워드 부족): 음식과 삶의 공통적 특성(음미, 다채로움 등)이 문장에 드러나지 않습니다.")

    elif method == "인과":
        # 필수 원인-결과 구조 및 결론 방향 확인
        # 원인: 천천히 음미하지 않으면 / 빠르게 달리기만 하면
        # 결론 방향: 세상을 제대로 느낄 수 없다 / 아름다움을 포착할 수 없다
        cause_keywords = ["빠르게", "달리기만", "음미하지"]
        effect_keywords = ["포착할 수 없다", "느낄 수 없다", "제대로 느끼지 못"]
        
        if any(c in user_ans for c in cause_keywords) and any(e in user_ans for e in effect_keywords):
            score = 4
            feedback.append("정답입니다! '빠르게 달리기만 하면 아름다움을 느낄 수 없다'는 인과적 결론 방향이 완벽합니다.")
        else:
            feedback.append("오답(결론/인과 오류): 원인에 따른 부정적 결론 방향('제대로 느낄 수 없다')이 명확히 드러나지 않았습니다.")
            
    return score, feedback


# --- Streamlit UI 구성 ---
st.title("📝 중등 국어 서논술형 자동 채점 AI 시스템")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["[1세트] 사회적 촉진/억제", "[2세트] 정전기의 특징", "[3세트] 삶을 대하는 태도"])

# --- TAB 1: 1세트 채점 인터페이스 ---
with tab1:
    st.header("실전 적용-1: '사회적 촉진'과 '사회적 억제'")
    st.subheader("[문항 1] 요약 표 빈칸 채우기 (총 6점)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        ans_1_a = st.text_input("㉠ 입력 (과제의 특성):", placeholder="예: 비교적 쉬운 과제")
    with col2:
        ans_1_b = st.text_input("㉡ 입력 (효율적인 방법):", placeholder="예: 혼자 차분하게 집중함")
    with col3:
        ans_1_c = st.text_input("㉢ 입력 (관련 심리 현상):", placeholder="예: 사회적 억제")
        
    if st.button("1세트 문항1 채점하기"):
        scores, feedbacks = evaluate_set1_q1(ans_1_a, ans_1_b, ans_1_c)
        st.markdown("#### 📊 채점 결과")
        for i, key in enumerate(['㉠', '㉡', '㉢']):
            st.metric(label=f"빈칸 {key} 점수", value=f"{scores[i]} / 2점")
            if scores[i] == 2:
                st.success(feedbacks[i])
            else:
                st.error(feedbacks[i])

# --- TAB 3: 3세트 채점 인터페이스 (서술형 집중 구현) ---
with tab3:
    st.header("실전 적용-3: 음식을 맛보는 일과 세상을 살아가는 일")
    
    st.subheader("[문항 2] 조건에 맞는 설명문 작성 (4점 만점)")
    st.info("**[주어진 첫 문장]** 우리가 세상을 살아가는 데에는 다채로움을 온전히 느끼기 위한 올바른 태도가 필요하다.")
    
    st.markdown("""
    **⚠️ 작성 조건:**
    1. 지문에 제시된 내용만을 활용할 것 (외부 지식 활용 불가)
    2. 문장 끝에 자신이 사용한 설명 방법의 명칭을 괄호 `(비교)` 또는 `(인과)`로 표기할 것.
    """)
    
    # 모범 답안 아코디언 제공
    with st.expander("💡 선택지별 모범 답안 확인하기"):
        st.markdown("""
        * **선택지 1 (비교):** 음식의 맛을 천천히 음미하며 먹어야 하듯이, 세상을 살아갈 때도 모든 사람과 풍경을 천천히 음미하는 태도가 요구됩니다. **(비교)**
        * **선택지 2 (인과):** 만약 세상의 아름다움을 천천히 음미하지 않고 그냥 빠르게 달리기만 한다면, 세상을 제대로 포착하고 느낄 수 없습니다. **(인과)**
        """)
        
    user_description = st.text_area("이어질 문장 ㉮를 작성하세요:", height=100, placeholder="예: 만약 빠르게 달리기만 한다면 세상의 아름다움을 제대로 느낄 수 없습니다. (인과)")
    
    if st.button("3세트 문항2 채점하기"):
        if not user_description.strip():
            st.warning("답안을 입력해 주세요.")
        else:
            score, feedback = evaluate_set3_q2(user_description)
            st.markdown("#### 📊 채점 결과")
            st.metric(label="획득 점수", value=f"{score} / 4점")
            if score == 4:
                st.success(feedback[0])
            else:
                st.error(feedback[0])