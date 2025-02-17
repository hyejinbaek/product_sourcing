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
    
    #############################################################
    # 4. 기간 선택
    ## 여기부터 기간 수정 필요
    #############################################################
    period_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//label[@for='8_set_period0']")))
    period_btn.click()
    time.sleep(1)

    # 현재 날짜 구하기
    today = datetime.today()
    start_date = today.replace(day=1)  # 이번 달 1일
    end_date = today  # 🔹 변경: 마지막 날짜가 오늘 날짜가 되도록 수정

    # 연도 선택 (시작 연도)
    year_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='select w2']/span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", year_btn)
    time.sleep(1)
    year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{start_date.year}']")))
    year_option.click()
    time.sleep(1)

    # 월 선택 (시작 월)
    month_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='select w3']/span[@class='select_btn'])[1]")))
    driver.execute_script("arguments[0].click();", month_btn)
    time.sleep(1)
    month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{start_date.month:02d}']")))
    month_option.click()
    time.sleep(1)

    # 일 선택 (시작일)
    day_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='select w3']/span[@class='select_btn'])[2]")))
    driver.execute_script("arguments[0].click();", day_btn)
    time.sleep(1)
    day_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{start_date.day:02d}']")))
    day_option.click()
    time.sleep(1)

    # 종료 연도 선택 (오늘 날짜 기준)
    end_year_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='select w2']/span[@class='select_btn'])[2]")))
    driver.execute_script("arguments[0].click();", end_year_btn)
    time.sleep(1)
    end_year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{end_date.year}']")))
    end_year_option.click()
    time.sleep(1)

    # 종료 월 선택 (오늘 날짜 기준)
    end_month_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='select w3']/span[@class='select_btn'])[3]")))
    driver.execute_script("arguments[0].click();", end_month_btn)
    time.sleep(1)
    end_month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{end_date.month:02d}']")))
    end_month_option.click()
    time.sleep(1)

    # 종료 일 선택 (오늘 날짜 기준)
    end_day_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//div[@class='select w3']/span[@class='select_btn'])[4]")))
    driver.execute_script("arguments[0].click();", end_day_btn)
    time.sleep(1)
    end_day_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//a[text()='{end_date.day:02d}']")))
    end_day_option.click()
    time.sleep(1)

    print(f"✅ 기간 선택 완료: {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}")

    
    # 5. 기기별 선택
    
    # 6. 성별 선택
    
    # 7. 연령 선택
    
    # 8. 조회하기 버튼 클릭

    

except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    driver.quit()
