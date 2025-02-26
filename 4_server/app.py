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
    # 초기 로딩 시 데이터 로드 생략
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
        WHERE d.date = %s
        ORDER BY d.date, p.rank_list;
        """
        df = pd.read_sql(query, conn, params=[selected_date])
        daily_clicks = df.groupby('date')['click_count'].sum().reset_index().to_dict(orient='records')
        conn.close()
        return jsonify({'data': df.to_dict(orient='records'), 'daily_clicks': daily_clicks})
    return jsonify({'error': '❌ 데이터베이스 연결 실패'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
