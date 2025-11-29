import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from pathlib import Path
from datetime import datetime  
import base64
import uuid
from view_counter import increase_view

is_autorefresh = False
increase_view("설문_추천", is_autorefresh)



ROOT_DIR = Path(__file__).resolve().parents[2]   # term2_5/
DATA_DIR = ROOT_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATH = DATA_DIR / "survey_results.csv"
EVENT_CSV = DATA_DIR / "events.csv"

if "client_id" not in st.session_state:
    st.session_state["client_id"] = str(uuid.uuid4())

CLIENT_ID = st.session_state["client_id"]

APP_DIR = Path(__file__).resolve().parents[1]   # .../WaterOfLife/app
IMG_DIR = APP_DIR / "images"

def img(path: str) -> str:
    """images 폴더 기준 경로 헬퍼"""
    return str(IMG_DIR / path)

def img_to_base64(path: str) -> str:
    """로컬 이미지 파일을 base64 문자열로 변환"""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data
def load_springbank_images_b64():
    filenames = [
        "springbank1.jpeg",
        "springbank2.jpeg",
        "springbank3.jpeg",
        "springbank4.jpeg",
        "springbank5.jpeg",
        "springbank6.jpeg",
        "springbank7.jpeg",
        "springbank8.jpeg",
        "springbank9.jpeg",
    ]
    result = []
    for name in filenames:
        path = IMG_DIR / name
        ext = path.suffix.lower()
        mime = "image/png" if ext == ".png" else "image/jpeg"
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        result.append(f"data:{mime};base64,{b64}")
    return result

