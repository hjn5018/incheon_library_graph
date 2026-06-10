import pandas as pd
import json
import os

# 현재 실행 중인 파이썬 스크립트의 디렉터리 경로를 구합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))

# 스크립트 위치 기준 상위 폴더(incheon_library_graph)를 프로젝트 루트로 지정합니다.
project_root = os.path.dirname(current_dir)

# 입력받을 CSV 파일 경로와 생성할 JS 파일 경로를 설정합니다.
csv_path = os.path.join(project_root, "data", "incheon_library.csv")
js_path = os.path.join(project_root, "data", "dashboard_data.js")

# CSV 데이터를 Pandas DataFrame으로 불러옵니다.
df = pd.read_csv(csv_path)

# 도서관명이 누락된(결측치) 행은 대시보드 표시에서 제외하기 위해 정제합니다.
df = df.dropna(subset=['도서관명'])

# 열람좌석수, 자료수 등 수치 데이터 중 결측치가 있는 값을 0으로 채우고 정수형(int)으로 변환합니다.
df['열람좌석수'] = pd.to_numeric(df['열람좌석수'], errors='coerce').fillna(0).astype(int)
df['자료수(도서)'] = pd.to_numeric(df['자료수(도서)'], errors='coerce').fillna(0).astype(int)
df['위도'] = pd.to_numeric(df['위도'], errors='coerce').fillna(0.0)
df['경도'] = pd.to_numeric(df['경도'], errors='coerce').fillna(0.0)
df['자료수(연속간행물)'] = pd.to_numeric(df['자료수(연속간행물)'], errors='coerce').fillna(0).astype(int)
df['자료수(비도서)'] = pd.to_numeric(df['자료수(비도서)'], errors='coerce').fillna(0).astype(int)

# 문자열(object) 타입의 컬럼 중 결측치(NaN)가 있으면 빈 문자열("")로 대체합니다.
for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].fillna("")
        
# 주요 대시보드 통계 수치(KPI)들을 계산합니다.
total_libraries = len(df)                          # 전체 도서관 개수
total_books = int(df['자료수(도서)'].sum())        # 총 도서 보유량 합계
total_seats = int(df['열람좌석수'].sum())          # 총 열람 좌석수 합계

# 도서 보유량이 가장 많은 도서관을 찾아냅니다.
top_library_row = df.loc[df['자료수(도서)'].idxmax()]
top_library_name = str(top_library_row['도서관명'])
top_library_books = int(top_library_row['자료수(도서)'])

# 필터링 드롭다운에 쓰일 시군구명 및 도서관유형 고유값을 정렬하여 추출합니다.
regions = sorted(list(df['시군구명'].unique()))
regions = [r for r in regions if r != ""]

types = sorted(list(df['도서관유형'].unique()))
types = [t for t in types if t != ""]

# 전체 도서관 데이터를 자바스크립트 객체 배열 형태로 변환하기 위해 딕셔너리 리스트로 변환합니다.
records = df.to_dict(orient='records')

# 대시보드 상단 요약용 통계 객체를 정의합니다.
stats = {
    "totalLibraries": total_libraries,
    "totalBooks": total_books,
    "totalSeats": total_seats,
    "topLibraryName": top_library_name,
    "topLibraryBooks": top_library_books,
    "regions": regions,
    "types": types
}

# 대시보드 HTML에서 전역 변수로 바로 사용할 수 있도록 JS 파일 형식으로 내보냅니다.
with open(js_path, "w", encoding="utf-8") as f:
    f.write("// Automatically generated from incheon_library.csv. Do not edit manually.\n")
    f.write(f"const LIBRARY_STATS = {json.dumps(stats, ensure_ascii=False, indent=2)};\n\n")
    f.write(f"const LIBRARY_DATA = {json.dumps(records, ensure_ascii=False, indent=2)};\n")
    
print("Successfully generated dashboard_data.js")
