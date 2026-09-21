import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests
import streamlit as st


# ============================================================
# 1. 기본 화면 설정
# ============================================================

st.set_page_config(
    page_title="오늘 뭐 볼까?",
    page_icon="🎬",
    layout="centered",
)


# ============================================================
# 2. KOBIS API 설정
# ============================================================
# 중요:
# 인증키를 코드에 직접 적지 않습니다.
#
# Streamlit Cloud의 Settings → Secrets에
# 아래처럼 등록하세요.
#
# KOBIS_KEY = "실제_인증키"
#
# 코드에서는 st.secrets를 통해 가져옵니다.


try:
    KOBIS_KEY = st.secrets["KOBIS_KEY"]

except (KeyError, FileNotFoundError):

    st.error(
        """
        KOBIS 인증키를 찾을 수 없습니다.

        Streamlit Cloud에서 다음을 확인해 주세요.

        1. 앱의 Settings로 이동
        2. Secrets 메뉴 선택
        3. 아래 형식으로 등록

        KOBIS_KEY = "발급받은 인증키"

        4. 저장 후 앱을 다시 실행

        인증키는 main.py 코드에 직접 넣지 마세요.
        """
    )

    st.stop()


# KOBIS Open API 기본 주소
KOBIS_BASE_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest"
)


# ============================================================
# 3. 한국 시간 설정
# ============================================================
# Streamlit Cloud 서버가 한국 시간이 아닐 수 있기 때문에
# 반드시 Asia/Seoul을 지정합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()

# 사용자가 영화를 추천받는 기준 날짜입니다.
# 오늘 데이터가 아직 완전히 집계되지 않았을 수 있으므로
# 반드시 '어제'를 사용합니다.
yesterday_kst = today_kst - timedelta(days=1)

# KOBIS API가 요구하는 YYYYMMDD 형식
YESTERDAY_STRING = yesterday_kst.strftime("%Y%m%d")

# 화면 표시용
YESTERDAY_DISPLAY = yesterday_kst.strftime(
    "%Y년 %m월 %d일"
)


# ============================================================
# 4. 질문 데이터
# ============================================================
# 각 답변에는 추천 알고리즘에서 사용할 점수가 들어갑니다.
#
# 장르:
# action, comedy, romance, drama,
# thriller, fantasy, adventure
#
# 취향:
# popularity = 대중적인 영화 선호
# classic = 오래된/검증된 작품 선호
# recent = 최신 영화 선호
# exploration = 새로운 영화 탐험 성향
# long_movie = 긴 영화 선호
#
# 국가:
# korea, foreign, asia, europe, country_free


