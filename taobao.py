# 타오바우 사이트


import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from urllib.parse import quote
import time
import random
from dotenv import load_dotenv 
# 환경 변수 로드
load_dotenv() 

chrome_options = Options()
# chrome_options.add_argument('--headless')  # 헤드리스 모드
chrome_options.add_argument('--disable-gpu')  # GPU 비활성화 (윈도우용)
chrome_options.add_argument('--no-sandbox')  # 리눅스 환경에서 필요
chrome_options.add_argument('--disable-dev-shm-usage')  # 메모리 문제 해결
chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36')
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window() #전체 화면 시행 
wait = WebDriverWait(driver, 5)

# 사용자 정보 설정 
ID = os.getenv("ID") 
PASSWORD = os.getenv("PASSWORD") 

# url = 'https://login.taobao.com/member/login.jhtml'
url = 'https://login.taobao.com/'
driver.get(url=url)
time.sleep(2)

id_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-id")))
id_input.send_keys(ID)

pw_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-password")))
pw_input.send_keys(PASSWORD)

time.sleep(2)

# # 로그인 버튼 클릭
# wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fm-btn"))).click()

# 로그인 버튼 클릭
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fm-btn"))).click()

# 보안 확인 처리
try:
    # 보안 캡차 대기
    slider = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "nc_iconfont.btn_slide")))
    
    # 드래그 앤 드롭 처리
    action = ActionChains(driver)
    action.click_and_hold(slider).perform()
    action.move_by_offset(300, 0).perform()  # 적절한 거리로 드래그
    action.release().perform()
    time.sleep(2)  # 보안 처리 대기
except TimeoutException:
    print("보안 확인이 필요하지 않음.")

# 로그인 성공 여부 확인
try:
    taobao_name_tag = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "site-nav-login-info-nick")))
    print(f" >>>> 접속자:{taobao_name_tag.text}")
except TimeoutException:
    print("로그인 실패 또는 추가 보안 확인 필요.")


# 로그인대기
time.sleep(random.randint(5, 10))

taobao_name_tag = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "site-nav-login-info-nick ")))
print(f" >>>> 접속자:{taobao_name_tag.text}")

url = 'https://s.taobao.com/search?q=' + quote('压片糖果')
driver.get(url)
time.sleep(2)

#이미지 검색
img_path = '이미지경로'

img_search = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_IMGSeachUploadBtn"]')))
img_search.send_keys(img_path)
time.sleep(2)

search_link = driver.current_url
product_link = driver.find_element_by_xpath('//*[@id="imgsearch-itemlist"]/div/div/div/div[1]/div[1]/div/div[1]/a').get_attribute('href')
product_price = driver.find_element_by_xpath('//*[@id="imgsearch-itemlist"]/div/div/div/div[1]/div[2]/div[1]/strong').text

print('검색링크 > ', search_link)
print('첫번째 상품 상품링크 > ', product_link)
print('첫번째 상품 상품가격 > ', product_price)
