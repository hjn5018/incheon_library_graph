import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import folium
from folium.plugins import MarkerCluster
import os

# 한글 깨짐 방지를 위해 시스템 기본 폰트(맑은 고딕)를 설정합니다.
matplotlib.rc('font', family='Malgun Gothic')

# 스크립트 실행 경로를 기반으로 프로젝트 루트 디렉터리를 구합니다.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

# 입출력 파일 경로를 설정합니다.
csv_path = os.path.join(project_root, "data", "incheon_library.csv")
pie_path = os.path.join(project_root, "charts", "libraries_by_region_pie.png")
bar_path = os.path.join(project_root, "charts", "top_books_barh.png")
scatter_path = os.path.join(project_root, "charts", "books_vs_seats_plot.png")
map_path = os.path.join(project_root, "maps", "library_map.html")

# CSV 파일 로드 및 기본 데이터 정제
df = pd.read_csv(csv_path)

# 도서관명이 결측치(NaN)인 행을 제거합니다.
df = df.dropna(subset=['도서관명'])
# 마지막 불필요한 열을 제거합니다.
df = df.iloc[:, :-1]

# 수치형 컬럼들의 문자열 타입 값을 숫자로 변환하고, 결측치는 0으로 대체합니다.
df['열람좌석수'] = pd.to_numeric(df['열람좌석수'], errors='coerce').fillna(0).astype(int)
df['자료수(도서)'] = pd.to_numeric(df['자료수(도서)'], errors='coerce').fillna(0).astype(int)
df['위도'] = pd.to_numeric(df['위도'], errors='coerce')
df['경도'] = pd.to_numeric(df['경도'], errors='coerce')


# %% 1. 구/군별 도서관 분포 비율 (Pie 차트 생성)
plt.figure(figsize=(10, 8))
# 각 시군구별 도서관의 빈도를 계산합니다.
region_counts = df['시군구명'].value_counts()

# 파스텔톤 컬러맵을 지정하여 가독성을 높입니다.
colors = plt.cm.Pastel1(range(len(region_counts)))

# 원형 차트(Pie Chart)를 그립니다.
plt.pie(region_counts, labels=region_counts.index, autopct='%1.1f%%', 
        startangle=140, colors=colors, wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
plt.title('인천광역시 구/군별 도서관 분포 비율', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
# 차트를 이미지 파일로 저장합니다.
plt.savefig(pie_path, dpi=300)
plt.close()


# %% 2. 도서 보유량 상위 10개 도서관 (수평 Bar 차트 생성)
plt.figure(figsize=(12, 8))
# 도서 보유량 상위 10개 도서관 데이터를 가져와 오름차순 정렬합니다.
top10_books = df.nlargest(10, '자료수(도서)').sort_values(by='자료수(도서)', ascending=True)

# 수평 막대 차트(Barh)를 그립니다.
bars = plt.barh(top10_books['도서관명'], top10_books['자료수(도서)'])

# 막대 끝부분에 책 권수 텍스트 라벨을 추가합니다.
for bar in bars:
    width = bar.get_width()
    plt.text(width + 5000, bar.get_y() + bar.get_height()/2, f"{width:,}권", 
             va='center', ha='left', fontsize=10, fontweight='bold')

plt.title('인천광역시 도서 보유량 상위 10개 도서관', fontsize=16, fontweight='bold', pad=20)
plt.xlabel('자료수(도서)', fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)
# 라벨 텍스트가 잘리지 않도록 X축의 최댓값 범위를 소폭 늘립니다.
plt.xlim(0, max(top10_books['자료수(도서)']) * 1.15)
plt.tight_layout()
plt.savefig(bar_path, dpi=300)
plt.close()


# %% 3. 열람좌석수 대비 도서 보유량 관계 (산점도 Scatter 차트 생성)
plt.figure(figsize=(10, 7))

# 좌석수(X축)와 도서량(Y축)의 상관관계를 산점도로 시각화합니다.
plt.scatter(df['열람좌석수'], df['자료수(도서)'], alpha=0.7, edgecolors='none', s=80, c='#e74c3c')

# 특정 기준(도서수 20만 권 이상 혹은 좌석수 500석 이상)을 넘는 대형 도서관에 이름을 라벨링합니다.
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


# %% 4. 지도 시각화 (Folium Map 생성)
# 위도와 경도 정보가 정상적으로 존재하는 데이터만 필터링합니다.
map_df = df.dropna(subset=['위도', '경도'])

# 인천 중심 좌표를 기준으로 지도를 초기화합니다.
incheon_center = [37.456, 126.705]
m = folium.Map(location=incheon_center, zoom_start=11)

# 여러 마커들이 겹칠 때 그룹화해주는 클러스터 레이어를 추가합니다.
marker_cluster = MarkerCluster().add_to(m)

# 각 도서관의 마커 정보 및 정보 팝업창(HTML 구조)을 생성합니다.
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

# 동적으로 생성된 지도를 HTML 파일로 보존합니다.
m.save(map_path)
print("All visualization tasks completed successfully!")
