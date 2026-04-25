# car_repository.py
# MySQL에서 데이터를 가져오는 메소드 모음

import mysql.connector
import streamlit as st

# ── 공통 접속 정보 ────────────────────────────────────────────
# config 정보 딕셔너리로 묶어서 호출 편리성 강화
DB_CONFIG = {
    "host":     "localhost", # IP(host) 입력
    "user":     "root", # username 입력
    "password": "dusdn369", # MySQL 비밀번호 입력 
    "database": "used_car_db",
    "charset":  "utf8mb4"
}
# ─────────────────────────────────────────────────────────────
# [시세 조회 페이지] 차량 목록 조회
# ─────────────────────────────────────────────────────────────
def get_cars(brand_list, fuel_list, accident, price_min, price_max,
             mileage_max, year_min, year_max, sort):
    conn   = mysql.connector.connect(**DB_CONFIG) # 생성해둔 딕셔너리 Key : value 로 펼쳐서 접속
    cursor = conn.cursor(dictionary=True)

    sql    = "SELECT * FROM cars WHERE avg_price BETWEEN %s AND %s"
    params = [price_min, price_max]

    # 제조사 필터
    if brand_list:
        placeholders = ", ".join(["%s"] * len(brand_list)) # 플레이스 홀더 in값이 몇개일지 몰라서 동적으로 필터값 조정 해줍니다.
        sql   += f" AND brand IN ({placeholders})"
        params += brand_list # 파라미터에 브랜드 필터 추가

    # 연료 필터
    if fuel_list:
        placeholders = ", ".join(["%s"] * len(fuel_list))
        sql   += f" AND fuel IN ({placeholders})"
        params += fuel_list

    # 사고 필터 (사고여부 컬럼값: 'X' 또는 NULL)
    if accident == "사고 X": # streamlit 필터 사고 X 선택시 DB 사고컬럼 X 가져오기
        sql += " AND accident = 'X'"
    elif accident == "사고 O":
        sql += " AND (accident != 'X' OR accident IS NULL)"

    # 연식 필터 (YYYYMM → 앞 4자리만 비교)
    sql   += " AND FLOOR(year / 100) BETWEEN %s AND %s" # FLOOR 소숫점 버림(내림) YYYYMM양식에서 YYYY만 비교하기위해 100 나누기.
    params += [year_min, year_max]

    # 주행거리 필터
    sql   += " AND mileage <= %s" # 필터 미만 주행거리 차량만 조회
    params.append(mileage_max)

    # 정렬
    sort_map = {
        "가격 낮은순":    "avg_price ASC",
        "가격 높은순":    "avg_price DESC",
        "연식 최신순":    "year DESC",
        "주행거리 낮은순": "mileage ASC",
    }
    sql += f" ORDER BY {sort_map.get(sort, 'avg_price ASC')}" # sort값 사용자가 선택하면 그게 우선, default는 가격 낮은순.

    cursor.execute(sql, params)
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result


# ─────────────────────────────────────────────────────────────
# [시세 조회 페이지] 검색 결과 건수
# ─────────────────────────────────────────────────────────────
# 검색 결과 건수 표시 & 페이지 수 계산 streamlit 1페이지에서 사용하려고 카운트합니다.
def count_cars(brand_list, fuel_list, accident, price_min, price_max,
               mileage_max, year_min, year_max):
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    sql    = "SELECT COUNT(*) FROM cars WHERE avg_price BETWEEN %s AND %s"
    params = [price_min, price_max]

    if brand_list:
        placeholders = ", ".join(["%s"] * len(brand_list))
        sql   += f" AND brand IN ({placeholders})"
        params += brand_list

    if fuel_list:
        placeholders = ", ".join(["%s"] * len(fuel_list))
        sql   += f" AND fuel IN ({placeholders})"
        params += fuel_list

    if accident == "사고 X":
        sql += " AND accident = 'X'"
    elif accident == "사고 O":
        sql += " AND (accident != 'X' OR accident IS NULL)"

    sql   += " AND FLOOR(year / 100) BETWEEN %s AND %s"
    params += [year_min, year_max]

    sql   += " AND mileage <= %s"
    params.append(mileage_max)

    cursor.execute(sql, params)
    result = cursor.fetchone()[0]

    cursor.close()
    conn.close()
    return result

# ─────────────────────────────────────────────────────────────
# [내 차 시세 페이지] 제조사+모델명 키워드 검색
# ─────────────────────────────────────────────────────────────
def search_my_car(brand, model_keyword):
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    sql    = "SELECT * FROM cars WHERE brand = %s AND model LIKE %s ORDER BY year DESC" # 연식 내림차순 / LIKE = 패턴 문자열 검색해주는 연산자.
    cursor.execute(sql, (brand, f"%{model_keyword}%")) # 브랜드 & 모델명은 키워드로 검색.
    result = cursor.fetchall()

    cursor.close()
    conn.close()
    return result

# ─────────────────────────────────────────────────────────────
# [내 차 시세 페이지] 유사 차량 시세 통계
# ─────────────────────────────────────────────────────────────
# 사용자가 입력한 브랜드 + 모델명(키워드로 추적) 데이터베이스에서 비교해서 일치하는 조건의 차량들 평균시세 조회해서 등록하려는 가격과 비교 + 총 몇대가 검색되었는지 COUNT값 검색결과로 표시.
def get_price_stats(brand, model_keyword):
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    sql = """ 
        SELECT
            ROUND(AVG(avg_price)) AS avg_price,
            MIN(min_price)        AS min_price,
            MAX(max_price)        AS max_price,
            COUNT(*)              AS total_count
        FROM cars
        WHERE brand = %s AND model LIKE %s 
    """
    cursor.execute(sql, (brand, f"%{model_keyword}%"))
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result

# ─────────────────────────────────────────────────────────────
# [공통] 제조사 목록 (사이드바 체크박스용)
# ─────────────────────────────────────────────────────────────
def get_brands():
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT brand FROM cars ORDER BY brand")
    result = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return result


# ─────────────────────────────────────────────────────────────
# [공통] 연료 종류 목록 (사이드바 체크박스용)
# ─────────────────────────────────────────────────────────────
def get_fuel_types():
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT fuel FROM cars WHERE fuel IS NOT NULL ORDER BY fuel")
    result = [row[0] for row in cursor.fetchall()] # fetchall이 튜플의 리스트로 반환하는데 예) ("현대", ) 여기서 꺼내기위해 row[0] 반환 

    cursor.close()
    conn.close()
    return result


# ─────────────────────────────────────────────────────────────
# [공통] 전체 요약 통계 (총 매물 수, 평균 시세, 최신 연식)
# ─────────────────────────────────────────────────────────────
def get_summary_stats():
    conn   = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

# total_cars= 총 매물, avg_price= 평균 시세, newest_year= 최신 연식, brand_count= 브랜드 갯수
    cursor.execute("""
        SELECT
            COUNT(*)                         AS total_cars, 
            ROUND(AVG(avg_price))            AS avg_price,
            MAX(FLOOR(year / 100))           AS newest_year,
            COUNT(DISTINCT brand)            AS brand_count
        FROM cars
    """)
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result