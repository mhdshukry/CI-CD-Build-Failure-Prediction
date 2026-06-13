from local_repo_analyzer import analyze_latest_commit

repo_path = r"D:\CI-CD-Build-Failure-Prediction"

result = analyze_latest_commit(repo_path)

print("\n==============================")
print("LATEST COMMIT ANALYSIS")
print("==============================")

for key, value in result.items():
    print(f"{key}: {value}")