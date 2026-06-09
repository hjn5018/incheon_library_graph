# %%
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import folium
from folium.plugins import MarkerCluster
import os

matplotlib.rc('font', family='Malgun Gothic')

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

csv_path = os.path.join(project_root, "data", "incheon_library.csv")
pie_path = os.path.join(project_root, "charts", "libraries_by_region_pie.png")
bar_path = os.path.join(project_root, "charts", "top_books_barh.png")
scatter_path = os.path.join(project_root, "charts", "books_vs_seats_plot.png")
map_path = os.path.join(project_root, "maps", "library_map.html")

df = pd.read_csv(csv_path)

df = df.dropna(subset=['도서관명'])
df = df.iloc[:, :-1]

df['열람좌석수'] = pd.to_numeric(df['열람좌석수'], errors='coerce').fillna(0).astype(int)
df['자료수(도서)'] = pd.to_numeric(df['자료수(도서)'], errors='coerce').fillna(0).astype(int)
df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
df['경도'] = pd.to_numeric(df['경도'], errors='coerce')






# %%
plt.figure(figsize=(10, 8))
region_counts = df['시군구명'].value_counts()

colors = plt.cm.Pastel1(range(len(region_counts)))

plt.pie(region_counts, labels=region_counts.index, autopct='%1.1f%%', 
        startangle=140, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
plt.title('인천광역시 구/군별 도서관 분포 비율', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(pie_path, dpi=300)
plt.close()






# %%
plt.figure(figsize=(12, 8))
top10_books = df.nlargest(10, '자료수(도서)').sort_values(by='자료수(도서)', ascending=True)

bars = plt.barh(top10_books['도서관명'], top10_books['자료수(도서)'])

for bar in bars:
    width = bar.get_width()
    plt.text(width + 5000, bar.get_y() + bar.get_height()/2, f"{width:,}권", 
             va='center', ha='left', fontsize=10, fontweight='bold')

plt.title('인천광역시 도서 보유량 상위 10개 도서관', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('자료수(도서)', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.xlim(0, max(top10_books['자료수(도서)']) * 1.15)
plt.tight_layout()
plt.savefig(bar_path, dpi=300)
plt.close()






# %%
plt.figure(figsize=(10, 7))

plt.scatter(df['열람좌석수'], df['자료수(도서)'], alpha=0.7, edgecolors='none', s=80, c='#e74c3c')

for idx, row in df.iterrows():
    if row['자료수(도서)'] >= 200000 or row['열람좌석수'] >= 500:
        plt.text(row['열람좌석수'] + 15, row['자료수(도서)'], row['도서관명'], 
                 fontsize=9, alpha=0.8, va='center')

plt.title('도서관 열람좌석수 대비 도서 보유량 관계', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('열람좌석수', fontsize=12)
plt.ylabel('자료수(도서)', fontsize=12)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig(scatter_path, dpi=300)
plt.close()







# %%
map_df = df.dropna(subset=['위도', '경도'])

incheon_center = [37.456, 126.705]
m = folium.Map(location=incheon_center, zoom_start=11)

marker_cluster = MarkerCluster().add_to(m)

for idx, row in map_df.iterrows():
    popup_text = f"""
    <div style='font-family: Arial, sans-serif; width: 250px;'>
        <h4 style='margin: 0 0 5px 0; color: #2c3e50;'><b>{row['도서관명']}</b></h4>
        <p style='margin: 3px 0; font-size: 12px;'><b>유형:</b> {row['도서관유형']}</p>
        <p style='margin: 3px 0; font-size: 12px;'><b>주소:</b> {row['소재지도로명주소']}</p>
        <p style='margin: 3px 0; font-size: 12px;'><b>전화번호:</b> {row['도서관전화번호']}</p>
        <hr style='margin: 8px 0; border: 0; border-top: 1px solid #eee;'>
        <p style='margin: 3px 0; font-size: 12px; color: #e74c3c;'><b>열람좌석수:</b> {row['열람좌석수']:,}석</p>
        <p style='margin: 3px 0; font-size: 12px; color: #3498db;'><b>도서보유량:</b> {row['자료수(도서)']:,}권</p>
    </div>
    """
    
    popup = folium.Popup(popup_text, max_width=300)
    
    folium.Marker(
        location=[row['위도'], row['경도']],
        popup=popup,
        tooltip=row['도서관명'],
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(marker_cluster)

m.save(map_path)
print("All visualization tasks completed successfully!")
