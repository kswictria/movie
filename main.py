import streamlit as st
import requests

from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# 1. 기본 설정
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
# Streamlit Cloud의 Secrets에 아래처럼 등록하세요.
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

        Streamlit Cloud의 앱 설정 → Secrets에서

        KOBIS_KEY = "발급받은 인증키"

        형태로 등록했는지 확인해 주세요.
        """
    )
    st.stop()


KOBIS_BASE_URL = (
    "https://www.kobis.or.kr/"
    "kobisopenapi/webservice/rest"
)


# ============================================================
# 3. 질문 데이터
# ============================================================
# 각 답변에는 추천 알고리즘에 사용할 점수가 들어 있습니다.
#
# 예:
# 액션을 좋아하는 답변을 선택하면
# action 점수가 올라갑니다.
#
# 탐험 성향은 exploration,
# 대중적인 영화 선호는 popularity,
# 오래된/검증된 영화 선호는 classic,
# 최신 영화 선호는 recent 등으로 관리합니다.


QUESTIONS = [
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
    {
        "question": "친구가 '요즘 엄청 인기 있는 영화'라고 추천한다면?",
        "options": [
            (
                "🔥 인기 있는 데는 이유가 있지! 바로 본다.",
                {"popularity": 4},
            ),
            (
                "🙂 재미있다면 보고 싶다.",
                {"popularity": 2},
            ),
            (
                "🤔 인기보다는 내 취향이 중요하다.",
                {"popularity": 0},
            ),
            (
                "👀 오히려 사람들이 잘 모르는 영화가 궁금하다.",
                {"popularity": -2},
                ),
            (
                "🕵️ 숨은 영화를 발견하는 게 더 좋다.",
                {"popularity": -4},
            ),
        ],
    },
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
    {
        "question": "평소 보지 않던 장르의 영화가 눈에 띈다면?",
        "options": [
            (
                "🎯 익숙한 장르가 아니면 잘 안 본다.",
                {"exploration": 0},
            ),
            (
                "👍 평소 좋아하는 장르라면 새로운 영화도 본다.",
                {"exploration": 1},
            ),
            (
                "🤔 예고편이 재미있으면 도전한다.",
                {"exploration": 2},
            ),
            (
                "🧭 평소 안 보던 장르도 가끔 도전한다.",
                {"exploration": 3},
            ),
            (
                "🚀 새로운 장르를 적극적으로 찾아본다.",
                {"exploration": 4},
            ),
        ],
    },
    {
        "question": "영화 추천을 받는다면 어느 쪽이 더 좋은가요?",
        "options": [
            (
                "🎯 내가 좋아할 가능성이 높은 영화만 추천해줘.",
                {"exploration": 0},
            ),
            (
                "🙂 대부분 취향에 맞는 영화면 좋겠어.",
                {"exploration": 1},
            ),
            (
                "🎲 한 편 정도는 의외의 영화도 좋아.",
                {"exploration": 2},
            ),
            (
                "🧭 새로운 영화도 섞어줘.",
                {"exploration": 3},
            ),
            (
                "🚀 내가 몰랐던 영화를 발견하고 싶어.",
                {"exploration": 4},
            ),
        ],
    },
    {
        "question": "2시간 30분짜리 영화라면?",
        "options": [
            (
                "😎 재미있으면 길이는 상관없다.",
                {"long_movie": 3},
            ),
            (
                "🙂 조금 길어도 괜찮다.",
                {"long_movie": 2},
            ),
            (
                "😐 2시간 정도가 가장 좋다.",
                {"long_movie": 1},
            ),
            (
                "🥱 긴 영화는 조금 부담스럽다.",
                {"long_movie": -1},
            ),
        ],
    },
    {
        "question": "어떤 영화에 더 끌리나요?",
        "options": [
            (
                "🇰🇷 한국 영화",
                {"korea": 3},
            ),
            (
                "🌎 미국 등 영어권 영화",
                {"foreign": 2},
            ),
            (
                "🇯🇵 일본 등 아시아 영화",
                {"asia": 3},
            ),
            (
                "🇪🇺 유럽 영화",
                {"europe": 3},
            ),
            (
                "🎲 나라보다는 재미가 중요하다.",
                {"country_free": 3},
            ),
        ],
    },
    {
        "question": "영화의 개봉 시기는 얼마나 중요한가요?",
        "options": [
            (
                "🆕 무조건 최신작!",
                {"recent": 4},
            ),
            (
                "📅 최근 몇 년 안의 영화가 좋다.",
                {"recent": 3},
            ),
            (
                "🎬 언제 만들어졌는지는 별로 중요하지 않다.",
                {"recent": 1, "classic": 1},
            ),
            (
                "🕰️ 오래된 영화도 좋은 작품이면 본다.",
                {"classic": 3},
            ),
            (
                "📼 고전영화를 찾아보는 것도 좋아한다.",
                {"classic": 4},
            ),
        ],
    },
    {
        "question": "오늘 영화를 보는 가장 큰 이유는?",
        "options": [
            (
                "😂 그냥 웃고 싶어서",
                {"comedy": 3},
            ),
            (
                "😭 감정을 제대로 느끼고 싶어서",
                {"drama": 3},
            ),
            (
                "🧠 생각할 거리가 필요해서",
                {"drama": 3},
            ),
            (
                "😱 긴장감을 느끼고 싶어서",
                {"thriller": 3},
            ),
            (
                "🥰 설레고 싶어서",
                {"romance": 3},
            ),
            (
                "🌿 아무 생각 없이 쉬고 싶어서",
                {"comedy": 1, "drama": 1},
            ),
            (
                "🚀 현실에서 잠깐 벗어나고 싶어서",
                {"fantasy": 3, "adventure": 2},
            ),
        ],
    },
]


# ============================================================
# 4. KOBIS API 호출 함수
# ============================================================

def kobis_get(endpoint, params):
    """
    KOBIS API를 호출하는 공통 함수입니다.

    KOBIS는 인증키가 잘못되어도 HTTP 200을 반환하고
    faultInfo를 보내는 경우가 있기 때문에
    faultInfo를 별도로 검사합니다.
    """

    url = f"{KOBIS_BASE_URL}/{endpoint}"

    params = {
        "key": KOBIS_KEY,
        **params,
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

    except requests.exceptions.Timeout:
        return None, "KOBIS API 요청 시간이 초과되었습니다."

    except requests.exceptions.RequestException as e:
        return None, f"KOBIS API 요청에 실패했습니다: {e}"

    except ValueError:
        return None, "KOBIS API 응답을 JSON으로 읽을 수 없습니다."

    # 인증키 오류 등 KOBIS 자체 오류 확인
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
# 5. 어제 날짜 계산
# ============================================================
# 서버가 한국 시간이 아닐 수도 있으므로
# 반드시 Asia/Seoul을 지정합니다.

KST = ZoneInfo("Asia/Seoul")

today_kst = datetime.now(KST).date()

# 테스트와 추천 데이터는 최신 데이터 위주로 사용합니다.
today_string = today_kst.strftime("%Y%m%d")


# ============================================================
# 6. 최근 박스오피스 가져오기
# ============================================================

@st.cache_data(ttl=60 * 30)
def get_daily_boxoffice(target_date):
    """
    특정 날짜의 KOBIS 일일 박스오피스를 가져옵니다.

    30분 동안은 캐시해서 불필요한 API 호출을 줄입니다.
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
        return None, "boxOfficeResult가 없습니다."

    movies = result.get(
        "dailyBoxOfficeList",
        [],
    )

    if not movies:
        return None, "해당 날짜의 박스오피스 데이터가 없습니다."

    return movies, None


