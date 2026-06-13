import pandas as pd
import os

input_file = "data/raw/large_build_history.csv"
output_file = "data/processed/clean_build_history.csv"

df = pd.read_csv(input_file)

print("Original records:", len(df))
print(df["conclusion"].value_counts(dropna=False))

df = df[df["conclusion"].isin(["success", "failure"])]

df["build_result"] = df["conclusion"].map({
    "success": 0,
    "failure": 1
})

df = df.dropna(subset=["commit_id", "build_result"])

os.makedirs("data/processed", exist_ok=True)

df.to_csv(output_file, index=False)

print("\nCleaned records:", len(df))
print(df["build_result"].value_counts())

print("\nCleaned dataset saved:", output_file)