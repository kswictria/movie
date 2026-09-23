import streamlit as st
from openai import OpenAI

# 1. 페이지 기본 설정 및 다크 테마 커스텀 CSS
st.set_page_config(
    page_title="🕵️ AI 추리 게임: 저택의 하얀 독약",
    page_icon="🔍",
    layout="wide"
)

# 고급스러운 딥 다크 미스터리 스타일링
st.markdown("""
<style>
    /* 전체 배경 및 기본 글자색 설정 */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* 메인 타이틀 */
    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #FF4B4B;
        text-align: center;
        margin-bottom: 5px;
        text-shadow: 0px 0px 10px rgba(255, 75, 75, 0.3);
    }
    .sub-title {
        font-size: 1rem;
        color: #B0B3B8;
        text-align: center;
        margin-bottom: 30px;
    }
    
    /* 정보 카드 (피해자 프로필 & 사건 현장 단서) */
    .info-card {
        background: linear-gradient(135deg, #1A1D24 0%, #14171D 100%);
        border-left: 5px solid #FFD700;
        border-radius: 10px;
        padding: 22px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.5);
    }
    
    /* 정보 카드 내부 헤더 */
    .victim-header {
        color: #FFD700;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 15px;
        border-bottom: 1px solid #2D323E;
        padding-bottom: 8px;
    }
    
    /* 카드 내부 모든 본문 텍스트 - 완전한 하얀색 적용 */
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
    .info-card li b {
        color: #FFFFFF !important;
    }
    
    /* 단서 배지 */
    .clue-badge {
        background-color: #2D3748;
        color: #FFD700;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 6px;
        border: 1px solid #4A5568;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🕵️ CASE #042 : 저택의 하얀 독약</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">용의자들을 심문하고 모순을 찾아 진범을 밝혀내세요.</div>', unsafe_allow_html=True)

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

# 3. [상단 배치] 피해자(회장) 정보 및 사건 현장 수사 일지
st.markdown("### 📋 사건 개요 및 피해자 정보")

col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("""
    <div class="info-card">
        <div class="victim-header">👤 피해자 프로필: 한승주 회장 (68세)</div>
        <ul>
            <li><b>신분:</b> 글로벌 제약 기업 '한성바이오'의 창업주이자 회장</li>
            <li><b>성격:</b> 의심이 매우 많고 완벽주의 성향. 최근 누군가 자신을 해치려 한다는 환각 증세를 호소함.</li>
            <li><b>최근 동향:</b> 사망 당일 밤, 기존 유언장을 전면 수정하여 사회에 환원하겠다고 선언할 예정이었음.</li>
            <li><b>사망 시각:</b> 어젯밤 22:30 ~ 23:00 사이</li>
            <li><b>사원 및 사인:</b> 2층 개인 서재에서 독극물(신경독) 중독으로 사망. 마시다 남은 홍차 찻잔에서 독극물 성분 검출.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="info-card">
        <div class="victim-header">🔎 사건 현장 발견 단서</div>
        <ul>
            <li><span class="clue-badge">단서 1</span> <b>깨진 찻잔:</b> 회장의 책상 위에는 따뜻한 온기가 남은 홍차 잔이 깨져 있었음.</li>
            <li><span class="clue-badge">단서 2</span> <b>구겨진 수표:</b> 서재 바닥에서 거액의 액수가 적힌 수표 조각이 발견됨.</li>
            <li><span class="clue-badge">단서 3</span> <b>창틀의 흙자국:</b> 서재 창문 외부 난간에 누군가 밟고 지난 듯한 흙자국이 남아있음.</li>
            <li><span class="clue-badge">단서 4</span> <b>약통:</b> 수복용 약통이 비어 있었으나, 원래 회장이 먹던 약과는 색깔이 다름.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# 4. 용의자 프로필 및 페르소나 설정
suspect_profiles = {
    "집사 (김철수, 52세)": {
        "desc": "20년간 회장을 모신 최측근. 회장의 모든 비밀과 비자금을 알고 있음.",
        "prompt": (
            "너는 살인사건 용의자인 '집사 김철수'야. "
            "회장을 20년간 모셨고 정중하며 침착한 어조를 써. "
            "너는 회장의 비밀 장부를 숨기고 있어서 약간 머뭇거릴 때가 있어. "
            "사건 당일 밤 10시쯤 회장에게 홍차를 타줄 것을 가사도우미에게 지시했다고 주장해."
        )
    },
    "가사도우미 (이영희, 41세)": {
        "desc": "저택의 가사를 담당. 최근 사채 빚으로 심각한 경제적 어려움을 겪고 있음.",
        "prompt": (
            "너는 살인사건 용의자인 '가사도우미 이영희'야. "
            "질문을 받으면 조급하고 불안한 태도를 보여. "
            "사건 시각에 2층 복도를 청소 중이었다고 주장하지만, 홍차를 서재로 들고 간 인물이야. "
            "질문이 날카로워지면 말을 얼버무리거나 핑계를 대."
        )
    },
    "정원사 (박영수, 45세)": {
        "desc": "저택 정원을 관리함. 사건 당일 오후 회장과 돈 문제로 고성을 지르며 다툼.",
        "prompt": (
            "너는 살인사건 용의자인 '정원사 박영수'야. "
            "말투가 거칠고 무뚝뚝하며 억울함에 화가 나 있어. "
            "회장과 다툰 것은 인정하지만, 사건 시각엔 온실에서 화분을 정리하고 있었다고 주장해."
        )
    }
}

st.markdown("### 🎙️ 용의자 심문실")

selected_suspect = st.selectbox(
    "심문할 용의자를 선택하세요:",
    list(suspect_profiles.keys())
)

# 선택된 용의자 프로필 요약 카드
st.info(f"📌 **용의자 정보:** {suspect_profiles[selected_suspect]['desc']}")

# 용의자별 대화 세션 관리
session_key = f"detective_messages_{selected_suspect}"
if session_key not in st.session_state:
    st.session_state[session_key] = [
        {"role": "system", "content": suspect_profiles[selected_suspect]["prompt"]},
        {"role": "assistant", "content": f"탐정님, 할 말이 있으신가요? 저는 떳떳합니다."}
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
            st.error("용의자가 심문에 답하지 않고 있습니다. 다시 시도해 주세요.")

# 5. 최종 범인 지목 섹션
st.divider()
st.markdown("### ⚖️ 최종 범인 지목")
st.caption("심문을 통해 얻은 진술의 모순과 현장 단서를 조합하여 범인을 지목하세요.")

chosen_suspect = st.radio(
    "진범이라고 생각되는 용의자를 선택하세요:",
    list(suspect_profiles.keys())
)

if st.button("🚔 체포 영장 집행 (범인 지목)"):
    if "가사도우미" in chosen_suspect:
        st.balloons()
        st.success("""
        🎉 **정답입니다! 진범을 체포했습니다!**  
        
        **[사건의 전말]**  
        가사도우미 이영희는 사채 빚을 갚기 위해 회장의 서재에서 거액의 수표를 도둑질하려다 회장에게 들켰습니다. 
        당황한 그녀는 집사의 지시로 끓여온 홍차에 몰래 신경독을 탔고, 회장이 발작을 일으키며 찻잔을 깨뜨리자 수표 조각만 챙긴 채 서재를 빠져나왔던 것입니다!
        """)
    else:
        st.error("""
        ❌ **오판입니다! 해당 용의자는 범인이 아닙니다.**  
        
        당신의 잘못된 지목으로 진범이 증거를 인멸하고 저택을 유유히 빠져나갔습니다. 진술을 다시 확인해 보세요!
        """)
