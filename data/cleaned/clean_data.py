import pandas as pd
import numpy as np


def clean_column_names(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def handle_nulls(df):
    # Fill numeric columns with mean
    for col in df.select_dtypes(include=np.number).columns:
        df[col].fillna(df[col].mean(), inplace=True)

    # Fill categorical columns with mode
    for col in df.select_dtypes(include='object').columns:
        df[col].fillna(df[col].mode()[0], inplace=True)

    return df


def remove_duplicates(df):
    return df.drop_duplicates()


def standardize_units(df):
    for col in df.columns:
        if "µg" in col:
            df[col] = df[col] / 1000  # µg to mg
            df.rename(columns={col: col.replace("µg", "mg")}, inplace=True)

    return df


delhi = pd.read_excel("data/raw/Delhi_AQI_Dataset.xlsx")
mumbai = pd.read_excel("data/raw/Mumbai_AQI_Dataset.xlsx")
marine = pd.read_csv("data/raw/Marine_Microplastics.csv")
soil = pd.read_csv("data/raw/soil_pollution_diseases.csv")



datasets = [delhi, mumbai, marine, soil]
cleaned_datasets = []

for df in datasets:
    df = clean_column_names(df)
    df = handle_nulls(df)
    df = remove_duplicates(df)
    df = standardize_units(df)
    cleaned_datasets.append(df)



cleaned_datasets[0]['source'] = 'Delhi AQI'
cleaned_datasets[1]['source'] = 'Mumbai AQI'
cleaned_datasets[2]['source'] = 'Marine Microplastics'
cleaned_datasets[3]['source'] = 'Soil Pollution'


master_df = pd.concat(cleaned_datasets, ignore_index=True, sort=False)


master_df.to_csv("data/cleaned/master_dataset.csv", index=False)

print("Data cleaning complete. Master dataset saved.")
