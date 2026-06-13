import requests
import pandas as pd
import os
import time

REPOS = [
    ("spring-projects", "spring-petclinic"),
    ("pallets", "flask"),
    ("psf", "requests"),
    ("django", "django"),
    ("fastapi", "fastapi"),
]

PER_PAGE = 100
MAX_PAGES = 10   # 10 pages x 100 = 1000 builds per repo

all_data = []

headers = {
    "Accept": "application/vnd.github+json"
}

for owner, repo in REPOS:
    print(f"\nCollecting builds from {owner}/{repo}")

    for page in range(1, MAX_PAGES + 1):
        url = (
            f"https://api.github.com/repos/{owner}/{repo}/actions/runs"
            f"?per_page={PER_PAGE}&page={page}"
        )

        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Error:", response.status_code, response.text[:200])
            break

        runs = response.json().get("workflow_runs", [])

        if len(runs) == 0:
            print("No more records.")
            break

        for run in runs:
            all_data.append({
                "repository": f"{owner}/{repo}",
                "run_id": run.get("id"),
                "commit_id": run.get("head_sha"),
                "branch": run.get("head_branch"),
                "workflow_name": run.get("name"),
                "event": run.get("event"),
                "status": run.get("status"),
                "conclusion": run.get("conclusion"),
                "created_at": run.get("created_at"),
                "updated_at": run.get("updated_at"),
                "html_url": run.get("html_url")
            })

        print(f"Page {page}: {len(runs)} records collected")

        time.sleep(1)

df = pd.DataFrame(all_data)

os.makedirs("data/raw", exist_ok=True)

df.to_csv("data/raw/large_build_history.csv", index=False)

print("\n=================================")
print("Large Build History Dataset Created")
print("=================================")
print("Total records:", len(df))
print(df["conclusion"].value_counts(dropna=False))