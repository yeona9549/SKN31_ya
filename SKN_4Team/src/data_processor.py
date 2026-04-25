# data_processor.py
# DB에서 받은 데이터를 화면 출력용으로 가공하는 함수 모음

import pandas as pd

# ─────────────────────────────────────────────────────────────
# 연식 >> 0000년 00월로 양식을 수정해주는 메소드
# ─────────────────────────────────────────────────────────────
def format_year(year_int):
    s = str(year_int)                                           # 정수형 연식 >> 문자열로 변경
    if len(s) >= 6:                                             # 연식(문자열)의 길이가 6보다 크거나 같으면 f-string으로 반환
        return f"{s[:4]}년 {s[4:6]}월"
    elif len(s) == 4:                                           # 4자리밖에 없으면 0000년만 반환
        return f"{s}년"
    return str(year_int)

# ─────────────────────────────────────────────────────────────
# 차량 한대씩 카드 HTML 변환
# ─────────────────────────────────────────────────────────────
def build_card_html(car):
    # 데이터를 꺼내는 과정 / 예시) car = {"brand": "현대", "model": "그랜저", "fuel": "하이브리드", ... }

    brand    = car.get("brand") or ""                                                       # 결측치가 확인되면 공백 / - / 0 으로 가져오기
    model    = car.get("model") or "-"
    fuel     = car.get("fuel")  or "-"
    year_str = format_year(car["year"]) if car.get("year") else "-"
    mileage  = car.get("mileage")
    avg_price = int(car.get("avg_price") or 0)
    min_price = int(car.get("min_price") or 0)
    max_price = int(car.get("max_price") or 0)

    mileage_str = f"{int(mileage):,}km" if mileage else "-"

    accident_val = str(car.get("accident") or "")
    if accident_val == "X":
        acc_badge = "<span class='badge badge-acc-n'>사고 X</span>"                          # 사고 없으면 초록 뱃지
    else:
        acc_badge = "<span class='badge badge-acc-y'>사고 O</span>"                          # 사고 있으면 빨간 뱃지

# 브랜드 / 모델명, 시세 평균, 연료, 연식, 주행거리, 전체 시세 HTML로 리턴
    return f"""
<div class='result-card'>
  <div class='car-name'>{brand} {model}</div>                                               
  <div class='car-price'>{avg_price:,}만원</div>                                             
  <div style='margin: 0.4rem 0;'>                                                           
    <span class='badge badge-fuel'>{fuel}</span>                                            
    {acc_badge}
  </div>
  <div class='car-detail'>
    📅 {year_str} &nbsp;|&nbsp; 🛣️ {mileage_str}                                             
  </div>
  <div class='car-detail' style='margin-top:0.3rem; font-size:0.78rem; color:#7b82a8;'>
    시세 {min_price:,} ~ {max_price:,}만원                                                     
  </div>
</div>
"""

# ─────────────────────────────────────────────────────────────
# 차량 목록 = > pandas DataFrame
# ─────────────────────────────────────────────────────────────
# 차량 목록을 판다스 모듈을 이용해 데이터프레임으로 변형해주는 메소드 / st.dataframe() 으로 사용가능하게 해줌.
def cars_to_dataframe(cars):
    if not cars:                                                                   # cars가 비었으면 빈 표를 반환. (빈 데이터 시에 오류 방어)
        return pd.DataFrame()

    df = pd.DataFrame(cars)                                                        # 리스트들을 데이터프레임으로 변환

    # 연식 포맷
    if "year" in df.columns:                                                    
        df["year"] = df["year"].apply(lambda x: format_year(x) if x else "-")      # apply: 사용자 정의 함수를 일괄 적용
                                                                                   # 연식을 000000 -> 0000년 00월로 일괄 적용

    # 주행거리 포맷
    if "mileage" in df.columns:
        df["mileage"] = df["mileage"].apply(                                       # 주행거리를 00000 -> 00,000으로 일괄 적용
            lambda x: f"{int(x):,}" if x else "-"
        )

    # 사고여부 포맷
    if "accident" in df.columns:
        df["accident"] = df["accident"].apply(                                     # 사고여부: 'X'면 사고 X , 나머지는 사고 O로 처리.
            lambda x: "사고 X" if str(x) == "X" else "사고 O"
        )

    # 컬럼명 한글화 + 필요한 컬럼만
    df = df.rename(columns={                                                       # 영어로 된 컬럼명 한글로 전환시키는 작업
        "brand":     "제조사",
        "model":     "모델명",
        "fuel":      "연료",
        "year":      "연식",
        "mileage":   "주행거리(km)",
        "avg_price": "시세_평균(만원)",
        "min_price": "시세_최저(만원)",
        "max_price": "시세_최고(만원)",
        "accident":  "사고여부",
    })

    show_cols = ["제조사", "모델명", "연료", "연식", "주행거리(km)",
                 "시세_평균(만원)", "시세_최저(만원)", "시세_최고(만원)", "사고여부"]           # 필요한 컬럼들 한곳에 묶어주고
    show_cols = [c for c in show_cols if c in df.columns]                          # 에러 방지
    return df[show_cols]


# ─────────────────────────────────────────────────────────────
# 시세 판별: 내 차 가격 vs 유사 매물 평균가 비교
# ─────────────────────────────────────────────────────────────
def get_price_verdict(my_price, stats):
    avg = stats.get("avg_price") or 0                                               # 유사 매물 조사 후, 있으면 값 가져오고 없으면 0 가져오고 판정불가 출력
    if avg == 0:
        return "판정불가", "info"

    ratio = my_price / avg                                                          # 사용자가 입력한 가격을 평균으로 나눠서 동일가격 == 1 기준으로 시세 평가

    if ratio <= 0.9:
        return "💚 시세보다 저렴해요!", "success"
    elif ratio <= 1.1:
        return "💛 시세와 비슷해요", "warning"
    else:
        return "🔴 시세보다 비싼 편이에요", "error"

# ─────────────────────────────────────────────────────────────
# 필터 요약 텍스트 생성 (상단 필터 바 출력용)
# ─────────────────────────────────────────────────────────────
# 선택 필터들 정리해서 요약해주는 메소드
def build_filter_summary(brand_list, fuel_list, accident,
                         price_min, price_max, mileage_max, year_min, year_max):
    parts = [f"가격: {price_min:,}~{price_max:,}만원"]

    if brand_list:
        parts.append(f"제조사: {', '.join(brand_list)}")
    if fuel_list:
        parts.append(f"연료: {', '.join(fuel_list)}")
    if accident != "전체":
        parts.append(f"사고: {accident}")

    parts.append(f"주행거리: {mileage_max:,}km 이하")
    parts.append(f"연식: {year_min}~{year_max}년")

    body = " &nbsp;&middot;&nbsp; ".join(parts)
    return f"<div class='filter-summary'>🔎 적용 필터 &nbsp;|&nbsp; {body}</div>"

