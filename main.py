import requests
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


# ---------------------------------------------------------
# 1. 기본 화면 설정
# ---------------------------------------------------------

st.set_page_config(
    page_title="어제의 박스오피스",
    page_icon="🎬",
    layout="wide",
)

st.title("🎬 어제의 박스오피스")
st.caption("KOBIS 영화관입장권통합전산망의 일일 박스오피스 데이터를 보여줍니다.")


# ---------------------------------------------------------
# 2. 한국 시간 기준으로 '어제' 날짜 계산
# ---------------------------------------------------------
# 배포 서버가 어느 나라 시간대를 사용하더라도
# 한국 시간(Asia/Seoul)을 기준으로 날짜를 계산합니다.

KST = ZoneInfo("Asia/Seoul")
today_kst = datetime.now(KST).date()
yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API가 요구하는 날짜 형식: YYYYMMDD
target_date = yesterday_kst.strftime("%Y%m%d")

# 화면에 보여줄 날짜 형식
display_date = yesterday_kst.strftime("%Y년 %m월 %d일")


# ---------------------------------------------------------
# 3. KOBIS API 주소
# ---------------------------------------------------------

API_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest/boxoffice/"
    "searchDailyBoxOfficeList.json"
)


# ---------------------------------------------------------
# 4. KOBIS 인증키 가져오기
# ---------------------------------------------------------
# 인증키는 코드에 직접 적지 않습니다.
# Streamlit Cloud의 Secrets에 KOBIS_KEY를 등록해 두고 읽습니다.

try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]
except (KeyError, FileNotFoundError):
    st.error(
        "KOBIS 인증키를 찾을 수 없습니다.\n\n"
        "확인할 것:\n"
        "1. Streamlit Cloud의 앱 설정 → Secrets에 들어갑니다.\n"
        "2. KOBIS_KEY라는 이름으로 인증키를 등록했는지 확인합니다.\n"
        "3. 키 이름에 오타나 불필요한 공백이 없는지 확인합니다."
    )
    st.stop()


# ---------------------------------------------------------
# 5. KOBIS API 호출 함수
# ---------------------------------------------------------

def get_box_office(target_dt: str):
    """KOBIS 일일 박스오피스 데이터를 가져옵니다."""

    # API에 전달할 값입니다.
    params = {
        "key": KOBIS_KEY,
        "targetDt": target_dt,
    }

    try:
        # 외부 API가 너무 오래 응답하지 않는 경우를 대비해
        # 10초 후에는 요청을 중단합니다.
        response = requests.get(
            API_URL,
            params=params,
            timeout=10,
        )

        # HTTP 오류가 발생하면 예외를 발생시킵니다.
        response.raise_for_status()

        # JSON 형식으로 변환합니다.
        data = response.json()

    except requests.exceptions.Timeout:
        return None, (
            "KOBIS API 요청 시간이 초과되었습니다.\n\n"
            "확인할 것:\n"
            "- 잠시 후 다시 실행해 보세요.\n"
            "- KOBIS 서버 또는 네트워크 상태를 확인해 보세요."
        )

    except requests.exceptions.RequestException as e:
        return None, (
            "KOBIS API 요청에 실패했습니다.\n\n"
            f"오류 내용: {e}\n\n"
            "확인할 것:\n"
            "- 인터넷 연결 상태\n"
            "- KOBIS API 주소\n"
            "- KOBIS 서비스의 일시적인 장애 여부"
        )

    except ValueError:
        return None, (
            "KOBIS 서버의 응답을 JSON으로 읽을 수 없습니다.\n\n"
            "KOBIS API가 정상적인 응답을 보내고 있는지 확인해 주세요."
        )

    # -----------------------------------------------------
    # KOBIS는 인증키가 잘못되어도 HTTP 상태코드가 200일 수 있습니다.
    # 따라서 faultInfo가 있는지 반드시 확인합니다.
    # -----------------------------------------------------

    if "faultInfo" in data:
        fault_info = data["faultInfo"]

        # faultInfo의 구조가 달라질 가능성을 고려해
        # 가능한 값을 안전하게 가져옵니다.
        message = fault_info.get(
            "message",
            fault_info.get("errorMessage", "KOBIS API 오류가 발생했습니다."),
        )

        return None, (
            "KOBIS API에서 오류를 반환했습니다.\n\n"
            f"오류 내용: {message}\n\n"
            "확인할 것:\n"
            "- KOBIS_KEY가 정확한지 확인하세요.\n"
            "- KOBIS API 사용 권한과 발급 상태를 확인하세요.\n"
            "- targetDt가 올바른 날짜인지 확인하세요."
        )

    # 정상 응답인지 확인합니다.
    if "boxOfficeResult" not in data:
        return None, (
            "KOBIS 응답에 boxOfficeResult가 없습니다.\n\n"
            "KOBIS API 응답 형식이 예상과 다른 상태입니다."
        )

    result = data["boxOfficeResult"]

    # 영화 목록을 가져옵니다.
    movie_list = result.get("dailyBoxOfficeList", [])

    # 목록이 비어 있으면 사용자에게 확인할 내용을 알려줍니다.
    if not movie_list:
        return None, (
            f"{display_date}의 영화 목록이 비어 있습니다.\n\n"
            "확인할 것:\n"
            "- 해당 날짜의 KOBIS 일일 박스오피스가 집계되었는지 확인하세요.\n"
            "- 날짜가 한국 시간 기준으로 계산되었는지 확인하세요.\n"
            "- KOBIS 서비스의 일시적인 데이터 지연 여부를 확인하세요."
        )

    return movie_list, None


