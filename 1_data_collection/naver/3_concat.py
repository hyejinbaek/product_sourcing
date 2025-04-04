# 데이터랩 인기검색어 파일과 추가 클릭수 파일 합치기

import pandas as pd

# 파일 경로 (업로드한 파일로 변경해야 함)
file_xlsx = "./dataset/month_3depth/2017-2025_튜닝용품_인기검색어.xlsx"  # 1번 데이터 파일 (엑셀)
file_csv = "./dataset/month_3depth_result/2017-2025_튜닝용품_인기검색어_검색량.csv"  # 2번 데이터 파일 (CSV)

# 1번 데이터 로드 (엑셀)
df1 = pd.read_excel(file_xlsx)

# 2번 데이터 로드 (CSV)
df2 = pd.read_csv(file_csv)


df1["연-월"] = df1["연도"].astype(str) + "-" + df1["월"].str[-2:]
df2["연-월"] = pd.to_datetime(df2["date"]).dt.strftime("%Y-%m")

# 키워드 기준으로 검색량 매칭
merged_df = df1.merge(df2.melt(id_vars=["연-월"], var_name="인기검색어", value_name="검색량"),
                    on=["연-월", "인기검색어"], how="left")

print(merged_df)

merged_df.to_csv("./dataset/final/2017-2025_튜닝용품_final.csv", index=False, encoding="utf-8-sig")