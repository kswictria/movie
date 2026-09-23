import streamlit as st
from openai import OpenAI

# 페이지 제목 설정
st.title("🔍 AI 추리 게임: 저택의 비밀")
st.caption("저택에서 일어난 의문의 살인사건! 범인을 찾아내세요.")

# 1. secrets에서 API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API 키를 찾을 수 없습니다. .streamlit/secrets.toml 설정을 확인해 주세요.")
    st.stop()

# 2. OpenAI 클라이언트 초기화
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. 게임 용어 및 기본 정보 안내
with st.expander("📌 사건 개요 및 규칙 (클릭하여 열기)", expanded=True):
    st.write("""
    **사건:** 지난 밤, 유명한 자산가 한 회장이 자신의 서재에서 독살된 채 발견되었습니다.  
    **용의자:** 
    1. **집사 (김철수):** 회장의 가장 가까운 조력자. 은근히 침착하지만 뭔가를 숨기는 듯합니다.
    2. **가사도우미 (이영희):** 사건 당일 서재 근처를 서성였습니다. 질문을 받으면 불안해합니다.
    3. **정원사 (박영수):** 최근 회장과 돈 문제로 다투었습니다. 말투가 무뚝뚝합니다.

    * **주의:** 진범은 **'가사도우미(이영희)'**입니다. 하지만 AI는 용의자로서 거짓말과 진실을 섞어 말하며 본인의 알리바이를 주장할 것입니다. 질문을 통해 모순을 찾으세요!
    """)

# 4. 용의자 선택
suspect = st.selectbox(
    "심문할 용의자를 선택하세요:",
    ["집사 (김철수)", "가사도우미 (이영희)", "정원사 (박영수)"]
)

# 용의자별 페르소나 설정
system_prompts = {
    "집사 (김철수)": (
        "너는 살인사건의 용의자인 '집사 김철수'야. "
        "너는 범인이 아니지만 회장의 비밀 장부를 숨기고 있어서 정직하게 다 말하진 못해. "
        "정중하고 침착한 어조를 유지해. 회장이 죽기 직전 차를 가져다주었다고 진술해."
    ),
    "가사도우미 (이영희)": (
        "너는 실제 범인인 '가사도우미 이영희'야. 너는 독약을 서재 찻잔에 넣었어. "
        "절대 자신이 범인임을 직접 인정하지 마. 질문을 받으면 매우 불안해하며, "
        "사건 시각에 청소를 하고 있었다고 거짓 알리바이를 대지만 유도신문을 당하면 말이 조금씩 꼬여."
    ),
    "정원사 (박영수)": (
        "너는 살인사건의 용의자인 '정원사 박영수'야. "
        "회장과 돈 문제로 싸운 적이 있어서 억울하게 누명을 쓸까 봐 화가 나 있어. "
        "무뚝뚝하고 거친 말투를 쓰지만, 사건 시각엔 온실에 있었다는 확실한 증거가 있어."
    )
}

# 5. 용의자별 독립된 세션 상태 초기화
session_key = f"detective_messages_{suspect}"
if session_key not in st.session_state:
    st.session_state[session_key] = [
        {"role": "system", "content": system_prompts[suspect]},
        {"role": "assistant", "content": f"안녕하세요, 탐정님. 저는 {suspect}입니다. 무엇이든 물어보십시오."}
    ]

# 6. 이전 대화 기록 화면 출력
for msg in st.session_state[session_key]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 7. 사용자 입력 및 AI 심문 응답
if prompt := st.chat_input(f"{suspect}에게 질문하기..."):
    # 사용자 질문 저장 및 출력
    st.session_state[session_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 용의자 응답 생성
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state[session_key],
                stream=True
            )
            
            full_response = st.write_stream(response)
            st.session_state[session_key].append({"role": "assistant", "content": full_response})

        except Exception:
            st.error("용의자가 심문에 응하지 않고 있습니다. 잠시 후 다시 질문해 주세요.")

# 8. 범인 지목 및 하단 피날레 버튼
st.divider()
st.subheader("⚖️ 범인 지목하기")
chosen_suspect = st.radio("범인이라고 생각하는 사람을 선택하세요:", ["집사 (김철수)", "가사도우미 (이영희)", "정원사 (박영수)"])

if st.button("범인으로 지목하기"):
    if "가사도우미" in chosen_suspect:
        st.balloons()
        st.success("🎉 정답입니다! 가사도우미 이영희가 범인입니다! 그녀의 거짓 알리바이를 간파하셨군요.")
    else:
        st.error("❌ 틀렸습니다! 진짜 범인은 유유히 저택을 빠져나갔습니다. 다시 심문해 보세요!")
