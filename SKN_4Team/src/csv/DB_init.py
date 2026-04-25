# DB_init.py 
# 최초 1회만 실행 / DB 생성 + 테이블 생성 + CSV 데이터 적재

import mysql.connector
import pandas as pd
import os

# ── DB 접속 정보 ──────────────────────────────────────────────
conn = mysql.connector.connect(
    host="localhost", # IP(host) 입력
    port="3306", # port번호 입력
    user="root", # username 입력
    password="dusdn369", # MySQL 비밀번호로 변경
    charset="utf8mb4" # 이모지 지원 UTF-8 Most Bytes 4로 설정
)
cursor = conn.cursor()

# ── DB 생성 ───────────────────────────────────────────────────
cursor.execute("CREATE DATABASE IF NOT EXISTS used_car_db DEFAULT CHARACTER SET utf8mb4")
cursor.execute("USE used_car_db")

# ── 테이블 생성 ───────────────────────────────────────────────
# id, brand, model, fuel, year, mileage, avg_price, min_price, max_price, accident
# 인덱스, 브랜드, 모델, 연료, 연식, 주행거리, 평균가격, 최소가격, 최대가격, 사고이력 순입니다.
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id          INT AUTO_INCREMENT PRIMARY KEY,  
        brand       VARCHAR(50),
        model       VARCHAR(200),
        fuel        VARCHAR(30),
        year        INT,
        mileage     INT,
        avg_price   INT,
        min_price   INT,
        max_price   INT,
        accident    VARCHAR(5)
    )
""")
conn.commit()
print("Table Check")

# ── CSV 적재 ──────────────────────────────────────────────────

base_dir = os.path.dirname(__file__)
csv_path = os.path.join(base_dir, "usedcar_info.csv")

df = pd.read_csv(csv_path, encoding="cp949")
#df = pd.read_csv("src/csv/usedcar_info.csv", encoding="cp949")

# 컬럼명 -> DB 컬럼에 맞게 정리
df = df.rename(columns={
    "제조사":       "brand",
    "모델명":       "model",
    "연료":         "fuel",
    "연식":         "year",
    "주행거리(km)": "mileage",
    "시세_평균(만원)": "avg_price",
    "시세_최저(만원)": "min_price",
    "시세_최고(만원)": "max_price",
    "사고여부":     "accident",
})

# iterrows는 데이터프레임에 한 행씩 가져오는 메소드라 한행씩 가져오며 비교하는 for in 문입니다.
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO cars (brand, model, fuel, year, mileage, avg_price, min_price, max_price, accident)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row.get("brand"),
        row.get("model"),
        row.get("fuel"),
        int(row["year"])      if pd.notna(row.get("year"))      else None, # nan값 대비해서 방어처리로 if문 notna넣었습니다. 결측치 확인되면 None지정할거고 값이 있으면 수를 가져올거에요~
        int(row["mileage"])   if pd.notna(row.get("mileage"))   else None, 
        int(row["avg_price"]) if pd.notna(row.get("avg_price")) else None,
        int(row["min_price"]) if pd.notna(row.get("min_price")) else None,
        int(row["max_price"]) if pd.notna(row.get("max_price")) else None,
        row.get("accident"),
    ))

conn.commit()
print(f"CSV 체크: {len(df)}건")

cursor.close()
conn.close()
print("DB 초기화 체크 / streamlit run main.py 실행")