def get_bucket_name_from_project_name(project_name: str) -> str:
    return project_name.replace("_", "-")


def get_project_name_from_bucket_name(bucket_name: str) -> str:
    return bucket_name.replace("-", "_")
