from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service('chromedriver-win64/chromedriver.exe'), options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

try:
    # 1. 네이버 데이터랩 접속
    url = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    driver.get(url)
    time.sleep(3)

    # 2. '생활/건강' 카테고리 버튼 클릭 (자바스크립트 사용)
    category_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", category_btn)
    time.sleep(1)

    # 3. 드롭다운 메뉴에서 '생활/건강' 카테고리 선택
    category_life_health = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000008']")))
    category_life_health.click()
    time.sleep(2)
    print("✅ '생활/건강' 카테고리 선택 완료!")
    
    subcategory_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='select_btn'])[2]")))
    driver.execute_script("arguments[0].click();", subcategory_btn)
    time.sleep(1)

    subcategory_car = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000055']")))
    subcategory_car.click()
    time.sleep(2)
    print("✅ '자동차용품' 2차 카테고리 선택 완료!")
    
    # 4. 기간 선택 (오늘 날짜의 1일부터 오늘까지)
    today = datetime.today()
    start_date = today.replace(day=1)  # 이번 달 1일
    end_date = today  # 오늘 날짜

    def select_date(xpath, value, needs_scroll=False):
        """드롭다운을 열고 원하는 값을 선택하는 함수"""
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        driver.execute_script("arguments[0].click();", element)  # 드롭다운 열기
        time.sleep(1)

        option = wait.until(EC.presence_of_element_located((By.XPATH, f"//a[text()='{value}']")))

        if needs_scroll:
            # JavaScript로 스크롤 이동 후 클릭
            driver.execute_script("arguments[0].scrollIntoView(false);", option)
            time.sleep(1)

        driver.execute_script("arguments[0].click();", option)  # 옵션 선택
        time.sleep(1)
        
    # 종료 날짜 선택 (일(day) 선택 시 스크롤 필요)
    select_date("(//div[@class='select w2']/span[@class='select_btn'])[2]", end_date.year)
    select_date("(//div[@class='select w3']/span[@class='select_btn'])[3]", f"{end_date.month:02d}")
    select_date("(//div[@class='select w3']/span[@class='select_btn'])[4]", f"{end_date.day:02d}", needs_scroll=True)

    # 시작 날짜 선택 (일(day) 선택 시 스크롤 필요)
    select_date("//div[@class='select w2']/span[@class='select_btn']", start_date.year)
    select_date("(//div[@class='select w3']/span[@class='select_btn'])[1]", f"{start_date.month:02d}")
    select_date("(//div[@class='select w3']/span[@class='select_btn'])[2]", f"{start_date.day:02d}", needs_scroll=True)

    print(f"✅ 기간 선택 완료: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")
    
    # 5. 기기별 선택
    device_all_checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[@id='18_device_0']")))  # 기기별 > 전체 체크박스
    driver.execute_script("arguments[0].click();", device_all_checkbox)
    time.sleep(1)
    print("✅ '기기별 > 전체' 선택 완료")
    
    # 6. 성별 선택
    sex_all_checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[@id='19_gender_0']")))  # 성별 > 전체 체크박스
    driver.execute_script("arguments[0].click();", sex_all_checkbox)
    time.sleep(1)
    print("✅ '성별 > 전체' 선택 완료")
    
    # 7. 연령 선택
    age_all_checkbox = wait.until(EC.presence_of_element_located((
        By.XPATH, "//input[@id='20_age_0']")))  # 성별 > 전체 체크박스
    driver.execute_script("arguments[0].click();", age_all_checkbox)
    time.sleep(1)
    print("✅ '성별 > 전체' 선택 완료")
    
    # 8. 조회하기 버튼 클릭
    search_button = wait.until(EC.presence_of_element_located((
        By.XPATH, "//a[@class='btn_submit']/span[text()='조회하기']")))  # 조회하기 버튼
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(2)
    print("✅ 조회버튼 클릭 완료!")
    
    # 9. 결과 데이터 추출
    try:
        time.sleep(3)

        # ✅ 조회결과 다운로드 버튼 클릭
        download_button = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='btn_document_down' and text()='조회결과 다운로드']")))
        driver.execute_script("arguments[0].click();", download_button)
        time.sleep(3)  # 다운로드 대기
        print("✅ '조회결과 다운로드' 버튼 클릭 완료!")
        
    except Exception as e:
        print(f"❌ 데이터 추출 오류: {e}")
        
    # 10. 기기별 / 성별 / 연령별 비중 추출
    try:
        time.sleep(3)
        
        # 기기별 div class = 'popup_grap_area'
        
        
        # 성별
        
        
        # 연령별
        
    except Exception as e:
        print(f"❌ 추출 오류: {e}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    driver.quit()
