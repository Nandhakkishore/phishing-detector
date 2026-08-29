import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)

# --- Load hybrid feature sets ---
train_df = pd.read_csv("dataset/processed/train_hybrid_features.csv")
val_df = pd.read_csv("dataset/processed/val_hybrid_features.csv")

X_train = train_df.drop(columns=["label"])
y_train = train_df["label"]
X_val = val_df.drop(columns=["label"])
y_val = val_df["label"]

print(f"Train: {X_train.shape}, Val: {X_val.shape}")

# --- Define models (same config as URL-only run, for a fair comparison) ---
models = {
    "logistic_regression": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "random_forest": RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1),
    "xgboost": XGBClassifier(eval_metric="logloss", random_state=42, n_jobs=-1),
}

results = []

for name, model in models.items():
    print(f"\nTraining {name} (hybrid)...")
    model.fit(X_train, y_train)

    preds = model.predict(X_val)

    acc = accuracy_score(y_val, preds)
    prec = precision_score(y_val, preds)
    rec = recall_score(y_val, preds)
    f1 = f1_score(y_val, preds)
    cm = confusion_matrix(y_val, preds)

    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-score:  {f1:.4f}")
    print(f"  Confusion matrix:\n{cm}")

    results.append({
        "model": name,
        "feature_type": "hybrid",
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
    })

    joblib.dump(model, f"ml/saved_models/{name}_hybrid.pkl")

results_df = pd.DataFrame(results)
results_df.to_csv("ml/hybrid_results.csv", index=False)

# --- Combine with URL-only results for the final comparison table ---
url_only_df = pd.read_csv("ml/url_only_results.csv")
comparison_df = pd.concat([url_only_df, results_df], ignore_index=True)
comparison_df.to_csv("ml/model_comparison.csv", index=False)

print("\n=== Hybrid Results ===")
print(results_df)
print("\n=== Full Comparison (URL-only vs Hybrid) ===")
print(comparison_df)
print("\nSaved to ml/hybrid_results.csv and ml/model_comparison.csv")