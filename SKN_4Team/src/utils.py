# utils.py >> DB/테이블 초기화 + CSV 적재
# src/ui_utils.py

import streamlit as st

def load_css(file_path):
    with open(file_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def fmt_price(price):
    if price is None:
        return "-"
    return f"{int(price):,}만원"

def render_metrics(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)

def render_car_cards(cars, columns=3):
    cols = st.columns(columns)
    for i, car in enumerate(cars):
        with cols[i % columns]:
            st.write(car)

def render_pagination(total, page_size):
    pages = (total - 1) // page_size + 1
    if "page" not in st.session_state:
        st.session_state["page"] = 0

    col1, col2, col3 = st.columns([1,2,1])
    with col1:
        if st.button("이전"):
            st.session_state["page"] = max(0, st.session_state["page"] - 1)
    with col3:
        if st.button("다음"):
            st.session_state["page"] = min(pages-1, st.session_state["page"] + 1)

    return st.session_state["page"]