from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime, timedelta
import pandas as pd

chrome_options = Options()
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service('chromedriver-win64/chromedriver.exe'), options=chrome_options)
driver.maximize_window()
wait = WebDriverWait(driver, 10)

# 엑셀 파일명에 포함할 변수 초기화
week_label = ""
period = ""
category_1 = ""
category_2 = ""
category_3 = ""

data = {
    "인기검색어 순위": [],
    "인기검색어": []
}


def select_period(start_year, start_month, start_day, end_year, end_month, end_day, week_number):
    global period
    global week_label
    # 시작 연도 선택
    start_year_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w2'])[1]//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", start_year_btn)
    time.sleep(1)
    start_year_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//ul[@class='select_list scroll_cst']//li/a[text()='{start_year}']")))
    driver.execute_script("arguments[0].click();", start_year_option)
    time.sleep(1)

    # 시작 월 선택
    start_month_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w3'])[1]//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", start_month_btn)
    time.sleep(1)
    start_month_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"//ul[@class='select_list scroll_cst']//li/a[text()='{start_month.zfill(2)}']")))
    driver.execute_script("arguments[0].click();", start_month_option)
    time.sleep(1)

    # 시작일 선택
    start_day_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w3'])[2]//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", start_day_btn)
    time.sleep(1)
    start_day_option = wait.until(EC.presence_of_element_located((By.XPATH, f"(//div[@class='select w3'])[2]//ul[@class='select_list scroll_cst']//a[text()='{start_day.zfill(2)}']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", start_day_option)
    driver.execute_script("arguments[0].click();", start_day_option)
    time.sleep(1)

    # ✅ 종료 연도 선택
    print("🔍 종료 연도 선택 중...")
    end_year_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w2'])[2]//span[@class='select_btn']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", end_year_btn)
    driver.execute_script("arguments[0].click();", end_year_btn)
    time.sleep(1)
    
    # 모든 연도 옵션 가져와서 일치하는 값 클릭
    options = driver.find_elements(By.XPATH, "//div[@class='select w2']//ul[@class='select_list scroll_cst']//li/a")
    for option in options:
        if option.text.strip() == end_year:
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            driver.execute_script("arguments[0].click();", option)
            print(f"✅ 종료 연도 {end_year} 선택 완료.")
            break
    
    else:
        print(f"❌ {end_year} 연도를 찾을 수 없습니다.")
    period = f"{start_year}-{start_month}-{start_day}~{end_year}-{end_month}-{end_day}"
    week_label = f"{int(start_month)}월 {week_number}주차"
    print(f"✅ 기간 선택 완료: {period}")


    # ✅ 종료 월 선택 (경로 수정됨)
    print("🔍 종료 월 선택 중...")
    end_month_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w3'])[3]//span[@class='select_btn']")))
    driver.execute_script("arguments[0].scrollIntoView(true);", end_month_btn)
    driver.execute_script("arguments[0].click();", end_month_btn)
    time.sleep(1)
    
    # 모든 연도 옵션 가져와서 일치하는 값 클릭
    options = driver.find_elements(By.XPATH, "//div[@class='select w3']//ul[@class='select_list scroll_cst']//li/a")
    for option in options:
        if option.text.strip() == end_month:
            driver.execute_script("arguments[0].scrollIntoView(true);", option)
            driver.execute_script("arguments[0].click();", option)
            print(f"✅ 종료 월 {end_month} 선택 완료.")
            break
    else:
        print(f"❌ {end_month} 연도를 찾을 수 없습니다.")
    
    # ✅ 종료 일 선택
    try:
        print(f"🔍 종료 일 {end_day} 찾는 중...")
        # 종료 일 드롭다운 클릭
        end_day_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//div[@class='select w3'])[4]//span[@class='select_btn']")))
        driver.execute_script("arguments[0].click();", end_day_btn)
        time.sleep(1)

        # 모든 일 옵션 가져와서 일치하는 값 클릭
        day_options = driver.find_elements(By.XPATH, "//div[@class='select w3']//ul[@class='select_list scroll_cst']//li/a")
        for option in day_options:
            if option.text.strip() == end_day:
                driver.execute_script("arguments[0].scrollIntoView(true);", option)
                driver.execute_script("arguments[0].click();", option)
                print(f"✅ 종료 일 {end_day} 선택 완료.")
                break
        else:
            print(f"❌ {end_day} 일을 찾을 수 없습니다.")
    except Exception as e:
        print(f"❌ 종료 일 선택 중 오류 발생: {e}")
    
    print(f"✅ 기간 선택 완료: {start_year}-{start_month}-{start_day} ~ {end_year}-{end_month}-{end_day}")



try:
    # 1. 네이버 데이터랩 접속
    url = 'https://datalab.naver.com/shoppingInsight/sCategory.naver'
    driver.get(url)
    time.sleep(2)

    # 2. '생활/건강' 카테고리 버튼 클릭 (자바스크립트 사용)
    category_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//span[@class='select_btn']")))
    driver.execute_script("arguments[0].click();", category_btn)
    time.sleep(1)

    # 3. 드롭다운 메뉴에서 '생활/건강' 카테고리 선택
    category_life_health = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000008']")))
    category_life_health.click()
    time.sleep(1)
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
    
    subcategory_3 = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@data-cid='50000933']")))
    subcategory_3.click()
    time.sleep(2)
    print("✅ 3차 카테고리 선택 완료!")
    category_3 = "DIY용품"
    
    # 4. 기간 선택
    
    # 4월
    select_period(start_year="2024", start_month="04", start_day="01", end_year="2024", end_month="04", end_day="07", week_number="1")
    # select_period(start_year="2024", start_month="04", start_day="08", end_year="2024", end_month="04", end_day="14", week_number="2")
    # select_period(start_year="2024", start_month="04", start_day="15", end_year="2024", end_month="04", end_day="21", week_number="3")
    # select_period(start_year="2024", start_month="04", start_day="22", end_year="2024", end_month="04", end_day="28", week_number="4")
    # select_period(start_year="2024", start_month="04", start_day="29", end_year="2024", end_month="05", end_day="05", week_number="5")
    #############################################################################################################################################
    #############################################################################################################################################
    # 5월
    # select_period(start_year="2024", start_month="05", start_day="06", end_year="2024", end_month="05", end_day="12", week_number="1")
    # select_period(start_year="2024", start_month="05", start_day="13", end_year="2024", end_month="05", end_day="19", week_number="2")
    # select_period(start_year="2024", start_month="05", start_day="20", end_year="2024", end_month="05", end_day="26", week_number="3")
    # select_period(start_year="2024", start_month="05", start_day="27", end_year="2024", end_month="06", end_day="02", week_number="4")
    
    # 6월
    # select_period(start_year="2024", start_month="06", start_day="03", end_year="2024", end_month="06", end_day="09", week_number="1")
    # select_period(start_year="2024", start_month="06", start_day="10", end_year="2024", end_month="06", end_day="16", week_number="2")
    # select_period(start_year="2024", start_month="06", start_day="17", end_year="2024", end_month="06", end_day="23", week_number="3")
    # select_period(start_year="2024", start_month="06", start_day="24", end_year="2024", end_month="06", end_day="30", week_number="4")
    
    # 7월
    # select_period(start_year="2024", start_month="07", start_day="01", end_year="2024", end_month="07", end_day="07", week_number="1")
    # select_period(start_year="2024", start_month="07", start_day="08", end_year="2024", end_month="07", end_day="14", week_number="2")
    # select_period(start_year="2024", start_month="07", start_day="15", end_year="2024", end_month="07", end_day="21", week_number="3")
    # select_period(start_year="2024", start_month="07", start_day="22", end_year="2024", end_month="07", end_day="28", week_number="4")
    # select_period(start_year="2024", start_month="07", start_day="29", end_year="2024", end_month="08", end_day="04", week_number="5")
    
    # 8월
    # select_period(start_year="2024", start_month="08", start_day="05", end_year="2024", end_month="08", end_day="11", week_number="1")
    # select_period(start_year="2024", start_month="08", start_day="12", end_year="2024", end_month="08", end_day="18", week_number="2")
    # select_period(start_year="2024", start_month="08", start_day="19", end_year="2024", end_month="08", end_day="25", week_number="3")
    # select_period(start_year="2024", start_month="08", start_day="26", end_year="2024", end_month="09", end_day="01", week_number="4")
    
    # 9월
    
    print(f"✅ 기간 선택 완료:")
    
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
        
        
    # 11. 인기검색어
    try:
        print("🔍 [인기검색어 500개] 추출 중...")
        popular_keywords = []

        while True:
            # 현재 페이지 인기검색어 추출
            keywords_elements = driver.find_elements(By.CSS_SELECTOR, ".rank_top1000_list li a")
            for element in keywords_elements:
                rank = element.find_element(By.CLASS_NAME, "rank_top1000_num").text
                keyword = element.text.replace(rank, "").strip()
                popular_keywords.append((rank, keyword))

                # ✅ 500개 이상 추출 시 중단
                if len(popular_keywords) >= 500:
                    print(f"🎯 500개 키워드 추출 완료!\n")
                    break

            print(f"📜 현재까지 추출된 키워드 수: {len(popular_keywords)}개")

            # ✅ 500개 도달 시 루프 종료
            if len(popular_keywords) >= 500:
                break

            # ✅ 다음 페이지 버튼 클릭 여부 확인
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, ".btn_page_next")
                if "disabled" in next_button.get_attribute("class") or not next_button.is_enabled():
                    print("✅ 마지막 페이지 도달. 추출 완료!\n")
                    break
                else:
                    print("➡️ 다음 페이지로 이동 중...")
                    driver.execute_script("arguments[0].click();", next_button)
                    time.sleep(2)
            except Exception as e:
                print(f"⚠️ 다음 페이지 버튼 클릭 실패 또는 마지막 페이지 도달: {e}")
                break

        # ✅ 전체 키워드 출력
        print(f"\n🎯 인기검색어 총 {len(popular_keywords)}개 추출 완료!\n")
        for rank, keyword in popular_keywords:
            data["인기검색어 순위"].append(rank)
            data["인기검색어"].append(keyword)
            print(f"{rank}. {keyword}")
        
    except Exception as e:
        print(f"❌ 인기검색어 데이터 추출 오류: {e}")
        
    df = pd.DataFrame(data)
    output_file = f"./crawled_data/{week_label}_{period}_{category_1}_{category_2}_{category_3}.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='조회결과')
    print(f"엑셀 파일 './{output_file}'로 저장 완료!")

except Exception as e:
    print(f"❌ 오류 발생: {e}")

finally:
    driver.quit()