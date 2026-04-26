import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

df = pd.read_excel("data/cleaned/master_dataset.xslx.xlsx")

print("Shape of dataset:", df.shape)
print("\nColumns:\n", df.columns)

# -----------------------------
# 1. Correlation Matrix
# -----------------------------
corr_matrix = df.corr(numeric_only=True)

print("\nCorrelation Matrix:\n", corr_matrix)

# -----------------------------
# 2. Heatmap
# -----------------------------
plt.figure(figsize=(12, 8))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5)
plt.title("Correlation Heatmap (Master Dataset)")
plt.xticks(rotation=45)
plt.yticks(rotation=45)
plt.tight_layout()
plt.show()

# -----------------------------
# 3. Scatter Plot Matrix (Pairplot)
# -----------------------------
numeric_df = df.select_dtypes(include=['number'])

sample_df = numeric_df.sample(n=500, random_state=42) if len(numeric_df) > 500 else numeric_df

sns.pairplot(sample_df)
plt.suptitle("Scatter Plot Matrix (Sampled Data)", y=1.02)
plt.show()

# -----------------------------
# 4. Focused Scatter Plots
# -----------------------------
important_cols = numeric_df.columns[:4] 

for i in range(len(important_cols)):
    for j in range(i+1, len(important_cols)):
        plt.figure(figsize=(6, 4))
        sns.scatterplot(data=df, x=important_cols[i], y=important_cols[j])
        plt.title(f"{important_cols[i]} vs {important_cols[j]}")
        plt.tight_layout()
        plt.show()

# -----------------------------
# 5.Correlation with Target 
# -----------------------------
target_col = 'AQI'  
if target_col in df.columns:
    corr_target = corr_matrix[target_col].sort_values(ascending=False)
    print(f"\nCorrelation with {target_col}:\n", corr_target)
