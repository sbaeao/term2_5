from supabase_client import supabase
import uuid
import streamlit as st
from datetime import datetime, timezone, timedelta
import httpx  # ReadError 잡기 위해 필요
import time

TIMEOUT = 60  # 1분


# ---------------------------- #
#        USER ID 생성
# ---------------------------- #

def get_user_id():
    """세션별 고유 사용자 ID"""
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = str(uuid.uuid4())
    return st.session_state["user_id"]


# ---------------------------- #
#        HEARTBEAT
# ---------------------------- #

def heartbeat():
    """현재 사용자 heartbeat 갱신"""
    user_id = get_user_id()
    now = datetime.now(timezone.utc).isoformat()

    try:
        supabase.table("realtime_users").upsert({
            "user_id": user_id,
            "last_seen": now,
        }).execute()
    except Exception as e:
        # Supabase 오류 → 앱 죽지 않도록 무시
        print("[heartbeat] ERROR:", repr(e))

    return user_id


# ---------------------------- #
#        CLEANUP (안전 버전)
# ---------------------------- #

def cleanup():
    """60초 이상 지난 사용자 삭제 (안전 처리)"""
    now = datetime.now(timezone.utc)

    try:
        result = supabase.table("realtime_users").select("*").execute()
    except Exception as e:
        print("[cleanup] 오류 발생 - cleanup 스킵:", repr(e))
        return  # 실패해도 앱은 계속 돌아가야 함

    # 정상 조회되면 정리 로직 수행
    for row in result.data:
        try:
            last_seen = datetime.fromisoformat(row["last_seen"])
        except Exception:
            continue

        diff = (now - last_seen).total_seconds()

        if diff > TIMEOUT:
            try:
                supabase.table("realtime_users") \
                    .delete() \
                    .eq("user_id", row["user_id"]) \
                    .execute()
            except Exception as e:
                print("[cleanup] 삭제 실패:", repr(e))
                continue


# ---------------------------- #
#        CLEANUP 실행 제한
# ---------------------------- #

def cleanup_throttled(interval_seconds=30):
    """Streamlit rerun을 고려해 cleanup을 interval 초마다 1번만 실행"""
    if "last_cleanup" not in st.session_state:
        st.session_state["last_cleanup"] = datetime.min

    now = datetime.now()
    last = st.session_state["last_cleanup"]

    if (now - last).total_seconds() > interval_seconds:
        cleanup()
        st.session_state["last_cleanup"] = now


# ---------------------------- #
#     ACTIVE USERS (캐시)
# ---------------------------- #

_last_active_users = None
_last_active_users_time = 0

def get_active_users():
    global _last_active_users, _last_active_users_time
    now = time.time()

    # 15초 캐시
    if _last_active_users is not None and (now - _last_active_users_time) < 15:
        return _last_active_users

    try:
        result = supabase.table("realtime_users").select("user_id").execute()
        count = len(result.data)
    except Exception as e:
        print("[get_active_users] 조회 실패:", repr(e))
        return _last_active_users or 0   # 실패 시 마지막 값 유지

    # 캐싱
    _last_active_users = count
    _last_active_users_time = now

    return count
