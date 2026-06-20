import streamlit as st

st.set_page_config(page_title="서논술형 자동 채점 시스템", layout="wide")

# --- 세션 상태(Session State) 초기화 ---
if "wrong_questions" not in st.session_state:
    st.session_state.wrong_questions = {}

# --- 안내 문구 및 우측 정렬 초기화 버튼 한 줄 배치 (프롬프트 13 반영) ---
col_text, col_btn = st.columns([7, 1])
with col_text:
    st.write("모든 문제를 제출하면 복습할 내용 탭에서 틀린 개념을 확인할 수 있어요. 답안을 초기화하고 처음부터 다시 풀고 싶다면 다음의 버튼을 누르세요.")
with col_btn:
    st.markdown('<div style="text-align: right; margin-top: -5px;">', unsafe_value_allowed=True)
    if st.button("처음부터 다시 풀기", key="reset_all_btn", help="모든 입력과 오답 노트를 초기화합니다."):
        st.session_state.wrong_questions = {}
        st.rerun()
    st.markdown('</div>', unsafe_value_allowed=True)

st.markdown("---")

# --- 채점 핵심 로직 함수 정의 (프롬프트 6, 7, 8, 9 반영) ---
def evaluate_set3_q2(user_ans):
    if not user_ans.strip():
        return 0, "답안이 입력되지 않았습니다."
    
    if "(비교)" in user_ans: method = "비교"
    elif "(인과)" in user_ans: method = "인과"
    else: return 0, "문장 끝에 사용할 설명 방법인 (비교) 또는 (인과)를 괄호 안에 표기해야 합니다."

    if any(b in user_ans for b in ["스마트폰", "게임", "유튜브"]):
        return 0, "오답(지문 외 지식 활용 불가): 지문에 없는 외부 개념을 사용하여 문장을 구성했습니다."

    if method == "비교":
        # 프롬프트 6 반영: 타 개념의 특성(인과 결론, 대조 차이점) 기술 시 오답
        if any(mis in user_ans for mis in ["차이", "다르다", "반면", "달리기만 하면", "포착할 수 없다", "느낄 수 없다"]):
            return 0, "오답(오개념 발견): 비교를 선택했으나, 인과의 결론이나 대조의 특성을 혼용하여 서술했습니다."
        if any(k in user_ans for k in ["음식", "맛", "살아가는", "삶", "경험", "비슷", "음미"]):
            return 4, "정답입니다! 음식과 세상을 살아가는 일의 공통 속성을 바탕으로 비교의 문장을 올바르게 구성했습니다."
        return 0, "오답(키워드 부족): 음식과 삶의 공통적 특성이 문장에 드러나지 않습니다."

    elif method == "인과":
        # 프롬프트 7 반영: 발생 조건 불일치(긍정 상황 우회) 오답 차단
        if any(pos in user_ans for pos in ["음미하면", "천천히 살면", "느낄 수 있다"]) and not any(neg in user_ans for neg in ["없다", "못한다"]):
            return 0, "오답(조건 미충족): 이 개념은 부정적 상황에서 발생하는 현상입니다. 발생 조건이 맞지 않는 긍정적 상황을 서술하여 오답 처리되었습니다."
        # 프롬프트 8 반영: 조건에서 요구한 결론이 빠진 경우 오답 차단
        if not any(rc in user_ans for rc in ["포착할 수 없다", "느낄 수 없다", "제대로 느끼지 못"]):
            return 0, "오답(결론 누락): 개념에 대한 원인만 설명되어 있고, 조건에서 요구한 최종 결론(아름다움을 포착하거나 느낄 수 없다)이 명확히 드러나지 않았습니다."
        if any(c in user_ans for c in ["빠르게", "달리기만", "음미하지"]):
            return 4, "정답입니다! 개념 발생 조건과 그에 따른 최종 결론의 방향성이 명확하게 서술되었습니다."
        return 0, "오답(원인 누락): 인과의 결과는 있으나 올바른 발생 조건이 문장에 명시되지 않았습니다."

def evaluate_set3_q3(elem_a_plan, elem_b_effect, mode="visual"):
    # 프롬프트 9 반영: 요소 A에 필수 내용 검증
    if not any(rc in elem_a_plan for rc in ["천천히", "느리게", "멈추", "여유", "슬로우", "잔잔", "고요"]):
        return 0, "오답(요소 A 조건 미충족): 연출 계획에 천천히 음미하는 삶을 표현하기 위해 필요한 핵심 내용이 누락되었습니다."

    # 프롬프트 9 반영: 요소 A와 요소 B의 실질적 연결성(감각 도메인 미스매치) 차단
    if mode == "visual":
        if any(mk in elem_b_effect for mk in ["듣다", "소리", "음악", "멜로디"]) and not any(vk in elem_b_effect for vk in ["보다", "화면", "시각"]):
            return 0, "오답(논리적 연결 오류): 요소 A는 시각 연출인데, 요소 B(효과)에는 청각적 특성만 서술하여 실질적으로 연결되지 않습니다."
        if not any(k in elem_b_effect for k in ["시각", "화면", "부각", "강조", "보여", "전달"]):
            return 0, "오답(요소 B 오류): 연출 계획이 지문의 핵심 내용을 어떻게 시각적으로 전달하는지 명확히 서술되지 않았습니다."
    elif mode == "auditory":
        if any(mk in elem_b_effect for mk in ["보다", "화면", "시각", "표정"]) and not any(ak in elem_b_effect for ak in ["듣다", "소리", "음악", "멜로디"]):
            return 0, "오답(논리적 연결 오류): 요소 A는 청각 연출인데, 요소 B(효과)에는 시각적 특성만 서술하여 실질적으로 연결되지 않습니다."
        if not any(k in elem_b_effect for k in ["청각", "소리", "음악", "대비", "강조", "들려", "전달"]):
            return 0, "오답(요소 B 오류): 연출 계획이 지문의 핵심 내용을 어떻게 청각적으로 강조하는지 명확히 서술되지 않았습니다."
    return 2, "정답입니다!"

