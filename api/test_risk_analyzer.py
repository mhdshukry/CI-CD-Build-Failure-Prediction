from risk_analyzer import predict_build_risk

sample_commit = {
    "files_changed": 35,
    "lines_added": 420,
    "lines_deleted": 120,
    "total_changes": 540,
    "dependency_file_changed": 1,
    "test_file_changed": 0,
    "workflow_changed": 1,
    "source_file_changed": 1,
    "risk_file_count": 3
}

result = predict_build_risk(sample_commit)

print(result)