import pandas as pd
import pymysql
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

def connect_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.connect.Error as err:
        print(f"❌ DB 연결 실패: {err}")
        return None

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    table_queries = [
        """
        CREATE TABLE IF NOT EXISTS file_info (
            file_id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            category_1 VARCHAR(50) NOT NULL,
            category_2 VARCHAR(50) NOT NULL,
            category_3 VARCHAR(100) NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            month CHAR(7) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS popular_keywords (
            keyword_id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            month CHAR(7) NOT NULL,
            rank_list INT NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES file_info(file_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_clicks (
            click_id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            click_count INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES file_info(file_id) ON DELETE CASCADE
        )
        """
    ]
    for query in table_queries:
        cursor.execute(query)

    conn.commit()
    conn.close()
    print("✅ 모든 테이블 생성 완료")

def parse_filename(file_name):
    pattern = (
        r'(\d+월\s\d+주차)_'          # 주차 정보
        r'(\d{4}-\d{2}-\d{2})~'       # 시작 날짜
        r'(\d{4}-\d{2}-\d{2})_'       # 종료 날짜
        r'([^\_]+(?:\_[^\_]+)*)_'     # 카테고리 1
        r'([^_]+)_'                    # 카테고리 2
        r'(.+)'                        # 카테고리 3
    )
    match = re.match(pattern, file_name)

    if match:
        return match.groups()
    else:
        raise ValueError(f"❌ 파일명이 예상된 형식과 다릅니다: {file_name}")

