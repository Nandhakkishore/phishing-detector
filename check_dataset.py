import pandas as pd

df = pd.read_csv("dataset/raw/PhiUSIIL_Phishing_URL_Dataset.csv")

print("Label counts:")
print(df['label'].value_counts())

print("\nUnique labels:", df['label'].unique())

print("\nTotal nulls:", df.isnull().sum().sum())

print("\nDuplicate URLs:", df.duplicated(subset='URL').sum())