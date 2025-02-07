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
        time.sleep(10)

    except TimeoutException:
        print("팝업 닫기 실패: .pop-close-btn")
    except ElementNotInteractableException:
        print("팝업이 상호작용할 수 없음: .pop-close-btn")
    except Exception as e:
        print("팝업 처리 중 오류:", e)

    # 3️⃣ 검색창 찾기
    search_box = wait.until(EC.presence_of_element_located((By.NAME, "SearchText")))

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

    # 4️⃣ 상품 정보 가져오기
    products = driver.find_elements(By.CSS_SELECTOR, ".manhattan--container--1lP57Ag")
    results = []
    max_results = 2  # 가져올 최대 상품 개수
    for product in products[:max_results]:
        try:
            title = product.find_element(By.CSS_SELECTOR, ".manhattan--titleText--WccSjUS").text
            price = product.find_element(By.CSS_SELECTOR, ".manhattan--price-sale--1CCSZfK").text
            link = product.find_element(By.CSS_SELECTOR, "a").get_attribute("href")

            results.append({
                "상품명": title,
                "가격": price,
                "링크": link
            })
        except NoSuchElementException as e:
            print("일부 데이터를 가져오지 못했습니다:", e)

    # 결과 출력
    for result in results:
        print(result)

finally:
    driver.quit()