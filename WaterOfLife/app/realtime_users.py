from supabase_client import supabase
import time
import uuid
import streamlit as st

TIMEOUT = 60  # 1분


def get_user_id():
    """세션별 고유 사용자 ID"""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


def heartbeat():
    """현재 사용자 heartbeat 갱신"""
    user_id = get_user_id()
    now = int(time.time())

    supabase.table("realtime_users").upsert({
        "user_id": user_id,
        "last_seen": supabase.func.to_timestamp(now),
    }).execute()

    return user_id


def cleanup():
    """60초 이상 지난 사용자 삭제"""
    now = int(time.time())
    threshold = now - TIMEOUT

    supabase.table("realtime_users") \
        .delete() \
        .lt("last_seen", supabase.func.to_timestamp(threshold)) \
        .execute()


def get_active_users():
    """현재 실시간 사용자 수"""
    result = supabase.table("realtime_users").select("user_id").execute()
    return len(result.data)
