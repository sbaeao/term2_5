import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from pathlib import Path
from realtime_users import heartbeat, cleanup, get_active_users
from page_counter import increase_page_view, get_all_page_views

# 실시간 사용자 유지
heartbeat()
cleanup()

# 페이지 조회수 증가
increase_page_view("통계")

active_users_count = get_active_users()

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="취향 통계 | 생명의물",
    page_icon="📊",
    layout="centered",
)

# 자동 새로고침
st_autorefresh(interval=5000, key="stats_refresh")


# ─────────────────────────────────────────────
# 파일 경로 설정
# ─────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "survey_results.csv"
EVENT_CSV = DATA_DIR / "events.csv"


# ─────────────────────────────────────────────
# UI 시작
# ─────────────────────────────────────────────
st.title("📊 생명의물 취향 통계")
st.markdown("#### 지금까지 설문에 참여한 사람들의 취향 데이터를 모아봤어요.")
st.markdown("---")

# 실시간 카운터 표시
st.subheader("📈 페이지별 조회수")

from page_counter import get_all_page_views

views = get_all_page_views()

if views:
    df_views = (
        pd.DataFrame(views)
        .rename(columns={"page_name": "페이지", "view_count": "조회수"})
        .sort_values("조회수", ascending=False)
    )
    st.dataframe(df_views, use_container_width=True)
    st.write(f"🔥 **현재 실시간 사용자:** {active_users_count}명")
else:
    st.info("아직 조회수 데이터가 없습니다.")

# 🔥 전환율 계산
if EVENT_CSV.exists():
    events = pd.read_csv(EVENT_CSV)

    survey_clients = set(events.loc[events["event"] == "survey_completed", "client_id"])
    stats_clients = set(events.loc[events["event"] == "stats_viewed", "client_id"])

    total_survey = len(survey_clients)
    total_stats = len(survey_clients & stats_clients)

    conversion_rate = (total_stats / total_survey * 100) if total_survey > 0 else 0.0

    st.markdown(
        f"""
        ### 🔁 설문 → 통계 페이지 전환율

        - 설문 완료 세션 수: **{total_survey}**
        - 통계 페이지까지 온 세션 수: **{total_stats}**
        - 전환율: **{conversion_rate:.1f}%**
        """
    )
else:
    st.info("아직 이벤트 데이터가 없습니다. 설문/통계 페이지를 이용해 주세요.")
    st.stop()

# ─────────────────────────────────────────────
# 설문 데이터 로드
# ─────────────────────────────────────────────
if not CSV_PATH.exists():
    st.warning("아직 설문 데이터가 없습니다!")
    st.page_link("pages/01_survey.py", label="🍸 설문하러 가기", icon="🍸")
    st.stop()

df = pd.read_csv(CSV_PATH)

# ─────────────────────────────────────────────
# 1. 전체 요약
# ─────────────────────────────────────────────
total_count = len(df)
mean_abv = df["abv"].mean() if "abv" in df.columns and len(df) > 0 else None

st.subheader("1. 전체 요약")

col1, col2 = st.columns(2)
with col1:
    st.metric("총 설문 응답 수", f"{total_count}명")

with col2:
    st.metric("평균 선호 도수", f"{mean_abv:.1f}도" if mean_abv else "-")

st.markdown("---")

# ─────────────────────────────────────────────
# 2. 추천 술 타입 분포
# ─────────────────────────────────────────────
st.subheader("2. 추천 술 타입 분포")

if "recommended" in df.columns:
    rec_counts = df["recommended"].value_counts().rename_axis("술 타입").reset_index(name="응답 수")
    rec_counts = rec_counts.sort_values("술 타입")

    st.dataframe(rec_counts, use_container_width=True)
    st.bar_chart(rec_counts.set_index("술 타입")["응답 수"])
else:
    st.info("추천 결과 데이터가 없어 분포를 표시할 수 없습니다.")

st.markdown("---")

# ─────────────────────────────────────────────
# 3. 분위기/목적별 교차 분석
# ─────────────────────────────────────────────
st.subheader("3. 분위기/목적별 추천 패턴")

if "mood" in df.columns and "recommended" in df.columns:
    mood_rec = df.groupby(["mood", "recommended"]).size().reset_index(name="count")
    pivot = mood_rec.pivot(index="mood", columns="recommended", values="count").fillna(0).astype(int)

    st.markdown("##### 분위기 × 추천 술 타입 테이블")
    st.dataframe(pivot, use_container_width=True)
else:
    st.info("교차 분석에 필요한 컬럼이 없습니다.")

st.markdown("---")

# ─────────────────────────────────────────────
# 4. 안주/음식
# ─────────────────────────────────────────────
st.subheader("4. 어떤 안주를 원하나요?")

if "food" in df.columns:
    food_counts = df["food"].value_counts().rename_axis("안주/음식").reset_index(name="응답 수")

    st.dataframe(food_counts, use_container_width=True)
    st.bar_chart(food_counts.set_index("안주/음식")["응답 수"])
else:
    st.info("안주 데이터가 없어 분포를 표시할 수 없습니다.")

st.markdown("---")

# ─────────────────────────────────────────────
# 5. 인사이트
# ─────────────────────────────────────────────
st.subheader("5. 데이터 기반 인사이트")

st.markdown(
    """
- **추천 술 타입 분포** → 어떤 술이 가장 많이 추천되는지 확인 가능  
- **분위기/목적별 추천 차이** → 어떤 상황에서 어떤 술을 선호하는지 알 수 있음  
- **안주 선호 분포** → 메뉴 기획에 유용  
"""
)

st.markdown("---")
st.page_link("WaterOfLife.py", label="🏠 메인 페이지로 돌아가기", icon="🏠")
st.page_link("pages/01_survey.py", label="🍸 설문 다시 하러 가기", icon="🍸")
