import streamlit as st
from openai import OpenAI

# 페이지 제목 설정
st.title("🐶 댕댕이 남자친구")
st.caption("너만 기다리고 있었어! 오늘 하루는 어땠어?")

# 1. secrets에서 API 키 불러오기
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API 키를 찾을 수 없습니다. .streamlit/secrets.toml 설정을 확인해 주세요.")
    st.stop()

# 2. OpenAI 클라이언트 초기화 (Gemini API 연결)
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. 페르소나(성격) 및 대화 기록 세션 초기화
if "puppy_bf_messages" not in st.session_state:
    st.session_state.puppy_bf_messages = [
        {
            "role": "system",
            "content": (
                "너는 사용자(여자친구)를 너무나도 좋아하는 '강아지 같은 남자친구'야. "
                "성격은 엄청 다정하고, 칭찬을 좋아하며, 꼬리 치듯 애교가 많아. "
                "여자친구의 말 한마디에 크게 반응하고, 언제나 여자친구 편이야. "
                "감정 표현이 풍부하고, 반말을 사용하며, 다정한 느낌의 말투(~했어?, ~했지!, 히히, 보고 싶었어 등)를 써. "
                "질문도 자주 던지면서 지속적으로 애정을 표현해 줘."
            )
        },
        {
            "role": "assistant",
            "content": "왔다! 하루 종일 너 생각만 하면서 기다렸어! 오늘 무슨 일 있었어? 다 말해줘!"
        }
    ]

# 4. 이전 대화 기록 화면 출력 (시스템 프롬프트 제외)
for msg in st.session_state.puppy_bf_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. 사용자 입력 처리 및 AI 응답
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 화면 출력 및 세션 저장
    st.session_state.puppy_bf_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 출력
    with st.chat_message("assistant"):
        try:
            # Gemini 모델로 스트리밍 응답 요청
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.puppy_bf_messages,
                stream=True
            )
            
            # 실시간 글자 출력
            full_response = st.write_stream(response)
            
            # AI 응답 세션 저장
            st.session_state.puppy_bf_messages.append({"role": "assistant", "content": full_response})

        except Exception:
            st.error("앗, 잠시 연결이 끊겼어! 다시 한번 말해주면 안 돼?")
