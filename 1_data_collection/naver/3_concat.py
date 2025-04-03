# 데이터랩 인기검색어 파일과 클릭수 파일 합치기

import pandas as pd

# 파일 경로 (업로드한 파일로 변경해야 함)
file_xlsx = "./dataset/month_3depth/24년_튜닝용품_인기검색어.xlsx"  # 1번 데이터 파일 (엑셀)
file_csv = "./dataset/month_3depth_result/keyword.csv"  # 2번 데이터 파일 (CSV)

# 1번 데이터 로드 (엑셀)
df_keywords = pd.read_excel(file_xlsx)

# 2번 데이터 로드 (CSV)
df_search = pd.read_csv(file_csv)

# 데이터 확인
print("📌 1번 데이터 샘플")
print(df_keywords.head())

print("\n📌 2번 데이터 샘플")
print(df_search.head())

# 2번 데이터 (CSV) 형태 변경: 'long-form'으로 변환
df_search_melted = df_search.melt(id_vars=["date"], var_name="인기검색어", value_name="검색량")

# 병합 (인기검색어 기준)
df_merged = pd.merge(df_search_melted, df_keywords, on="인기검색어", how="left")

# 날짜 기준 정렬
df_merged = df_merged.sort_values(by=["date", "인기검색어"])

# 결과 저장
output_file = "./dataset/final/final.csv"
df_merged.to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"✅ 병합 완료! 파일 저장: {output_file}")
