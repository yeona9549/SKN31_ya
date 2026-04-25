import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================================
# 페이지 설정
# =====================================================
st.set_page_config(page_title="유기동물 보호시설 현황 2024", page_icon="🐾", layout="wide")

# =====================================================
# CSS 스타일 (기존 디자인 유지 + 인터랙션 요소)
# =====================================================
st.markdown("""
<style>
    :root { --cream: #F7F3EE; --warm: #EDE5DA; --dark: #1E1A16; --accent: #C4793A; --muted: #7A6A60; }
    .stApp { background: var(--cream) !important; }
    .custom-header { background: var(--dark); color: #F7F3EE; padding: 2rem; text-align: center; border-radius: 16px; margin-bottom: 2rem; }
    .sec-title { font-family: 'Noto Serif KR', serif; font-size: 1.4rem; font-weight: 700; color: var(--dark); margin: 2rem 0 1rem; border-left: 5px solid var(--accent); padding-left: 15px; }
    .stat-card { background: white; border-radius: 14px; padding: 1.5rem; text-align: center; border: 1px solid var(--warm); box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .stat-num { font-family: 'Noto Serif KR', serif; font-size: 1.8rem; font-weight: 700; color: var(--accent); }
    .alert-box { background: #FFF8F0; border-left: 4px solid var(--accent); padding: 1rem; border-radius: 0 10px 10px 0; margin-bottom: 1rem; font-size: 0.9rem; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 사이드바 (기능성 추가)
# =====================================================
with st.sidebar:
    st.header("🔍 대시보드 옵션")
    selected_year = st.selectbox("분석 연도 선택", [2024, 2023, 2022])
    st.info("데이터 출처: 농림축산식품부\n\n이 대시보드는 유기동물 보호시설의 현황을 시각화합니다.")

# =====================================================
# 헤더
# =====================================================
st.markdown("""
<div class="custom-header">
    <h1>🐾 유기동물 보호시설 현황 Dashboard</h1>
    <p>2024년 농림축산검역본부 반려동물 보호·복지 실태조사 기반</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# 탭 구성 (정보 구조화)
# =====================================================
tab1, tab2, tab3 = st.tabs(["📊 핵심 지표", "📈 연도별 추이 분석", "🗺️ 지역별 및 상세 데이터"])

# 탭 1: 핵심 지표
with tab1:
    st.markdown('<div class="sec-title">2024년 주요 통계</div>', unsafe_allow_html=True)
    cols = st.columns(5)
    metrics = [
        ("🐕 발생 건수", "106,824", "전년 대비 5.5% 감소"),
        ("🏠 보호센터", "263개", "지자체 직영 증가"),
        ("💰 관리 비용", "464억", "역대 최대"),
        ("📅 보호 기간", "27.8일", "평균 대기 시간"),
        ("👨‍👩‍👧 반려가구", "591만", "전체 가구의 26.7%")
    ]
    for i, (label, val, sub) in enumerate(metrics):
        with cols[i]:
            st.markdown(f'<div class="stat-card"><div class="stat-num">{val}</div><div style="font-size:0.8rem; color:gray;">{label}</div><div style="font-size:0.7rem; color:green;">{sub}</div></div>', unsafe_allow_html=True)
    
    st.markdown('<div class="alert-box"><strong>💡 Insight:</strong> 유기동물 발생 건수는 감소 추세이나, 보호 시설 및 관리 비용 투자는 강화되고 있습니다.</div>', unsafe_allow_html=True)

# 탭 2: 연도별 추이 (인터랙티브 차트)
with tab2:
    st.markdown('<div class="sec-title">연도별 유기동물 발생 추이</div>', unsafe_allow_html=True)
    
    # 데이터 생성
    trend_data = pd.DataFrame({
        "연도": [2019, 2020, 2021, 2022, 2023, 2024],
        "발생건수": [135791, 130401, 118273, 113440, 113072, 106824]
    })
    
    # Plotly 그래프
    fig = px.bar(trend_data, x="연도", y="발생건수", text_auto='.2s', 
                 color="발생건수", color_continuous_scale="Oranges")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# 탭 3: 지역별 현황 및 상세
with tab3:
    st.markdown('<div class="sec-title">지역별 현황 데이터</div>', unsafe_allow_html=True)
    
    region_data = {
        "순위": ["1위", "2위", "3위", "4위", "5위"],
        "지역": ["경기도", "전라남도", "경상남도", "서울특별시", "세종특별자치시"],
        "발생건수": [21966, 12000, 11500, 8000, 1200],
        "특이사항": ["최다 구조", "함평군 밀집", "밀양시 밀집", "최단 보호기간", "최장 보호기간"]
    }
    df = pd.DataFrame(region_data)
    
    # 인터랙티브 데이터프레임
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    with st.expander("📊 처리 결과 상세 확인"):
        st.write("""
        - **반환율**: 11.4%
        - **입양률**: 27.7%
        - **자연사/안락사**: ~50%
        - 고양이의 경우 동물등록 의무가 없어 반환율이 1.3%로 매우 낮습니다.
        """)

# =====================================================
# 푸터
# =====================================================
st.markdown("---")
st.markdown("<p style='text-align: center; color: #888; font-size: 0.8rem;'>© 2026 유기동물 보호시설 대시보드 - 데이터 시각화 프로젝트</p>", unsafe_allow_html=True)