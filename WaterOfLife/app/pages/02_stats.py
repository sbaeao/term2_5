import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import requests
import uuid

# 🔥 GA 공통 유틸
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


base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
csv_path = os.path.join(base_dir, "data", "survey_results.csv")

# 🔥 GA page_view: stats + 이벤트
inject_ga("stats")

try:
    send_ga_event("stats_viewed")
except Exception:
    pass

# 페이지 기본 설정
st.set_page_config(
    page_title="취향 통계 | 생명의물",
    page_icon="📊",
    layout="centered",
)

st.title("📊 생명의물 취향 통계")
st.markdown("#### 지금까지 설문에 참여한 사람들의 취향 데이터를 모아봤어요.")
st.markdown("---")


# 데이터 존재 여부 체크
if not os.path.exists(csv_path):
    st.warning("아직 설문 데이터가 없습니다. 먼저 설문을 제출해 주세요!")
    st.page_link("pages/01_survey.py", label="🍸 설문하러 가기", icon="🍸")
    st.stop()

# 데이터 로드
df = pd.read_csv(csv_path)

# 기본 정보 정리
total_count = len(df)
mean_abv = df["abv"].mean() if "abv" in df.columns and len(df) > 0 else None

st.subheader("1. 전체 요약")

col1, col2 = st.columns(2)
with col1:
    st.metric("총 설문 응답 수", f"{total_count}명")

with col2:
    if mean_abv is not None:
        st.metric("평균 선호 도수", f"{mean_abv:.1f}도")
    else:
        st.metric("평균 선호 도수", "-")


st.markdown("---")

# 추천 술 타입 분포
st.subheader("2. 추천 술 타입 분포 (위스키/사케/전통주/와인)")

if "recommended" in df.columns:
    rec_counts = df["recommended"].value_counts().rename_axis("술 타입").reset_index(name="응답 수")
    rec_counts = rec_counts.sort_values("술 타입")  # 보기 좋게 정렬

    st.dataframe(rec_counts, use_container_width=True)

    st.bar_chart(
        data=rec_counts.set_index("술 타입")["응답 수"]
    )
else:
    st.info("추천 결과 데이터가 없어 분포를 표시할 수 없습니다.")


st.markdown("---")

# 분위기/목적(mood)별 추천 결과
st.subheader("3. 분위기/목적별로 어떤 술이 많이 추천되었나요?")

if "mood" in df.columns and "recommended" in df.columns:
    mood_rec = (
        df.groupby(["mood", "recommended"])
        .size()
        .reset_index(name="count")
    )

    # 피벗 테이블 형태로 변환
    pivot = mood_rec.pivot(index="mood", columns="recommended", values="count").fillna(0).astype(int)

    st.markdown("##### 분위기/목적 × 추천 술 타입 테이블")
    st.dataframe(pivot, use_container_width=True)

    st.markdown(
        """
        예를 들어,
        - `선물 할거에요` 를 선택한 사람들에게는 위스키/와인이 얼마나 추천됐는지,
        - `진지한 대화가 좋아요` 를 선택한 사람들에게는 위스키/와인이 비중이 높은지
        등을 한눈에 볼 수 있습니다.
        """
    )
else:
    st.info("분위기/목적(mood) 혹은 추천 결과 컬럼이 없어 교차분석을 표시할 수 없습니다.")


st.markdown("---")

# 안주/음식 선호 분포
st.subheader("4. 어떤 안주와 함께 마시고 싶어 할까요?")

if "food" in df.columns:
    food_counts = df["food"].value_counts().rename_axis("안주/음식").reset_index(name="응답 수")
    st.dataframe(food_counts, use_container_width=True)

    st.bar_chart(
        data=food_counts.set_index("안주/음식")["응답 수"]
    )
else:
    st.info("안주(food) 데이터가 없어 분포를 표시할 수 없습니다.")


st.markdown("---")

st.subheader("5. 데이터 기반 인사이트 예시")

st.markdown(
    """
- **추천 술 타입 분포**를 보면, 현재 설문 응답자들에게 어떤 술이 많이 추천되는지 알 수 있습니다.  
- **분위기/목적별 교차분석**을 통해,  
  - `선물 할거에요`를 선택한 사람들에게는 위스키·와인이 주로 추천되는지,  
  - `조용히 분위기만 즐기고 싶어요`를 선택한 사람들에게는 와인/사케 비중이 높은지  
  같은 패턴을 확인할 수 있습니다.  
- **안주 선호 분포**를 보면, 생명의물에서 어떤 안주/메뉴 비중을 높여야 할지에 대한 힌트를 얻을 수 있습니다.

이런 데이터를 바탕으로,  
생명의물은 **타깃 고객의 실제 취향에 맞춘 메뉴 구성과 프로모션**을 설계할 수 있습니다.
"""
)

st.markdown("---")
st.page_link("WaterOfLife.py", label="🏠 메인 페이지로 돌아가기", icon="🏠")
st.page_link("pages/01_survey.py", label="🍸 설문 다시 하러 가기", icon="🍸")
