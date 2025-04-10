from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import time
import os

# 셀레니움 드라이버 설정
chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 10)
driver.maximize_window()

# 엑셀 저장 폴더 생성
if not os.path.exists("./crawled_data"):
    os.makedirs("./crawled_data")

def select_dropdown_option(dropdown_xpath, option_text):
    """드롭다운 옵션 선택 함수"""
    try:
        dropdown_btn = wait.until(EC.element_to_be_clickable((By.XPATH, dropdown_xpath)))
        driver.execute_script("arguments[0].click();", dropdown_btn)
        time.sleep(0.5)

        # ✅ 기존 방식에서 구조 보완
        option_xpath = f"{dropdown_xpath}/parent::div/ul/li/a[text()='{option_text}']"
        option = wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
        driver.execute_script("arguments[0].click();", option)
        time.sleep(0.5)
    except Exception as e:
        print(f"❌ 드롭다운 선택 실패 - 옵션: {option_text}, 에러: {e}")
        raise e


def crawl_keywords(period, category_1, category_2, category_3):
    """월별 인기 검색어 크롤링 후 저장 함수"""
    data = {"인기검색어 순위": [], "인기검색어": []}
    popular_keywords = []

    try:
        print(f"🔍 [인기검색어 500개] 추출 중: {period}")
        while True:
            keywords_elements = driver.find_elements(By.CSS_SELECTOR, ".rank_top1000_list li a")
            for element in keywords_elements:
                rank = element.find_element(By.CLASS_NAME, "rank_top1000_num").text
                keyword = element.text.replace(rank, "").strip()
                popular_keywords.append((rank, keyword))

                if len(popular_keywords) >= 500:
                    break
            if len(popular_keywords) >= 500:
                break
            
            # ✅ 수집 개수 실시간 출력
            if len(popular_keywords) % 10 == 0:
                print(f"  ▶ 수집 진행 중... {len(popular_keywords)} / 500개")

            if len(popular_keywords) >= 500:
                break

            # 다음 페이지 이동
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".btn_page_next")
                if "disabled" in next_button.get_attribute("class"):
                    break
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)
            except:
                break

        for rank, keyword in popular_keywords:
            data["인기검색어 순위"].append(rank)
            data["인기검색어"].append(keyword)

        df = pd.DataFrame(data)
        filename = f"./crawled_data/{period}_{category_1}_{category_2}_{category_3}.xlsx"
        df.to_excel(filename, index=False, sheet_name="조회결과")
        print(f"✅ {period} 엑셀 저장 완료 ({len(popular_keywords)}개)\n")
    except Exception as e:
        print(f"❌ [{period}] 검색어 추출 오류: {e}")

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
    category_1 = "생활_건강"
    print("✅ '생활/건강' 카테고리 선택 완료!")

    
    subcategory_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='select_btn'])[2]")))
    driver.execute_script("arguments[0].click();", subcategory_btn)
    category_2 = "자동차용품"
    time.sleep(1)

    subcategory_car = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000055']")))
    subcategory_car.click()
    time.sleep(2)
    
    print("✅ '자동차용품' 2차 카테고리 선택 완료!")
    
    ### 3차 카테고리 선택 (아래의 내용은 id 번호 정리 - 순서대로 진행)
    # <a href="#" data-cid="50000933" class="option">DIY용품</a></li><li class="">
    # <a href="#" data-cid="50000934" class="option">램프</a></li><li class="">
    # <a href="#" data-cid="50000936" class="option">배터리용품</a></li><li class="">
    # <a href="#" data-cid="50000937" class="option">공기청정용품</a></li><li class="">
    # <a href="#" data-cid="50000938" class="option">세차용품</a></li><li class="">
    # <a href="#" data-cid="50000939" class="option">키용품</a></li><li class="">
    # <a href="#" data-cid="50000940" class="option">편의용품</a></li><li class="">
    # <a href="#" data-cid="50000941" class="option">오일/소모품</a></li><li class="">
    # <a href="#" data-cid="50000942" class="option">익스테리어용품</a></li><li class="">
    # <a href="#" data-cid="50000943" class="option">인테리어용품</a></li><li class="">
    # <a href="#" data-cid="50000944" class="option">전기용품</a></li><li class="">
    # <a href="#" data-cid="50000945" class="option">수납용품</a></li><li class="">
    # <a href="#" data-cid="50000946" class="option">휴대폰용품</a></li><li class="">
    # <a href="#" data-cid="50000947" class="option">타이어/휠</a></li><li class="">
    # <a href="#" data-cid="50000948" class="option">튜닝용품</a></li></ul></div>
    subcategory_3_btn = wait.until(EC.presence_of_element_located((By.XPATH, "(//span[@class='select_btn'])[3]")))
    driver.execute_script("arguments[0].click();", subcategory_3_btn)
    time.sleep(1)
    
    subcategory_3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000947']")))
    subcategory_3.click()
    time.sleep(2)
    print("✅ 3차 카테고리 선택 완료!")
    category_3 = "타이어_휠"
    
    print("🔍 주기 선택 중...")
    period_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='select w4']//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", period_btn)
    time.sleep(1)

    monthly_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@class='select w4']//a[text()='월간']")))
    driver.execute_script("arguments[0].click();", monthly_option)
    print("✅ '월간' 주기 선택 완료!")
    time.sleep(1)

    # 날짜 반복 설정
    start_date = datetime(2017, 8, 1)
    end_date = datetime(2025, 3, 1)
    current_date = start_date

    while current_date <= end_date:
        period = current_date.strftime("%Y_%m")
        year = current_date.strftime("%Y")
        month = current_date.strftime("%m")

        print(f"\n📆 현재 작업 중: {period}")

        # 날짜 설정
        select_dropdown_option("(//div[@class='set_period_target']//div[@class='select w2'])[1]/span", year)
        time.sleep(0.5)
        select_dropdown_option("(//div[@class='set_period_target']//div[@class='select w3'])[1]/span", month)
        time.sleep(0.5)
        select_dropdown_option("(//div[@class='set_period_target']//div[@class='select w2'])[2]/span", year)
        time.sleep(0.5)
        # select_dropdown_option("(//div[@class='set_period_target']//div[@class='select w3'])[2]/span", month)
        # time.sleep(0.5)

        # 조회 클릭
        search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn_submit']/span[text()='조회하기']")))
        driver.execute_script("arguments[0].click();", search_button)
        time.sleep(3)

        # 인기 키워드 수집 및 저장
        crawl_keywords(period, category_1, category_2, category_3)

        # 다음 달로 이동
        current_date += relativedelta(months=1)

except Exception as e:
    print(f"❌ 전체 크롤링 오류: {e}")
finally:
    driver.quit()
    print("🚀 크롤링 완료!")