QUESTIONS = [

    # --------------------------------------------------------
    # 질문 1
    # --------------------------------------------------------

    {
        "question": "지금 가장 보고 싶은 영화는?",

        "options": [

            (
                "💥 숨 막히는 액션과 긴장감",
                {
                    "action": 3,
                    "thriller": 1,
                },
            ),

            (
                "😂 아무 생각 없이 실컷 웃는 영화",
                {
                    "comedy": 3,
                },
            ),

            (
                "❤️ 사람 사이의 관계와 감정",
                {
                    "romance": 3,
                    "drama": 1,
                },
            ),

            (
                "😱 무슨 일이 벌어질지 모르는 영화",
                {
                    "thriller": 3,
                },
            ),

            (
                "🪐 현실에서 벗어난 새로운 세계",
                {
                    "fantasy": 3,
                    "adventure": 2,
                },
            ),

            (
                "🎭 사람의 심리를 깊게 들여다보는 영화",
                {
                    "drama": 3,
                },
            ),

            (
                "🌿 마음이 편안해지는 영화",
                {
                    "drama": 2,
                    "comedy": 1,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 2
    # --------------------------------------------------------

    {
        "question": "영화에서 가장 중요한 것은?",

        "options": [

            (
                "📖 탄탄한 스토리",
                {
                    "drama": 2,
                },
            ),

            (
                "🎭 배우들의 연기",
                {
                    "drama": 2,
                },
            ),

            (
                "⚡ 계속되는 긴장감",
                {
                    "thriller": 2,
                    "action": 1,
                },
            ),

            (
                "✨ 눈을 사로잡는 볼거리",
                {
                    "action": 1,
                    "fantasy": 1,
                },
            ),

            (
                "🤣 웃음",
                {
                    "comedy": 2,
                },
            ),

            (
                "💗 설레는 감정",
                {
                    "romance": 2,
                },
            ),

            (
                "🧠 보고 나서 생각할 거리",
                {
                    "drama": 2,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 3
    # --------------------------------------------------------

    {
        "question": "친구가 '요즘 엄청 인기 있는 영화'라고 추천한다면?",

        "options": [

            (
                "🔥 인기 있는 데는 이유가 있지! 바로 본다.",
                {
                    "popularity": 4,
                },
            ),

            (
                "🙂 재미있다면 보고 싶다.",
                {
                    "popularity": 2,
                },
            ),

            (
                "🤔 인기보다는 내 취향이 중요하다.",
                {
                    "popularity": 0,
                },
            ),

            (
                "👀 오히려 사람들이 잘 모르는 영화가 궁금하다.",
                {
                    "popularity": -2,
                    "exploration": 2,
                },
            ),

            (
                "🕵️ 숨은 영화를 발견하는 게 더 좋다.",
                {
                    "popularity": -4,
                    "exploration": 4,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 4
    # --------------------------------------------------------

    {
        "question": "영화를 고를 때 어느 쪽에 더 가까운가요?",

        "options": [

            (
                "🍿 요즘 가장 화제인 영화를 보고 싶다.",
                {
                    "recent": 4,
                    "popularity": 2,
                },
            ),

            (
                "🎬 흥행도 하고 좋은 평가를 받은 영화가 좋다.",
                {
                    "popularity": 2,
                    "classic": 1,
                },
            ),

            (
                "🏆 시간이 지나도 기억되는 영화를 보고 싶다.",
                {
                    "classic": 4,
                },
            ),

            (
                "🎞️ 오래된 영화라도 좋은 작품이면 본다.",
                {
                    "classic": 4,
                    "recent": -1,
                },
            ),

            (
                "🔎 유명하지 않아도 영화적으로 의미 있는 작품을 찾는다.",
                {
                    "classic": 2,
                    "popularity": -2,
                    "exploration": 2,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 5
    # --------------------------------------------------------

    {
        "question": "평소 보지 않던 장르의 영화가 눈에 띈다면?",

        "options": [

            (
                "🎯 익숙한 장르가 아니면 잘 안 본다.",
                {
                    "exploration": 0,
                },
            ),

            (
                "👍 평소 좋아하는 장르라면 새로운 영화도 본다.",
                {
                    "exploration": 1,
                },
            ),

            (
                "🤔 예고편이 재미있으면 도전한다.",
                {
                    "exploration": 2,
                },
            ),

            (
                "🧭 평소 안 보던 장르도 가끔 도전한다.",
                {
                    "exploration": 3,
                },
            ),

            (
                "🚀 새로운 장르를 적극적으로 찾아본다.",
                {
                    "exploration": 4,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 6
    # --------------------------------------------------------

    {
        "question": "영화 추천을 받는다면 어느 쪽이 더 좋은가요?",

        "options": [

            (
                "🎯 내가 좋아할 가능성이 높은 영화만 추천해줘.",
                {
                    "exploration": 0,
                },
            ),

            (
                "🙂 대부분 취향에 맞는 영화면 좋겠어.",
                {
                    "exploration": 1,
                },
            ),

            (
                "🎲 한 편 정도는 의외의 영화도 좋아.",
                {
                    "exploration": 2,
                },
            ),

            (
                "🧭 새로운 영화도 섞어줘.",
                {
                    "exploration": 3,
                },
            ),

            (
                "🚀 내가 몰랐던 영화를 발견하고 싶어.",
                {
                    "exploration": 4,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 7
    # --------------------------------------------------------

    {
        "question": "2시간 30분짜리 영화라면?",

        "options": [

            (
                "😎 재미있으면 길이는 상관없다.",
                {
                    "long_movie": 3,
                },
            ),

            (
                "🙂 조금 길어도 괜찮다.",
                {
                    "long_movie": 2,
                },
            ),

            (
                "😐 2시간 정도가 가장 좋다.",
                {
                    "long_movie": 1,
                },
            ),

            (
                "🥱 긴 영화는 조금 부담스럽다.",
                {
                    "long_movie": -1,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 8
    # --------------------------------------------------------

    {
        "question": "어떤 영화에 더 끌리나요?",

        "options": [

            (
                "🇰🇷 한국 영화",
                {
                    "korea": 3,
                },
            ),

            (
                "🌎 미국 등 영어권 영화",
                {
                    "foreign": 3,
                },
            ),

            (
                "🇯🇵 일본 등 아시아 영화",
                {
                    "asia": 3,
                },
            ),

            (
                "🇪🇺 유럽 영화",
                {
                    "europe": 3,
                },
            ),

            (
                "🎲 나라보다는 재미가 중요하다.",
                {
                    "country_free": 3,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 9
    # --------------------------------------------------------

    {
        "question": "영화의 개봉 시기는 얼마나 중요한가요?",

        "options": [

            (
                "🆕 무조건 최신작!",
                {
                    "recent": 4,
                },
            ),

            (
                "📅 최근 몇 년 안의 영화가 좋다.",
                {
                    "recent": 3,
                },
            ),

            (
                "🎬 언제 만들어졌는지는 별로 중요하지 않다.",
                {
                    "recent": 1,
                    "classic": 1,
                },
            ),

            (
                "🕰️ 오래된 영화도 좋은 작품이면 본다.",
                {
                    "classic": 3,
                },
            ),

            (
                "📼 고전영화를 찾아보는 것도 좋아한다.",
                {
                    "classic": 4,
                },
            ),
        ],
    },


    # --------------------------------------------------------
    # 질문 10
    # --------------------------------------------------------

    {
        "question": "오늘 영화를 보는 가장 큰 이유는?",

        "options": [

            (
                "😂 그냥 웃고 싶어서",
                {
                    "comedy": 3,
                },
            ),

            (
                "😭 감정을 제대로 느끼고 싶어서",
                {
                    "drama": 3,
                },
            ),

            (
                "🧠 생각할 거리가 필요해서",
                {
                    "drama": 3,
                },
            ),

            (
                "😱 긴장감을 느끼고 싶어서",
                {
                    "thriller": 3,
                },
            ),

            (
                "🥰 설레고 싶어서",
                {
                    "romance": 3,
                },
            ),

            (
                "🌿 아무 생각 없이 쉬고 싶어서",
                {
                    "comedy": 1,
                    "drama": 1,
                },
            ),

            (
                "🚀 현실에서 잠깐 벗어나고 싶어서",
                {
                    "fantasy": 3,
                    "adventure": 2,
                },
            ),
        ],
    },
]


# ============================================================
# 5. KOBIS API 공통 호출 함수
# ============================================================

def kobis_get(endpoint, params):
    """
    KOBIS API를 호출하는 공통 함수입니다.

    KOBIS는 인증키가 잘못되어도 HTTP 200을 반환하고
    faultInfo를 보내는 경우가 있기 때문에
    HTTP 상태코드만으로 성공 여부를 판단하지 않습니다.
    """

    url = f"{KOBIS_BASE_URL}/{endpoint}"

    request_params = {
        "key": KOBIS_KEY,
        **params,
    }

    try:

        response = requests.get(
            url,
            params=request_params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.Timeout:

        return (
            None,
            "KOBIS API 요청 시간이 초과되었습니다.",
        )

    except requests.exceptions.RequestException as error:

        return (
            None,
            f"KOBIS API 요청에 실패했습니다: {error}",
        )

    except ValueError:

        return (
            None,
            "KOBIS API 응답을 JSON으로 읽을 수 없습니다.",
        )

    # --------------------------------------------------------
    # KOBIS 자체 오류 확인
    # --------------------------------------------------------
    # 인증키가 틀려도 HTTP 200이 나올 수 있으므로
    # 반드시 faultInfo를 확인합니다.

    if "faultInfo" in data:

        fault = data["faultInfo"]

        message = fault.get(
            "message",
            fault.get(
                "errorMessage",
                "KOBIS API 오류가 발생했습니다.",
            ),
        )

        return None, message

    return data, None


# ============================================================
# 6. 일일 박스오피스 가져오기
# ============================================================

@st.cache_data(ttl=60 * 30)
def get_daily_boxoffice(target_date):
    """
    특정 날짜의 KOBIS 일일 박스오피스를 가져옵니다.

    같은 데이터를 30분 동안 캐시해서
    API를 반복 호출하지 않도록 합니다.
    """

    data, error = kobis_get(
        "boxoffice/searchDailyBoxOfficeList.json",
        {
            "targetDt": target_date,
        },
    )

    if error:
        return None, error

    if not data:
        return None, "KOBIS 응답이 비어 있습니다."

    result = data.get("boxOfficeResult")

    if not result:
        return None, "KOBIS 응답에 boxOfficeResult가 없습니다."

    movies = result.get(
        "dailyBoxOfficeList",
        [],
    )

    if not movies:
        return (
            None,
            "해당 날짜의 박스오피스 영화 목록이 비어 있습니다.",
        )

    return movies, None


# ============================================================
# 7. 영화 상세정보 가져오기
# ============================================================

@st.cache_data(ttl=60 * 60 * 24)
def get_movie_info(movie_cd):
    """
    영화 코드로 KOBIS 영화 상세정보를 가져옵니다.

    장르, 제작국가, 러닝타임 등을 활용하기 위해 사용합니다.

    상세정보 API에 문제가 생기더라도
    전체 추천 시스템이 멈추지 않도록 None을 반환합니다.
    """

    if not movie_cd:
        return None

    data, error = kobis_get(
        "movie/searchMovieInfo.json",
        {
            "movieCd": movie_cd,
        },
    )

    if error:
        return None

    if not data:
        return None

    result = data.get(
        "movieInfoResult",
        {},
    )

    return result.get("movieInfo")


# ============================================================
# 8. KOBIS 영화 데이터를 추천용 데이터로 변환
# ============================================================

def normalize_movie(movie):
    """
    KOBIS 영화 정보를 추천 알고리즘에서 사용하기
    편한 형태로 바꿉니다.
    """

    movie_cd = movie.get(
        "movieCd",
        "",
    )

    info = get_movie_info(movie_cd)

    # 상세정보를 가져오지 못해도
    # 박스오피스 데이터만으로 계속 진행합니다.
    if not info:
        info = {}

    # --------------------------------------------------------
    # 장르
    # --------------------------------------------------------

    genres = info.get(
        "genres",
        [],
    )

    genre_names = [
        genre.get("genreNm", "")
        for genre in genres
        if genre.get("genreNm")
    ]

    # --------------------------------------------------------
    # 제작국가
    # --------------------------------------------------------

    countries = info.get(
        "nations",
        [],
    )

    country_names = [
        country.get("nationNm", "")
        for country in countries
        if country.get("nationNm")
    ]

    # --------------------------------------------------------
    # 개봉일
    # --------------------------------------------------------

    open_date = movie.get(
        "openDt",
        info.get("openDt", ""),
    )

    # --------------------------------------------------------
    # 관객수
    # --------------------------------------------------------

    try:

        audience = int(
            movie.get(
                "audiCnt",
                0,
            )
        )

    except (ValueError, TypeError):

        audience = 0

    # --------------------------------------------------------
    # 누적 관객수
    # --------------------------------------------------------

    try:

        accumulated = int(
            movie.get(
                "audiAcc",
                0,
            )
        )

    except (ValueError, TypeError):

        accumulated = 0

    # --------------------------------------------------------
    # 러닝타임
    # --------------------------------------------------------

    try:

        show_time = int(
            info.get(
                "showTm",
                0,
            )
        )

    except (ValueError, TypeError):

        show_time = 0

    return {
        "movieCd": movie_cd,

        "title": movie.get(
            "movieNm",
            info.get(
                "movieNm",
                "제목 없음",
            ),
        ),

        "rank": movie.get(
            "rank",
            "",
        ),

        "audience": audience,

        "accumulated": accumulated,

        "open_date": open_date,

        "genres": genre_names,

        "countries": country_names,

        "show_time": show_time,
    }


# ============================================================
# 9. KOBIS 장르 → 추천 시스템 장르 변환
# ============================================================

GENRE_MAP = {

    "액션": ["action"],

    "코미디": ["comedy"],

    "멜로/로맨스": ["romance"],

    "로맨스": ["romance"],

    "드라마": ["drama"],

    "스릴러": ["thriller"],

    "공포": ["thriller"],

    "판타지": ["fantasy"],

    "SF": ["fantasy"],

    "모험": ["adventure"],

    "애니메이션": ["fantasy"],
}


# ============================================================
# 10. 영화의 장르 점수 계산
# ============================================================

def movie_genre_scores(movie):
    """
    KOBIS의 장르명을 우리가 사용하는 장르 점수로 변환합니다.
    """

    scores = {}

    for genre in movie["genres"]:

        mapped_genres = GENRE_MAP.get(
            genre,
            [],
        )

        for item in mapped_genres:

            scores[item] = (
                scores.get(item, 0) + 1
            )

    return scores


# ============================================================
# 11. 제작국가 취향 계산
# ============================================================

def country_match_score(movie, preferences):
    """
    사용자의 국가 취향과 영화의 제작국가를 비교합니다.
    """

    # 나라에 대한 선호가 없는 경우
    # 국가 때문에 점수를 크게 바꾸지 않습니다.
    if preferences.get("country_free", 0) > 0:
        return 2

    countries = movie["countries"]

    if not countries:
        return 0

    score = 0

    for country in countries:

        # 한국
        if "한국" in country:
            score += preferences.get(
                "korea",
                0,
            )

        # 영어권 주요 국가
        elif any(
            name in country
            for name in [
                "미국",
                "영국",
                "캐나다",
                "호주",
            ]
        ):
            score += preferences.get(
                "foreign",
                0,
            )

        # 아시아
        elif any(
            name in country
            for name in [
                "일본",
                "중국",
                "대만",
                "홍콩",
                "태국",
                "인도",
            ]
        ):
            score += preferences.get(
                "asia",
                0,
            )

        # 유럽
        elif any(
            name in country
            for name in [
                "프랑스",
                "독일",
                "이탈리아",
                "스페인",
                "영화",
                "덴마크",
                "스웨덴",
                "노르웨이",
                "핀란드",
                "벨기에",
                "네덜란드",
                "아일랜드",
                "영국",
            ]
        ):
            score += preferences.get(
                "europe",
                0,
            )

    return score


# ============================================================
# 12. 영화 하나의 추천 점수 계산
# ============================================================

def calculate_movie_score(movie, preferences):
    """
    사용자 취향과 영화 정보를 비교하여
    영화의 최종 추천 점수를 계산합니다.
    """

    score = 0.0

    # ========================================================
    # A. 장르 점수
    # ========================================================

    genre_scores = movie_genre_scores(movie)

    genre_keys = [
        "action",
        "comedy",
        "romance",
        "drama",
        "thriller",
        "fantasy",
        "adventure",
    ]

    user_genre_total = sum(
        max(
            preferences.get(
                key,
                0,
            ),
            0,
        )
        for key in genre_keys
    )

    if user_genre_total > 0:

        for genre, movie_value in genre_scores.items():

            user_value = max(
                preferences.get(
                    genre,
                    0,
                ),
                0,
            )

            score += (
                user_value
                / user_genre_total
                * movie_value
                * 100
            )

    # ========================================================
    # B. 대중성
    # ========================================================

    popularity_preference = preferences.get(
        "popularity",
        0,
    )

    if movie["accumulated"] > 0:

        popularity_value = min(
            math.log10(
                movie["accumulated"] + 1
            ) / 7,
            1,
        )

        score += (
            popularity_preference
            * popularity_value
            * 10
        )

    # ========================================================
    # C. 최신작 / 오래된 작품
    # ========================================================

    try:

        movie_year = int(
            movie["open_date"][:4]
        )

    except (ValueError, TypeError):

        movie_year = today_kst.year

    age = max(
        today_kst.year - movie_year,
        0,
    )

    recent_preference = preferences.get(
        "recent",
        0,
    )

    classic_preference = preferences.get(
        "classic",
        0,
    )

    # 최근 영화일수록 1에 가까워집니다.
    recent_value = max(
        0,
        1 - age / 15,
    )

    # 오래된 영화일수록 1에 가까워집니다.
    classic_value = min(
        age / 20,
        1,
    )

    score += (
        recent_preference
        * recent_value
        * 10
    )

    score += (
        classic_preference
        * classic_value
        * 10
    )

    # ========================================================
    # D. 탐험 성향
    # ========================================================

    exploration = preferences.get(
        "exploration",
        0,
    )

    if exploration >= 3:

        # 제작국가 정보가 있으면 탐험 보너스
        if movie["countries"]:
            score += 5

        # 여러 장르가 섞인 영화에도 약간의 보너스
        if len(movie["genres"]) >= 2:
            score += 3

    # ========================================================
    # E. 러닝타임
    # ========================================================

    long_movie_preference = preferences.get(
        "long_movie",
        0,
    )

    if movie["show_time"]:

        # 140분 이상이면 긴 영화
        if movie["show_time"] >= 140:

            score += (
                long_movie_preference * 2
            )

        # 100분 이하라면 짧은 영화
        elif movie["show_time"] <= 100:

            score += (
                -long_movie_preference * 0.5
            )

    # ========================================================
    # F. 국가 취향
    # ========================================================

    score += (
        country_match_score(
            movie,
            preferences,
        )
        * 2
    )

    # ========================================================
    # G. 탐험 성향이 높은 경우
    #    지나치게 유명한 영화만 선택되지 않도록 보정
    # ========================================================

    if exploration >= 3:

        # 누적 관객수가 상대적으로 낮은 영화에
        # 작은 탐험 보너스를 줍니다.
        if movie["accumulated"] < 500_000:
            score += 4

        elif movie["accumulated"] < 1_000_000:
            score += 2

    return score


# ============================================================
# 13. 추천 이유 만들기
# ============================================================

def make_reason(movie, preferences):
    """
    사용자가 왜 이 영화에 추천되었는지
    짧은 문장으로 설명합니다.
    """

    reasons = []

    genre_scores = movie_genre_scores(
        movie
    )

    genre_names = {

        "action": "액션",

        "comedy": "코미디",

        "romance": "로맨스",

        "drama": "드라마",

        "thriller": "스릴러",

        "fantasy": "판타지",

        "adventure": "모험",
    }

    # --------------------------------------------------------
    # 가장 잘 맞는 장르 찾기
    # --------------------------------------------------------

    favorite_genres = sorted(
        genre_scores.keys(),
        key=lambda genre: preferences.get(
            genre,
            0,
        ),
        reverse=True,
    )

    if favorite_genres:

        best_genre = favorite_genres[0]

        if preferences.get(
            best_genre,
            0,
        ) > 0:

            reasons.append(
                f"{genre_names.get(best_genre, best_genre)} 취향과 잘 맞아요."
            )

    # --------------------------------------------------------
    # 대중성
    # --------------------------------------------------------

    if preferences.get(
        "popularity",
        0,
    ) >= 3:

        reasons.append(
            "많은 사람이 본 대중적인 영화를 선호하는 취향과 잘 맞아요."
        )

    # --------------------------------------------------------
    # 탐험 성향
    # --------------------------------------------------------

    if preferences.get(
        "exploration",
        0,
    ) >= 3:

        reasons.append(
            "새로운 영화와 색다른 선택을 좋아하는 성향에 잘 맞아요."
        )

    # --------------------------------------------------------
    # 고전/검증된 작품
    # --------------------------------------------------------

    if preferences.get(
        "classic",
        0,
    ) >= 3:

        reasons.append(
            "시간이 지나도 볼 만한 작품을 찾는 취향과 잘 맞아요."
        )

    # --------------------------------------------------------
    # 최신작
    # --------------------------------------------------------

    if preferences.get(
        "recent",
        0,
    ) >= 3:

        reasons.append(
            "최근 개봉한 영화를 선호하는 취향과 잘 맞아요."
        )

    # --------------------------------------------------------
    # 긴 영화
    # --------------------------------------------------------

    if (
        movie["show_time"] >= 140
        and preferences.get(
            "long_movie",
            0,
        ) >= 2
    ):

        reasons.append(
            "긴 러닝타임도 괜찮아하는 취향과 잘 맞아요."
        )

    # --------------------------------------------------------
    # 설명이 없는 경우
    # --------------------------------------------------------

    if not reasons:

        reasons.append(
            "테스트에서 입력한 여러 취향을 종합해 추천한 영화예요."
        )

    # 최대 3개의 이유만 표시합니다.
    return " ".join(
        reasons[:3]
    )


# ============================================================
# 14. 사용자 답변을 취향 점수로 합치기
# ============================================================

def calculate_preferences(answers):
    """
    사용자가 선택한 모든 답변의 점수를 합칩니다.
    """

    preferences = {}

    for answer_score in answers:

        for key, value in answer_score.items():

            preferences[key] = (
                preferences.get(
                    key,
                    0,
                )
                + value
            )

    return preferences


# ============================================================
# 15. 영화 추천
# ============================================================

def recommend_movies(
    movies,
    preferences,
):
    """
    KOBIS 영화 목록에 사용자 취향 점수를 적용하고
    점수가 높은 순서로 정렬합니다.
    """

    normalized_movies = []

    for movie in movies:

        normalized = normalize_movie(
            movie
        )

        normalized["recommend_score"] = (
            calculate_movie_score(
                normalized,
                preferences,
            )
        )

        normalized["reason"] = (
            make_reason(
                normalized,
                preferences,
            )
        )

        normalized_movies.append(
            normalized
        )

    # 추천 점수가 높은 순서
    normalized_movies.sort(
        key=lambda movie: movie[
            "recommend_score"
        ],
        reverse=True,
    )

    return normalized_movies


# ============================================================
# 16. 세션 상태 초기화
# ============================================================

if "question_index" not in st.session_state:

    st.session_state.question_index = 0


if "answers" not in st.session_state:

    st.session_state.answers = []


if "finished" not in st.session_state:

    st.session_state.finished = False


if "recommendations" not in st.session_state:

    st.session_state.recommendations = []


if "preferences" not in st.session_state:

    st.session_state.preferences = {}


# ============================================================
# 17. 메인 제목
# ============================================================

st.title("🎬 오늘 뭐 볼까?")

st.markdown(
    """
    ### 당신의 영화 취향을 찾아볼게요.

    몇 가지 질문에 답하면  
    **KOBIS의 실제 영화 데이터를 바탕으로 오늘 볼 영화를 추천**해 드립니다.
    """
)


# ============================================================
# 18. 심리테스트 화면
# ============================================================

if not st.session_state.finished:

    question_index = (
        st.session_state.question_index
    )

    total_questions = len(
        QUESTIONS
    )

    # 현재 진행률
    progress = (
        question_index
        / total_questions
    )

    st.progress(
        progress
    )

    st.caption(
        f"{question_index + 1} / {total_questions}"
    )

    current_question = QUESTIONS[
        question_index
    ]

    st.subheader(
        current_question["question"]
    )

    option_labels = [
        option[0]
        for option in current_question[
            "options"
        ]
    ]

    selected_option = st.radio(
        "하나를 선택해 주세요.",
        option_labels,
        key=f"question_{question_index}",
    )

    selected_score = None

    for option in current_question[
        "options"
    ]:

        if option[0] == selected_option:

            selected_score = option[1]

            break

    st.write("")

    if st.button(
        "다음 →",
        type="primary",
        use_container_width=True,
    ):

        st.session_state.answers.append(
            selected_score
        )

        if (
            question_index + 1
            >= total_questions
        ):

            st.session_state.finished = True

        else:

            st.session_state.question_index += 1

        st.rerun()


# ============================================================
# 19. 테스트 완료 후 영화 추천
# ============================================================

else:

    # 추천 결과가 아직 만들어지지 않은 경우
    if not st.session_state.recommendations:

        with st.spinner(
            "🎬 KOBIS에서 어제의 영화 데이터를 가져오는 중이에요..."
        ):

            movies, error = (
                get_daily_boxoffice(
                    YESTERDAY_STRING
                )
            )

        # ----------------------------------------------------
        # API 오류
        # ----------------------------------------------------

        if error:

            st.error(
                f"""
                영화 데이터를 가져오지 못했습니다.

                **확인해 주세요.**

                - KOBIS_KEY가 정확하게 등록되어 있는지 확인
                - Streamlit Cloud → Settings → Secrets 확인
                - KOBIS API가 일시적으로 장애가 없는지 확인
                - KOBIS에서 해당 날짜의 박스오피스가 집계되었는지 확인

                조회 날짜:
                **{YESTERDAY_DISPLAY}**

                API 메시지:
                **{error}**
                """
            )

            st.stop()

        # ----------------------------------------------------
        # 영화 목록이 비어 있는 경우
        # ----------------------------------------------------

        if not movies:

            st.error(
                f"""
                {YESTERDAY_DISPLAY}의
                박스오피스 영화 목록이 비어 있습니다.

                KOBIS에서 해당 날짜의 데이터가 아직 집계되지 않았거나
                API 응답에 영화 목록이 없는 상태일 수 있습니다.
                """
            )

            st.stop()

        # ----------------------------------------------------
        # 사용자 취향 계산
        # ----------------------------------------------------

        preferences = (
            calculate_preferences(
                st.session_state.answers
            )
        )

        st.session_state.preferences = (
            preferences
        )

        # ----------------------------------------------------
        # 추천
        # ----------------------------------------------------

        recommendations = (
            recommend_movies(
                movies,
                preferences,
            )
        )

        # 최대 5편 저장
        st.session_state.recommendations = (
            recommendations[:5]
        )


# ============================================================
# 20. 추천 결과 화면
# ============================================================

if st.session_state.finished:

    st.success(
        "🎉 테스트가 끝났어요!"
    )

    st.markdown(
        f"""
        ## 🍿 당신을 위한 영화 추천

        **{YESTERDAY_DISPLAY} KOBIS 박스오피스**를
        바탕으로 취향에 맞는 영화를 골랐어요.
        """
    )

    recommendations = (
        st.session_state.recommendations
    )

    # 추천 영화가 없는 경우
    if not recommendations:

        st.warning(
            """
            추천할 영화를 찾지 못했습니다.

            KOBIS에서 가져온 영화 데이터와
            현재 취향 점수를 확인해 주세요.
            """
        )

        st.stop()

    # ========================================================
    # 1위 추천 영화
    # ========================================================

    first_movie = recommendations[0]

    st.markdown(
        f"# 🥇 {first_movie['title']}"
    )

    st.info(
        first_movie["reason"]
    )

    # --------------------------------------------------------
    # 기본 정보 카드
    # --------------------------------------------------------

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "KOBIS 박스오피스",
            f"{first_movie['rank']}위",
        )

    with col2:

        st.metric(
            "누적 관객",
            f"{first_movie['accumulated']:,}명",
        )

    with col3:

        if first_movie["show_time"]:

            st.metric(
                "러닝타임",
                f"{first_movie['show_time']}분",
            )

        else:

            st.metric(
                "러닝타임",
                "정보 없음",
            )

    # --------------------------------------------------------
    # 장르
    # --------------------------------------------------------

    if first_movie["genres"]:

        st.write(
            "🎭 **장르:** "
            + ", ".join(
                first_movie["genres"]
            )
        )

    # --------------------------------------------------------
    # 제작국가
    # --------------------------------------------------------

    if first_movie["countries"]:

        st.write(
            "🌎 **제작국가:** "
            + ", ".join(
                first_movie["countries"]
            )
        )

    st.divider()

    # ========================================================
    # 2~5위 추천
    # ========================================================

    st.markdown(
        "### 🎬 함께 추천하는 영화"
    )

    for index, movie in enumerate(
        recommendations[1:],
        start=2,
    ):

        st.markdown(
            f"### {index}. {movie['title']}"
        )

        st.write(
            movie["reason"]
        )

        details = []

        if movie["genres"]:

            details.append(
                "장르: "
                + ", ".join(
                    movie["genres"]
                )
            )

        if movie["accumulated"]:

            details.append(
                "누적 관객: "
                + f"{movie['accumulated']:,}명"
            )

        if movie["show_time"]:

            details.append(
                "러닝타임: "
                + f"{movie['show_time']}분"
            )

        if movie["countries"]:

            details.append(
                "제작국가: "
                + ", ".join(
                    movie["countries"]
                )
            )

        if details:

            st.caption(
                " · ".join(details)
            )

        st.divider()


# ============================================================
# 21. 나의 영화 취향 분석
# ============================================================

if st.session_state.finished:

    preferences = (
        st.session_state.preferences
    )

    with st.expander(
        "🔎 나의 영화 취향 분석 보기"
    ):

        st.write(
            "테스트 답변을 바탕으로 계산한 취향 점수입니다."
        )

        preference_names = {

            "action": "액션",

            "comedy": "코미디",

            "romance": "로맨스",

            "drama": "드라마",

            "thriller": "스릴러",

            "fantasy": "판타지",

            "adventure": "모험",

            "popularity": "대중적인 영화 선호",

            "classic": "명작·고전 선호",

            "recent": "최신작 선호",

            "exploration": "새로운 영화 탐험",

            "long_movie": "긴 영화 선호",

            "korea": "한국 영화",

            "foreign": "영어권 영화",

            "asia": "아시아 영화",

            "europe": "유럽 영화",

            "country_free": "국가보다 영화 자체를 중시",
        }

        rows = []

        for key, value in preferences.items():

            rows.append(
                {
                    "취향": preference_names.get(
                        key,
                        key,
                    ),
                    "점수": value,
                }
            )

        if rows:

            import pandas as pd

            preference_df = pd.DataFrame(
                rows
            )

            st.dataframe(
                preference_df,
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# 22. 다시 테스트
# ============================================================

if st.session_state.finished:

    st.write("")

    if st.button(
        "🔄 다시 테스트하기",
        use_container_width=True,
    ):

        st.session_state.question_index = 0

        st.session_state.answers = []

        st.session_state.finished = False

        st.session_state.recommendations = []

        st.session_state.preferences = {}

        st.rerun()


# ============================================================
# 23. 하단 안내
# ============================================================

st.divider()

st.caption(
    "영화 데이터: 영화관입장권통합전산망(KOBIS) Open API"
)

st.caption(
    "추천 결과는 심리테스트 답변과 KOBIS 영화 데이터를 "
    "바탕으로 계산한 개인화 추천입니다."
)

st.caption(
    f"조회 기준일: {YESTERDAY_DISPLAY} "
    "(한국 시간 기준 어제)"
)
