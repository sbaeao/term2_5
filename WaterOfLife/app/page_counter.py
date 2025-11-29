from supabase_client import supabase


def increase_page_view(page_name: str):
    """특정 페이지의 조회수 +1"""
    supabase.rpc("increment_page_view", {"p_page_name": page_name}).execute()


def get_all_page_views():
    """전체 페이지별 조회수 불러오기"""
    result = supabase.table("page_views").select("*").execute()
    return result.data
