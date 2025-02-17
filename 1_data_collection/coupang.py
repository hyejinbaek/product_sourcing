# 국내시장(쿠팡) 상품 전체 페이지 데이터 수집

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
    # 1. 쿠팡 접속
    url = "https://www.coupang.com/"
    driver.get(url)
    time.sleep(3)

    # 2. 키워드 검색
    search_box = driver.find_element(By.ID, "headerSearchKeyword")

    search_query = '자동차 용품'
    search_box.send_keys(search_query)
    
    # 엔터 키 입력 (또는 검색 버튼 클릭 가능)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)
    print("키워드 검색 완료!")
    
    # 3. 판매량 기준 정렬
    try:
        sort_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@id='sorter-saleCountDesc']/following-sibling::label")))
        sort_button.click()
        print("판매량 기준 정렬 클릭 완료 ✅")
        time.sleep(5)  # 정렬 반영 대기
    except TimeoutException:
        print("❌ 판매량 정렬 버튼을 찾을 수 없음")
        
        
    # 4. 상품 정보 가져오기 (스크롤 포함)
    product_list = []
    collected_links = set()  # 중복 방지를 위한 링크 저장
    SCROLL_PAUSE_TIME = 2  # 스크롤 대기 시간

    try:
        last_height = driver.execute_script("return document.body.scrollHeight")  # 초기 페이지 높이
        
        while True:
            products = driver.find_elements(By.CLASS_NAME, "search-product")

            for product in products:
                try:
                    name = product.find_element(By.CLASS_NAME, "name").text.strip()
                except NoSuchElementException:
                    name = ""

                try:
                    discount_rate = product.find_element(By.CLASS_NAME, "instant-discount-rate").text.strip()
                except NoSuchElementException:
                    discount_rate = ""

                try:
                    original_price = product.find_element(By.CLASS_NAME, "base-price").text.strip()
                except NoSuchElementException:
                    original_price = ""

                try:
                    sale_price = product.find_element(By.CLASS_NAME, "price-value").text.strip()
                except NoSuchElementException:
                    sale_price = ""

                try:
                    unit_price = product.find_element(By.CLASS_NAME, "unit-price").text.strip()
                except NoSuchElementException:
                    unit_price = ""

                try:
                    delivery_date = product.find_element(By.CLASS_NAME, "arrival-info").text.strip()
                except NoSuchElementException:
                    delivery_date = ""

                try:
                    rating = product.find_element(By.CLASS_NAME, "rating").text.strip()
                except NoSuchElementException:
                    rating = ""

                try:
                    review_count = product.find_element(By.CLASS_NAME, "rating-total-count").text.strip().replace("(", "").replace(")", "")
                except NoSuchElementException:
                    review_count = ""

                try:
                    cashback = product.find_element(By.CLASS_NAME, "reward-cash-txt").text.strip()
                except NoSuchElementException:
                    cashback = ""

                try:
                    rocket_shipping = product.find_element(By.CLASS_NAME, "badge.rocket img").get_attribute("alt")
                    if "로켓배송" in rocket_shipping:
                        rocket_shipping = "O"
                    else:
                        rocket_shipping = "X"
                except NoSuchElementException:
                    rocket_shipping = "X"

                product_list.append({
                    "상품명": name,
                    "할인율": discount_rate,
                    "원가": original_price,
                    "할인가": sale_price,
                    "100ml당 가격": unit_price,
                    "배송 예정일": delivery_date,
                    "평점": rating,
                    "리뷰 수": review_count,
                    "적립금": cashback,
                    "로켓배송 여부": rocket_shipping
                })
            
            print(f"현재까지 {len(product_list)}개의 상품 수집 완료 ✅")

            # 스크롤 다운
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)  # 페이지 로딩 대기

            # 새로운 페이지 높이 확인
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # 더 이상 스크롤이 불가능하면 종료
            last_height = new_height

    except NoSuchElementException as e:
        print(f"❌ 상품 정보를 찾을 수 없음: {e}")

    # 5. 데이터 저장 (Excel 파일)
    df = pd.DataFrame(product_list)
    df.to_excel("coupang_products.xlsx", index=False)
    print("데이터 저장 완료 ✅ (coupang_products.xlsx)")


finally:
    driver.quit()