def insert_file_info(cursor, file_name, week_info, start_date, end_date, cat1, cat2, cat3, month):
    query = """
        INSERT INTO file_info (file_name, category_1, category_2, category_3, week_info, start_date, end_date, month)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (file_name, cat1, cat2, cat3, week_info, start_date, end_date, month))
    return cursor.lastrowid

def insert_popular_keywords(cursor, file_id, week_info, month, df_keywords):
    query = """
        INSERT INTO popular_keywords (file_id, week_info, month, rank_list, keyword)
        VALUES (%s, %s, %s, %s, %s)
    """
    data = [
        (file_id, week_info, month, row['인기검색어 순위'], row['인기검색어'])
        for _, row in df_keywords.iterrows()
    ]
    cursor.executemany(query, data)

def insert_daily_clicks(cursor, file_id, week_info, df_clicks):
    query = """
        INSERT INTO daily_clicks (file_id, week_info, date, click_count)
        VALUES (%s, %s, %s, %s)
    """
    data = [
        (file_id, week_info, row['날짜'], int(row['클릭량']))
        for _, row in df_clicks.iterrows()
    ]
    cursor.executemany(query, data)

def process_excel(file_path):
    file_name = os.path.basename(file_path)
    week_info, start_date, end_date, cat1, cat2, cat3 = parse_filename(file_name)

    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m")

    df_keywords = pd.read_excel(file_path, sheet_name='조회결과')
    df_clicks = pd.read_excel(file_path, sheet_name='날짜별 클릭량')

    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        file_id = insert_file_info(cursor, file_name, week_info, start_date, end_date, cat1, cat2, cat3, month)
        insert_popular_keywords(cursor, file_id, week_info, month, df_keywords)
        insert_daily_clicks(cursor, file_id, week_info, df_clicks)
        conn.commit()
        print(f"✅ 업로드 성공: {file_name}")
    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생 ({file_name}): {e}")
    finally:
        conn.close()

def main():
    folder_path = '../1_data_collection/crawled_data/test_data'

    print("📂 폴더 내 모든 파일 처리 시작")

    create_tables()

    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file)
            try:
                process_excel(file_path)
            except Exception as e:
                print(f"⚠️ 파일 처리 중 오류 발생 ({file}): {e}")

    print("✅ 모든 파일 처리 완료")

if __name__ == '__main__':
    main()
import pandas as pd
import pymysql
import re
import os
from datetime import datetime
from dotenv import load_dotenv

# ✅ .env 파일 로드
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'port': int(os.getenv('DB_PORT')),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE')
}

def connect_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.connect.Error as err:
        print(f"❌ DB 연결 실패: {err}")
        return None

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    table_queries = [
        """
        CREATE TABLE IF NOT EXISTS file_info (
            file_id INT AUTO_INCREMENT PRIMARY KEY,
            file_name VARCHAR(255) NOT NULL,
            category_1 VARCHAR(50) NOT NULL,
            category_2 VARCHAR(50) NOT NULL,
            category_3 VARCHAR(100) NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            month CHAR(7) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS popular_keywords (
            keyword_id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            month CHAR(7) NOT NULL,
            rank_list INT NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES file_info(file_id) ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_clicks (
            click_id INT AUTO_INCREMENT PRIMARY KEY,
            file_id INT NOT NULL,
            week_info VARCHAR(20) NOT NULL,
            date DATE NOT NULL,
            click_count INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (file_id) REFERENCES file_info(file_id) ON DELETE CASCADE
        )
        """
    ]
    for query in table_queries:
        cursor.execute(query)

    conn.commit()
    conn.close()
    print("✅ 모든 테이블 생성 완료")

def parse_filename(file_name):
    pattern = (
        r'(\d+월\s\d+주차)_'          # 주차 정보
        r'(\d{4}-\d{2}-\d{2})~'       # 시작 날짜
        r'(\d{4}-\d{2}-\d{2})_'       # 종료 날짜
        r'([^\_]+(?:\_[^\_]+)*)_'     # 카테고리 1
        r'([^_]+)_'                    # 카테고리 2
        r'(.+)'                        # 카테고리 3
    )
    match = re.match(pattern, file_name)

    if match:
        return match.groups()
    else:
        raise ValueError(f"❌ 파일명이 예상된 형식과 다릅니다: {file_name}")

def insert_file_info(cursor, file_name, week_info, start_date, end_date, cat1, cat2, cat3, month):
    query = """
        INSERT INTO file_info (file_name, category_1, category_2, category_3, week_info, start_date, end_date, month)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (file_name, cat1, cat2, cat3, week_info, start_date, end_date, month))
    return cursor.lastrowid

def insert_popular_keywords(cursor, file_id, week_info, month, df_keywords):
    query = """
        INSERT INTO popular_keywords (file_id, week_info, month, rank_list, keyword)
        VALUES (%s, %s, %s, %s, %s)
    """
    data = [
        (file_id, week_info, month, row['인기검색어 순위'], row['인기검색어'])
        for _, row in df_keywords.iterrows()
    ]
    cursor.executemany(query, data)

def insert_daily_clicks(cursor, file_id, week_info, df_clicks):
    query = """
        INSERT INTO daily_clicks (file_id, week_info, date, click_count)
        VALUES (%s, %s, %s, %s)
    """
    data = [
        (file_id, week_info, row['날짜'], int(row['클릭량']))
        for _, row in df_clicks.iterrows()
    ]
    cursor.executemany(query, data)

def process_excel(file_path):
    file_name = os.path.basename(file_path)
    week_info, start_date, end_date, cat1, cat2, cat3 = parse_filename(file_name)

    month = datetime.strptime(start_date, "%Y-%m-%d").strftime("%Y-%m")

    df_keywords = pd.read_excel(file_path, sheet_name='조회결과')
    df_clicks = pd.read_excel(file_path, sheet_name='날짜별 클릭량')

    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()

    try:
        file_id = insert_file_info(cursor, file_name, week_info, start_date, end_date, cat1, cat2, cat3, month)
        insert_popular_keywords(cursor, file_id, week_info, month, df_keywords)
        insert_daily_clicks(cursor, file_id, week_info, df_clicks)
        conn.commit()
        print(f"✅ 업로드 성공: {file_name}")
    except Exception as e:
        conn.rollback()
        print(f"❌ 오류 발생 ({file_name}): {e}")
    finally:
        conn.close()

def main():
    folder_path = '../1_data_collection/crawled_data/weekly_data'

    print("📂 폴더 내 모든 파일 처리 시작")

    create_tables()

    for file in os.listdir(folder_path):
        if file.endswith('.xlsx'):
            file_path = os.path.join(folder_path, file)
            try:
                process_excel(file_path)
            except Exception as e:
                print(f"⚠️ 파일 처리 중 오류 발생 ({file}): {e}")

    print("✅ 모든 파일 처리 완료")

if __name__ == '__main__':
    main()
