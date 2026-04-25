# 01_Market_Price.py
# 시세 조회 페이지 - DB 연동 버전

import streamlit as st
import sys
import os

#sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)
from src.car_repository import get_cars, count_cars, get_brands, get_fuel_types, get_summary_stats
from src.data_processor  import build_filter_summary, cars_to_dataframe
#from src.utils           import load_css, render_car_cards, render_pagination, render_metrics, fmt_price
from src.utils import (
    load_css,
    render_car_cards,
    render_pagination,
    render_metrics,
    fmt_price
)
# ── 페이지 설정 ───────────────────────────────────────────────
st.set_page_config(page_title="중고차 시세 조회", page_icon="🚗", layout="wide")
load_css("assets/app.css")

PAGE_SIZE = 9   # 한 페이지에 카드 9개 (3열 × 3행)

# ── 필터 변경 시 페이지 초기화 ────────────────────────────────
if "page" not in st.session_state:
    st.session_state["page"] = 0

# ── DB에서 필터 목록 가져오기 ─────────────────────────────────
all_brands = get_brands()
all_fuels  = get_fuel_types()

# ── 사이드바 필터 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='section-header'>🏭 제조사</div>", unsafe_allow_html=True)
    selected_brands = []
    for brand in all_brands:
        if st.checkbox(brand, key=f"brand_{brand}"):
            selected_brands.append(brand)

    st.markdown("<div class='section-header'>⛽ 연료</div>", unsafe_allow_html=True)
    selected_fuels = []
    for fuel in all_fuels:
        if st.checkbox(fuel, key=f"fuel_{fuel}"):
            selected_fuels.append(fuel)

    st.markdown("<div class='section-header'>💰 시세 범위</div>", unsafe_allow_html=True)
    price_range = st.slider(
        "시세(만원)", min_value=0, max_value=10000,
        value=(0, 10000), step=100, label_visibility="collapsed"
    )

    st.markdown("<div class='section-header'>🛣️ 최대 주행거리</div>", unsafe_allow_html=True)
    mileage_max = st.slider(
        "주행거리(km)", min_value=0, max_value=200000,
        value=200000, step=5000, label_visibility="collapsed"
    )

    st.markdown("<div class='section-header'>📅 연식</div>", unsafe_allow_html=True)
    year_range = st.slider(
        "연식", min_value=2011, max_value=2025,
        value=(2011, 2025), step=1, label_visibility="collapsed"
    )

    st.markdown("<div class='section-header'>🔧 사고 여부</div>", unsafe_allow_html=True)
    accident = st.radio(
        "사고 여부", ["전체", "사고 X", "사고 O"],
        horizontal=True, label_visibility="collapsed"
    )

    # 필터 변경 시 페이지 0으로 리셋
    if st.button("🔄 필터 초기화", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── 공통 필터 파라미터 ────────────────────────────────────────
filter_params = dict(
    brand_list  = selected_brands or None,
    fuel_list   = selected_fuels  or None,
    accident    = accident,
    price_min   = price_range[0],
    price_max   = price_range[1],
    mileage_max = mileage_max,
    year_min    = year_range[0],
    year_max    = year_range[1],
)

# ── 상단 요약 통계 ────────────────────────────────────────────
stats = get_summary_stats()
render_metrics([
    ("전체 매물",   f"{stats.get('total_cars', 0):,}건"),
    ("평균 시세",   fmt_price(stats.get("avg_price"))),
    ("최신 연식",   f"{stats.get('newest_year', '-')}년"),
    ("제조사 수",   f"{stats.get('brand_count', 0)}개"),
])

st.divider()

# ── 필터 요약 바 ──────────────────────────────────────────────
st.markdown(
    build_filter_summary(
        selected_brands, selected_fuels, accident,
        price_range[0], price_range[1],
        mileage_max, year_range[0], year_range[1]
    ),
    unsafe_allow_html=True
)

# ── 정렬 + 결과 건수 ─────────────────────────────────────────
col_title, col_sort = st.columns([3, 1])
with col_sort:
    sort_label = st.selectbox(
        "정렬", ["가격 낮은순", "가격 높은순", "연식 최신순", "주행거리 낮은순"],
        label_visibility="collapsed"
    )

total = count_cars(**filter_params)

with col_title:
    st.markdown(
        f"#### 검색 결과 &nbsp;"
        f"<span style='color:#e05c3a; font-size:1.1rem;'>{total:,}건</span>",
        unsafe_allow_html=True
    )

# ── DB 조회 ───────────────────────────────────────────────────
page = render_pagination(total=total, page_size=PAGE_SIZE)

cars = get_cars(
    **filter_params,
    sort = sort_label,
)

# 현재 페이지 슬라이싱 (DB 쪽에 LIMIT/OFFSET 없이 Python 슬라이싱)
paged_cars = cars[page * PAGE_SIZE: (page + 1) * PAGE_SIZE]

# ── 카드 렌더링 ───────────────────────────────────────────────
render_car_cards(paged_cars, columns=3)

# ── 테이블 뷰 (토글) ──────────────────────────────────────────
with st.expander("📋 표로 보기"):
    st.dataframe(cars_to_dataframe(cars), use_container_width=True)