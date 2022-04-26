import concurrent.futures
import os
from functools import partial
from pathlib import Path

from src.database import Database
from src.gdrive import GDriveCredential
from src.image import create_image_table
from src.project import Project, create_project_database

PROJECT_PATH = Path(__file__).parents[1]
FOLDER_RAW_DATA_ID = os.getenv("RAW_DATA_FOLDER_ID")


def main():
    credentials = GDriveCredential().credentials
    database = Database()
    projects = create_project_database(
        credentials, database, FOLDER_RAW_DATA_ID
    )

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                create_image_table, credentials, Database(), project
            )
            for project in projects
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()


if __name__ == "__main__":
    main()
