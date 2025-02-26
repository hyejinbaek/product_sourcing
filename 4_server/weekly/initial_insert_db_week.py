# 인기 키워드 월별 데이터를 주별 데이터로 변경
# ec2 ubuntu 서버에서 실제 작업 진행중
# 코드 기록을 위해 저장

import os
import pymysql
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine

DB_CONFIG = {

}

def connect_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.MySQLError as err:
        print(f"❌ DB 연결 실패: {err}")
        return None

def create_table(conn):
    """
    새로운 테이블 생성: all_weekly_popular_keywords
    """
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS all_weekly_popular_keywords (
        id INT AUTO_INCREMENT PRIMARY KEY,
        week_label VARCHAR(20),
        week_number INT,
        category_1 VARCHAR(100),
        category_2 VARCHAR(100),
        category_3 VARCHAR(100),
        rank_list INT,
        keyword VARCHAR(255),
        week_range VARCHAR(50)  -- 주차별 연도/월/일 범위를 추가한 컬럼
    );
    """
    with conn.cursor() as cursor:
        cursor.execute(create_table_sql)
    conn.commit()
    print("✅ 테이블 'all_weekly_popular_keywords' 생성 완료!")

def get_total_weeks(year):
    """
    해당 년도의 모든 월에 대해 주차 계산 (7일 단위로 주차 계산)
    """
    total_weeks = []
    
    for month in range(1, 13):
        # 월의 시작일을 계산
        month_str = f"{year}-{month:02d}"
        month_start = datetime.strptime(month_str, "%Y-%m")
        
        # 첫 번째 주는 해당 월의 첫날부터 시작
        week_start = month_start
        week_num = 1
        
        while week_start.month == month:
            # 주차의 시작일과 종료일 계산
            week_end = week_start + timedelta(days=6)  # 7일 간격
            if week_end.month != week_start.month:
                # 만약 주차의 끝이 다음 달로 넘어가면 종료일을 해당 월의 마지막 날로 설정
                week_end = month_start.replace(day=28) + timedelta(days=4)  # 다음 달 1일 이전
            
            # 주차 정보에 주차 범위 (week_range) 추가
            week_range = f"{week_start.strftime('%Y-%m-%d')} ~ {week_end.strftime('%Y-%m-%d')}"
            
            total_weeks.append((year, month, week_num, week_start.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d'), week_range))
            
            # 다음 주의 시작일을 설정
            week_start = week_end + timedelta(days=1)
            week_num += 1

    return total_weeks


if __name__ == '__main__':
    conn = connect_db()
    create_table(conn)

    all_weekly_data = []

    # ✅ 1. 2024년 모든 월 데이터 처리
    year = 2024
    total_weeks = get_total_weeks(year)

    for year, month, week_num, week_start, week_end, week_range in total_weeks:
        month_str = f"{year}-{month:02d}"
        print(f"\n📅 {month_str} {week_num}주차 ({week_start} ~ {week_end}) 데이터 처리 중...")

        query = f"""
        SELECT f.category_1, f.category_2, f.category_3, p.rank_list, p.keyword, p.month
        FROM popular_keywords p 
        JOIN file_info f ON f.file_id = p.file_id 
        WHERE p.month = '{month_str}';
        """
        df = pd.read_sql(query, conn)

        if df.empty:
            print(f"⚠️ {month_str} 데이터 없음. 다음 주차로 진행합니다.")
            continue

        for _, row in df.iterrows():
            all_weekly_data.append({
                'week_label': f"{month_str}-{week_num}주차",
                'week_number': week_num,
                'category_1': row['category_1'],
                'category_2': row['category_2'],
                'category_3': row['category_3'],
                'rank_list': row['rank_list'],
                'keyword': row['keyword'],
                'week_range': week_range  # 주차별 범위 추가
            })

    # ✅ 2. 전체 주차 데이터프레임 생성
    if all_weekly_data:
        weekly_df = pd.DataFrame(all_weekly_data)

        # ✅ 3. 요약 데이터 출력
        weekly_summary = weekly_df.groupby(['week_label']).size().reset_index(name='keyword_count')
        print("\n📈 ✅ 전체 월별 주차별 키워드 개수 요약:")
        print(weekly_summary)

        # ✅ 4. 데이터 샘플 출력
        print("\n🔎 ✅ 전체 주차별 상세 데이터 (상위 10개):")
        print(weekly_df[['week_label', 'keyword', 'rank_list', 'week_range']].head(10))

        # ✅ 5. 데이터 DB 저장
        engine = create_engine(f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}/{DB_CONFIG['database']}")
        weekly_df.to_sql('all_weekly_popular_keywords', engine, if_exists='replace', index=False)
        print("\n💾 ✅ 전체 주차별 데이터 'all_weekly_popular_keywords' 테이블에 저장 완료!")

    else:
        print("\n⚠️ 처리할 데이터가 없습니다.")

    # ✅ MySQL 연결 종료
    conn.close()