# 스크롤바를 좀 더 눈에 띄게
st.markdown(
    """
    <style>
    .h-scroll-gallery::-webkit-scrollbar {
        height: 8px;
    }
    .h-scroll-gallery::-webkit-scrollbar-thumb {
        background: rgba(180, 180, 180, 0.9);
        border-radius: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🍸 나에게 맞는 술 추천")

st.markdown("#### 몇 가지 질문만으로, 오늘 당신에게 딱 맞는 한 잔을 추천해드릴게요.")
st.markdown("---")

st.markdown(
    """
    <style>

    /* 🔥 st.radio 위쪽 기본 간격 제거 */
    div.stRadio > div {
        margin-top: 0px !important;
        padding-top: 0px !important;
    }

    /* 🔥 subheader 역할 직접 구현용 (간격 조절 자유) */
    .question-title {
        font-size: 1.05rem;
        font-weight: 600;
        margin-bottom: 4px;
        margin-top: 12px;
    }

    /* 🔥 설문 제출 버튼 스타일 (form_submit_button) */
    button[kind="secondaryFormSubmit"] {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 18px 40px;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f71ff 0%, #6cc6ff 50%, #90e0ff 100%);
        color: #ffffff !important;
        font-size: 20px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.18);
        animation: pulse 1.5s infinite;
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
    }

    button[kind="secondaryFormSubmit"]:hover {
        transform: translateY(-3px) scale(1.03);
        box-shadow: 0 14px 26px rgba(0, 0, 0, 0.22);
        color: #ffffff !important;
    }

    /* 🔥 애니메이션 */
    @keyframes pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0.7);
        }
        70% {
            transform: scale(1.05);
            box-shadow: 0 0 0 18px rgba(79, 113, 255, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0);
        }
    }

    </style>
    """,
    unsafe_allow_html=True
)

with st.form("survey_form"):
    # Q1. 동반자
    st.subheader("1. 오늘 누구와 마실 계획인가요?")
    companion = st.radio(
        "",
        ["혼자", "연인/썸", "친구/동기", "직장동료/회식"],
        index=1,
        label_visibility="collapsed",
    )

    # Q2. 분위기/목적
    st.subheader("2. 오늘의 분위기/목적은 어떤가요?")
    mood = st.radio(
        "",
        [
            "가볍게 한잔 마시고 싶어요",
            "진지한 대화가 좋아요",
            "텐션 업! 신나게 마시고 싶어요",
            "조용히 분위기만 즐기고 싶어요",
            "선물 할거에요"
        ],
        label_visibility="collapsed",
    )

    # Q3. 도수
    st.subheader("3. 오늘 괜찮다고 느끼는 술의 도수는 어느 정도인가요?")
    abv = st.slider("도수(°)", min_value=5, max_value=60, value=12)

    # Q4. 맛/스타일
    st.subheader("4. 어떤 맛/스타일을 좋아하세요?")
    taste_pref = st.radio(
        "",
        [
            "달콤한 맛이 좋아요",
            "강하고 묵직한 맛이 좋아요",
            "상큼/깔끔한 스타일이 좋아요",
            "잘 모르겠어요, 추천에 맡길래요",
        ],
        label_visibility="collapsed",
    )

    # Q5. 안주/음식
    st.subheader("5. 어떤 종류의 안주와 함께 마시고 싶나요?")
    food = st.radio(
        "",
        [
            "한식 안주 (찌개, 전, 튀김, 고기 등)",
            "일식/해산물 (초밥, 사시미 등)",
            "서양식 (파스타, 스테이크, 치즈 등)",
            "가벼운 안주/간단한 스낵",
            "안주 없이 술 위주로 마실래요",
        ],
        label_visibility="collapsed",
    )

    # 🔥 버튼 가운데 정렬
    st.markdown(
        "<div style='text-align: center; margin-top: 24px;'>",
        unsafe_allow_html=True,
    )
    submitted = st.form_submit_button("🍷 내 추천 결과 보기")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")


def recommend_drink(companion, mood, abv, taste_pref, food):
    """
    5개 질문을 바탕으로 위스키/사케/전통주/와인 중 하나를 추천하는 점수 로직
    """
    scores = {"위스키": 0, "사케": 0, "전통주": 0, "와인": 0}

    # 1) 동반자
    if companion == "혼자":
        scores["위스키"] += 2
        scores["전통주"] += 1
    elif companion == "연인/썸":
        scores["와인"] += 2
        scores["사케"] += 1
    elif companion == "친구/동기":
        scores["전통주"] += 2
        scores["와인"] += 1
    elif companion == "직장동료/회식":
        scores["전통주"] += 2
        scores["위스키"] += 1

    # 2) 분위기/목적
    if mood == "가볍게 한잔 마시고 싶어요":
        scores["사케"] += 1
        scores["전통주"] += 1
        scores["와인"] += 1
        scores["위스키"] += 1
    elif mood == "진지한 대화가 좋아요":
        scores["위스키"] += 2
        scores["와인"] += 2
    elif mood == "텐션 업! 신나게 마시고 싶어요":
        scores["위스키"] += 1
        scores["전통주"] += 2
    elif mood == "조용히 분위기만 즐기고 싶어요":
        scores["와인"] += 2
        scores["사케"] += 2
    elif mood == "선물 할거에요":
        scores["와인"] += 2
        scores["위스키"] += 2    

    # 3) 도수
    if abv <= 10:
        scores["전통주"] += 1
        scores["와인"] += 1
    elif 11 <= abv <= 30:
        scores["사케"] += 2
        scores["와인"] += 2
        scores["전통주"] += 1
    else:
        scores["위스키"] += 2

    # 4) 맛/스타일
    if taste_pref == "달콤한 맛이 좋아요":
        scores["사케"] += 2
        scores["전통주"] += 2
        scores["와인"] += 1
        scores["위스키"] += 1
    elif taste_pref == "강하고 묵직한 맛이 좋아요":
        scores["위스키"] += 2
        scores["와인"] += 1
    elif taste_pref == "상큼/깔끔한 스타일이 좋아요":
        scores["사케"] += 2
        scores["전통주"] += 1
        scores["와인"] += 1
    # "잘 모르겠어요"면 다른 요소로만 판단

    # 5) 안주/음식
    if food.startswith("한식"):
        scores["전통주"] += 3
    elif food.startswith("일식/해산물"):
        scores["사케"] += 3
    elif food.startswith("서양식"):
        scores["와인"] += 3
    elif food.startswith("가벼운 안주"):
        scores["위스키"] += 2
        scores["와인"] += 1
    elif food.startswith("안주 없이"):
        scores["위스키"] += 2

    recommended = max(scores, key=scores.get)
    return recommended, scores


def get_recommendation_copy(category: str):
    '''
    if category == "위스키":
        st.markdown("## 🥃 오늘의 추천: 위스키")

        st.markdown("""
        **위스키**는 스모키, 과일향, 곡물향…  
        숙성과 캐스크에 따라 완전히 다른 얼굴을 가진 깊은 한 잔입니다.
                    
        **LiqureMate**에서 두 가지의 특별한 위스키를 추천해 드릴게요.
        """)

        st.image(img("springbank10yo.jpg"), width=400)

        st.markdown(
        """
        첫 번째는 스프링뱅크 정규 라인업의 포문을 여는 완벽한 소개서 **스프링뱅크 10년** 위스키입니다.
        **스프링뱅크 10년**은 2.5회 증류를 거친 라이트한 피트 위스키입니다.
        이 위스키의 향을 먼저 맡아보시면 약한 피트와 바닐라, 그리고 몰트의 달콤함을 느낄 수 있습니다.
        입안에서는 폭발적으로 올라오는 다양한 과일의 캐릭터, 육두구와 계피류의 스파이시 풍미가 피어오릅니다.
        이후 달고 짠 재미있는 피니시가 긴 여운으로 남습니다.
        처음 한 모금부터 마지막 피니시까지 입안 가득 완벽한 균형을 자랑합니다.
                    
        스프링뱅크 위스키와의 첫 만남이시라면, **스프링뱅크 10년**의 달콤하고 짠 균형미로 여러분을 초대합니다.
        """)
        imgs = [
            img("springbank1.png"),
            img("springbank2.jpeg"),
            img("springbank3.jpeg"),
            img("springbank4.jpeg"),
        ]

        # =========================
        # 옆으로 넘기는 이미지 슬라이드 (안정형)
        # =========================

        spring_imgs = [
            img("springbank1.png"),
            img("springbank2.jpeg"),
            img("springbank3.jpeg"),
            img("springbank4.jpeg"),
        ]

        # ✅ 세션 상태 초기화 (가장 중요)
        if "spring_idx" not in st.session_state:
            st.session_state.spring_idx = 0

        # ✅ 현재 이미지
        current_img = spring_imgs[st.session_state.spring_idx]

        # ✅ 이미지 출력
        st.image(current_img, width=420)

        # ✅ 좌/우 버튼
        col_l, col_c, col_r = st.columns([1, 6, 1])

        with col_l:
            if st.button("◀", key="spring_prev"):
                st.session_state.spring_idx -= 1
                if st.session_state.spring_idx < 0:
                    st.session_state.spring_idx = len(spring_imgs) - 1
                st.rerun()

        with col_r:
            if st.button("▶", key="spring_next"):
                st.session_state.spring_idx += 1
                if st.session_state.spring_idx >= len(spring_imgs):
                    st.session_state.spring_idx = 0
                st.rerun()

        st.markdown("""
        - 진지한 대화, 혼자 정리하는 시간에 잘 어울리고  
        - 하이볼로 가볍게, 온더락으로 천천히 향을 느끼며 즐길 수 있어요.
        """)
    '''
    if category == "위스키":
        st.markdown("## 🥃 오늘의 추천: 위스키")

        st.markdown("""
    **위스키**는 한 잔 안에 스모키함, 과일향, 곡물향이 켜켜이 쌓여 있는 술입니다.  
    증류와 숙성, 캐스크의 종류에 따라 전혀 다른 표정을 보여주기 때문에  
    마실수록 새로운 매력이 드러나는 ‘탐구형 술’이기도 하죠.

    오늘은 그중에서도 **위스키 마니아들에게 사랑받는 스프링뱅크 10년**과  
    그 개성을 한눈에 느낄 수 있는 몇 장의 이미지를 함께 소개해 드릴게요.
    """)
        
        # 메인 병 사진
        st.image(img("springbank10yo.jpg"), width=400)

        st.markdown(
            """
    ### 🥃 스프링뱅크 10년 — 스프링뱅크의 문을 여는 첫 한 잔

    **스프링뱅크 10년**은 증류소의 개성을 가장 균형 있게 보여주는 정규 라인업의 시작점입니다.  
    2.5회 증류를 거친 가벼운 피트 위스키로, 아래와 같은 특징을 가지고 있어요.

    - 코에서는 은은한 피트 향과 함께 바닐라, 곡물의 달콤함이 먼저 올라오고  
    - 입안에서는 잘 익은 과일, 육두구·계피 계열의 스파이시함이 폭발하듯 퍼지며  
    - 마지막에는 **달고 짠 오묘한 피니시**가 길게 이어집니다.

    처음 한 모금부터 피니시까지 큰 굴곡 없이 **탄탄한 밸런스**를 유지하기 때문에,  
    스프링뱅크를 처음 만나는 분들께도 아주 좋은 시작점이 됩니다.
    """
        )
        st.markdown("### 📸 스프링뱅크의 다양한 모습 살펴보기")

        st.caption("👉 사진을 좌우로 스크롤해서 더 많은 이미지를 살펴보세요.")

        spring_sources = load_springbank_images_b64()

        img_tags = "".join(
            f'<img src="{src}" '
            f'style="height:210px; border-radius:12px; flex:0 0 auto;">'
            for src in spring_sources
        )

        gallery_html = f"""
        <div class="h-scroll-gallery" style="
            display: flex;
            overflow-x: auto;
            gap: 12px;
            padding: 12px 0 6px 0;
            scrollbar-width: thin;
            border-bottom: 1px solid rgba(255,255,255,0.08);
        ">
            {img_tags}
        </div>
        """

        st.markdown(gallery_html, unsafe_allow_html=True)

        st.markdown("""
    - 깊이 있는 대화가 필요한 날, 혼자 생각을 정리하고 싶은 날에 잘 어울리고  
    - 하이볼로 가볍게 즐기거나, 온더락으로 천천히 향을 음미하며 마시기에도 좋습니다.
    """)

    elif category == "사케":
        st.markdown("## 🍶 오늘의 추천 1: 노구치 나오히코 사케")

        st.markdown("""
        ### 사케의 신, 80년 인생을 바친 양조 장인

        1932년 노토 반도에서 태어나, 16세부터 일본 각지의 주조장에서 양조 수련을 시작한 노구치 나오히코는  
        수십 년간 최고의 품질을 추구하며 사케 양조를 이어온 ‘살아 있는 전설’입니다.  
        그는 전통 방식인 ‘야마하이’ 양조의 부활을 이끌었고,  
        2017년에는 자신의 이름을 내건 새로운 양조장인 **Noguchi Naohiko Sake Institute**를 설립해  
        젊은 세대 양조인들에게 자신의 철학과 기술을 전수하고 있습니다.

        이 사케는 단순한 술이 아니라,  
        양조자의 손끝부터 발효, 숙성에 이르는 모든 과정을 살아 숨 쉬게 만든 ‘장인의 혼’이 담긴 한 병입니다.
        """)

        st.image(img("sake.jpg"), width=400)
        st.markdown("""        ---

        ### 🌸 노구치 사케의 매력 포인트

        - 🍚 **쌀 본연의 감칠맛과 깊은 향** —  
          노토 두지(能登杜氏) 가문의 양조 전통을 계승하면서도,  
          청량하면서도 농후한 쌀맛과 부드러운 목넘김을 동시에 실현한 균형감.

        - 🌿 **산미와 부드러움의 공존** —  
          차갑게 했을 때는 깔끔하고 청량한 인상,  
          살짝 데우거나 상온에서는 감칠맛과 은은한 향이 살아나는 변화무쌍함.

        - 🥂 **음식과의 궁합이 뛰어남** —  
          회·사시미, 신선한 해산물, 가볍고 우아한 안주와 잘 어울리며,  
          미식과 분위기를 함께 즐기기에 이상적.

        - 🔄 **양조 철학이 담긴 깊이** —  
          누룩, 쌀, 물, 공기, 효모까지 모두 철저히 관찰하며  
          “쌀과 미생물에 맞추는 양조”를 철학으로 삼은 집요함.
                    
        ---
        """)

        st.markdown("## 🍶 오늘의 추천 2: 닷사이 23 (獺祭 23)")

        st.markdown("""

        ### 세계에서 가장 유명한 프리미엄 사케 중 하나

        **닷사이 23**은 일본 야마구치현의 아사히주조(旭酒造)가 만든 최고급 준마이다이긴죠 사케로,  
        **쌀을 무려 23%까지 깎아낸 극한의 정미율**로 만들어진 극도의 섬세함을 가진 사케입니다.

        전통적인 사케의 묵직함보다,  
        **과일처럼 맑고 화사한 향과 유려한 단맛**이 특징이며  
        “사케는 어렵다”는 인식을 완전히 바꿔준 상징적인 작품으로 평가받습니다.

        LiquorMate에서 **입문자에게 가장 먼저 추천**하는 사케입니다.
        """)

        st.image(img("sake2.jpg"), width=500)
        
        st.markdown("""
        ---

        ### 🌸 닷사이 23의 매력 포인트

        - 🍏 **청포도·배·사과 같은 과일향** —  
          코를 대는 순간 퍼지는 맑고 달콤한 아로마,  
          기존 사케에서 느끼기 힘든 ‘와인 같은 향의 구조’를 가지고 있습니다.

        - 💧 **물처럼 부드러운 목넘김** —  
          알코올 도수는 16도 전후지만,  
          자극 없이 미끄러지듯 넘어가는 초크리한 질감이 특징입니다.

        - 🥂 **누구나 ‘맛있다’고 느끼는 사케** —  
          사케에 익숙하지 않은 사람도 첫 모금에 바로 호감을 느끼는 타입으로,  
          선물용·데이트용·기념일용으로 모두 안정적인 선택입니다.

        - 🍣 **해산물·치즈·화이트소스 요리와 궁합 최상** —  
          회, 초밥, 가벼운 샐러드, 크림 파스타와도 조화가 뛰어납니다.
        """)

        st.markdown("""
        ✅ **이런 분께 특히 추천합니다**
        - 사케를 처음 접하는 분  
        - 향이 화사하고 깔끔한 술을 좋아하는 분  
        - 데이트, 기념일, 선물용 사케를 찾는 분  
        - “실패 없는 프리미엄 사케”를 원하시는 분
        """)

    elif category == "전통주":
        st.markdown("## 🍶 오늘의 추천: 전통주")

        st.markdown("""
            ### 한국 술의 매력을 가장 잘 보여주는 두 가지 선택

            전통주는 단순한 ‘막걸리’가 아니라,  
            쌀·누룩·물·시간이 만나 만들어낸 **한국 발효 문화의 결정체**입니다.  
            오늘은 **증류식 소주 화요와 감성적인 막걸리 복순도가**를 추천해 드릴게요.
            """)

        st.markdown("---")

        # ✅ 추천 1: 화요 41
        st.markdown("## 🥃 오늘의 전통주 추천 1: 화요 41")

        st.markdown("""
            **화요 41**은 쌀 100%로 빚어 항아리에서 숙성한 프리미엄 증류식 소주로,  
            기존 소주의 ‘알코올 자극’이 아닌 **부드럽고 깊은 쌀 향과 단맛**이 특징입니다.

            - 🔥 **도수 41도의 묵직한 바디감**
            - 🌾 **쌀 본연의 단맛과 은은한 곡물향**
            - 🪵 **항아리 숙성에서 오는 부드러운 질감**
            - 🥩 **고기, 한식 안주, 구이류와 최고의 궁합**

            스트레이트로 천천히 음미하면  
            위스키처럼 ‘향을 즐기는 술’로도 손색이 없고,  
            온더락으로 즐기면 부드러움이 더욱 살아납니다.

            ✅ **이런 분께 추천**
            - 위스키나 증류주를 좋아하는 분  
            - 회식이나 중요한 자리에서 ‘격이 다른 소주’를 찾는 분  
            - 한식 안주와 잘 어울리는 고도수 술을 원하는 분
            """)

        # 원하면 이미지 추가 가능
        st.image(img("hwayo41.png"), width=400)

        st.markdown("---")

        # ✅ 추천 2: 복순도가 손막걸리
        st.markdown("## 🍶 오늘의 전통주 추천 2: 복순도가 손막걸리")

        st.markdown("""
            **복순도가 손막걸리**는 샴페인처럼 자연 탄산이 살아 있는 프리미엄 막걸리로,  
            ‘막걸리도 이렇게 세련될 수 있다’는 인식을 만든 대표적인 전통주입니다.

            - 🍾 **자연 발효 탄산의 청량감**
            - 🍚 **부드러운 쌀 단맛 + 상큼한 산미**
            - 💧 **낮은 도수지만 풍부한 질감**
            - 🥗 **가벼운 안주, 치즈, 샐러드와도 잘 어울림**

            뚜껑을 여는 순간 터져 나오는 탄산은  
            마치 스파클링 와인을 여는 듯한 느낌을 주고,  
            첫 모금부터 끝까지 **청량하고 기분 좋은 마무리**를 제공합니다.

            ✅ **이런 분께 추천**
            - 전통주를 처음 접하는 분  
            - 달콤하고 가볍게 즐길 수 있는 술을 좋아하는 분  
            - 데이트, 기념일, 캐주얼한 자리에서 분위기를 살리고 싶은 분
            """)

        # 원하면 이미지 추가 가능
        st.image(img("boksoondoga.jpg"), width=500)

        st.markdown("""
        ---
    
        ### 🍽 전통주 추천 페어링 요약
    
        - **화요 41** → 삼겹살, 소고기, 전, 구이류, 진한 한식  
        - **복순도가 손막걸리** → 과일, 치즈, 샐러드, 가벼운 튀김
    
        오늘의 기분과 안주에 맞춰,  
        **묵직하게 즐길지 / 상큼하게 즐길지 선택해 보세요.**
        """)

    elif category == "와인":
        st.markdown("## 🍷 오늘의 추천: 와인")

        st.markdown("""
    ### 분위기와 스토리를 동시에 즐길 수 있는 두 가지 와인

    와인은 단순한 ‘술’이 아니라,  
    **향·산지·스토리·분위기까지 함께 마시는 문화의 술**입니다.  
    오늘은 **데일리 와인 1종과 재밌는 스토리를 지닌 와인 1종**을 추천해 드릴게요.
    """)

        st.markdown("---")

        # ✅ 추천 1: 브레드 앤 버터 (Bread & Butter)
        st.markdown("## 🍷 오늘의 와인 추천 1: 브레드 앤 버터 (Bread & Butter Series)")

        st.markdown("""
            **브레드 앤 버터**는 미국 캘리포니아 나파 밸리 스타일의 와인으로,  
            이름 그대로 **‘빵과 버터처럼 누구나 편하게 즐길 수 있는 와인’**을 지향하는 브랜드입니다.

            과하지 않은 오크, 부드러운 과실미, 매끄러운 질감 덕분에  
            와인을 처음 마시는 사람부터 애호가까지 모두에게 호평을 받는 **데일리 프리미엄 와인**입니다.

            - 🍑 **풍부한 과실향 + 부드러운 바닐라 노트**
            - 🧈 **오크 숙성에서 오는 크리미한 질감**
            - 💧 **떫지 않고 매끄러운 탄닌 구조**
            - 🥩 **스테이크, 파스타, 크림소스 요리와 최적의 조합**

            특히 **브레드 앤 버터 샤르도네 / 피노 누아**는  
            “와인이 어렵지 않아도 충분히 고급스러울 수 있다”는 인식을 만들어 준 대표 라인입니다.

            ✅ **이런 분께 추천**
            - 와인을 부담 없이 즐기고 싶은 분  
            - 데이트, 기념일, 저녁 식사 자리용 와인을 찾는 분  
            - 부드럽고 달콤한 과실미를 좋아하는 분
            """)

        st.image(img("bread_and_butter.png"), width=400)

        st.markdown("---")

        # ✅ 추천 2: 19 크라임즈 (19 Crimes Series)
        st.markdown("## 🍷 오늘의 와인 추천 2: 19 크라임즈 (19 Crimes Series)")

        st.markdown("""
            **19 크라임즈**는 18~19세기 영국에서 실제로 처벌받아  
            호주로 유배된 범죄자들의 실화를 콘셉트로 만든 **스토리텔링 와인**입니다.  
            라벨 속 인물의 사연과 함께 와인을 마시는 독특한 경험을 제공합니다.

            와인 스타일은 **묵직한 바디, 강한 과실미, 스파이시한 피니시**가 특징이며,  
            첫 모금부터 임팩트 있는 맛으로 인상을 강하게 남깁니다.

            - 🔥 **강렬한 블랙베리·블랙체리 풍미**
            - 🌶 **후추·스파이스 계열의 묵직한 피니시**
            - 🖤 **풀바디 스타일의 진한 레드 와인**
            - 🥩 **바비큐, 고기구이, 치즈 플래터와 최고의 궁합**

            특히 **19 크라임즈 레드 블렌드 / 쉬라즈**는  
            와인을 ‘이야기와 함께 즐기는 술’로 만들어 주는 상징적인 라인입니다.

            ✅ **이런 분께 추천**
            - 와인을 스토리와 함께 즐기고 싶은 분  
            - 묵직하고 진한 레드 와인을 좋아하는 분  
            - 회식, 파티, 남성적인 분위기의 술자리에 어울리는 와인을 찾는 분
            """)

        st.image(img("19crimes.jpg"), width=360)

        st.markdown("""
            ---

            ### 🍽 와인 페어링

            - **브레드 앤 버터** → 파스타, 스테이크, 크림소스, 가벼운 치즈  
            - **19 크라임즈** → 바비큐, 소고기 구이, 숙성 치즈, 진한 육류 요리

            오늘의 분위기에 따라  
            **부드럽게 즐길지 / 강렬하게 즐길지 선택해 보세요.**
            """)


# LOG
def log_event(event_name: str):
    df_new = pd.DataFrame({
        "timestamp": [datetime.now().isoformat()],
        "client_id": [CLIENT_ID],   # 🔥 누가 했는지
        "event": [event_name],      # "survey_completed" / "stats_viewed"
    })
    if EVENT_CSV.exists():
        df_old = pd.read_csv(EVENT_CSV)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(EVENT_CSV, index=False)
    
# 통계용
def save_result(companion, mood, abv, taste_pref, food, recommended):
    data = {
        "timestamp": [datetime.now().isoformat()],
        "companion": [companion],
        "mood": [mood],
        "abv": [abv],
        "taste_pref": [taste_pref],
        "food": [food],
        "recommended": [recommended],
    }

    df_new = pd.DataFrame(data)

    # 기존 파일이 있으면 불러와 병합
    if CSV_PATH.exists():
        df_old = pd.read_csv(CSV_PATH)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new

    df_all.to_csv(CSV_PATH, index=False)


if submitted:
    recommended, scores = recommend_drink(
        companion, mood, abv, taste_pref, food
    )
    save_result(companion, mood, abv, taste_pref, food, recommended)
    log_event("survey_completed")
    st.success("✨ 설문이 완료되었습니다. 오늘 당신에게 어울리는 한 잔은…")

    get_recommendation_copy(recommended)
    #st.markdown(f"## {title}")
    #st.markdown(desc)

    with st.expander("🔎 추천 결과에 영향을 준 요소(카테고리별 점수) 보기"):
        st.write(scores)

    st.markdown("---")
    st.markdown(
        """
