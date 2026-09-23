import streamlit as st
from openai import OpenAI

# 페이지 제목 설정
st.title("💬 친절한 정보 선생님 AI")
st.caption("궁금한 점이 있다면 무엇이든 물어보세요!")

# 1. secrets에서 API 키 가져오기
# .streamlit/secrets.toml 파일의 GEMINI_API_KEY를 불러옵니다.
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API 키를 찾을 수 없습니다. .streamlit/secrets.toml 파일에 GEMINI_API_KEY를 설정해 주세요.")
    st.stop()

# 2. OpenAI 클라이언트 초기화 (Gemini 엔드포인트 연결)
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. 세션 상태(Session State)를 활용한 대화 기록 관리
# 앱이 새로고침되어도 이전 대화 내용이 사라지지 않도록 st.session_state에 저장합니다.
if "messages" not in st.session_state:
    # 최초 접속 시 AI의 역할(System Prompt)과 기본 인사말을 설정합니다.
    st.session_state.messages = [
        {
            "role": "system",
            "content": "너는 중고등학생에게 설명하는 친절한 정보 선생님이야. 어려운 말은 쉬운 말로 바꿔 주고, 반드시 순수 한국어로만 답해"
        },
        {
            "role": "assistant",
            "content": "안녕하세요! 궁금한 점이 있으면 언제든 편하게 물어보세요. 쉬운 말로 친절하게 설명해 드릴게요!"
        }
    ]

# 4. 이전 대화 목록을 화면에 말풍선 형태로 표시
# system 메시지는 화면에 띄우지 않고, user와 assistant 메시지만 표시합니다.
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 5. 사용자 입력창 생성 및 처리
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자가 입력한 메시지를 대화 기록에 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 사용자가 입력한 메시지를 화면의 채팅 말풍선으로 출력
    with st.chat_message("user"):
        st.markdown(prompt)

    # AI 응답 생성
    with st.chat_message("assistant"):
        try:
            # Gemini 모델에 지금까지의 대화 기록 전체를 전달하여 답변 생성 (스트리밍 옵션 포함)
            response = client.chat.completions.create(
                model="gemini-3.5-flash-lite",
                messages=st.session_state.messages,
                stream=True
            )
            
            # 실시간으로 글자가 흘러나오도록 st.write_stream 활용
            full_response = st.write_stream(response)
            
            # AI 답변을 대화 기록에 추가
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception:
            # API 요청 실패 등 에러 발생 시 한국어 안내 문구 표시
            error_message = "오류가 발생하여 답변을 생성하지 못했습니다. 잠시 후 다시 시도해 주세요."
            st.error(error_message)
