# 국내시장(쿠팡) 상품 상세 페이지 데이터 수집

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
chrome_options.add_argument('--enable-unsafe-swiftshader')  # WebGL 관련 경고 해결를 위한 설정 추가


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
    product_data = []

    products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-product-wrap")))

    for index, product in enumerate(products[:2]):  # 상위 2개 상품 크롤링
        try:
            product_name = product.find_element(By.CSS_SELECTOR, ".name").text
            product_price = product.find_element(By.CSS_SELECTOR, ".price-value").text
            print(f"{index + 1}. {product_name} - {product_price}원")

            # 상품 클릭하여 상세 페이지 이동
            product.click()
            time.sleep(3)

            try:
                product_title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".prod-buy-header__title"))).text.strip()
                print(" 1. 상품명 : ", product_title)
            except NoSuchElementException:
                product_title = "정보 없음"

            try:
                product_price_detail = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.total-price > strong"))).text.strip()
            except NoSuchElementException:
                product_price_detail = "정보 없음"

            try:
                product_description = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.prod-description"))).text.strip()
            except NoSuchElementException:
                product_description = "정보 없음"

            # 상품 상태(품절 여부)
            try:
                stock_message = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.fashion-unavailable-msg"))).text.strip()
            except NoSuchElementException:
                stock_message = "구매 가능"

            # 쿠폰 가격 등 추가 정보 수집
            try:
                coupon_price = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "span.prod-coupon-price > span.total-price > strong"))).text.strip()
            except NoSuchElementException:
                coupon_price = "정보 없음"

            # 데이터 저장
            product_data.append({
                "상품명": product_title,
                "가격": product_price_detail,
                "상세정보": product_description,
                "품절 여부": stock_message,
                "쿠폰 가격": coupon_price,
            })
            print(f"✅ {product_title} 정보 저장 완료")

            driver.back()
            time.sleep(3)
            products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".search-product-wrap")))
            
        except Exception as e:
            print(f"⚠️ {index+1}번째 상품 크롤링 중 오류 발생: {e}")
            continue
    

    # 5. 데이터 저장 (Excel 파일)
    df = pd.DataFrame(product_data)
    df.to_excel("coupang_products.xlsx", index=False)
    print("데이터 저장 완료 ✅ (coupang_products.xlsx)")


finally:
    driver.quit()