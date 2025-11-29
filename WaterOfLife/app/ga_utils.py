# app/ga_utils.py
import streamlit as st
import os
import streamlit.components.v1 as components
import uuid
import requests
import time


# 🔹 secrets 에서 설정 읽기
try:
    GA_ID = st.secrets["ga"]["measurement_id"]
    GA_API_SECRET = st.secrets["ga"]["api_secret"]
    GA_ENABLED = True
except Exception:
    GA_ENABLED = False

GA_ENDPOINT = (
    f"https://www.google-analytics.com/mp/collect"
    f"?measurement_id={GA_ID}&api_secret={GA_API_SECRET}"
)


def generate_ids():
    """client_id, session_id 생성 (브라우저 쿠키 대체)"""
    client_id = str(uuid.uuid4())      # 유저 고유 식별 (쿠키 역할)
    session_id = int(time.time())      # 세션 ID = 현재 Unix timestamp
    return client_id, session_id


def send_session_start(client_id, session_id, page_title, page_location):
    """GA4 세션 시작 이벤트 전송"""
    payload = {
        "client_id": client_id,
        "events": [{
            "name": "session_start",
            "params": {
                "session_id": session_id,
                "page_title": page_title,
                "page_location": page_location,
            }
        }]
    }
    requests.post(GA_ENDPOINT, json=payload, timeout=3)


def send_page_view(client_id, session_id, page_title, page_location):
    """page_view 이벤트 전송"""
    payload = {
        "client_id": client_id,
        "events": [{
            "name": "page_view",
            "params": {
                "session_id": session_id,
                "page_title": page_title,
                "page_location": page_location,
            }
        }]
    }
    requests.post(GA_ENDPOINT, json=payload, timeout=3)


def send_custom_event(name, params=None):
    """추가 커스텀 이벤트 (기존 stats_viewed 등)"""
    if params is None:
        params = {}

    client_id, session_id = generate_ids()

    payload = {
        "client_id": client_id,
        "events": [{
            "name": name,
            "params": params
        }]
    }

    requests.post(GA_ENDPOINT, json=payload, timeout=3)
