from supabase_client import supabase
import uuid
import streamlit as st
from datetime import datetime, timezone

TIMEOUT = 60  # 1분


def get_user_id():
    """세션별 고유 사용자 ID"""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


def heartbeat():
    """현재 사용자 heartbeat 갱신"""
    user_id = get_user_id()
    now = datetime.now(timezone.utc).isoformat()

    supabase.table("realtime_users").upsert({
        "user_id": user_id,
        "last_seen": now,
    }).execute()

    return user_id


def cleanup():
    """60초 이상 지난 사용자 삭제"""
    now = datetime.now(timezone.utc)

    # DB에서 모든 사용자 가져오기
    result = supabase.table("realtime_users").select("*").execute()

    for row in result.data:
        last_seen = datetime.fromisoformat(row["last_seen"])
        diff = (now - last_seen).total_seconds()

        if diff > TIMEOUT:
            supabase.table("realtime_users") \
                .delete() \
                .eq("user_id", row["user_id"]) \
                .execute()


def get_active_users():
    """현재 실시간 사용자 수"""
    result = supabase.table("realtime_users").select("user_id").execute()
    return len(result.data)
