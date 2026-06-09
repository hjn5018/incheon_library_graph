import pandas as pd
import json

import os

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
csv_path = os.path.join(project_root, "data", "incheon_library.csv")
js_path = os.path.join(project_root, "data", "dashboard_data.js")

df = pd.read_csv(csv_path)

df = df.dropna(subset=['도서관명'])

df['열람좌석수'] = pd.to_numeric(df['열람좌석수'], errors='coerce').fillna(0).astype(int)
df['자료수(도서)'] = pd.to_numeric(df['자료수(도서)'], errors='coerce').fillna(0).astype(int)
df['위도'] = pd.to_numeric(df['위도'], errors='coerce').fillna(0.0)
df['경도'] = pd.to_numeric(df['경도'], errors='coerce').fillna(0.0)
df['자료수(연속간행물)'] = pd.to_numeric(df['자료수(연속간행물)'], errors='coerce').fillna(0).astype(int)
df['자료수(비도서)'] = pd.to_numeric(df['자료수(비도서)'], errors='coerce').fillna(0).astype(int)

for col in df.columns:
    if df[col].dtype == object:
        df[col] = df[col].fillna("")
        
total_libraries = len(df)
total_books = int(df['자료수(도서)'].sum())
total_seats = int(df['열람좌석수'].sum())

top_library_row = df.loc[df['자료수(도서)'].idxmax()]
top_library_name = str(top_library_row['도서관명'])
top_library_books = int(top_library_row['자료수(도서)'])

regions = sorted(list(df['시군구명'].unique()))
regions = [r for r in regions if r != ""]

types = sorted(list(df['도서관유형'].unique()))
types = [t for t in types if t != ""]

records = df.to_dict(orient='records')

stats = {
    "totalLibraries": total_libraries,
    "totalBooks": total_books,
    "totalSeats": total_seats,
    "topLibraryName": top_library_name,
    "topLibraryBooks": top_library_books,
    "regions": regions,
    "types": types
}

with open(js_path, "w", encoding="utf-8") as f:
    f.write("// Automatically generated from incheon_library.csv. Do not edit manually.\n")
    f.write(f"const LIBRARY_STATS = {json.dumps(stats, ensure_ascii=False, indent=2)};\n\n")
    f.write(f"const LIBRARY_DATA = {json.dumps(records, ensure_ascii=False, indent=2)};\n")
    
print("Successfully generated dashboard_data.js")
