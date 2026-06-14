import pandas as pd
import matplotlib.pyplot as plt
import os

os.makedirs("reports/figures", exist_ok=True)

# Load files
dataset = pd.read_csv("data/processed/final_ml_dataset.csv")
results = pd.read_csv("reports/model_results.csv")

# 1. Dataset distribution
counts = dataset["build_result"].value_counts()
labels = ["Success", "Failure"]

plt.figure(figsize=(7, 5))
plt.bar(labels, [counts.get(0, 0), counts.get(1, 0)])
plt.title("Build Result Distribution")
plt.xlabel("Build Result")
plt.ylabel("Number of Builds")
plt.tight_layout()
plt.savefig("reports/figures/build_distribution.png")
plt.close()

# 2. Model F1 comparison
plt.figure(figsize=(8, 5))
plt.bar(results["Model"], results["F1"])
plt.title("Model Comparison Based on F1 Score")
plt.xlabel("Model")
plt.ylabel("F1 Score")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("reports/figures/model_f1_comparison.png")
plt.close()

# 3. Model Recall comparison
plt.figure(figsize=(8, 5))
plt.bar(results["Model"], results["Recall"])
plt.title("Model Comparison Based on Recall")
plt.xlabel("Model")
plt.ylabel("Recall")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("reports/figures/model_recall_comparison.png")
plt.close()

# 4. Model ROC-AUC comparison
plt.figure(figsize=(8, 5))
plt.bar(results["Model"], results["ROC_AUC"])
plt.title("Model Comparison Based on ROC-AUC")
plt.xlabel("Model")
plt.ylabel("ROC-AUC")
plt.xticks(rotation=15)
plt.tight_layout()
plt.savefig("reports/figures/model_roc_auc_comparison.png")
plt.close()

print("Graphs generated successfully:")
print("reports/figures/build_distribution.png")
print("reports/figures/model_f1_comparison.png")
print("reports/figures/model_recall_comparison.png")
print("reports/figures/model_roc_auc_comparison.png")