import pandas as pd
import os

build_df = pd.read_csv("data/processed/clean_build_history.csv")
commit_df = pd.read_csv("data/processed/commit_features_full.csv")

final_df = pd.merge(
    build_df,
    commit_df,
    on=["repository", "commit_id"],
    how="inner"
)

final_df = final_df.drop_duplicates()

final_df["risk_file_count"] = (
    final_df["dependency_file_changed"]
    + final_df["test_file_changed"]
    + final_df["workflow_changed"]
    + final_df["source_file_changed"]
)

os.makedirs("data/processed", exist_ok=True)

final_df.to_csv("data/processed/final_ml_dataset.csv", index=False)

print("==============================")
print("Final ML Dataset Created")
print("==============================")
print("Records:", len(final_df))
print("Columns:", final_df.columns.tolist())
print("\nTarget Distribution:")
print(final_df["build_result"].value_counts())
print("\nSample:")
print(final_df.head())