# ---------------------------------------------------------
# 6. API 데이터 가져오기
# ---------------------------------------------------------

movies, error_message = get_box_office(target_date)


# 오류가 발생했다면 빈 화면으로 끝내지 않고
# 사용자가 확인할 내용을 보여줍니다.
if error_message:
    st.error(error_message)

    with st.expander("현재 앱이 조회하려고 한 날짜 보기"):
        st.write(f"한국 시간 기준 오늘: {today_kst}")
        st.write(f"조회 대상 날짜: {display_date}")
        st.write(f"KOBIS targetDt: {target_date}")

    st.stop()


# ---------------------------------------------------------
# 7. 데이터프레임으로 변환
# ---------------------------------------------------------

df = pd.DataFrame(movies)


# 필요한 열이 실제로 들어왔는지 확인합니다.
required_columns = [
    "rank",
    "movieNm",
    "openDt",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        "KOBIS 응답에 필요한 데이터가 없습니다.\n\n"
        f"누락된 항목: {', '.join(missing_columns)}\n\n"
        "KOBIS API 응답 형식이나 서비스 상태를 확인해 주세요."
    )
    st.stop()


# ---------------------------------------------------------
# 8. 문자열로 온 숫자를 숫자형으로 변환
# ---------------------------------------------------------
# KOBIS API에서는 숫자도 문자열로 전달되므로
# 그래프와 숫자 표시를 위해 정수로 바꿉니다.

numeric_columns = [
    "rank",
    "audiCnt",
    "audiAcc",
    "scrnCnt",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    ).fillna(0).astype(int)


# 순위순으로 정렬합니다.
df = df.sort_values("rank").reset_index(drop=True)


# ---------------------------------------------------------
# 9. 제목과 조회 날짜 표시
# ---------------------------------------------------------

st.subheader(f"📅 {display_date} 일일 박스오피스")

st.caption(
    f"KOBIS 조회 날짜: {target_date} · "
    f"한국 시간 기준 '어제' 데이터"
)


# ---------------------------------------------------------
# 10. 1위 영화 지표 카드
# ---------------------------------------------------------

first_movie = df.iloc[0]

st.markdown("### 🏆 1위 영화")

st.markdown(
    f"## {first_movie['movieNm']}"
)

card1, card2, card3 = st.columns(3)

with card1:
    st.metric(
        label="어제 관객수",
        value=f"{first_movie['audiCnt']:,}명",
    )

with card2:
    st.metric(
        label="누적 관객수",
        value=f"{first_movie['audiAcc']:,}명",
    )

with card3:
    st.metric(
        label="스크린수",
        value=f"{first_movie['scrnCnt']:,}개",
    )


# ---------------------------------------------------------
# 11. 관객수 상위 5편 막대그래프
# ---------------------------------------------------------

st.markdown("### 📊 관객수 상위 5편")

top5 = (
    df.sort_values("audiCnt", ascending=False)
    .head(5)
    .copy()
)

# 영화명을 그래프의 인덱스로 사용합니다.
chart_data = top5.set_index("movieNm")[["audiCnt"]]

st.bar_chart(
    chart_data,
    x_label="영화",
    y_label="관객수",
)


# ---------------------------------------------------------
# 12. 전체 박스오피스 표
# ---------------------------------------------------------

st.markdown("### 🎞️ 전체 순위")

# 화면에 표시할 한국어 컬럼명을 만듭니다.
table_df = df[
    [
        "rank",
        "movieNm",
        "openDt",
        "audiCnt",
        "audiAcc",
        "scrnCnt",
    ]
].copy()

table_df.columns = [
    "순위",
    "영화명",
    "개봉일",
    "관객수",
    "누적관객",
    "스크린수",
]


# 숫자를 보기 편하게 천 단위 콤마로 표시합니다.
for column in ["관객수", "누적관객", "스크린수"]:
    table_df[column] = table_df[column].map(
        lambda value: f"{value:,}"
    )


st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
)


# ---------------------------------------------------------
# 13. 데이터 출처
# ---------------------------------------------------------

st.caption(
    "데이터 출처: 영화관입장권통합전산망(KOBIS) 일일 박스오피스 API"
)
