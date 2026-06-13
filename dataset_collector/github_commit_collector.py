import requests
import pandas as pd
import os


# ===============================
# GitHub Repository Details
# ===============================

OWNER = "spring-projects"
REPO = "spring-petclinic"


API_URL = f"https://api.github.com/repos/{OWNER}/{REPO}/commits"


dataset = []


print("Collecting commits...")


response = requests.get(API_URL)

commits = response.json()


for commit in commits:


    commit_sha = commit["sha"]


    commit_detail_url = (
        f"https://api.github.com/repos/"
        f"{OWNER}/{REPO}/commits/{commit_sha}"
    )


    details = requests.get(
        commit_detail_url
    ).json()



    changed_files = []


    for file in details["files"]:

        changed_files.append(
            file["filename"]
        )


    row = {


        "repository":
            REPO,


        "commit_id":
            commit_sha,


        "developer":
            commit["commit"]["author"]["name"],


        "files_changed":
            len(details["files"]),


        "lines_added":
            details["stats"]["additions"],


        "lines_deleted":
            details["stats"]["deletions"],


        "total_changes":
            details["stats"]["total"],


        "changed_files":
            ",".join(changed_files)

    }


    dataset.append(row)



df = pd.DataFrame(dataset)



os.makedirs(
    "data/raw",
    exist_ok=True
)


df.to_csv(

    "data/raw/commit_features.csv",

    index=False

)



print("==============================")
print("Commit Dataset Created")
print("==============================")

print(df.head())