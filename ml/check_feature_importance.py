import pandas as pd
import joblib

model = joblib.load("ml/saved_models/random_forest_hybrid.pkl")
train_df = pd.read_csv("dataset/processed/train_hybrid_features.csv")
feature_names = train_df.drop(columns=["label"]).columns

importances = pd.Series(model.feature_importances_, index=feature_names)
importances = importances.sort_values(ascending=False)

print("Top 15 most important features:")
print(importances.head(15))