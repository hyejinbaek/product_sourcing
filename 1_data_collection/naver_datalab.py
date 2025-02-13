# 네이버 데이터랩

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


try:
    # 1. 접속
    url = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    driver.get(url)
    time.sleep(3)
    
    # 2. 생활/건강 카테고리 클릭
    try:
        # category_life_health = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'생활/건강')]")))
        category_life_health = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='생활/건강']")))

        category_life_health.click()
        time.sleep(3)

        # 3. 자동차용품 카테고리 클릭
        category_auto = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'자동차용품')]")))
        category_auto.click()
        time.sleep(3)

        # 4. 공기청정용품 카테고리 클릭
        category_air_purifier = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'공기청정용품')]")))
        category_air_purifier.click()
        time.sleep(3)

        # 5. 차량용방향제 카테고리 클릭
        category_air_freshener = wait.until(EC.visibility_of_element_located((By.XPATH, "//span[contains(text(),'차량용방향제')]")))
        category_air_freshener.click()
        time.sleep(3)

        # 원하는 데이터 추출 작업을 여기서 진행
        # 예시: 상품 리스트 추출
        products = driver.find_elements(By.CLASS_NAME, 'product_name_class')  # 실제 클래스명으로 수정 필요
        for product in products:
            print(product.text)
    
    except TimeoutException:
        print("카테고리 클릭 중 시간 초과 오류 발생")
        


finally:
    driver.quit()