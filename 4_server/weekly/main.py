import os
from flask import Flask, render_template, request, jsonify
import pymysql
import pandas as pd
import os

app = Flask(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', '3.39.226.9'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'user': os.getenv('DB_USER', 'hyejin'),
    'password': os.getenv('DB_PASSWORD', 'auton1234'),
    'database': os.getenv('DB_DATABASE', 'raw_data')
}

def connect_db():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        print(f"✅ DB 연결 성공: {DB_CONFIG['host']}, {DB_CONFIG['database']}")
        return conn
    except pymysql.MySQLError as err:
        print(f"❌ DB 연결 실패: {err}")
        return None
    
@app.route('/')
def dashboard():
    return render_template('dashboard.html', data=[], daily_clicks=[], selected_date=None)

@app.route('/get_data', methods=['POST'])
def get_data():
    conn = connect_db()
    if conn:
        selected_date = request.json.get('search_date')
        query = """
        SELECT p.month, p.rank_list, p.keyword, d.date, d.click_count
        FROM popular_keywords p
        JOIN daily_clicks d ON p.file_id = d.file_id
        WHERE p.month = %s
        ORDER BY d.date, p.rank_list;
        """
        df = pd.read_sql(query, conn, params=[selected_date])

        # 날짜를 기준으로 주를 계산하여 'week' 컬럼 추가
        df['date'] = pd.to_datetime(df['date'])
        df['week'] = df['date'].dt.isocalendar().week

        # 주차별로 그룹화하여 인기검색어 순위를 계산
        df['week_rank'] = df.groupby(['week', 'keyword'])['rank_list'].rank().astype(int)

        # 주차별 데이터로 변환
        weekly_data = df.groupby(['week', 'keyword'])[['rank_list', 'click_count']].agg({
            'rank_list': 'first', 
            'click_count': 'sum'
        }).reset_index()

        # 주차별로 데이터 반환
        weekly_data = weekly_data.sort_values(by=['week', 'rank_list'])
        
        # 일별 클릭 수 합계 계산
        daily_clicks = df.groupby('date')['click_count'].sum().reset_index().to_dict(orient='records')

        conn.close()
        return jsonify({'data': weekly_data.to_dict(orient='records'), 'daily_clicks': daily_clicks})
    return jsonify({'error': '❌ 데이터베이스 연결 실패'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
