# 네이버 데이터랩 데이터 + 클릭량 파일 다운로드 -> 하나의 파일로 합치기
import pandas as pd
from openpyxl import load_workbook

# 1. CSV 파일 읽기
csv_file = '../../../../../Downloads/naver_datalab_shoppingInsight_category_일간_data_20250221135638.csv'  # CSV 파일 경로
df = pd.read_csv(csv_file, header=7)  # 8번째 행부터 데이터를 읽어옵니다.
print("CSV Data:")
print(df.head())

# 2. 기존 Excel 파일 읽기
excel_file = './crawled_data/2024-01-01~2024-01-31_생활_건강_자동차용품_DIY용품_전체_전체_전체.xlsx'  # 기존 Excel 파일 경로
df_excel = pd.read_excel(excel_file)  # sheet_name을 지정하지 않으면 기본적으로 단일 시트를 읽습니다.
print("Excel Data:")
print(df_excel.head())

# 3. 컬럼 이름 변경
# CSV와 Excel 파일의 컬럼 이름이 겹치지 않도록 이름을 변경
df.columns = ['날짜', '클릭량']  # CSV 파일의 컬럼 이름을 변경

with pd.ExcelWriter(excel_file, engine='openpyxl', mode='a',if_sheet_exists='replace') as writer:
    # 기존 Excel 파일을 열고, 추가하려는 데이터프레임을 새로운 시트에 작성
    df.to_excel(writer, sheet_name='날짜별 클릭량', index=False)
    df_excel.to_excel(writer, sheet_name='조회결과', index=False)

print(f"'{excel_file}'에 새로운 시트가 추가되었습니다.")