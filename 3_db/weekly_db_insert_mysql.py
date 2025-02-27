# 주별 데이터 insert 테이블 코드

import pandas as pd
import pymysql
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

# ✅ MySQL 연결 정보
DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}
print(f"🌐 DB 연결 정보: host={os.getenv('DB_HOST')}, user={os.getenv('DB_USER')}, database={os.getenv('DB_NAME')}")

def connect_db():
    """MySQL 데이터베이스 연결"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.connect.Error as err:
        print(f"❌ DB 연결 실패: {err}")
        return None  # 연결 실패 시 None 반환


def parse_filename(file_name):
    """파일명에서 날짜 및 카테고리 정보 파싱 (카테고리 구분은 언더스코어로 처리)"""
    print(f"🔍 파싱할 파일명: {file_name}")
    # 정규식을 수정하여 언더스코어로 구분된 카테고리 처리
    pattern = (
        r'(\\d+월 \\d+주차)_'            # 주차 정보
        r'(\d{4}-\d{2}-\d{2})~'       # 시작 날짜
        r'(\d{4}-\d{2}-\d{2})_'       # 종료 날짜
        r'([^\_]+(?:\_[^\_]+)*)_'      # 카테고리 1 (생활_건강 처럼 _ 포함된 카테고리)
        r'([^_]+)_'                   # 카테고리 2
        r'([^_]+)_'                   # 카테고리 3

    )
    match = re.match(pattern, file_name)
    
    if match:
        week_info, start_date, end_date, cat1, cat2, cat3 = match.groups()
        print(f"✅ 파일명 파싱 성공: {week_info}, {start_date}, {end_date}, {cat1}, {cat2}, {cat3}")
        return week_info, start_date, end_date, cat1, cat2, cat3
    else:
        raise ValueError(f"❌ 파일명이 예상된 형식과 다릅니다: {file_name}")



def insert_file_info(cursor, file_name, start_date, end_date, cat1, cat2, cat3 month):
    """file_info 테이블에 데이터 삽입 후 file_id 반환"""
    print(f"📥 file_info 테이블에 데이터 삽입 시도: {file_name}")
    query = """
        INSERT INTO file_info (file_name, category_1, category_2, category_3, start_date, end_date, month)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (file_name, cat1, cat2, cat3, start_date, end_date, month))
        print(f"✅ file_info 삽입 성공, 영향을 받은 행 수: {cursor.rowcount}")
        return cursor.lastrowid
    except Exception as e:
        print(f"❌ file_info 삽입 실패: {e}")
        raise

def insert_popular_keywords(cursor, file_id, month, df_keywords):
    """popular_keywords 테이블에 인기 검색어 데이터 삽입 (month 컬럼 추가)"""
    query = """
        INSERT INTO popular_keywords (file_id, month, rank_list, keyword)
        VALUES (%s, %s, %s, %s)
    """
    try:
        data = [(file_id, month, row['인기검색어 순위'], row['인기검색어']) for _, row in df_keywords.iterrows()]
        cursor.executemany(query, data)
        print(f"✅ 인기 검색어 삽입 성공, 삽입된 행 수: {cursor.rowcount}")
    except Exception as e:
        print(f"❌ 인기 검색어 삽입 실패: {e}")
        raise


def insert_daily_clicks(cursor, file_id, df_clicks):
    """daily_clicks 테이블에 날짜별 클릭량 데이터 삽입"""
    query = """
        INSERT INTO daily_clicks (file_id, date, click_count)
        VALUES (%s, %s, %s)
    """
    try:
        data = [(file_id, row['날짜'], int(row['클릭량'])) for _, row in df_clicks.iterrows()]
        cursor.executemany(query, data)
        print(f"✅ 날짜별 클릭량 삽입 성공, 삽입된 행 수: {cursor.rowcount}")
    except Exception as e:
        print(f"❌ 날짜별 클릭량 삽입 실패: {e}")
        raise

def process_excel(file_path):
    """Excel 파일을 읽고 MySQL에 저장"""
    file_name = os.path.basename(file_path)
    start_date, end_date, cat1, cat2, cat3 = parse_filename(file_name)

    # ✅ month 값 생성 (YYYY-MM 형식)
    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m")

    # ✅ Excel 파일 읽기
    df_keywords = pd.read_excel(file_path, sheet_name='조회결과')
    df_clicks = pd.read_excel(file_path, sheet_name='날짜별 클릭량')
    print("📁 조회결과 데이터:\n", df_keywords.head())
    print("📁 날짜별 클릭량 데이터:\n", df_clicks.head())

    conn = connect_db()
    print("---------------")
    if conn is None:
        print("❌ DB 연결 실패. 작업을 종료합니다.")
        return  # DB 연결 실패 시 작업을 중단
    cursor = conn.cursor()

    try:
        # ✅ file_info 저장 (month 값 추가)
        file_id = insert_file_info(cursor, file_name, start_date, end_date, cat1, cat2, cat3, month)
        print(f"file_info 저장 완료 (file_id={file_id})")

        # ✅ 인기 검색어 저장 (month 추가)
        insert_popular_keywords(cursor, file_id, month, df_keywords)
        print("popular_keywords 저장 완료")

        # ✅ 날짜별 클릭량 저장
        insert_daily_clicks(cursor, file_id, df_clicks)
        print("daily_clicks 저장 완료")

        conn.commit()
        print(f"✅ 모든 데이터가 성공적으로 업로드되었습니다: {file_name}")

    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생: {e}")

def main():
    """📂 지정된 폴더 내 모든 Excel 파일 처리"""
    folder_path = '../1_data_collection/crawled_data/weekly_data'
    print(f"📂 폴더 내 모든 파일 처리 시작: {folder_path}")

    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file)
            print(f"🚀 처리 시작: {file}")
            try:
                process_excel(file_path)
            except Exception as e:
                print(f"⚠️ 파일 처리 중 오류 발생 ({file}): {e}")
            print("==============================")

if __name__ == "__main__":
    main()
