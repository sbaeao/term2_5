import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import datetime
import os
import requests
import uuid

# GA 공통 유틸
try:
    GA_ID = st.secrets["ga"]["measurement_id"]
    GA_API_SECRET = st.secrets["ga"]["api_secret"]
    GA_ENABLED = True
except Exception:
    GA_ENABLED = False


def inject_ga(page_name: str):
    if not GA_ENABLED:
        return

    ga_js = f"""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){{dataLayer.push(arguments);}}
      gtag('js', new Date());
      gtag('config', '{GA_ID}', {{
        'page_title': '{page_name}',
        'page_path': '/{page_name}'
      }});
    </script>
    """
    components.html(ga_js, height=0)


def send_ga_event(event_name: str, params: dict | None = None):
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

# GA page_view: survey
inject_ga("survey")

st.title("🍸 나에게 맞는 술 추천")

st.markdown("#### 몇 가지 질문만으로, 오늘 당신에게 딱 맞는 한 잔을 추천해드릴게요.")
st.markdown("---")

st.markdown(
    """
    <style>

    /* 🔥 st.radio 위쪽 기본 간격 제거 */
    div.stRadio > div {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    /* 🔥 subheader 역할 직접 구현용 (간격 조절 자유) */
    .question-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 4px;
        margin-top: 12px;
    }

    /* 🔥 설문 제출 버튼 스타일 (form_submit_button) */
    button[kind="secondaryFormSubmit"] {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 18px 40px;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f71ff 0%, #6cc6ff 50%, #90e0ff 100%);
        color: #ffffff !important;
        font-size: 20px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
        animation: pulse 1.5s infinite;
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
    }

    button[kind="secondaryFormSubmit"]:hover {
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 14px 26px rgba(0, 0, 0, 0.22);
        color: #ffffff !important;
    }

    /* 🔥 애니메이션 */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0.7);
        }
        70% {
            transform: scale(1.05);
            box-shadow: 0 0 0 18px rgba(79, 113, 255, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0);
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

with st.form("survey_form"):
    # Q1. 동반자
    st.subheader("1. 오늘 누구와 마실 계획인가요?")
    companion = st.radio(
        "",
        ["혼자", "연인/썸", "친구/동기", "직장동료/회식"],
        index=1,
        label_visibility="collapsed",
    )

    # Q2. 분위기/목적
    st.subheader("2. 오늘의 분위기/목적은 어떤가요?")
    mood = st.radio(
        "",
        [
            "가볍게 한잔 마시고 싶어요",
            "진지한 대화가 좋아요",
            "텐션 업! 신나게 마시고 싶어요",
            "조용히 분위기만 즐기고 싶어요",
            "선물 할거에요"
        ],
        label_visibility="collapsed",
    )

    # Q3. 도수
    st.subheader("3. 오늘 괜찮다고 느끼는 술의 도수는 어느 정도인가요?")
    abv = st.slider("도수(°)", min_value=5, max_value=60, value=12)

    # Q4. 맛/스타일
    st.subheader("4. 어떤 맛/스타일을 좋아하세요?")
    taste_pref = st.radio(
        "",
        [
            "달콤한 맛이 좋아요",
            "강하고 묵직한 맛이 좋아요",
            "상큼/깔끔한 스타일이 좋아요",
            "잘 모르겠어요, 추천에 맡길래요",
        ],
        label_visibility="collapsed",
    )

    # Q5. 안주/음식
    st.subheader("5. 어떤 종류의 안주와 함께 마시고 싶나요?")
    food = st.radio(
        "",
        [
            "한식 안주 (찌개, 전, 튀김, 고기 등)",
            "일식/해산물 (초밥, 사시미 등)",
            "서양식 (파스타, 스테이크, 치즈 등)",
            "가벼운 안주/간단한 스낵",
            "안주 없이 술 위주로 마실래요",
        ],
        label_visibility="collapsed",
    )

    # 🔥 버튼 가운데 정렬
    st.markdown(
        "<div style='text-align: center; margin-top: 24px;'>",
        unsafe_allow_html=True,
    )
    submitted = st.form_submit_button("🍷 내 추천 결과 보기")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")


def recommend_drink(companion, mood, abv, taste_pref, food):
    """
    5개 질문을 바탕으로 위스키/사케/전통주/와인 중 하나를 추천하는 점수 로직
    """
    scores = {"위스키": 0, "사케": 0, "전통주": 0, "와인": 0}

    # 1) 동반자
    if companion == "혼자":
        scores["위스키"] += 2
        scores["전통주"] += 1
    elif companion == "연인/썸":
        scores["와인"] += 2
        scores["사케"] += 1
    elif companion == "친구/동기":
        scores["전통주"] += 2
        scores["와인"] += 1
    elif companion == "직장동료/회식":
        scores["전통주"] += 2
        scores["위스키"] += 1

    # 2) 분위기/목적
    if mood == "가볍게 한잔 마시고 싶어요":
        scores["사케"] += 1
        scores["전통주"] += 1
        scores["와인"] += 1
        scores["위스키"] += 1
    elif mood == "진지한 대화가 좋아요":
        scores["위스키"] += 2
        scores["와인"] += 2
    elif mood == "텐션 업! 신나게 마시고 싶어요":
        scores["위스키"] += 1
        scores["전통주"] += 2
    elif mood == "조용히 분위기만 즐기고 싶어요":
        scores["와인"] += 2
        scores["사케"] += 2
    elif mood == "선물 할거에요":
        scores["와인"] += 2
        scores["위스키"] += 2    

    # 3) 도수
    if abv <= 10:
        scores["전통주"] += 1
        scores["와인"] += 1
    elif 11 <= abv <= 30:
        scores["사케"] += 2
        scores["와인"] += 2
        scores["전통주"] += 1
    else:
        scores["위스키"] += 2

    # 4) 맛/스타일
    if taste_pref == "달콤한 맛이 좋아요":
        scores["사케"] += 2
        scores["전통주"] += 2
        scores["와인"] += 1
        scores["위스키"] += 1
    elif taste_pref == "강하고 묵직한 맛이 좋아요":
        scores["위스키"] += 2
        scores["와인"] += 1
    elif taste_pref == "상큼/깔끔한 스타일이 좋아요":
        scores["사케"] += 2
        scores["전통주"] += 1
        scores["와인"] += 1
    # "잘 모르겠어요"면 다른 요소로만 판단

    # 5) 안주/음식
    if food.startswith("한식"):
        scores["전통주"] += 3
    elif food.startswith("일식/해산물"):
        scores["사케"] += 3
    elif food.startswith("서양식"):
        scores["와인"] += 3
    elif food.startswith("가벼운 안주"):
        scores["위스키"] += 2
        scores["와인"] += 1
    elif food.startswith("안주 없이"):
        scores["위스키"] += 2

    recommended = max(scores, key=scores.get)
    return recommended, scores


def get_recommendation_copy(category: str):
    """
    메인 페이지에 적어둔 설명을 결과용 문구로 정리
    """
    if category == "위스키":
        title = "🥃 오늘의 추천: 위스키"
        desc = """
**위스키**는 스모키, 과일향, 곡물향…  
숙성과 캐스크에 따라 완전히 다른 얼굴을 가진 깊은 한 잔입니다.

- 진지한 대화, 혼자 정리하는 시간에 잘 어울리고  
- 하이볼로 가볍게, 온더락으로 천천히 향을 느끼며 즐길 수 있어요.
"""
    elif category == "사케":
        title = "🍶 오늘의 추천: 사케"
        desc = """
**사케**는 쌀의 단맛과 감칠맛, 부드러운 산미로  
음식과 함께할 때 진가를 드러내는 일본식 생명의 물입니다.

- 회·초밥 같은 해산물 안주와 잘 어울리고  
- 차갑게 혹은 살짝 데워서, 오늘 기분에 맞게 즐길 수 있어요.
"""
    elif category == "전통주":
        title = "🍶 오늘의 추천: 전통주"
        desc = """
**전통주**는 막걸리, 약주, 청주, 증류주까지  
곡물과 발효의 풍미를 한국적인 방식으로 풀어낸 우리의 술입니다.

- 찌개, 전, 튀김 같은 한식 안주와 찰떡궁합이고  
- 가볍게 한 잔부터 진한 증류식까지 단계적으로 즐길 수 있어요.
"""
    else:  # 와인
        title = "🍷 오늘의 추천: 와인"
        desc = """
**와인**은 포도 품종, 산지, 숙성 방식에 따라  
과일 향과 구조가 완전히 달라지는 세계의 한 잔입니다.

- 연인/친구와 분위기를 나누고 싶을 때 잘 어울리고  
- 파스타, 스테이크, 치즈와 함께하면 매력이 더 살아나요.
"""
    return title, desc


def save_result(companion, mood, abv, taste_pref, food, recommended):
    """
    통계용으로 쓰기 위한 CSV 저장
    """
    data = {
        "timestamp": [datetime.now().isoformat()],
        "companion": [companion],
        "mood": [mood],
        "abv": [abv],
        "taste_pref": [taste_pref],
        "food": [food],
        "recommended": [recommended],
    }
    df_new = pd.DataFrame(data)

    os.makedirs("data", exist_ok=True)
    csv_path = os.path.join("data", "survey_results.csv")

    if os.path.exists(csv_path):
        df_old = pd.read_csv(csv_path)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(csv_path, index=False)


if submitted:
    recommended, scores = recommend_drink(
        companion, mood, abv, taste_pref, food
    )
    save_result(companion, mood, abv, taste_pref, food, recommended)
     # 🔥 GA 이벤트: 설문 완료
    try:
        send_ga_event(
            "survey_completed",
            {
                "companion": companion,
                "mood": mood,
                "abv": abv,
                "taste_pref": taste_pref,
                "food": food,
                "recommended": recommended,
            },
        )
    except Exception:
        pass  # GA 실패해도 앱 안 죽게

    st.success("✨ 설문이 완료되었습니다. 오늘 당신에게 어울리는 한 잔은…")

    title, desc = get_recommendation_copy(recommended)
    st.markdown(f"## {title}")
    st.markdown(desc)

    with st.expander("🔎 추천 결과에 영향을 준 요소(카테고리별 점수) 보기"):
        st.write(scores)

    st.markdown("---")
    st.markdown(
        """
이제 **생명의물 메인 페이지**에서  
추천받은 술 타입에 맞는 메뉴와 자리를 골라보세요.
"""
    )

    # 🔥 통계 버튼 스타일 (일반 st.button용)
st.markdown(
    """
    <style>
    button[kind="secondary"] {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 14px 32px;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f71ff 0%, #6cc6ff 50%, #90e0ff 100%);
        color: #ffffff !important;
        font-size: 18px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 18px rgba(0, 0, 0, 0.18);
        animation: stats-pulse 1.5s infinite;
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
    }
    button[kind="secondary"]:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 14px 24px rgba(0, 0, 0, 0.22);
        color: #ffffff !important;
    }
    @keyframes stats-pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0.4);
        }
        70% {
            transform: scale(1.04);
            box-shadow: 0 0 0 16px rgba(79, 113, 255, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🔁 통계 페이지로 이동 (같은 세션에서)
cols = st.columns([1, 2, 1])
with cols[1]:
    go_stats = st.button("📊 다른 사람들 취향 통계 보러가기")
if go_stats:
    st.switch_page("pages/02_stats.py")

    # 🔁 메인으로 돌아가기 
    st.page_link("WaterOfLife.py", label="🏠 메인으로 돌아가기", icon="🏠")