import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
from pathlib import Path

# ============================================================
# 1) 페이지 설정 (항상 최상단)
st.set_page_config(
    page_title="취향 통계 | 생명의물",
    page_icon="📊",
    layout="centered",
)
# 2) 파일 경로 정의 (전환율 계산 전에 반드시 필요)
ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "survey_results.csv"
EVENT_CSV = DATA_DIR / "events.csv"

# 3) 자동 새로고침
st_autorefresh(interval=10000, key="stats_refresh")

# ============================================================
# 4) 실시간 사용자 + 조회수 시스템
# ============================================================
from realtime_users import heartbeat, cleanup_throttled, get_active_users
from page_counter import increase_page_view, get_all_page_views

# 실시간 업데이트
heartbeat()
cleanup_throttled()  # 30초에 한 번만 cleanup 실행 (realtime_users.py에서 interval 조정 가능)
active_users_count = get_active_users()

# 조회수 (세션당 1번만)
if "view_logged_stats" not in st.session_state:
    increase_page_view("통계")
    st.session_state["view_logged_stats"] = True


# ============================================================
#  UI 시작
# ============================================================
st.title("📊 생명의물 취향 통계")
st.markdown("#### 지금까지 설문에 참여한 사람들의 취향 데이터를 모아봤어요.")
st.markdown("---")

# ============================================================
# 페이지별 조회수
# ============================================================
st.subheader("📈 페이지별 조회수")

views = get_all_page_views()

if views:
    df_views = (
        pd.DataFrame(views)
        .rename(columns={"page_name": "페이지", "view_count": "조회수"})
        .sort_values("조회수", ascending=False)
    )
    st.dataframe(df_views, width="stretch")
else:
    st.info("아직 조회수 데이터가 없습니다.")

st.write(f"🔥 **현재 실시간 사용자:** {active_users_count}명")
st.markdown("---")


# ============================================================
# 전환율 계산
# ============================================================
if EVENT_CSV.exists():
    events = pd.read_csv(EVENT_CSV)

else:
    st.info("아직 이벤트 데이터가 없습니다. 설문/통계 페이지를 이용해 주세요.")
    st.stop()

if "timestamp" in events.columns:
    events["timestamp"] = pd.to_datetime(events["timestamp"])
else:
    st.warning("⚠ events.csv에 'timestamp' 컬럼이 없어 시간대/재방문 통계가 제한될 수 있습니다.")

st.subheader("🔁 유입 → 설문 → 통계 흐름 분석 (Funnel)")
st.markdown("`client_id` 기준으로 설문 완료 후 통계 페이지까지 도달한 비율을 계산합니다.")

# 유입 세션: events에 등장한 client_id 전체
all_clients = set(events["client_id"]) if "client_id" in events.columns else set()

survey_clients = set(events.loc[events["event"] == "survey_completed", "client_id"])
stats_clients = set(events.loc[events["event"] == "stats_viewed", "client_id"])

total_inflow = len(all_clients)
total_survey = len(survey_clients)
total_stats = len(survey_clients & stats_clients)

def ratio(part, whole):
    return (part / whole * 100) if whole > 0 else 0.0

funnel_data = [
    {"단계": "유입(홈)", "세션 수": total_inflow, "전 단계 대비 전환율(%)": 100.0},
    {"단계": "설문 완료", "세션 수": total_survey, "전 단계 대비 전환율(%)": ratio(total_survey, total_inflow)},
    {"단계": "통계 페이지 방문", "세션 수": total_stats, "전 단계 대비 전환율(%)": ratio(total_stats, total_survey)},
]

df_funnel = pd.DataFrame(funnel_data)
st.dataframe(df_funnel, width="stretch")

st.bar_chart(df_funnel.set_index("단계")["세션 수"])
st.markdown("---")

# 체류시간 분포
st.subheader("설문 완료 → 통계 페이지 진입까지 소요 시간 분포")

