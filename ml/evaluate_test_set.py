import pandas as pd
import joblib
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix
)

test_df = pd.read_csv("dataset/processed/test_hybrid_features.csv")
X_test = test_df.drop(columns=["label"])
y_test = test_df["label"]

models_to_test = {
    "logistic_regression": "ml/saved_models/logistic_regression_hybrid.pkl",
    "random_forest": "ml/saved_models/random_forest_hybrid.pkl",
    "xgboost": "ml/saved_models/xgboost_hybrid.pkl",
}

results = []

for name, path in models_to_test.items():
    model = joblib.load(path)
    preds = model.predict(X_test)

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds)
    rec = recall_score(y_test, preds)
    f1 = f1_score(y_test, preds)
    cm = confusion_matrix(y_test, preds)

    print(f"\n{name} (final test set)")
    print(f"  Accuracy:  {acc:.4f}")
    print(f"  Precision: {prec:.4f}")
    print(f"  Recall:    {rec:.4f}")
    print(f"  F1-score:  {f1:.4f}")
    print(f"  Confusion matrix:\n{cm}")

    results.append({
        "model": name, "feature_type": "hybrid_TEST_SET",
        "accuracy": acc, "precision": prec, "recall": rec, "f1_score": f1,
    })

results_df = pd.DataFrame(results)
results_df.to_csv("ml/final_test_set_results.csv", index=False)
print("\n=== Final Test-Set Summary ===")
print(results_df)
print("\nSaved to ml/final_test_set_results.csv")
