import streamlit as st
import pandas as pd
import pymysql
import os

# 환경 변수에서 DB 설정값을 가져옵니다
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '13.209.73.238'),  # 기본값을 지정
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'hyejin'),
    'password': os.getenv('DB_PASSWORD', 'auton1234'),
    'database': os.getenv('DB_DATABASE', 'raw_data')
}

# 데이터베이스 연결 함수
def connect_db():
    """MySQL 데이터베이스 연결"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.MySQLError as err:
        print(f"❌ DB 연결 실패: {err}")
        return None  # 연결 실패 시 None 반환

# DB 연결
conn = connect_db()

if conn:
    query = """
    SELECT p.month, p.rank_list, p.keyword, d.date, d.click_count
    FROM popular_keywords p
    JOIN daily_clicks d ON p.file_id = d.file_id
    ORDER BY p.month, p.rank_list;
    """


    # 쿼리 실행 및 결과를 DataFrame으로 변환
    df = pd.read_sql(query, conn)

    # Streamlit 대시보드
    st.title('인기 검색어 분석 대시보드')

    # 날짜별 클릭 수 합계로 차트 표시
    daily_clicks = df.groupby('date')['click_count'].sum().reset_index()
    st.line_chart(daily_clicks.set_index('date')['click_count'])

    # 전체 데이터를 테이블로 표시
    st.dataframe(df)

    # DB 연결 종료
    conn.close()
else:
    st.error("DB 연결에 실패했습니다.")
