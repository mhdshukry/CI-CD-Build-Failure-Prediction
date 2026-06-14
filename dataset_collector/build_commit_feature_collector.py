from dotenv import load_dotenv
import pandas as pd
import requests
import os
import time

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

headers = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

input_file = "data/processed/clean_build_history.csv"
df = pd.read_csv(input_file)

features = []

print("Collecting commit features with GitHub token...")

for index, row in df.iterrows():
    repo = row["repository"]
    commit = row["commit_id"]

    url = f"https://api.github.com/repos/{repo}/commits/{commit}"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print("Skipped:", index, response.status_code)
        continue

    data = response.json()
    files = data.get("files", [])

    filenames = [f["filename"] for f in files]

    dependency = any(x.endswith(("requirements.txt", "package.json", "pom.xml", "build.gradle")) for x in filenames)
    test_change = any("test" in x.lower() for x in filenames)
    workflow_change = any(".github/workflows" in x for x in filenames)
    source_change = any(x.endswith((".py", ".java", ".js", ".ts")) for x in filenames)

    features.append({
        "repository": repo,
        "commit_id": commit,
        "files_changed": len(files),
        "lines_added": data["stats"]["additions"],
        "lines_deleted": data["stats"]["deletions"],
        "total_changes": data["stats"]["total"],
        "dependency_file_changed": int(dependency),
        "test_file_changed": int(test_change),
        "workflow_changed": int(workflow_change),
        "source_file_changed": int(source_change),
        "changed_files": ",".join(filenames)
    })

    if index % 100 == 0:
        print(index, "processed")

    time.sleep(0.1)

feature_df = pd.DataFrame(features)

os.makedirs("data/processed", exist_ok=True)

feature_df.to_csv("data/processed/commit_features_full.csv", index=False)

print("====================")
print("Finished")
print("====================")
print("Records:", len(feature_df))
print(feature_df.head())