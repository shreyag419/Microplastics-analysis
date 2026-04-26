import pandas as pd
import folium
from folium.plugins import HeatMap
import os

# Load proxy data
df = pd.read_csv('data/proxy/proxy_data.csv')

# Drop rows without coordinates
df = df.dropna(subset=['latitude', 'longitude'])

print(f"Working with {len(df)} locations")

# --- MAP 1: Risk Score Heatmap ---
m1 = folium.Map(location=[20, 0], zoom_start=2)

heat_data = [[row['latitude'], row['longitude'], row['risk_score']] 
             for _, row in df.iterrows()]
HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m1)

# Add markers for Delhi and Mumbai
for _, row in df[df['source'] == 'AQI'].iterrows():
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=f"{row['location']}<br>Risk Score: {row['risk_score']}<br>Urbanization: {row['urbanization_index']:.2f}",
        icon=folium.Icon(color='red' if row['risk_score'] > 0.5 else 'orange')
    ).add_to(m1)

os.makedirs('outputs', exist_ok=True)
m1.save('outputs/risk_heatmap.html')
print("✅ Map 1 saved — Risk Heatmap!")

# --- MAP 2: Industry Density Map ---
m2 = folium.Map(location=[20, 0], zoom_start=2)

for _, row in df.iterrows():
    color = 'red' if row['industry_density'] > 0.7 else \
            'orange' if row['industry_density'] > 0.4 else 'green'
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color,
        fill=True,
        popup=f"{row['location']}<br>Industry Density: {row['industry_density']:.2f}"
    ).add_to(m2)

m2.save('outputs/industry_density_map.html')
print("✅ Map 2 saved — Industry Density Map!")

# --- MAP 3: Urbanization Index Map ---
m3 = folium.Map(location=[20, 0], zoom_start=2)

for _, row in df.iterrows():
    color = 'red' if row['urbanization_index'] > 0.7 else \
            'orange' if row['urbanization_index'] > 0.4 else 'green'
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=5,
        color=color,
        fill=True,
        popup=f"{row['location']}<br>Urbanization: {row['urbanization_index']:.2f}"
    ).add_to(m3)

m3.save('outputs/urbanization_map.html')
print("✅ Map 3 saved — Urbanization Map!")

print("\n All 3 GIS maps saved to outputs/ folder!")
print("Open the .html files in your browser to view them!")