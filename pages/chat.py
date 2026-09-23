import streamlit as st
from openai import OpenAI

# 페이지 제목 설정
st.title("❄️ 차가운 남자친구")
st.caption("필요한 말만 합니다. 잡담은 사절이에요.")

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
if "bf_messages" not in st.session_state:
    st.session_state.bf_messages = [
        {
            "role": "system",
            "content": (
                "너는 사용자(여자친구)에게 답장하는 남자친구야. "
                "성격은 지극히 냉정하고, 이성적이며, 감정 표현을 거의 하지 않고 툭툭 던지듯 말해. "
                "아양을 떨거나 다정하게 굴지 마. 말수가 적고 단답형으로 응답해. "
                "하지만 아주 미세하게 비쳐 보이는 현실적인 챙김(무심한 척 챙겨주는 태도)은 가끔 섞어도 돼. "
                "반말로 대화하고 문장은 길지 않게 핵심만 말해."
            )
        },
        {
            "role": "assistant",
            "content": "할 말 있어? 없으면 나 공부해야 돼."
        }
    ]

# 4. 이전 대화 기록 화면 출력 (시스템 프롬프트 제외)
for msg in st.session_state.bf_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. 사용자 입력 처리 및 AI 응답
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 화면 출력 및 세션 저장
    st.session_state.bf_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 출력
    with st.chat_message("assistant"):
        try:
            # Gemini 모델로 스트리밍 응답 요청
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.bf_messages,
                stream=True
            )
            
            # 실시간 글자 출력
            full_response = st.write_stream(response)
            
            # AI 응답 세션 저장
            st.session_state.bf_messages.append({"role": "assistant", "content": full_response})

        except Exception:
            st.error("잠시 연결이 원활하지 않네요. 나중에 다시 말하세요.")
