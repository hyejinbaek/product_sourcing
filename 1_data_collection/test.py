from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

# Chrome WebDriver 설정
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service('chromedriver-win64/chromedriver.exe'), options=chrome_options)
    driver.maximize_window()
    return driver

driver = setup_driver()
wait = WebDriverWait(driver, 10)

# 데이터 저장용 딕셔너리
data = {
    "기간": [], "1차 카테고리": [], "2차 카테고리": [], "3차 카테고리": [],
    "기기별 선택": [], "성별 선택": [], "연령 선택": [], "인기검색어 순위": [], "인기검색어": []
}

def click_dropdown_option(btn_xpath, options_xpath, value):
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
    driver.execute_script("arguments[0].click();", btn)
    time.sleep(1)
    options = driver.find_elements(By.XPATH, options_xpath)
    for option in options:
        if option.text.strip() == value:
            driver.execute_script("arguments[0].click();", option)
            time.sleep(1)
            return
    raise Exception(f"Option '{value}' not found.")

def select_period(start_year, start_month, start_day, end_year, end_month, end_day):
    click_dropdown_option("(//div[@class='select w2'])[1]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", start_year)
    click_dropdown_option("(//div[@class='select w3'])[1]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", start_month.zfill(2))
    click_dropdown_option("(//div[@class='select w3'])[2]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", start_day.zfill(2))
    click_dropdown_option("(//div[@class='select w2'])[2]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", end_year)
    click_dropdown_option("(//div[@class='select w3'])[3]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", end_month.zfill(2))
    click_dropdown_option("(//div[@class='select w3'])[4]//span[@class='select_btn']", "//ul[@class='select_list scroll_cst']//li/a", end_day.zfill(2))
    period = f"{start_year}-{start_month}-{start_day} ~ {end_year}-{end_month}-{end_day}"
    data["기간"].append(period)
    print(f"✅ 기간 선택 완료: {period}")

# 페이지 진입 및 필요한 설정 진행
def access_naver_datalab():
    driver.get('https://datalab.naver.com/shoppingInsight/sCategory.naver')
    time.sleep(3)

    # 카테고리 선택 진행
    click_dropdown_option("//span[@class='select_btn']", "//a[@data-cid='50000008']", "생활/건강")
    data["1차 카테고리"].append("생활/건강")
    click_dropdown_option("(//span[@class='select_btn'])[2]", "//a[@data-cid='50000055']", "자동차용품")
    data["2차 카테고리"].append("자동차용품")
    click_dropdown_option("(//span[@class='select_btn'])[3]", "//a[@data-cid='50000933']", "DIY용품")
    data["3차 카테고리"].append("DIY용품")
    
    # 기간 설정
    select_period("2024", "01", "01", "2024", "01", "31")

def make_device_gender_age_selection():
    # 기기별/성별/연령별 설정
    selections = [("18_device_0", "기기별"), ("19_gender_0", "성별"), ("20_age_0", "연령")]
    
    for element_id, description in selections:
        try:
            checkbox = wait.until(EC.presence_of_element_located((By.XPATH, f"//input[@id='{element_id}']")))
            driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
            time.sleep(0.5) # 스크롤 후 잠시 대기
            if not checkbox.is_selected(): # 이미 선택된 상태인지 확인
                driver.execute_script("arguments[0].click();", checkbox)
            data[f"{description} 선택"].append("전체")
            time.sleep(1)
            print(f"✅ '{description} > 전체' 선택 완료")
        except Exception as e:
            print(f"❌ '{description} > 전체' 선택 중 오류 발생: {e}")

def perform_search_and_download():
    # 조회 버튼 클릭
    search_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn_submit']/span[text()='조회하기']")))
    driver.execute_script("arguments[0].click();", search_button)
    time.sleep(2)
    print("✅ 조회버튼 클릭 완료!")

    # 조회 결과 다운로드
    try:
        download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='btn_document_down' and text()='조회결과 다운로드']")))
        driver.execute_script("arguments[0].click();", download_button)
        time.sleep(3)
        print("✅ '조회결과 다운로드' 버튼 클릭 완료!")
    except Exception as e:
        print(f"❌ 데이터 추출 오류: {e}")

def extract_popular_keywords():
    popular_keywords = []
    try:
        while len(popular_keywords) < 500:
            keywords_elements = driver.find_elements(By.CSS_SELECTOR, ".rank_top1000_list li a")
            for element in keywords_elements:
                rank = element.find_element(By.CLASS_NAME, "rank_top1000_num").text
                keyword = element.text.replace(rank, "").strip()
                popular_keywords.append((rank, keyword))
                if len(popular_keywords) >= 500:
                    break

            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".btn_page_next")
                if "disabled" not in next_button.get_attribute("class"):
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
                else:
                    break
            except Exception as e:
                break

        for rank, keyword in popular_keywords:
            data["인기검색어 순위"].append(rank)
            data["인기검색어"].append(keyword)
            print(f"{rank}. {keyword}")

    except Exception as e:
        print(f"❌ 인기검색어 데이터 추출 오류: {e}")

def save_data_to_excel():
    df = pd.DataFrame(data)
    output_file = 'crawled_data.xlsx'
    df.to_excel(output_file, index=False, sheet_name='조회결과')
    print(f"엑셀 파일 '{output_file}'로 저장 완료!")

try:
    access_naver_datalab()
    make_device_gender_age_selection()
    perform_search_and_download()
    extract_popular_keywords()
    save_data_to_excel()
except Exception as e:
    print(f"❌ 오류 발생: {e}")
finally:
    driver.quit()