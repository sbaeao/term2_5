import json
from pathlib import Path

# data/page_views.json 경로
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

VIEW_FILE = DATA_DIR / "page_views.json"


def load_views():
    """페이지별 조회수 로드 (없으면 초기화)"""
    if not VIEW_FILE.exists():
        VIEW_FILE.write_text(json.dumps({}))
    try:
        return json.loads(VIEW_FILE.read_text())
    except:
        return {}


def save_views(data):
    """조회수 저장"""
    VIEW_FILE.write_text(json.dumps(data, indent=2))


def increase_view(page_name: str, is_autorefresh=False):
    """오토리프레시가 아닌 경우에만 조회수 증가"""
    if is_autorefresh:
        return load_views()  # 증가 없이 반환

    data = load_views()
    data[page_name] = data.get(page_name, 0) + 1
    save_views(data)
    return data
