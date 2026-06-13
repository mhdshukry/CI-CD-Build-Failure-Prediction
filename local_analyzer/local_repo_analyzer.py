import subprocess
import os


def run_git(repo_path, command):
    result = subprocess.run(
        command,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def should_ignore_file(file_path):
    file_path = file_path.lower()

    ignore_keywords = [
        "__pycache__",
        ".pyc",
        "venv/",
        ".git/",
        "data/",
        "reports/",
        "models/saved/",
        ".pkl",
        ".csv",
        ".png",
        ".jpg",
        ".jpeg",
        ".xlsx",
        ".pdf"
    ]

    return any(keyword in file_path for keyword in ignore_keywords)


def analyze_latest_commit(repo_path):
    if not os.path.exists(repo_path):
        return {
            "error": "Repository path not found"
        }

    is_git_repo = run_git(repo_path, "git rev-parse --is-inside-work-tree")

    if is_git_repo != "true":
        return {
            "error": "This folder is not a Git repository"
        }

    commit_id = run_git(
        repo_path,
        "git rev-parse HEAD"
    )

    commit_message = run_git(
        repo_path,
        "git log -1 --pretty=%B"
    )

    changed_files_output = run_git(
        repo_path,
        "git diff-tree --root --no-commit-id --name-only -r HEAD"
    )

    all_changed_files = [
        f.strip().replace("\\", "/")
        for f in changed_files_output.split("\n")
        if f.strip()
    ]

    changed_files = [
        f for f in all_changed_files
        if not should_ignore_file(f)
    ]

    stat_output = run_git(
        repo_path,
        "git diff-tree --root --numstat --no-commit-id -r HEAD"
    )

    added = 0
    deleted = 0

    for line in stat_output.split("\n"):
        parts = line.split()

        if len(parts) >= 3:
            file_name = parts[2].replace("\\", "/")

            if should_ignore_file(file_name):
                continue

            try:
                added += int(parts[0])
                deleted += int(parts[1])
            except ValueError:
                continue

    dependency_files = [
        "requirements.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pom.xml",
        "build.gradle",
        "composer.json",
        "pyproject.toml",
        "environment.yml"
    ]

    dependency_changed = any(
        file.lower().endswith(tuple(dependency_files))
        for file in changed_files
    )

    workflow_changed = any(
        ".github/workflows" in file.lower()
        for file in changed_files
    )

    test_changed = any(
        "test" in file.lower() or "tests/" in file.lower()
        for file in changed_files
    )

    source_changed = any(
        file.lower().endswith(
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

    config_changed = any(
        keyword in file.lower()
        for file in changed_files
        for keyword in [
            "config",
            ".env",
            "settings",
            "application.properties",
            "application.yml",
            "dockerfile",
            "docker-compose"
        ]
    )

    risk_count = sum(
        [
            dependency_changed,
            workflow_changed,
            test_changed,
            source_changed,
            config_changed
        ]
    )

    return {
        "commit_id": commit_id,
        "commit_message": commit_message,
        "files_changed": len(changed_files),
        "lines_added": added,
        "lines_deleted": deleted,
        "total_changes": added + deleted,
        "dependency_file_changed": int(dependency_changed),
        "test_file_changed": int(test_changed),
        "workflow_changed": int(workflow_changed),
        "source_file_changed": int(source_changed),
        "config_file_changed": int(config_changed),
        "risk_file_count": risk_count,
        "changed_files": ", ".join(changed_files),
        "ignored_files_count": len(all_changed_files) - len(changed_files)
    }