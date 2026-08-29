import pandas as pd
from sklearn.model_selection import train_test_split

# --- Load raw data ---
df = pd.read_csv("dataset/raw/PhiUSIIL_Phishing_URL_Dataset.csv")
print(f"Raw shape: {df.shape}")

# --- Fix label convention: make 1 = phishing, 0 = legitimate ---
# Original: 1 = legitimate, 0 = phishing (confirmed via value_counts)
df["label"] = df["label"].map({1: 0, 0: 1})
print("\nAfter relabeling (1=phishing, 0=legitimate):")
print(df["label"].value_counts())

# --- Drop duplicate URLs ---
before = len(df)
df = df.drop_duplicates(subset="URL")
print(f"\nDropped {before - len(df)} duplicate URLs")

# --- Check for label conflicts on the same URL (should be 0 now that dupes are gone) ---
conflict_check = df.groupby("URL")["label"].nunique()
conflicts = conflict_check[conflict_check > 1]
print(f"URLs with conflicting labels: {len(conflicts)}")

# --- Drop rows with missing URL or label (defensive, even though nulls were 0) ---
df = df.dropna(subset=["URL", "label"])

# --- Stratified 70/15/15 split ---
train, temp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=42)
val, test = train_test_split(temp, test_size=0.50, stratify=temp["label"], random_state=42)

print(f"\nTrain: {train.shape}, Val: {val.shape}, Test: {test.shape}")
print("\nTrain label balance:")
print(train["label"].value_counts(normalize=True))

# --- Save splits ---
train.to_csv("dataset/splits/train.csv", index=False)
val.to_csv("dataset/splits/val.csv", index=False)
test.to_csv("dataset/splits/test.csv", index=False)

print("\nDone. Splits saved to dataset/splits/")