from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import pandas as pd

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service('chromedriver-win64/chromedriver.exe'), options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# 카테고리 목록
categories = [
    ("DIY용품", '50000933'),
    ("램프", '50000934'),
    ("배터리용품", '50000936'),
    ("공기청정용품", '50000937'),
    ("세차용품", '50000938'),
    ("키용품", '50000939'),
    ("편의용품", '50000940'),
    ("오일/소모품", '50000941'),
    ("익스테리어용품", '50000942'),
    ("인테리어용품", '50000943'),
    ("전기용품", '50000944'),
    ("수납용품", '50000945'),
    ("휴대폰용품", '50000946'),
    ("타이어/휠", '50000947'),
    ("튜닝용품", '50000948')
]

# 엑셀 파일명에 포함할 변수 초기화
period = ""
category_1 = ""
category_2 = ""
category_3 = ""

data = {
    "인기검색어 순위": [],
    "인기검색어": []
}

# 주차별 자동 기간 계산
def get_weekly_period(year):
    start_date = datetime(year, 1, 1)
    weeks = []
    for i in range(1, 53):  # 1년을 52주로 나누기
        end_date = start_date + timedelta(days=6)  # 일주일 추가
        weeks.append((start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")))
        start_date = end_date + timedelta(days=1)  # 다음 주로 넘어가기
    return weeks

# 기간 선택 자동화
def select_period_for_week(start_date, end_date):
    # 예시로 선택된 날짜로 기간 설정 (이 코드는 select_period 함수의 동작을 대체)
    print(f"🔍 기간 선택 중... {start_date} ~ {end_date}")
    # 기간 선택 코드를 여기에 적용
    # 예: select_period(start_date.split('-')[0], start_date.split('-')[1], start_date.split('-')[2], end_date.split('-')[0], end_date.split('-')[1], end_date.split('-')[2])

# 카테고리 자동 순차 선택
def select_category(category_name, category_id):
    print(f"🔍 카테고리 '{category_name}' 선택 중...")
    subcategory_3_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='select_btn'])[3]")))

    driver.execute_script("arguments[0].click();", subcategory_3_btn)
    time.sleep(1)

    subcategory_3 = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[@data-cid='{category_id}']")))
    subcategory_3.click()
    time.sleep(2)
    print(f"✅ '{category_name}' 카테고리 선택 완료!")

try:
    url = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    driver.get(url)
    time.sleep(3)

    # 기본 카테고리 선택 (생활/건강 선택)
    category_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", category_btn)
    time.sleep(1)

    # '생활/건강' 카테고리 선택
    category_life_health = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000008']")))
    category_life_health.click()
    time.sleep(2)
    print("✅ '생활/건강' 카테고리 선택 완료!")

    # 하위 카테고리 선택
    subcategory_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='select_btn'])[2]")))

    driver.execute_script("arguments[0].click();", subcategory_btn)
    time.sleep(1)

    subcategory_car = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000055']")))
    subcategory_car.click()
    time.sleep(2)

    print("✅ '자동차용품' 2차 카테고리 선택 완료!")

    # 주차별 데이터 수집
    weeks = get_weekly_period(2024)  # 예: 2024년 기준
    for start_date, end_date in weeks:
        # 각 주차에 대해 데이터 수집
        select_period_for_week(start_date, end_date)
        
        # 카테고리 자동 선택
        for category_name, category_id in categories:
            select_category(category_name, category_id)

            # 검색 버튼 클릭 (기기, 성별, 연령 선택 후)
            search_button = wait.until(EC.presence_of_element_located((By.XPATH, "//a[@class='btn_submit']/span[text()='조회하기']")))
            driver.execute_script("arguments[0].click();", search_button)
            time.sleep(2)
            print(f"✅ '{category_name}' 카테고리 {start_date} ~ {end_date} 기간 조회 완료!")

        # 데이터 다운로드 및 처리 추가 (위에서 설명된 대로)
        # 예시로 다운로드 버튼 클릭 및 데이터를 처리하는 코드 삽입
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    driver.quit()
