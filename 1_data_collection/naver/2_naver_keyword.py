import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import urllib
from urllib import request
import re
import json
import time
from datetime import datetime
from random import shuffle
from dotenv import load_dotenv
import os
import csv

load_dotenv()

start_time = time.time()

API_KEYS = []
index = 1  # API 계정 번호

while True:
    client_id = os.getenv(f"NAVER_CLIENT_ID_{index}")
    client_secret = os.getenv(f"NAVER_CLIENT_SECRET_{index}")
    
    if not client_id or not client_secret:
        break  
    
    API_KEYS.append({"client_id": client_id, "client_secret": client_secret})
    index += 1

api_index = 0

def get_api_key():
    return API_KEYS[api_index]["client_id"], API_KEYS[api_index]["client_secret"]

def switch_api_key():
    global api_index
    api_index += 1
    if api_index >= len(API_KEYS):
        print("🚨 모든 API 키가 소진되었습니다. 1시간 대기 후 재시도합니다.")
        time.sleep(3600)  
        api_index = 0  
    print(f"🔄 새로운 API 키 사용: {API_KEYS[api_index]['client_id']}")

def send_request(requested, body, max_retries=5):
    global api_index
    retries = 0
    while retries < max_retries:
        client_id, client_secret = get_api_key()
        requested.add_header("X-Naver-Client-Id", client_id)
        requested.add_header("X-Naver-Client-Secret", client_secret)
        
        try:
            response = request.urlopen(requested, data=body.encode("utf-8"))
            return response.read().decode("utf-8")
        except request.HTTPError as e:
            if e.code == 429:
                print(f"🚨 API 키 {client_id} 요청 제한 초과! 다음 키로 변경 중...")
                switch_api_key()
                retries += 1
            else:
                raise  
    
    print("🚨 최대 재시도 횟수 초과, 요청 실패")
    return None

API_URL = "https://openapi.naver.com/v1/datalab/search"
requested = request.Request(API_URL)
requested.add_header("Content-Type", "application/json")

file_path = './dataset/month_3depth/test.xlsx'
file_ext = os.path.splitext(file_path)[1].lower()

if file_ext == ".csv":
    df = pd.read_csv(file_path)
elif file_ext in [".xls", ".xlsx"]:
    df = pd.read_excel(file_path)
else:
    raise ValueError(f"지원하지 않는 파일 형식: {file_ext}")

STANDARD_KEYWORD = df.iloc[0]["인기검색어"]
print("🎯 기준 키워드:", STANDARD_KEYWORD)

names = df["인기검색어"].values
body_dict = {
    "startDate": "2016-01-01",
    "endDate": "2025-03-31",
    "timeUnit": "month"
}

v_list = [{"groupName": STANDARD_KEYWORD, "keywords": [STANDARD_KEYWORD]}] + [
    {"groupName": i, "keywords": [i]} for i in names
]
shuffle(v_list[1:])
split_list = [
    [{"groupName": STANDARD_KEYWORD, "keywords": [STANDARD_KEYWORD]}] + v_list[i : i + 4]
    for i in range(1, len(v_list), 4)
]

sample_body = body_dict.copy()
sample_body["keywordGroups"] = split_list[0]
sample_body = json.dumps(sample_body, ensure_ascii=False)

sample_response = send_request(requested, sample_body)
if sample_response:
    sample_result = json.loads(sample_response)
    for i in sample_result["results"]:
        if i["title"] == STANDARD_KEYWORD:
            sample_standard = i["data"]

scale = sample_standard[0]["ratio"]
df_dict = {}
df_dict[STANDARD_KEYWORD] = np.array([i["ratio"] for i in sample_standard])
length = len(df_dict[STANDARD_KEYWORD])
date = np.array([i["period"] for i in sample_standard])

for keyword_group in split_list:
    body_dict["keywordGroups"] = keyword_group
    body = json.dumps(body_dict, ensure_ascii=False)
    response = send_request(requested, body)

    if response:
        result = json.loads(response)
        compare = next((i["data"] for i in result["results"] if i["title"] == STANDARD_KEYWORD), None)
        if compare:
            compare = compare[0]["ratio"]
            scaling = scale / compare if compare else 1

            for i in result["results"]:
                if i["title"] != STANDARD_KEYWORD:
                    value = [j["ratio"] * scaling for j in i["data"]]
                    if not value:
                        value = [0] * length
                    else:
                        value += [value[-1]] * (length - len(value))
                    df_dict[i["title"]] = np.array(value)
                    print(f"📊 키워드 '{i['title']}' 데이터 변환 완료")
                    
            print(f"⚖️ 기준값: {scale}, 비교값: {compare}, 스케일링 비율: {scaling}")
            
# 가장 긴 데이터 길이 찾기
max_length = max(len(v) for v in df_dict.values())

# date 배열 길이 조정 (max_length보다 짧으면 마지막 날짜 반복)
if len(date) < max_length:
    last_date = date[-1]
    date = np.append(date, [last_date] * (max_length - len(date)))

# df_dict 내부 데이터 길이 맞추기
for key in df_dict.keys():
    value_length = len(df_dict[key])
    
    if value_length < max_length:
        last_value = df_dict[key][-1] if value_length > 0 else 0  # 마지막 값 또는 0으로 채우기
        df_dict[key] = np.append(df_dict[key], [last_value] * (max_length - value_length))


df_result = pd.DataFrame(df_dict)
# date 배열을 맞춘 후 데이터프레임에 추가
df_result["date"] = date[:max_length]  # max_length에 맞춰 잘라서 추가
df_result.set_index("date", inplace=True)
df_result.to_csv("./dataset/month_3depth_result/keyword.csv", encoding="utf-8-sig")
print("✅ CSV 파일 저장 완료: keyword.csv")

end_time = time.time()
elapsed_time = end_time - start_time
print(f"🚀 전체 실행 완료 (총 소요 시간: {elapsed_time:.2f}초)")
