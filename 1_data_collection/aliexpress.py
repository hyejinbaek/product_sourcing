# 국외시장 (알리익스프레스) 데이터 수집

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
    # 1️⃣ AliExpress 접속
    driver.get("https://www.aliexpress.com/")
    time.sleep(3)

    # 2️⃣ 팝업 닫기
    try:
        # 팝업 닫기 버튼 (element 복사 후 반영)
        popup_close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".pop-close-btn")))
        # 팝업을 화면에 보이도록 스크롤
        driver.execute_script("arguments[0].scrollIntoView(true);", popup_close_btn)
        time.sleep(1)
        popup_close_btn.click()  # 팝업 닫기
        print("팝업 닫음 ✅ (pop-close-btn)")
        time.sleep(5)

    except TimeoutException:
        print("팝업 닫기 실패: .pop-close-btn")
    except ElementNotInteractableException:
        print("팝업이 상호작용할 수 없음: .pop-close-btn")
    except Exception as e:
        print("팝업 처리 중 오류:", e)

    # 3️⃣ 검색창 찾기
    search_box = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input.search--keyword--15P08Ji")))

    # 검색창이 상호작용 가능한지 기다린 후에 실행
    driver.execute_script("arguments[0].scrollIntoView(true);", search_box)
    time.sleep(1)

    # 입력 필드가 비어있다면 clear()를 호출하여 기존 값을 삭제 후 검색어 입력
    search_box.clear()

    # 검색어 입력
    search_query = '자동차 용품'
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    # 4️⃣ 주문 기준 정렬 버튼 클릭
    try:
        order_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '주문')]")))
        # driver.execute_script("arguments[0].scrollIntoView(true);", order_button)
        time.sleep(1)
        order_button.click()
        print("주문 기준 정렬 클릭 완료 ✅")
        time.sleep(5)  # 정렬이 반영될 시간을 기다림
    except TimeoutException:
        print("❌ 주문 정렬 버튼을 찾을 수 없음")
        
    # 4️⃣-1 리스트 버튼 클릭
    try:
        list_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '리스트')]")))
        time.sleep(1)
        list_button.click()
        print("리스트 화면 클릭 완료 ✅")
        time.sleep(5)  # 정렬이 반영될 시간을 기다림
    except TimeoutException:
        print("❌ 리스트 버튼을 찾을 수 없음")

    # 5️⃣ 페이지 순회하며 상품 정보 크롤링
    results = []
    max_products = 10  # 가져올 최대 상품 개수
    page = 1

    while len(results) < max_products:
        print(f"📄 현재 페이지: {page}")
        
        try:
            products = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.list--listWrapper--3kChcwS div.search-item-card-wrapper-list")))
        except TimeoutException:
            print("⚠️ 상품을 찾을 수 없습니다. 페이지 구조 변경 가능")
            break
        
        for product in products:
            if len(results) >= max_products:
                break
            
            # 상품명
            try:
                title = product.find_element(By.CSS_SELECTOR, ".us--title--2BLrXL3 .us--titleText--yB6enKW").text
                print("1. 상품명 : ", title)
            except NoSuchElementException:
                title = "N/A"

            # 상품 가격
            try:
                price = product.find_element(By.CSS_SELECTOR, ".us--price-sale--3MpboLs").text
                print("2. 상품 가격 : ", price)
            except NoSuchElementException:
                price = "N/A"

            # 판매량
            try:
                sales = product.find_element(By.CSS_SELECTOR, ".us--trade--DUuR2_0").text
                print("3. 판매량 : ", sales)
            except NoSuchElementException:
                sales = "N/A"

            # 평점
            try:
                review = product.find_element(By.CSS_SELECTOR, ".us--starRating--2L2TcCp").text
                print("4. 평점 : ", review)
            except NoSuchElementException:
                review = "N/A"

            # 이미지
            try:
                images = product.find_element(By.CSS_SELECTOR, "img.tag--imgStyle--1lYatsQ").get_attribute("src")
                print("5. 이미지 : ", images)
            except NoSuchElementException:
                images = "N/A"

            # 판매처
            try:
                source = product.find_element(By.CSS_SELECTOR, ".us--rainbow--2Ctjram").text
                print("6. 판매처 : ", source)
            except NoSuchElementException:
                source = "N/A"

            results.append({
                "상품명": title,
                "가격": price,
                "판매실적": sales,
                "리뷰": review,
                "이미지": images,
                "판매처": source
            })
            driver.execute_script("arguments[0].scrollIntoView(true);", product)
            
        ###### 다음 페이지 이동(해결필요)
        try:
            next_page_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[class*='next-next']")))
            next_page_btn.click()
            time.sleep(5)
            page += 1
        except TimeoutException:
            print("📌 마지막 페이지 도달. 크롤링 종료.")
            break

    # 결과 xlsx 저장
    xlsx_filename = "aliexpress_products.xlsx"
    df = pd.DataFrame(results)  # pandas DataFrame으로 변환
    df.to_excel(xlsx_filename, index=False, engine='openpyxl')  # 엑셀 파일로 저장
    print(f"✅ {xlsx_filename} 파일 저장 완료!")

finally:
    driver.quit()