# --- 화면 레이아웃 구성 (프롬프트 10, 11, 12 반영) ---
tab_q, tab_review = st.tabs(["📝 실전 연습 문항", "🔄 복습할 내용"])

with tab_q:
    # 프롬프트 10 반영: 자료는 파란 상자 안에 배치
    st.markdown("""
    <div style="border: 2px solid #2B6CB0; background-color: #EBF8FF; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
        <strong>[지문]</strong><br><br>
        기자: 우리가 세상을 살아가는 방식을 음식에 비유하여 설명해 주신다고 들었습니다. 이 둘은 어떤 점이 비슷한가요?<br>
        전문가: 네, 음식을 맛보는 일은 사는 일과 비슷합니다. 둘 다 사람에 따라 달라질 수 있지요. 사람마다 같은 음식을 먹어도 맛을 다르게 느끼듯, 같은 경험을 해도 다른 감정으로 받아들일 수 있으니까요.<br>
        기자: 사람마다 받아들이는 방식이 다르다는 뜻이군요. 또 다른 공통점이 있을까요?<br>
        전문가: 네, 바로 천천히 음미하는 시간이 필요하다는 점에서도 비슷합니다. 음식을 먹을 때 마구 삼켜서는 맛을 제대로 느낄 수 없죠. 천천히 음미하며 먹어야 맛의 다채로움을 느낄 수 있습니다.<br>
        기자: 우리가 사는 세상의 다채로움을 느끼는 것도 이와 같다는 말씀이시군요.<br>
        전문가: 맞습니다. 모든 사람과 풍경, 그 속의 아름다움을 천천히 음미해야 세상을 제대로 느낄 수 있어요. 그냥 빠르게 달리기만 해서는 이들을 포착하고 느낄 수 없답니다.
    </div>
    """, unsafe_value_allowed=True)

    # 프롬프트 11 반영: 발문 바로 아래 입력란 배치 (라벨 숨김 및 안내 문구 삭제)
    st.write("문항 2. 윗글을 활용하여 삶을 대하는 올바른 태도에 대한 설명문을 작성하려 한다. 주어진 첫 문장에 이어지는 내용인 ㉮를 조건에 맞추어 작성하시오.")
    st.write("우리가 세상을 살아가는 데에는 다채로움을 온전히 느끼기 위한 올바른 태도가 필요하다.")
    
    # 프롬프트 10 반영: 조건은 회색 박스에 담고 중요 이모지 장착
    st.markdown("""
    <div style="border: 1px solid #CBD5E0; background-color: #F7FAFC; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        🚨 서로 다른 2가지의 설명 방법을 사용하여, 주어진 문장에 이어지는 문장을 하나 작성할 것.<br>
        🚨 윗글에 제시된 내용만을 활용하여 문장을 구성할 것. 지문에 없는 외부 배경지식을 활용할 경우 인정하지 않음.<br>
        🚨 문장의 끝에 자신이 사용한 설명 방법의 명칭을 괄호에 넣어 표기할 것.
    </div>
    """, unsafe_value_allowed=True)
    
    user_q2 = st.text_area(label="문항 2 답안란", label_visibility="collapsed", placeholder="여기에 문항 2 답안을 입력하세요 (예: ... (인과))", key="q2_in")
    
    if st.button("문항 2 제출 및 채점"):
        sc2, fb2 = evaluate_set3_q2(user_q2)
        st.metric("문항 2 점수", f"{sc2} / 4")
        if sc2 == 4:
            st.success(fb2)
            if "문항 2" in st.session_state.wrong_questions: del st.session_state.wrong_questions["문항 2"]
        else:
            st.error(fb2)
            st.session_state.wrong_questions["문항 2"] = {
                "title": "3세트 문항 2: 조건부 설명문 작성", "my_answer": user_q2 if user_q2.strip() else "미제출", "reason": fb2,
                "point": "비교 방법을 쓸 때는 대상 간의 공통점만 명시해야 하며 차이점이나 결과를 섞으면 안 됩니다. 인과 방법을 쓸 때는 반드시 발생 조건(빠르게 달리기만 함)과 최종 결론(아름다움을 포착할 수 없다)이 모두 인과적 서술어로 끝나야 합니다."
            }

    st.markdown("---")
    
    st.write("문항 3. 윗글을 바탕으로 삶을 대하는 올바른 태도를 설명하는 영상을 제작하려 한다. 다음 기획안을 보고 장면 2에 들어갈 연출 계획과 효과를 서술하시오.")
    
    st.markdown("""
    <div style="border: 2px solid #2B6CB0; background-color: #EBF8FF; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        <strong>[영상 기획안 내용 일부]</strong><br>
        장면 2: 천천히 음미하는 삶<br>
        - 시각 요소: A<br>
        - 청각 요소: B
    </div>
    """, unsafe_color_conversion=True, unsafe_value_allowed=True)

    st.markdown("""
    <div style="border: 1px solid #CBD5E0; background-color: #F7FAFC; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
        🚨 윗글을 참고하여 천천히 음미하는 삶의 특성이 잘 드러나도록 A와 B에 들어갈 연출 계획을 세울 것.<br>
        🚨 자신이 설정한 시각 및 청각 요소가 글의 내용을 전달하는 데 어떤 효과가 있는지 각각 서술할 것.
    </div>
    """, unsafe_value_allowed=True)

    col_v, col_a = st.columns(2)
    with col_v:
        st.write("(1) 시각 요소 A 연출 계획 및 효과 작성")
        vis_a = st.text_input("계획 입력", label_visibility="collapsed", placeholder="시각 요소 연출 계획 [요소 A]", key="v_a")
        vis_b = st.text_input("효과 입력", label_visibility="collapsed", placeholder="시각 요소 연출 효과 [요소 B]", key="v_b")
        if st.button("시각 요소 제출"):
            v_sc, v_fb = evaluate_set3_q3(vis_a, vis_b, mode="visual")
            st.metric("시각 점수", f"{v_sc} / 2")
            if v_sc == 2:
                st.success(v_fb)
                if "시각" in st.session_state.wrong_questions: del st.session_state.wrong_questions["시각"]
            else:
                st.error(v_fb)
                st.session_state.wrong_questions["시각"] = {
                    "title": "3세트 문항 3: 시각 매체 연출 및 효과", "my_answer": f"계획: {vis_a} / 효과: {vis_b}", "reason": v_fb,
                    "point": "시각 연출 계획에는 세상을 천천히 음미하는 구체적 장면(느린 화면, 멈춤 등)이 들어가야 합니다. 또한 시각 효과에는 청각적 표현(음악, 소리 등)을 연결하는 논리적 오류를 범하지 않아야 합니다."
                }
                
    with col_a:
        st.write("(2) 청각 요소 B 연출 계획 및 효과 작성")
        aud_a = st.text_input("청각 계획 입력", label_visibility="collapsed", placeholder="청각 요소 연출 계획 [요소 A]", key="a_a")
        aud_b = st.text_input("청각 효과 입력", label_visibility="collapsed", placeholder="청각 요소 연출 효과 [요소 B]", key="a_b")
        if st.button("청각 요소 제출"):
            a_sc, a_fb = evaluate_set3_q3(aud_a, aud_b, mode="auditory")
            st.metric("청각 점수", f"{a_sc} / 2")
            if a_sc == 2:
                st.success(a_fb)
                if "청각" in st.session_state.wrong_questions: del st.session_state.wrong_questions["청각"]
            else:
                st.error(a_fb)
                st.session_state.wrong_questions["청각"] = {
                    "title": "3세트 문항 3: 청각 매체 연출 및 효과", "my_answer": f"계획: {aud_a} / 효과: {aud_b}", "reason": a_fb,
                    "point": "청각 연출 계획에는 여유를 줄 수 있는 소리(잔잔한 음악, 자연의 소리 등)가 적혀야 합니다. 연출 효과 역시 청각 도메인 내에서 주제 부각 효과로 매끄럽게 연결되어야 합니다."
                }

# --- 🔄 복습할 내용 탭 (프롬프트 12 반영) ---
with tab_review:
    st.header("🔄 맞춤형 오답 노트 및 핵심 복습 포인트")
    
    if not st.session_state.wrong_questions:
        st.balloons()
        st.success("🎉 현재 조건을 충족하지 못한 문제가 없습니다! 완벽합니다.")
    else:
        for q_key, q_info in list(st.session_state.wrong_questions.items()):
            with st.expander(f"❌ {q_info['title']}", expanded=True):
                st.markdown(f"""
                <div style="border: 2px solid #2B6CB0; background-color: #EBF8FF; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                    <strong>내가 제출한 답안</strong><br>
                    {q_info['my_answer']}
                </div>
                """, unsafe_value_allowed=True)
                
                st.write("내 답안의 부족한 부분:")
                st.warning(q_info['reason'])
                
                st.markdown(f"""
                <div style="border: 1px solid #CBD5E0; background-color: #F7FAFC; padding: 15px; border-radius: 5px; margin-top: 10px;">
                    🚨 <strong>감점 방지 핵심 복습 포인트</strong><br><br>
                    📌 {q_info['point']}
                </div>
                """, unsafe_value_allowed=True)
