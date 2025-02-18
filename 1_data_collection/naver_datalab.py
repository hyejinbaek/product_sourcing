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
        # 잠시 대기하여 결과 로딩 완료 후 데이터를 추출
        time.sleep(3)  # 페이지 로딩을 기다립니다 (시간은 필요에 따라 조절)

        # 결과 테이블 추출 (여기서는 예시로 테이블을 추출한다고 가정)
        results_table = wait.until(EC.presence_of_element_located((By.XPATH, "//table[@class='tbl_data']")))  # 테이블의 XPATH는 실제 상황에 맞게 조정

        # 테이블 내의 데이터 행 추출
        rows = results_table.find_elements(By.XPATH, ".//tr")
        
        data = []
        for row in rows[1:]:  # 첫 번째 행은 헤더이므로 제외
            cols = row.find_elements(By.XPATH, ".//td")
            if len(cols) > 0:
                # 각 열에서 데이터를 추출
                data_row = {
                    'Product Name': cols[0].text.strip(),
                    'Price': cols[1].text.strip(),
                    'Sales Count': cols[2].text.strip(),
                    'Rating': cols[3].text.strip()
                }
                data.append(data_row)
        
        # 데이터 출력
        for entry in data:
            print(entry)
        
        print("✅ 데이터 추출 완료!")
    except Exception as e:
        print(f"❌ 데이터 추출 오류: {e}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    driver.quit()
