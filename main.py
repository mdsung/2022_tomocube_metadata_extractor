import concurrent.futures
import logging
import os
from pathlib import Path

from src.database import Database
from src.gdrive import Credentials, GDriveCredential
from src.image import read_all_images_in_the_project
from src.logger import set_logger
from src.project import Project, get_target_project, insert_projects

PROJECT_PATH = Path(__file__).parents[1]
FOLDER_RAW_DATA_ID = os.getenv("RAW_DATA_FOLDER_ID")
logger = set_logger()


def create_project_tables(database: Database, project: Project):
    logger.info(f"Create Project Tables {project.name}")

    database.execute_sql_file("sql/create_project_tables.sql", project.name)


def run_each_project(credentials: Credentials, project: Project):
    logger.info(f"Start processing {project.name}")

    database = Database()
    create_project_tables(database, project)
    count = read_all_images_in_the_project(credentials, project)
    return count


def main():
    logger.info("Get credentials")
    credentials = GDriveCredential().credentials

    logger.info("Insert Projects")
    database = Database()
    projects = insert_projects(credentials, database, FOLDER_RAW_DATA_ID)
    target_project_names = get_target_project("src/target_project.txt")
    
    logger.info(f"Target projects: {', '.join(target_project_names)}")
    logger.info("Start multiprocessing")

    counts = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(run_each_project, credentials, project)
            for project in projects
            if project.name in target_project_names
        ]
        for future in concurrent.futures.as_completed(futures):
            counts.append(future.result())

    logger.info(f"{sum(counts)} images have been uploaded")
    database.conn.close()


if __name__ == "__main__":
    main()