# ============================================================
# 7. 영화 상세정보 가져오기
# ============================================================

@st.cache_data(ttl=60 * 60 * 24)
def get_movie_info(movie_cd):
    """
    KOBIS 영화 상세정보 API를 이용해
    장르, 제작국가 등의 정보를 가져옵니다.
    """

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

    result = data.get("movieInfoResult", {})
    return result.get("movieInfo")


# ============================================================
# 8. KOBIS 영화 데이터를 내부 추천 데이터로 변환
# ============================================================

def normalize_movie(movie):
    """
    KOBIS에서 받은 영화 정보를
    추천 알고리즘에서 사용하기 편한 형태로 바꿉니다.
    """

    movie_cd = movie.get("movieCd", "")

    info = get_movie_info(movie_cd)

    # 상세정보를 가져오지 못한 경우에도
    # 박스오피스 데이터만으로 추천이 가능하도록 합니다.
    if not info:
        info = {}

    genres = info.get("genres", [])

    genre_names = [
        genre.get("genreNm", "")
        for genre in genres
    ]

    countries = info.get("nations", [])

    country_names = [
        country.get("nationNm", "")
        for country in countries
    ]

    # KOBIS의 개봉일
    open_date = movie.get(
        "openDt",
        info.get("openDt", ""),
    )

    # 관객수는 문자열로 오므로 숫자로 변환합니다.
    try:
        audience = int(movie.get("audiCnt", 0))
    except (ValueError, TypeError):
        audience = 0

    try:
        accumulated = int(movie.get("audiAcc", 0))
    except (ValueError, TypeError):
        accumulated = 0

    # 상영시간
    try:
        show_time = int(info.get("showTm", 0))
    except (ValueError, TypeError):
        show_time = 0

    return {
        "movieCd": movie_cd,
        "title": movie.get(
            "movieNm",
            info.get("movieNm", "제목 없음"),
        ),
        "rank": movie.get("rank", ""),
        "audience": audience,
        "accumulated": accumulated,
        "open_date": open_date,
        "genres": genre_names,
        "countries": country_names,
        "show_time": show_time,
    }


