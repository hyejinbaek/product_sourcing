import pandas as pd
import numpy as np
import re

# 파일 경로 및 시트 이름 설정
file_path = '../dataset/test.xlsx'
sheet_name = 'Sheet1'

# 두 번째 행부터 데이터를 읽어서 헤더를 적용
df = pd.read_excel(file_path, sheet_name=sheet_name, header=1)

# '업체명'과 '분류' 열 이름 변경
df.rename(columns={df.columns[0]: '업체명', df.columns[1]: '분류'}, inplace=True)

# 날짜 형식 변환 함수
def convert_date_string(date_str):
    match = re.match(r"(\d+)월\.(\d+)", date_str)
    if match:
        month, year_suffix = match.groups()
        year = '20' + year_suffix  # 주의: 향후 연도를 고려하여 수정 필요
        return f"{year}-{int(month):02d}-01"
    else:
        print(f"잘못된 날짜 형식: {date_str}")
        return None

# 유효한 날짜 열 이름 변환
date_strings = [convert_date_string(col) for col in df.columns[2:]]
valid_dates = pd.to_datetime([d for d in date_strings if d is not None], format='%Y-%m-%d', errors='coerce')

# NaT values 제거
valid_dates = valid_dates.dropna()

print(f"유효한 날짜: {valid_dates}")

# 데이터프레임 준비
weekly_data = pd.DataFrame()

for index, row in df.iterrows():
    data = row.values[2:]
    
    # 데이터 변환을 숫자형으로 강제 변환
    valid_data = pd.to_numeric(data, errors='coerce')
    if len(valid_data) > len(valid_dates):
        valid_data = valid_data[:len(valid_dates)]
    
    series_data = pd.Series(valid_data, index=valid_dates)
    print(f"Row {index} - Monthly series data:")
    print(series_data)
    
    if not series_data.empty:
        # 주별로 데이터를 그룹핑하고 집계
        weekly_series = series_data.resample('W').sum()
        print(f"Weekly series: {weekly_series}")

        # 주당 레이블 설정
        weekly_labels = [f"{row['업체명']}_{row['분류']}_W{i+1}" for i in range(len(weekly_series))]

        # 변환된 데이터를 삽입
        for label, weekly_value in zip(weekly_labels, weekly_series):
            weekly_data.loc[label] = [weekly_value]

print(f"주간 데이터 출력: {weekly_data}")

# 인덱스를 정리
if not weekly_data.empty:
    weekly_data.reset_index(drop=True, inplace=True)
    weekly_data.columns = ['Value']
    
    # 결과를 파일로 저장
    output_file_path = '../dataset/output_weekly_data.xlsx'
    weekly_data.to_excel(output_file_path, index=False)

    print(f"데이터가 성공적으로 저장되었습니다: {output_file_path}")
else:
    print("주간 데이터가 없습니다.")