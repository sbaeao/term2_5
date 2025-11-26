import streamlit as st
import streamlit.components.v1 as components
import requests
import uuid
from pathlib import Path

# -----------------------------
# GA 설정
# -----------------------------
try:
    GA_ID = st.secrets["ga"]["measurement_id"]
    GA_API_SECRET = st.secrets["ga"]["api_secret"]
    GA_ENABLED = True
except Exception:
    GA_ENABLED = False


def inject_ga(page_name: str):
    """
    Google Analytics 4 page_view 삽입

    - gtag.js 로드
    - send_page_view 자동 전송 끄고
    - 명시적으로 page_view 이벤트 한 번 쏴줌
    - home은 page_path="/", 나머지는 "/{page_name}"
    """
    if not GA_ENABLED:
        return

    if page_name == "home":
        page_path = "/"
    else:
        page_path = f"/{page_name}"

    ga_js = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}};

      // GA 초기화
      gtag('js', new Date());

      // 기본 config (자동 page_view 비활성화)
      gtag('config', '{GA_ID}', {{
        'send_page_view': false
      }});

      // 수동 page_view 이벤트 전송
      gtag('event', 'page_view', {{
        'page_title': '{page_name}',
        'page_path': '{page_path}',
        'page_location': window.location.href
      }});
    </script>
    """
    components.html(ga_js, height=0)


def send_ga_event(event_name: str, params: dict | None = None):
    """
    GA4 Measurement Protocol로 커스텀 이벤트 전송
    (stats_viewed, survey_completed 등)
    """
    if not GA_ENABLED:
        return

    if params is None:
        params = {}

    payload = {
        "client_id": str(uuid.uuid4()),
        "events": [
            {
                "name": event_name,
                "params": params,
            }
        ],
    }

    requests.post(
        "https://www.google-analytics.com/mp/collect",
        params={
            "measurement_id": GA_ID,
            "api_secret": GA_API_SECRET,
        },
        json=payload,
        timeout=2,
    )


# -----------------------------
# 이미지 경로 설정
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent


def img(path: str) -> Path:
    return BASE_DIR / "images" / path


# -----------------------------
# 페이지 기본 설정
# -----------------------------
st.set_page_config(
    page_title="생명의물",
    page_icon=img("1_SiteLogo.png"),
    layout="centered",
)

# 🔥 GA page_view: home (메인)
inject_ga("home")

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.title("🍶 생명의물")
st.sidebar.markdown("취향 기반 술 추천 바")

# -----------------------------
# 메인 타이틀 섹션
# -----------------------------
st.image(img("0_LiqureMate.png"))
st.markdown("### 취향으로 찾아가는, 나만의 한 잔")
st.image(img("2_MainBanner.png"))

st.markdown(
    """
    **LiqureMate**는 여러 종류의 술을 단순히 나열하는 곳이 아니라,  
    당신의 취향을 설문으로 파악해서 가장 잘 어울리는 술을 추천해 주고,  
    실제로 그 술을 경험할 수 있는 공간입니다.
    """
)

# -----------------------------
# 소개 섹션 (좌: 설명, 우: 이미지)
# -----------------------------
col1, col2 = st.columns([1.3, 1])

with col1:
    st.markdown(
        """
        #### 🍷 어떤 술을 좋아하세요?

        생명의물에서는 네 가지 축을 중심으로 술을 소개합니다.

        - 🥃 **위스키**  
          스모키, 과일향, 곡물향… 숙성과 캐스크에 따라 완전히 다른 얼굴을 가진 깊은 한 잔

        - 🍶 **사케**  
          쌀의 단맛과 감칠맛, 부드러운 산미로 음식과 함께할 때 진가를 드러내는 일본식 생명의 물

        - 🍶 **전통주**  
          막걸리, 약주, 청주, 증류주까지  
          곡물과 발효의 풍미를 한국적인 방식으로 풀어낸 우리의 술

        - 🍷 **와인**  
          포도 품종, 산지, 숙성 방식에 따라  
          과일 향과 구조가 완전히 달라지는 세계의 한 잔

        ---

        **간단한 설문을 통해 당신의 맛·향·도수·분위기 취향을 파악**한 뒤,  
        그 결과를 바탕으로 우리의 공간인 **생명의물**에서 다양한 술을 경험해볼 수 있습니다.
        """
    )

with col2:
    st.image(
        img("mainpage_warehouse.png"),
        caption="당신의 취향에 맞는 한 잔을 찾는 공간, 생명의물",
    )

st.markdown("---")

# -----------------------------
# 이용 방법 섹션
# -----------------------------
st.subheader("🗺 어떻게 이용하나요?")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown(
        """
        ### 1. 설문으로 취향 입력  
        - 좋아하는 **맛/향**  
        - 선호 **도수 범위**  
        - 술을 마시는 **상황**  
        - 예산, 탄산 선호 등  
        """
    )

with col_b:
    st.markdown(
        """
        ### 2. 나에게 맞는 술 스타일 추천  
        - 위스키/사케/전통주/와인 중  
          취향에 맞는 **스타일** 추천  
        - 입문용, 분위기용, 식사 페어링 등  
          상황별 제안
        """
    )

with col_c:
    st.markdown(
        """
        ### 3. 우리 공간에서 실제로 즐기기  
        - 추천 결과를 바탕으로  
          **매장에서 한 잔 시음**  
        - 메뉴 선택이 어렵다면  
          설문 결과를 직원에게 보여 주세요  
        """
    )

st.markdown("---")

# -----------------------------
# CTA: 설문 페이지로 이동
# -----------------------------
st.subheader("🍸 지금, 나에게 맞는 술을 찾으러 가볼까요?")

st.markdown(
    """
    아래 버튼을 누르면 **취향 설문 페이지**로 이동합니다.  
    몇 가지 질문에 답하면, 오늘 당신에게 가장 잘 어울리는 술 스타일을 추천해 드릴게요.
    """
)

# 버튼 스타일
st.markdown(
    """
    <style>
    div.stButton > button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 18px 40px;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f71ff 0%, #6cc6ff 50%, #90e0ff 100%);
        color: #ffffff;
        font-size: 22px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
        animation: pulse 1.5s infinite;
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
    }
    div.stButton > button:hover {
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 14px 26px rgba(0, 0, 0, 0.22);
    }
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 154, 158, 0.7);
        }
        70% {
            transform: scale(1.05);
            box-shadow: 0 0 0 18px rgba(255, 154, 158, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(255, 154, 158, 0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 버튼 클릭 → 설문 페이지로 이동
clicked = st.button("🍸 나에게 맞는 술 찾기")

if clicked:
    st.switch_page("pages/01_survey.py")
