import streamlit as st
# ─────────────────────────────────────────
# 페이지 탭 상태 관리
# ─────────────────────────────────────────
if "tab" not in st.session_state:
    st.session_state.tab = "list"

def set_tab(tab):
    st.session_state.tab = tab
# ─────────────────────────────────────────
# 상단 배너 설정
# ─────────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 0rem;
}
</style>
""", unsafe_allow_html=True)

# 배너이미지
st.markdown("<div class='banner-container'>", unsafe_allow_html=True)
st.image("images/main top banner.png", use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────
st.set_page_config(
    page_title="중고차 시세 조회",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ─────────────────────────────────────────
# 탭 버튼 설정
# ─────────────────────────────────────────
st.markdown("""
<style>
div[data-baseweb="tab-list"] button {
    padding: 12px 15px !important;
}
div[data-baseweb="tab-list"] button * {
    font-size: 2.0rem !important;
    font-weight: 700 !important;
}
div[data-baseweb="tab-list"] button[aria-selected="true"] {
    background-color: #282681 !important;
    color: white !important;
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# CSS style 호출
# ─────────────────────────────────────────

with open("assets/app.css", encoding="utf-8") as f:
    style = f.read()

st.markdown(f"<style>{style}</style>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 데이터 정의
# ─────────────────────────────────────────
DOMESTIC_BRANDS = ["현대", "제네시스", "기아", "쉐보레(GM대우)", "르노코리아(삼성)", "KG모빌리티(쌍용)"]
IMPORT_BRANDS   = ["벤츠", "BMW", "아우디", "폭스바겐", "미니쿠퍼"]
CAR_TYPES       = ["경차", "소형차", "준중형차", "중형차", "대형차", "스포츠카", "SUV"]
FUEL_TYPES      = ["경유", "휘발유", "LPG", "전기"]
YEARS           = list(range(2003, 2027))   # 2003 ~ 2026

# 샘플 데이터 (실제 연동 시 DB / API 교체)
SAMPLE_DATA = [
    {"brand": "현대", "model": "아반떼 CN7", "type": "준중형차", "fuel": "휘발유",
     "price": 1850, "year": 2021, "mileage": 42000, "accident": False},
    {"brand": "기아",  "model": "K5 3세대",   "type": "중형차",   "fuel": "휘발유",
     "price": 2200, "year": 2022, "mileage": 31000, "accident": False},
    {"brand": "현대", "model": "투싼 NX4",    "type": "SUV",      "fuel": "경유",
     "price": 2650, "year": 2022, "mileage": 55000, "accident": True},
    {"brand": "BMW",  "model": "3시리즈 (G20)", "type": "중형차",  "fuel": "휘발유",
     "price": 4300, "year": 2020, "mileage": 67000, "accident": False},
    {"brand": "벤츠", "model": "E클래스 W213", "type": "대형차",   "fuel": "휘발유",
     "price": 5100, "year": 2019, "mileage": 82000, "accident": True},
    {"brand": "기아",  "model": "EV6 GT",      "type": "중형차",   "fuel": "전기",
     "price": 3900, "year": 2023, "mileage": 18000, "accident": False},
    {"brand": "현대", "model": "아이오닉6",    "type": "중형차",   "fuel": "전기",
     "price": 3400, "year": 2023, "mileage": 22000, "accident": False},
    {"brand": "쉐보레(GM대우)", "model": "트레일블레이저", "type": "SUV", "fuel": "휘발유",
     "price": 1950, "year": 2021, "mileage": 49000, "accident": False},
    {"brand": "아우디", "model": "A6 C8",      "type": "대형차",   "fuel": "경유",
     "price": 4800, "year": 2020, "mileage": 71000, "accident": False},
    {"brand": "제네시스", "model": "G80 3세대","type": "대형차",   "fuel": "휘발유",
     "price": 4500, "year": 2021, "mileage": 38000, "accident": False},
    {"brand": "르노코리아(삼성)", "model": "QM6", "type": "SUV",  "fuel": "LPG",
     "price": 1600, "year": 2019, "mileage": 93000, "accident": True},
    {"brand": "미니쿠퍼", "model": "쿠퍼 S",  "type": "소형차",   "fuel": "휘발유",
     "price": 2700, "year": 2020, "mileage": 44000, "accident": False},
]


# ─────────────────────────────────────────
# 사이드바 – 검색 필터
# ─────────────────────────────────────────
with st.sidebar:

    # ── 제조사 ──────────────────────────────
    st.markdown("<div class='section-header'>제조사 <span style='font-size:0.65rem;color:#7b82a8;'>(중복선택 가능)</span></div>",
                unsafe_allow_html=True)

  # 브랜드별 이미지
    brands_img = {"아우디":"logos-brand-audi.png", "쉐보레" : "logos-brand-chevrolet.png", "BMW" : "logos-brand-bmw. png", 
                  "벤츠" : "logos-brand-benz.png","현대": "logos-brand-hyundai.png","기아": "logos-brand-kia.png",
                   "미니쿠퍼" :"logos-brand-mini.png","폭스바겐" : "logos-brand-volkswagen.png", "르노" : "logos-brand-renault.svg",
                   "KG모빌리티": "logos-brand-kgm.svg","제네시스":"logos-brand-genesis.png" }

    # 국산
    st.markdown("<div class='brand-group-label'>🇰🇷 국산</div>", unsafe_allow_html=True)
    selected_brands = []
    dom_cols = st.columns(2)
    
    for i, brand in enumerate(DOMESTIC_BRANDS):  
        with dom_cols[i % 2]:
            if st.checkbox(brand, key=f"brand_{brand}"):
                selected_brands.append(brand)

    # 수입
    st.markdown("<div class='brand-group-label' style='margin-top:0.8rem;'>🌍 수입</div>",
                unsafe_allow_html=True)
    imp_cols = st.columns(2)
    for i, brand in enumerate(IMPORT_BRANDS):
        with imp_cols[i % 2]:
            if st.checkbox(brand, key=f"brand_{brand}"):
                selected_brands.append(brand)

    # ── 차종 ──────────────────────────────
    st.markdown("<div class='section-header'>차종 <span style='font-size:0.65rem;color:#7b82a8;'>(중복선택 가능)</span></div>",
                unsafe_allow_html=True)
    selected_types = []
    cols = st.columns(2)
    for i, ct in enumerate(CAR_TYPES):
        with cols[i % 2]:
            if st.checkbox(ct, key=f"type_{ct}"):
                selected_types.append(ct)

    # ── 가격 슬라이더 ───────────────────────
    st.markdown("<div class='section-header'>가격</div>", unsafe_allow_html=True)
    price_range = st.slider(
        label="가격 범위 (만원)",
        min_value=500,
        max_value=10000,
        value=(500, 10000),
        step=500,
        label_visibility="collapsed",
    )
    st.markdown(
        f"<span class='slider-value'>💰 {price_range[0]:,}만원 ~ {price_range[1]:,}만원</span>",
        unsafe_allow_html=True,
    )

    # ── 연료 ──────────────────────────────
    st.markdown("<div class='section-header'>연료</div>", unsafe_allow_html=True)
    selected_fuels = []
    fcols = st.columns(2)
    for i, ft in enumerate(FUEL_TYPES):
        with fcols[i % 2]:
            if st.checkbox(ft, key=f"fuel_{ft}"):
                selected_fuels.append(ft)

    # ── 사고 유무 ──────────────────────────
    st.markdown("<div class='section-header'>사고 유무</div>", unsafe_allow_html=True)
    accident_option = st.radio(
        label="사고 유무 선택",
        options=["전체", "사고 X", "사고 O"],
        index=0,
        label_visibility="collapsed",
        horizontal=True,
    )

    # ── 주행거리 슬라이더 ───────────────────
    st.markdown("<div class='section-header'>주행거리</div>", unsafe_allow_html=True)
    mileage_max = st.slider(
        label="최대 주행거리 (km)",
        min_value=10000,
        max_value=200000,
        value=200000,
        step=10000,
        label_visibility="collapsed",
    )
    st.markdown(
        f"<span class='slider-value'>🛣️ {mileage_max:,} km 이하</span>",
        unsafe_allow_html=True,
    )

    # ── 연식 ──────────────────────────────
    st.markdown("<div class='section-header'>연식</div>", unsafe_allow_html=True)
    year_range = st.select_slider(
        label="연식 범위",
        options=YEARS,
        value=(YEARS[0], YEARS[-1]),
        label_visibility="collapsed",
    )
    st.markdown(
        f"<span class='slider-value'>📅 {year_range[0]}년 ~ {year_range[1]}년</span>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────
# 메인 영역
# ─────────────────────────────────────────

# ─────────────────────────────────────────
# 탭 UI
# ─────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚗 중고차 시세 조회", "📊 내 차 시세 조회", "❤️ 찜 목록 조회"])

# 탭 선택시 이동
if st.session_state.tab == "list":
    # 👉 기존 차량 리스트 코드
    st.write("")

elif st.session_state.tab == "mycar":
    # 👉 내 차 시세 코드
    st.write("")

elif st.session_state.tab == "like":
    # 👉 저장한 중고차 리스트 코드
    st.write("")

# ─────────────────────────────────────────
# 🚗 탭1: 차량 조회
# ─────────────────────────────────────────
with tab1:

    # ── 필터 요약 ────────────────────────────
    filter_parts = []
    if selected_brands:
        filter_parts.append(f"브랜드: {', '.join(selected_brands)}")
    if selected_types:
        filter_parts.append(f"차종: {', '.join(selected_types)}")
    filter_parts.append(f"가격: {price_range[0]:,}~{price_range[1]:,}만원")
    if selected_fuels:
        filter_parts.append(f"연료: {', '.join(selected_fuels)}")
    if accident_option != "전체":
        filter_parts.append(f"사고: {accident_option}")
    filter_parts.append(f"주행: {mileage_max:,}km 이하")
    filter_parts.append(f"연식: {year_range[0]}~{year_range[1]}년")

    st.markdown(
        f"<div class='filter-summary'>🔎 적용 필터 &nbsp;|&nbsp; "
        + " &nbsp;&middot;&nbsp; ".join(filter_parts) + "</div>",
        unsafe_allow_html=True,
    )

    # ── 필터링 로직 ──────────────────────────
    def apply_filters(data):
        results = []
        for car in data:
            if selected_brands and car["brand"] not in selected_brands:
                continue
            if selected_types and car["type"] not in selected_types:
                continue
            if not (price_range[0] <= car["price"] <= price_range[1]):
                continue
            if selected_fuels and car["fuel"] not in selected_fuels:
                continue
            if accident_option == "사고X" and car["accident"]:
                continue
            if accident_option == "사고O" and not car["accident"]:
                continue
            if car["mileage"] > mileage_max:
                continue
            if not (year_range[0] <= car["year"] <= year_range[1]):
                continue
            results.append(car)
        return results

    filtered = apply_filters(SAMPLE_DATA)

    # ── 결과 표시 ────────────────────────────
    col_info, col_sort = st.columns([3, 1])

    with col_info:
        st.markdown(
            f"#### 검색 결과 &nbsp; <span style='color:#e05c3a;font-size:1.1rem;'>{len(filtered)}건</span>",
            unsafe_allow_html=True
        )

    with col_sort:
        sort_by = st.selectbox(
            "정렬",
            options=["가격 낮은순", "가격 높은순", "연식 최신순", "주행거리 낮은순"],
            label_visibility="collapsed",
        )

    # 정렬
    sort_map = {
        "가격 낮은순": lambda c: c["price"],
        "가격 높은순": lambda c: -c["price"],
        "연식 최신순": lambda c: -c["year"],
        "주행거리 낮은순": lambda c: c["mileage"],
    }
    filtered.sort(key=sort_map[sort_by])

    # 결과 출력
    if not filtered:
        st.info("🚫 조건에 맞는 매물이 없습니다.")
    else:
        for i in range(0, len(filtered), 3):
            row_cars = filtered[i:i+3]
            cols = st.columns(3)

            for col, car in zip(cols, row_cars):
                with col:
                    acc_badge = (
                        "<span class='badge badge-acc-n'>사고X</span>"
                        if not car["accident"]
                        else "<span class='badge badge-acc-y'>사고O</span>"
                    )

                    st.markdown(f"""
<div class='result-card'>
  <div class='car-name'>{car['brand']} {car['model']}</div>
  <div class='car-price' style='margin:0.4rem 0;'>{car['price']:,}만원</div>
  <div style='margin-bottom:0.5rem;'>
    <span class='badge badge-type'>{car['type']}</span>
    <span class='badge badge-fuel'>{car['fuel']}</span>
    {acc_badge}
  </div>
  <div class='car-detail'>
    📅 {car['year']}년형 &nbsp;|&nbsp; 🛣️ {car['mileage']:,}km
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────
# 📊 탭2: 내 차 시세
# ─────────────────────────────────────────
with tab2:

    st.markdown("### 💰 내 차는 지금 얼마?")

    col1, col2 = st.columns(2)

    with col1:
        brand = st.selectbox("브랜드", DOMESTIC_BRANDS + IMPORT_BRANDS)
        year = st.slider("연식", 2003, 2026, 2020)

    with col2:
        mileage = st.number_input("주행거리 (km)", 0, 200000, 50000)
        fuel = st.selectbox("연료", FUEL_TYPES)

    if st.button("시세 계산"):
        st.success("💰 예상 시세: 약 2,300만원 (샘플)")

# ─────────────────────────────────────────
# 📊 탭3: 찜 목록
# ─────────────────────────────────────────
with tab3:
    st.markdown("<div style='min-height:600px'>\n🚫 찜한 차량이 없습니다.</div>", unsafe_allow_html=True)
