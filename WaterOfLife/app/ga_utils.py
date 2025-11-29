# app/ga_utils.py
import streamlit as st
import streamlit.components.v1 as components
import uuid
import requests
import logging
from sys import stdout
import os

# 🔹 secrets 에서 설정 읽기
try:
    GA_ID = st.secrets["ga"]["measurement_id"]
    GA_API_SECRET = st.secrets["ga"]["api_secret"]
    GA_ENABLED = True
except Exception:
    GA_ENABLED = False


def inject_ga(page_title: str, page_path: str):
    """
    각 페이지 맨 위에서 한 번만 호출.
    gtag.js 를 주입하고 page_view 를 자동으로 쏨.
    """
    if not GA_ENABLED:
        return

    ga_js = (
        """
        <!-- Google tag (gtag.js) -->
        """
        + f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>\n'
        + f"""
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){{dataLayer.push(arguments);}}
          gtag('js', new Date());

          // 기본 page_view
          gtag('config', '{GA_ID}', {{
            'page_title': '{page_title}',
            'page_path': '{page_path}'
          }});
        </script>
        """
    )

    # head 에 직접 넣을 수는 없어서, 페이지 최상단에서 0px iframe으로 주입
    components.html(ga_js, height=0)


def send_ga_event(event_name: str, params: dict | None = None):
    """
    Measurement Protocol 로 커스텀 이벤트 전송 (survey_completed, stats_viewed 등)
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


logging.basicConfig(level=logging.INFO, stream=stdout)
log = logging.getLogger(__name__)

# Streamlit 패키지 폴더 찾기
streamlit_package_dir = os.path.dirname(streamlit.__file__)
index_path = os.path.join(streamlit_package_dir, "static", "index.html")

# 현재 파일 기준 head.html 경로
head_content_path = os.path.join(os.path.dirname(__file__), "head.html")


def customize_index_html():
    log.info(f"Using index.html at: {index_path}")
    log.info(f"Using head.html at: {head_content_path}")

    # 원래 index.html 읽어오기
    with open(index_path, "r", encoding="utf-8") as f:
        index_html = f.read()

    # 우리가 만든 head.html 읽어오기
    with open(head_content_path, "r", encoding="utf-8") as f:
        head_content = f.read()

    # </head> 바로 앞에 GA 코드 삽입
    if "</head>" in index_html:
        index_html = index_html.replace("</head>", f"{head_content}\n</head>")
    else:
        log.warning("</head> 태그를 index.html에서 찾지 못했습니다.")

    # (선택) 타이틀 변경도 가능
    index_html = index_html.replace(
        "<title>Streamlit</title>",
        "<title>My Streamlit App</title>",
    )

    # 다시 저장
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(index_html)

    log.info("index.html에 Google tag 삽입 완료!")


# 이 모듈이 import될 때 바로 실행
customize_index_html()