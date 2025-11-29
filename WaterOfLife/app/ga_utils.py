# app/ga_utils.py
import streamlit as st
import os
import streamlit.components.v1 as components
import uuid
import requests
import logging
from sys import stdout


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