# ============================================================
# 9. 장르 이름을 우리 추천 시스템의 장르로 연결
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


def movie_genre_scores(movie):
    """
    영화의 KOBIS 장르를 추천 시스템용 장르 점수로 변환합니다.
    """

    scores = {}

    for genre in movie["genres"]:
        mapped = GENRE_MAP.get(genre, [])

        for item in mapped:
            scores[item] = scores.get(item, 0) + 1

    return scores


# ============================================================
# 10. 영화 하나의 추천 점수 계산
# ============================================================

def calculate_movie_score(movie, preferences):
    """
    사용자의 취향과 영화 정보를 비교해서
    최종 추천 점수를 계산합니다.

    점수가 높을수록 사용자 취향과 가깝습니다.
    """

    score = 0.0

    # --------------------------------------------------------
    # A. 장르 점수
    # --------------------------------------------------------

    genre_scores = movie_genre_scores(movie)

    user_genre_total = sum(
        preferences.get(key, 0)
        for key in [
            "action",
            "comedy",
            "romance",
            "drama",
            "thriller",
            "fantasy",
            "adventure",
        ]
    )

    if user_genre_total > 0:

        for genre, movie_value in genre_scores.items():

            user_value = preferences.get(
                genre,
                0,
            )

            # 사용자가 좋아하는 장르일수록
            # 큰 가중치를 줍니다.
            score += (
                user_value
                / user_genre_total
                * movie_value
                * 100
            )

    # --------------------------------------------------------
    # B. 대중성
    # --------------------------------------------------------

    popularity_preference = preferences.get(
        "popularity",
        0,
    )

    # 관객수가 많을수록 대중성이 높은 영화로 봅니다.
    #
    # 여기서는 로그를 이용해
    # 엄청난 관객수 차이가 점수를 지나치게 지배하지
    # 않도록 합니다.

    if movie["accumulated"] > 0:

        import math

        popularity_value = min(
            math.log10(movie["accumulated"] + 1) / 7,
            1,
        )

        score += (
            popularity_preference
            * popularity_value
            * 10
        )

    # --------------------------------------------------------
    # C. 최신작 / 과거 작품
    # --------------------------------------------------------

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

    # 최근 영화일수록 recent 점수를 높입니다.
    recent_value = max(
        0,
        1 - age / 15,
    )

    # 오래된 영화일수록 classic 점수를 높입니다.
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

    # --------------------------------------------------------
    # D. 탐험 성향
    # --------------------------------------------------------
    # 탐험 성향이 높은 사람에게는
    # 너무 유명한 영화보다 다양한 영화를 조금 더 허용합니다.

    exploration = preferences.get(
        "exploration",
        0,
    )

    if exploration >= 3:

        # 제작국가가 있으면 약간의 탐험 보너스
        if len(movie["countries"]) > 0:
            score += 5

        # 여러 장르가 섞인 영화도 약간 보너스
        if len(movie["genres"]) >= 2:
            score += 3

    # --------------------------------------------------------
    # E. 러닝타임
    # --------------------------------------------------------

    long_movie_preference = preferences.get(
        "long_movie",
        0,
    )

    if movie["show_time"]:

        if movie["show_time"] >= 140:
            score += long_movie_preference * 2

        elif movie["show_time"] <= 100:
            score += -long_movie_preference * 0.5

    return score


# ============================================================
# 11. 추천 결과에 사용할 설명 만들기
# ============================================================

def make_reason(movie, preferences):
    """
    사용자에게 보여줄 추천 이유를 만듭니다.
    """

    reasons = []

    genre_scores = movie_genre_scores(movie)

    favorite_genres = sorted(
        genre_scores.keys(),
        key=lambda x: preferences.get(x, 0),
        reverse=True,
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

    if favorite_genres:

        best_genre = favorite_genres[0]

        if preferences.get(best_genre, 0) > 0:
            reasons.append(
                f"{genre_names.get(best_genre, best_genre)} 취향과 잘 맞아요"
            )

    if preferences.get("popularity", 0) >= 3:
        reasons.append("대중적으로 많이 본 영화를 선호하는 취향과 맞아요")

    if preferences.get("exploration", 0) >= 3:
        reasons.append("새로운 영화를 찾는 성향에 잘 맞아요")

    if preferences.get("classic", 0) >= 3:
        reasons.append("시간이 지나도 볼 만한 작품을 찾
