import concurrent.futures
import logging
import os
from pathlib import Path

from src.database import Database
from src.gdrive import Credentials, GDriveCredential
from src.image import (
    count_existing_images,
    count_working_images,
    read_all_images_in_the_project,
)
from src.logger import set_logger
from src.patient import ExistingPatients, NewPatients, WorkingPatients
from src.project import (
    ExistingProjects,
    FinalProjects,
    Project,
    S3WorkingProjects,
    TargetProjects,
    create_new_project,
)
from src.s3 import AWS_KEY, AWS_PASSWORD, S3Credential

PROJECT_PATH = Path(__file__).parents[1]
FOLDER_RAW_DATA_ID = os.getenv("RAW_DATA_FOLDER_ID")
logger = set_logger()
# logger.info("Get credentials")
gdrive_credentials = GDriveCredential().credentials
s3_credential = S3Credential(AWS_KEY, AWS_PASSWORD)


def run_each_project(project_name: str):
    logger.info(f"Start processing {project_name}")
    count = 0

    existing_patients = ExistingPatients(project_name).get()
    working_patients = WorkingPatients(project_name, s3_credential).get()
    new_patients = NewPatients(project_name).get(
        working_patients, existing_patients
    )

    # 1. 기존의 환자들 폴더에 있는 이미지 숫자랑 database metadata 숫자랑 같은지 확인
    for patient in existing_patients:
        if count_working_images(
            project_name, patient, s3_credential
        ) != count_existing_images(project_name, patient):
            new_patients.add(patient)

    # 2. 새로운 환자에 대해서 image metadata extract
    for patient in new_patients:
        count += run_each_patient(project_name, patient)

    return count


def run_each_patient(project_name: str, folder_name: str):
    count = 0
    return count


def main():

    logger.info("Insert Projects")

    database = Database()
    existing_projects = ExistingProjects().get(database)
    working_projects = S3WorkingProjects().get(s3_credential)
    target_projects = TargetProjects().get("src/target_project.txt")
    final_projects = FinalProjects().get(working_projects, target_projects)
    diff_projects = final_projects.difference(existing_projects)

    if len(diff_projects) > 0:
        create_new_project(diff_projects)

    logger.info("Start processing")
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(run_each_project, project_name)
            for project_name in final_projects
        ]
        for future in concurrent.futures.as_completed(futures):
            logger.info(future.result())

    # logger.info("Finish")
    # projects = insert_projects(credentials, database, FOLDER_RAW_DATA_ID)

    # logger.info(f"Target projects: {', '.join(target_project_names)}")
    # logger.info("Start multiprocessing")

    # counts = []
    # with concurrent.futures.ProcessPoolExecutor() as executor:
    #     futures = [
    #         executor.submit(run_each_project, credentials, project)
    #         for project in projects
    #         if project.name in target_project_names
    #     ]
    #     for future in concurrent.futures.as_completed(futures):
    #         counts.append(future.result())

    # logger.info(f"{sum(counts)} images have been uploaded")
    # database.conn.close()


if __name__ == "__main__":
    main()
