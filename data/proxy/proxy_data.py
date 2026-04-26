import pandas as pd
import numpy as np
import os

delhi = pd.read_csv('data/raw/Delhi_AQI_Dataset.csv')
mumbai = pd.read_csv('data/raw/Mumbai_AQI_Dataset.csv')
marine = pd.read_csv('data/raw/Marine_Microplastics.csv')
soil = pd.read_csv('data/raw/soil_pollution_diseases.csv')

#PROXY 1: AQI Cities (Delhi & Mumbai)
aqi = pd.concat([delhi, mumbai], ignore_index=True)
aqi_proxy = aqi.groupby('City').agg(
    avg_pm25=('PM2.5', 'mean'),
    avg_pm10=('PM10', 'mean'),
    avg_aqi=('AQI', 'mean')
).reset_index()

#Urbanization index: normalize AQI (higher AQI = more urban/industrial)
aqi_proxy['urbanization_index'] = (aqi_proxy['avg_aqi'] - aqi_proxy['avg_aqi'].min()) / \
                                   (aqi_proxy['avg_aqi'].max() - aqi_proxy['avg_aqi'].min())

#Industry density proxy: based on SO2 + NO2 levels (industrial gases)
aqi['industry_proxy'] = aqi['NO2'] + aqi['SO2']
industry = aqi.groupby('City')['industry_proxy'].mean().reset_index()
industry.columns = ['City', 'industry_density']
industry['industry_density'] = (industry['industry_density'] - industry['industry_density'].min()) / \
                                (industry['industry_density'].max() - industry['industry_density'].min())

aqi_proxy = aqi_proxy.merge(industry, on='City')
aqi_proxy['latitude'] = aqi_proxy['City'].map({'Delhi': 28.6139, 'Mumbai': 19.0760})
aqi_proxy['longitude'] = aqi_proxy['City'].map({'Delhi': 77.2090, 'Mumbai': 72.8777})
aqi_proxy['source'] = 'AQI'
aqi_proxy['location'] = aqi_proxy['City']

#PROXY 2: Marine Microplastics
marine_clean = marine[['Regions', 'Latitude', 'Longitude', 'Measurement']].dropna()
marine_clean.columns = ['location', 'latitude', 'longitude', 'avg_pm25']
marine_clean['urbanization_index'] = 0.2  # oceans = low urbanization
marine_clean['industry_density'] = 0.1
marine_clean['source'] = 'Marine'

#PROXY 3: Soil Pollution
soil_proxy = soil.groupby('Region').agg(
    avg_pm25=('Pollutant_Concentration_mg_kg', 'mean'),
).reset_index()
soil_proxy['location'] = soil_proxy['Region']
soil_proxy['latitude'] = np.nan
soil_proxy['longitude'] = np.nan

#Industry density from Nearby_Industry column
industry_map = soil.groupby('Region')['Nearby_Industry'].apply(
    lambda x: x.value_counts().index[0] if len(x) > 0 else 'None'
).reset_index()
industry_map.columns = ['Region', 'nearby_industry']
soil_proxy = soil_proxy.merge(industry_map, on='Region')
soil_proxy['industry_density'] = soil_proxy['nearby_industry'].apply(
    lambda x: 0.9 if 'Factory' in str(x) or 'Industrial' in str(x)
    else 0.5 if 'Farm' in str(x) else 0.2
)
soil_proxy['urbanization_index'] = soil_proxy['industry_density'] * 0.8
soil_proxy['source'] = 'Soil'

#combining proxies
cols = ['location', 'latitude', 'longitude', 'urbanization_index', 'industry_density', 'avg_pm25', 'source']

aqi_final = aqi_proxy[cols]
marine_final = marine_clean[cols]
soil_final = soil_proxy[cols]

proxy_df = pd.concat([aqi_final, marine_final, soil_final], ignore_index=True)

#Composite Risk Score (0-1 scale)
proxy_df['risk_score'] = (
    0.4 * proxy_df['urbanization_index'].fillna(0.5) +
    0.4 * proxy_df['industry_density'].fillna(0.5) +
    0.2 * (proxy_df['avg_pm25'].fillna(proxy_df['avg_pm25'].mean()) /
           proxy_df['avg_pm25'].max())
).round(4)

os.makedirs('data/proxy', exist_ok=True)
proxy_df.to_csv('data/proxy/proxy_data.csv', index=False)
print("✅ proxy_data.csv saved successfully!")
print(proxy_df.head(10))
print(f"\nShape: {proxy_df.shape}")