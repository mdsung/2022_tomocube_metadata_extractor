import concurrent.futures
import os
from pathlib import Path

from src.database import Database
from src.gdrive import GDriveCredential
from src.image import read_all_images_in_the_project
from src.project import Project, get_target_project, insert_projects

PROJECT_PATH = Path(__file__).parents[1]
FOLDER_RAW_DATA_ID = os.getenv("RAW_DATA_FOLDER_ID")


def create_project_tables(database: Database, project: Project):
    database.execute_sql_file("sql/create_project_tables.sql", project.name)


def main():
    credentials = GDriveCredential().credentials
    database = Database()
    projects = insert_projects(credentials, database, FOLDER_RAW_DATA_ID)
    target_project_names = get_target_project("src/target_project.txt")

    for project in projects:
        if project.name in target_project_names:
            create_project_tables(database, project)

    target_project = projects[3]

    print(read_all_images_in_the_project(credentials, target_project))

    database.conn.close()


if __name__ == "__main__":
    main()
