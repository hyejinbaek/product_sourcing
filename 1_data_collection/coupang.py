# 국내시장(쿠팡) 데이터 수집

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import time
from dotenv import load_dotenv 
import pandas as pd

# 환경 변수 로드
load_dotenv()

chrome_options = Options()
# chrome_options.add_argument('--headless')  # 헤드리스 모드 (테스트할 때 주석 처리 가능)
chrome_options.add_argument('--disable-gpu')  # GPU 비활성화
chrome_options.add_argument('--no-sandbox')  # 리눅스 환경에서 필요
chrome_options.add_argument('--disable-dev-shm-usage')  # 메모리 문제 해결
chrome_options.add_argument(
    'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'
)
chrome_options.add_argument('--ignore-certificate-errors')  # SSL 인증서 무시
chrome_options.add_argument('--ignore-ssl-errors')  # SSL 관련 오류 무시
chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 봇 탐지 우회


driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()  # 전체 화면 실행
wait = WebDriverWait(driver, 10)


url = "https://www.coupang.com/"
driver.get(url)
time.sleep(3)

search_box = driver.find_element(By.ID, "headerSearchKeyword")

# 검색어 입력
search_query = '자동차 용품'
search_box.send_keys(search_query)

# 엔터 키 입력 (또는 검색 버튼 클릭 가능)
search_box.send_keys(Keys.RETURN)

time.sleep(5)

print("완료!")