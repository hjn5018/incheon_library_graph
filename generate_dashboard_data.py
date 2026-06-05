import pandas as pd
import json

def generate_data():
    # Read CSV
    df = pd.read_csv("incheon_library.csv")
    
    # Clean data (matching the logic in visualize_libraries.py)
    df = df.dropna(subset=['도서관명'])
    
    # Process numeric fields
    df['열람좌석수'] = pd.to_numeric(df['열람좌석수'], errors='coerce').fillna(0).astype(int)
    df['자료수(도서)'] = pd.to_numeric(df['자료수(도서)'], errors='coerce').fillna(0).astype(int)
    df['위도'] = pd.to_numeric(df['위도'], errors='coerce').fillna(0.0)
    df['경도'] = pd.to_numeric(df['경도'], errors='coerce').fillna(0.0)
    df['자료수(연속간행물)'] = pd.to_numeric(df['자료수(연속간행물)'], errors='coerce').fillna(0).astype(int)
    df['자료수(비도서)'] = pd.to_numeric(df['자료수(비도서)'], errors='coerce').fillna(0).astype(int)
    
    # Convert empty strings/NaNs in other columns to empty string
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("")
            
    # Calculate stats
    total_libraries = len(df)
    total_books = int(df['자료수(도서)'].sum())
    total_seats = int(df['열람좌석수'].sum())
    
    top_library_row = df.loc[df['자료수(도서)'].idxmax()]
    top_library_name = str(top_library_row['도서관명'])
    top_library_books = int(top_library_row['자료수(도서)'])
    
    # Get filter lists
    regions = sorted(list(df['시군구명'].unique()))
    regions = [r for r in regions if r != ""]
    
    types = sorted(list(df['도서관유형'].unique()))
    types = [t for t in types if t != ""]
    
    # Transform rows to records
    records = df.to_dict(orient='records')
    
    # Stats structure
    stats = {
        "totalLibraries": total_libraries,
        "totalBooks": total_books,
        "totalSeats": total_seats,
        "topLibraryName": top_library_name,
        "topLibraryBooks": top_library_books,
        "regions": regions,
        "types": types
    }
    
    # Write to dashboard_data.js
    with open("dashboard_data.js", "w", encoding="utf-8") as f:
        f.write("// Automatically generated from incheon_library.csv. Do not edit manually.\n")
        f.write(f"const LIBRARY_STATS = {json.dumps(stats, ensure_ascii=False, indent=2)};\n\n")
        f.write(f"const LIBRARY_DATA = {json.dumps(records, ensure_ascii=False, indent=2)};\n")
        
    print("Successfully generated dashboard_data.js")

if __name__ == "__main__":
    generate_data()
