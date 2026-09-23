import streamlit as st
from openai import OpenAI

# 1. 페이지 기본 설정 및 스타일링
st.set_page_config(
    page_title="🔍 AI 추리 게임: 방과 후의 비밀",
    page_icon="🏫",
    layout="wide"
)

# 다크 배경 + 드롭다운 선택창 및 펼쳐지는 목록 내부 글씨는 완전 검은색 적용
st.markdown("""
<style>
    /* 전체 앱 배경 */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF !important;
    }
    
    /* 일반 텍스트, 라벨, 헤더를 하얀색으로 통일 */
    p, span, label, div {
        color: #FFFFFF !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #FFFFFF !important;
    }

    /* selectbox 클릭 전 입력 상자 내부 글씨 - 검은색 */
    div[data-baseweb="select"] * {
        color: #000000 !important;
    }

    /* selectbox 클릭 후 아래로 펼쳐지는 드롭다운 팝업 목록 내부 전체 - 검은색 */
    ul[role="listbox"] * {
        color: #000000 !important;
    }
    div[data-baseweb="popover"] * {
        color: #000000 !important;
    }

    /* 채팅 입력창 내부 텍스트 - 검은색 */
    div[data-baseweb="input"] input {
        color: #000000 !important;
    }

    /* 메인 타이틀 */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FF4B4B !important;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 0px 0px 10px rgba(255, 75, 75, 0.3);
    }
    .sub-title {
        font-size: 1rem;
        color: #D1D5DB !important;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* 사건 개요 카드 */
    .info-card {
        background: linear-gradient(135deg, #1A1D24 0%, #14171D 100%);
        border-left: 5px solid #FFD700;
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    .card-header {
        color: #FFD700 !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 15px;
        border-bottom: 1px solid #2D323E;
        padding-bottom: 8px;
    }
    
    .info-card ul {
        margin: 0;
        padding-left: 20px;
    }
    .info-card li {
        color: #FFFFFF !important;
        font-size: 0.98rem;
        line-height: 1.7;
        margin-bottom: 8px;
    }
    
    /* 단서 배지 */
    .clue-badge {
        background-color: #2D3748;
        color: #FFD700 !important;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 6px;
        border: 1px solid #4A5568;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏫 CASE #017 : 둔산여고 방과 후의 비밀</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">용의자 학생들을 심문하고 진술의 모순을 찾아 진범을 밝혀내세요.</div>', unsafe_allow_html=True)

# 2. API 키 확인 및 OpenAI 클라이언트 초기화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("API 키를 찾을 수 없습니다. .streamlit/secrets.toml 설정을 확인해 주세요.")
    st.stop()

client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 3. 상단 배치: 피해자 정보 및 사건 현장 단서
st.markdown("### 📋 사건 개요 및 피해자 정보")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="info-card">
        <div class="card-header">👤 피해자 프로필: 김채원 (고등학교 2학년)</div>
        <ul>
            <li><b>신분:</b> 둔산여자고등학교 전교 1등이자 방송부 부장</li>
            <li><b>성격:</b> 완벽주의 성향이 강하고 원리원칙을 따짐. 타인에게 모진 소리를 잘해 주변에 적이 많았음.</li>
            <li><b>사건 발생 시각:</b> 금요일 방과 후 18:30 ~ 19:00 사이</li>
            <li><b>사건 현장:</b> 본관 4층 동아리실(방송실)</li>
            <li><b>사인:</b> 머리 뒤쪽 충격으로 인한 뇌출혈. 현장 근처에서 혈흔이 묻은 청동 트로피가 발견됨.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <div class="card-header">🔎 현장 수사 일지 및 단서</div>
        <ul>
            <li><span class="clue-badge">단서 1</span> <b>혈흔이 묻은 청동 트로피:</b> 방송실 진열대에서 꺼내진 상태로 바닥에 떨어져 있었음.</li>
            <li><span class="clue-badge">단서 2</span> <b>찢어진 USB 메모리 커버:</b> 방송부 컴퓨터에 꽂혀 있던 USB의 뚜껑이 바닥에 떨어져 있었음.</li>
            <li><span class="clue-badge">단서 3</span> <b>학생증 목걸이 줄:</b> 방송실 문고리에 누군가의 학생증 줄이 걸려있다 끊어진 흔적이 있음.</li>
            <li><span class="clue-badge">단서 4</span> <b>CCTV 기록:</b> 18:20 경 누군가 동아리실 건물로 들어가는 모습이 찍혔으나 우산을 쓰고 있어 얼굴이 안 보임.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 4. 용의자 정보 및 AI 페르소나 설정
suspect_profiles = {
    "설하은 (동급생, 전교 2등)": {
        "desc": "김채원에게 매번 전교 1등을 빼앗기며 극심한 스트레스를 받아옴. 김채원에게 모진 소리를 자주 들었음.",
        "prompt": (
            "너는 둔산여고 살인사건 용의자인 학생 '설하은'이야. "
            "성적이 매우 뛰어나지만 피해자 김채원 때문에 늘 2등에 머물렀어. "
            "말투는 차분하고 이성적이지만, 김채원 이야기만 나오면 날이 서. "
            "사건 당일 방과 후엔 독서실에 가느라 학교를 일찍 떠났다고 주장해."
        )
    },
    "박채원 (방송부 부부장)": {
        "desc": "김채원과 함께 방송부를 이끌던 인물. 김채원의 독단적인 동아리 운영과 모진 언행으로 큰 다툼이 있었음.",
        "prompt": (
            "너는 둔산여고 살인사건 용의자인 학생 '박채원'이야. "
            "김채원의 독단적인 동아리 운영 방식과 날카로운 언행에 불만이 많았어. "
            "다소 억울하다는 듯 목소리를 높이고 당황해하는 편이야. "
            "사건 당일 방과 후 방송실 청소를 마치고 18:10쯤 먼저 집에 갔다고 진술해."
        )
    },
    "김지아 (피해자의 절친)": {
        "desc": "김채원과 가장 친했던 친구. 최근 김채원이 약점을 잡고 모진 소리를 하며 괴롭혔다는 소문이 있음.",
        "prompt": (
            "너는 둔산여고 살인사건 용의자인 학생 '김지아'이자 실제 진범이야. "
            "김채원이 네 비밀을 빌미로 모진 소리를 하며 지속적으로 협박하자 충동적으로 사건을 일으켰어. "
            "질문을 받으면 조심스럽고 슬픈 척을 하지만, 범행 시각이나 단서(청동 트로피, USB, 끊어진 학생증)에 대해 집요하게 물어보면 말이 꼬이거나 당황해. "
            "절대 스스로 범인이라고 순순히 인정하지 마."
        )
    }
}

st.markdown("### 🎙️ 용의자 학생 심문실")

# 드롭다운 - 펼쳐지는 목록의 내부 글씨까지 모두 검은색으로 고정
selected_suspect = st.selectbox(
    "심문할 용의자 학생을 선택하세요:",
    list(suspect_profiles.keys())
)

# 선택된 용의자 프로필 요약 카드
st.info(f"📌 **학생 프로필 요약:** {suspect_profiles[selected_suspect]['desc']}")

# 용의자별 대화 세션 관리
session_key = f"detective_messages_{selected_suspect}"
if session_key not in st.session_state:
    st.session_state[session_key] = [
        {"role": "system", "content": suspect_profiles[selected_suspect]["prompt"]},
        {"role": "assistant", "content": f"선생님(탐정님), 저 진짜 아니에요... 제 말 좀 들어주세요."}
    ]

# 이전 대화 출력
for msg in st.session_state[session_key]:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 질문 입력 및 AI 응답
if prompt := st.chat_input(f"{selected_suspect.split(' ')[0]}에게 질문하기..."):
    st.session_state[session_key].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

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
            st.error("학생이 심문에 답하지 못하고 있습니다. 다시 시도해 주세요.")

# 5. 최종 범인 지목 섹션
st.divider()
st.markdown("### ⚖️ 최종 범인 지목")
st.caption("학생들의 진술과 사건 현장의 단서를 조합해 범인을 가려내세요.")

chosen_suspect = st.radio(
    "진범이라고 생각되는 학생을 선택하세요:",
    list(suspect_profiles.keys())
)

if st.button("🚔 범인으로 지목하기"):
    if "김지아" in chosen_suspect:
        st.balloons()
        st.success("""
        🎉 **정답입니다! 진범은 김지아였습니다!**  
        
        **[사건의 전말]**  
        김지아는 자신의 약점을 잡고 모진 소리를 퍼붓는 김채원과 방송실에서 다투다 USB를 빼앗으려 했습니다. 
        그 과정에서 문고리에 학생증 줄이 걸려 끊어졌고, 김채원이 경찰에 신고하려 하자 홧김에 옆에 있던 청동 트로피로 머리 뒤쪽을 가해했던 것입니다!
        """)
    else:
        st.error("""
        ❌ **오판입니다! 해당 학생은 범인이 아닙니다.**  
        
        잘못된 지목으로 진짜 범인이 증거를 인멸할 시간을 벌어주었습니다. 다시 심문하여 진술의 모순을 찾아내세요!
        """)
