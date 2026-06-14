import requests
import re


# ==================================================
# Extract owner and repository name from GitHub URL
# ==================================================

def extract_owner_repo(repo_url):

    pattern = r"github\.com/([^/]+)/([^/]+)"

    match = re.search(
        pattern,
        repo_url
    )


    if not match:

        return None, None


    owner = match.group(1)

    repo = (
        match.group(2)
        .replace(".git", "")
    )


    return owner, repo





# ==================================================
# Create GitHub API headers
# ==================================================

def github_headers(github_token=""):


    headers = {

        "Accept":
        "application/vnd.github+json"

    }



    if github_token:


        headers[
            "Authorization"
        ] = (

            f"Bearer {github_token}"

        )


    return headers





# ==================================================
# Analyze GitHub Repository
# ==================================================

def analyze_github_repository(
        repo_url,
        github_token=""
):


    owner, repo = extract_owner_repo(
        repo_url
    )


    if not owner or not repo:


        return {

            "error":
            "Invalid GitHub repository URL"

        }



    headers = github_headers(
        github_token
    )



    # ==================================================
    # Get latest commit
    # ==================================================


    commits_url = (

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits"

    )



    response = requests.get(
        commits_url,
        headers=headers
    )



    if response.status_code != 200:


        return {

            "error":
            "Unable to access GitHub repository",

            "status_code":
            response.status_code

        }




    commits = response.json()



    if not commits:


        return {

            "error":
            "No commits found"

        }




    latest_commit = commits[0]



    commit_id = (
        latest_commit["sha"]
    )


    commit_message = (

        latest_commit
        ["commit"]
        ["message"]

    )




    # ==================================================
    # Commit details
    # ==================================================


    details_url = (

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/commits/"
        f"{commit_id}"

    )



    detail_response = requests.get(

        details_url,
        headers=headers

    )



    if detail_response.status_code != 200:


        return {

            "error":
            "Unable to fetch commit details"

        }




    commit_data = (
        detail_response.json()
    )




    files = (
        commit_data
        .get(
            "files",
            []
        )
    )



    changed_files = []


    for file in files:


        changed_files.append(

            file["filename"]

        )




    lines_added = (

        commit_data
        .get(
            "stats",
            {}
        )
        .get(
            "additions",
            0
        )

    )



    lines_deleted = (

        commit_data
        .get(
            "stats",
            {}
        )
        .get(
            "deletions",
            0
        )

    )





    # ==================================================
    # File type analysis
    # ==================================================



    dependency_files = [

        "requirements.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pom.xml",
        "build.gradle",
        "composer.json",
        "pyproject.toml"

    ]



    dependency_changed = any(

        file.lower()
        .endswith(
            tuple(
                dependency_files
            )
        )

        for file in changed_files

    )




    workflow_changed = any(

        ".github/workflows"

        in file.lower()

        for file in changed_files

    )





    test_changed = any(

        "test"

        in file.lower()

        or

        "tests/"

        in file.lower()


        for file in changed_files

    )





    source_changed = any(


        file.lower()
        .endswith(

            (

                ".py",
                ".java",
                ".js",
                ".jsx",
                ".ts",
                ".tsx",
                ".php",
                ".html",
                ".css"

            )

        )


        for file in changed_files

    )





    risk_count = sum(

        [

            dependency_changed,
            workflow_changed,
            test_changed,
            source_changed

        ]

    )





    # ==================================================
    # GitHub Actions previous build
    # ==================================================


    previous_status = "unknown"

    previous_failed_step = ""

    previous_error = ""



    actions_url = (

        f"https://api.github.com/repos/"
        f"{owner}/{repo}/actions/runs"

    )



    action_response = requests.get(

        actions_url,
        headers=headers

    )




    if action_response.status_code == 200:


        runs = (

            action_response
            .json()
            .get(
                "workflow_runs",
                []
            )

        )



        if runs:


            latest_run = runs[0]


            previous_status = (

                latest_run
                .get(
                    "conclusion"
                )

                or

                "running"

            )



            if previous_status == "failure":


                previous_failed_step = (

                    latest_run
                    .get(
                        "name",
                        "GitHub Action"

                    )

                )



                previous_error = (

                    "Previous GitHub Action failed"

                )





    # ==================================================
    # Final output for AI model
    # ==================================================


    return {


        "repository":
        f"{owner}/{repo}",


        "repo_url":
        repo_url,


        "commit_id":
        commit_id,


        "commit_message":
        commit_message,


        "files_changed":
        len(changed_files),


        "lines_added":
        lines_added,


        "lines_deleted":
        lines_deleted,


        "total_changes":
        lines_added + lines_deleted,


        "dependency_file_changed":
        int(
            dependency_changed
        ),


        "test_file_changed":
        int(
            test_changed
        ),


        "workflow_changed":
        int(
            workflow_changed
        ),


        "source_file_changed":
        int(
            source_changed
        ),


        "risk_file_count":
        risk_count,


        "changed_files":

        ", ".join(
            changed_files
        ),


        "previous_build_status":
        previous_status,


        "previous_failed_step":
        previous_failed_step,


        "previous_error_message":
        previous_error


    }