이제 **생명의물 메인 페이지**에서  
추천받은 술 타입에 맞는 메뉴와 자리를 골라보세요.
"""
    )

    # 🔥 통계 버튼 스타일 (일반 st.button용)
st.markdown(
    """
    <style>
    button[kind="secondary"] {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 14px 32px;
        border-radius: 999px;
        background: linear-gradient(135deg, #4f71ff 0%, #6cc6ff 50%, #90e0ff 100%);
        color: #ffffff !important;
        font-size: 18px;
        font-weight: 700;
        border: none;
        cursor: pointer;
        box-shadow: 0 10px 18px rgba(0, 0, 0, 0.18);
        animation: stats-pulse 1.5s infinite;
        transition: transform 0.15s ease-out, box-shadow 0.15s ease-out;
    }
    button[kind="secondary"]:hover {
        transform: translateY(-2px) scale(1.03);
        box-shadow: 0 14px 24px rgba(0, 0, 0, 0.22);
        color: #ffffff !important;
    }
    @keyframes stats-pulse {
        0% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0.4);
        }
        70% {
            transform: scale(1.04);
            box-shadow: 0 0 0 16px rgba(79, 113, 255, 0);
        }
        100% {
            transform: scale(1);
            box-shadow: 0 0 0 0 rgba(79, 113, 255, 0);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 🔁 통계 페이지로 이동 (같은 세션에서)
cols = st.columns([1, 2, 1])
with cols[1]:
    go_stats = st.button("📊 다른 사람들 취향 통계 보러가기")
if go_stats:
    log_event("stats_viewed")
    st.switch_page("pages/02_stats.py")

    # 🔁 메인으로 돌아가기 
    st.page_link("app.py", label="🏠 메인으로 돌아가기", icon="🏠")