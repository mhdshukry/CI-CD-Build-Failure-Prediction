import pandas as pd
import os
import joblib
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)

from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE


df = pd.read_csv("data/processed/final_ml_dataset.csv")

features = [
    "files_changed",
    "lines_added",
    "lines_deleted",
    "total_changes",
    "dependency_file_changed",
    "test_file_changed",
    "workflow_changed",
    "source_file_changed",
    "risk_file_count"
]

X = df[features]
y = df["build_result"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

smote = SMOTE(random_state=42)
X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

models = {
    "Random Forest + SMOTE": RandomForestClassifier(
        n_estimators=300,
        max_depth=10,
        random_state=42,
        class_weight="balanced"
    ),

    "XGBoost Balanced": XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.05,
        scale_pos_weight=(y_train.value_counts()[0] / y_train.value_counts()[1]),
        eval_metric="logloss",
        random_state=42
    )
}

results = []

best_model = None
best_f1 = 0

os.makedirs("reports/figures", exist_ok=True)
os.makedirs("models/saved", exist_ok=True)

for name, model in models.items():
    print("\nTraining:", name)

    if "SMOTE" in name:
        model.fit(X_train_smote, y_train_smote)
    else:
        model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    pre = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)

    results.append({
        "Model": name,
        "Accuracy": acc,
        "Precision": pre,
        "Recall": rec,
        "F1": f1,
        "ROC_AUC": roc,
        "PR_AUC": pr_auc
    })

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    if f1 > best_f1:
        best_f1 = f1
        best_model = model

result_df = pd.DataFrame(results)
print("\n========== IMPROVED RESULTS ==========")
print(result_df)

result_df.to_csv("reports/model_results.csv", index=False)

joblib.dump(best_model, "models/saved/best_build_failure_model.pkl")

print("\nBest model saved:")
print("models/saved/best_build_failure_model.pkl")

# Feature importance graph
importances = best_model.feature_importances_

importance_df = pd.DataFrame({
    "Feature": features,
    "Importance": importances
}).sort_values(by="Importance", ascending=False)

plt.figure(figsize=(10, 6))
plt.barh(importance_df["Feature"], importance_df["Importance"])
plt.xlabel("Importance")
plt.ylabel("Feature")
plt.title("Feature Importance for CI/CD Build Failure Prediction")
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig("reports/figures/feature_importance.png")
plt.close()

print("\nFeature importance saved:")
print("reports/figures/feature_importance.png")