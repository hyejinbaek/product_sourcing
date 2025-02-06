# 타오바우 사이트

from random import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from urllib.parse import quote
import time, random
#  132.0.6834.160
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
user_ag = UserAgent().random
options.add_argument('user-agent=%s'%user_ag)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)
options.add_experimental_option("prefs", {"prfile.managed_default_content_setting.images": 2})
driver = webdriver.Chrome('./chromedriver.exe', options=options)

# 크롤링 방지 설정을 undefined로 변경
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
})

wait = WebDriverWait(driver, 5)

# # 메인 화면
# main_url  = 'https://www.taobao.com/?spm=a1z02.1.icon.taobaologo'


url = 'https://login.taobao.com/member/login.jhtml'
driver.get(url=url)
time.sleep(2)

id_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-id")))
id_input.send_keys('타오바오아이디')

pw_input = wait.until(EC.presence_of_element_located((By.ID, "fm-login-password")))
pw_input.send_keys('타오바오패스워드')

wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fm-button"))).click()

#로그인대기
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