if "timestamp" in events.columns:
    # 설문 완료 & 통계 방문이 모두 있는 client만 대상
    survey_ev = events[events["event"] == "survey_completed"][["client_id", "timestamp"]]
    stats_ev = events[events["event"] == "stats_viewed"][["client_id", "timestamp"]]

    # 각 client_id별 최초 설문 완료 시각, 최초 통계 방문 시각
    survey_first = survey_ev.groupby("client_id")["timestamp"].min()
    stats_first = stats_ev.groupby("client_id")["timestamp"].min()

    joined = (
        pd.concat(
            [
                survey_first.rename("survey_time"),
                stats_first.rename("stats_time"),
            ],
            axis=1
        )
        .dropna()  # 둘 다 있는 client만
    )

    if not joined.empty:
        joined["diff_sec"] = (joined["stats_time"] - joined["survey_time"]).dt.total_seconds()
        joined["diff_min"] = joined["diff_sec"] / 60

        st.write(f"분석 대상 세션 수: **{len(joined)}**")

        st.subheader("요약 통계")
        st.dataframe(
            joined["diff_min"].describe()[["count", "mean", "50%", "max"]]
            .rename({"count": "개수", "mean": "평균(분)", "50%": "중앙값(분)", "max": "최대(분)"})
            .to_frame("값"),
            width="stretch",
        )

        # 간단한 히스토그램용 bin
        bins = [0, 1, 3, 5, 10, 30, 60, 9999]
        labels = ["0~1분", "1~3분", "3~5분", "5~10분", "10~30분", "30~60분", "60분 이상"]
        joined["bucket"] = pd.cut(joined["diff_min"], bins=bins, labels=labels, right=False)

        bucket_counts = joined["bucket"].value_counts().sort_index().reset_index()
        bucket_counts.columns = ["구간", "세션 수"]

        st.subheader("⏱ 설문→통계 이동 소요시간 구간별 세션 수")
        st.dataframe(bucket_counts, width="stretch")
        st.bar_chart(bucket_counts.set_index("구간")["세션 수"])
    else:
        st.info("설문 완료와 통계 페이지 방문이 모두 있는 세션이 아직 없습니다.")
else:
    st.info("timestamp 컬럼이 없어 체류 시간 분석이 어렵습니다.")
st.markdown("---")

# ============================================================
# 8) 설문 데이터 로드
# ============================================================
if not CSV_PATH.exists():
    st.warning("아직 설문 데이터가 없습니다!")
    st.page_link("pages/01_survey.py", label="🍸 설문하러 가기", icon="🍸")
    st.stop()

df = pd.read_csv(CSV_PATH)


# ============================================================
# 9) 1. 전체 요약
# ============================================================
total_count = len(df)
mean_abv = df["abv"].mean() if "abv" in df.columns and len(df) > 0 else None

st.subheader("설문 전체 요약")

col1, col2 = st.columns(2)
with col1:
    st.metric("총 설문 응답 수", f"{total_count}명")

with col2:
    st.metric("평균 선호 도수", f"{mean_abv:.1f}도" if mean_abv else "-")

st.markdown("---")


# ============================================================
# 10) 2. 추천 술 타입 분포
# ============================================================
st.subheader("3. 추천 술 타입 vs 분위기(무드) 상관 분석")
if CSV_PATH.exists():
    df_survey = pd.read_csv(CSV_PATH)
else:
    df_survey = None
    
if df_survey is not None and {"mood", "recommended"}.issubset(df_survey.columns):
    mood_rec = df_survey.groupby(["mood", "recommended"]).size().reset_index(name="count")
    pivot_count = mood_rec.pivot(index="mood", columns="recommended", values="count").fillna(0).astype(int)

    st.subheader("🔢 분위기 × 추천 술 타입 (개수)")
    st.dataframe(pivot_count, width="stretch")

    # 분위기(mood)별 비율(%)
    pivot_ratio = pivot_count.div(pivot_count.sum(axis=1), axis=0) * 100
    pivot_ratio = pivot_ratio.round(1)

    st.subheader("📊 분위기 × 추천 술 타입 (행 기준 비율 %)")
    st.dataframe(pivot_ratio, width="stretch")

    st.markdown(
        """
        - 각 분위기별로 어떤 술 타입 비율이 높은지 확인할 수 있습니다.  
        - 예: `선물할거에요`에서 위스키 비중이 60% 이상인지 등.
        """
    )
else:
    st.info("설문 데이터에 'mood' 혹은 'recommended' 컬럼이 없어 분석할 수 없습니다.")
st.markdown("---")

# ============================================================
# 11) 3. 분위기 × 추천 패턴
# ============================================================
st.subheader("분위기/목적별 추천 패턴")

if "mood" in df.columns and "recommended" in df.columns:
    mood_rec = df.groupby(["mood", "recommended"]).size().reset_index(name="count")
    pivot = mood_rec.pivot(index="mood", columns="recommended", values="count").fillna(0).astype(int)

    st.markdown("##### 분위기 × 추천 술 타입 테이블")
    st.dataframe(pivot, width="stretch")
else:
    st.info("교차 분석에 필요한 컬럼이 없습니다.")

st.markdown("---")


# ============================================================
# 12) 4. 안주/음식
# ============================================================
st.subheader("어떤 안주를 원하나요?")

if "food" in df.columns:
    food_counts = df["food"].value_counts().rename_axis("안주/음식").reset_index(name="응답 수")

    st.dataframe(food_counts, width="stretch")
    st.bar_chart(food_counts.set_index("안주/음식")["응답 수"])
else:
    st.info("안주 데이터가 없어 분포를 표시할 수 없습니다.")

st.markdown("---")


# ============================================================
# 13) 5. 인사이트
# ============================================================
st.subheader("데이터 기반 인사이트")

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
