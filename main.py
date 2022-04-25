import os
from pathlib import Path

from src.gdrive import GDriveCredential
from src.image import get_images
from src.project import Project, get_tomocube_projects

PROJECT_PATH = Path(__file__).parents[1]
FOLDER_RAW_DATA_ID = os.getenv("RAW_DATA_FOLDER_ID")


def main():
    credentials = GDriveCredential().credentials
    tomocube_projects = get_tomocube_projects(credentials, FOLDER_RAW_DATA_ID)

    target_project: Project = tomocube_projects[2]
    images = get_images(credentials, target_project)
    print(images)


if __name__ == "__main__":
    main()
