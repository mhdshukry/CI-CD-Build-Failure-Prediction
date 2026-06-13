import subprocess
import os


def run_git_command(repo_path, command):
    result = subprocess.run(
        command,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=True
    )

    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def analyze_latest_commit(repo_path):
    if not os.path.exists(repo_path):
        return {"error": "Repository path not found"}

    commit_id = run_git_command(
        repo_path,
        "git rev-parse HEAD"
    )

    changed_files_output = run_git_command(
        repo_path,
        "git diff-tree --no-commit-id --name-only -r HEAD"
    )

    numstat_output = run_git_command(
        repo_path,
        "git show --numstat --format= HEAD"
    )

    changed_files = [
        file.strip()
        for file in changed_files_output.split("\n")
        if file.strip()
    ]

    lines_added = 0
    lines_deleted = 0

    for line in numstat_output.split("\n"):
        parts = line.split()

        if len(parts) >= 3:
            try:
                lines_added += int(parts[0])
                lines_deleted += int(parts[1])
            except:
                pass

    dependency_file_changed = any(
        file.lower().endswith(
            ("requirements.txt", "package.json", "pom.xml", "build.gradle")
        )
        for file in changed_files
    )

    test_file_changed = any(
        "test" in file.lower()
        for file in changed_files
    )

    workflow_changed = any(
        ".github/workflows" in file.lower()
        for file in changed_files
    )

    source_file_changed = any(
        file.lower().endswith(
            (".py", ".java", ".js", ".ts", ".jsx", ".tsx")
        )
        for file in changed_files
    )

    return {
        "commit_id": commit_id,
        "files_changed": len(changed_files),
        "lines_added": lines_added,
        "lines_deleted": lines_deleted,
        "total_changes": lines_added + lines_deleted,
        "dependency_file_changed": int(dependency_file_changed),
        "test_file_changed": int(test_file_changed),
        "workflow_changed": int(workflow_changed),
        "source_file_changed": int(source_file_changed),
        "risk_file_count": (
            int(dependency_file_changed)
            + int(test_file_changed)
            + int(workflow_changed)
            + int(source_file_changed)
        ),
        "changed_files": ", ".join(changed_files)
    }