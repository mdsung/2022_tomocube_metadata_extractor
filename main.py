import concurrent.futures
import os
from pathlib import Path

from src.database import Database
from src.image import (
    ExistingImages,
    count_existing_images,
    count_working_images,
    extract_objects,
    write_to_database,
)
from src.logger import set_logger
from src.parser import find_patient_id, find_project_id
from src.patient import ExistingPatients, NewPatients, Patient, WorkingPatients
from src.project import (
    ExistingProjects,
    FinalProjects,
    S3WorkingProjects,
    TargetProjects,
    create_new_project,
)
from src.s3 import (
    AWS_KEY,
    AWS_PASSWORD,
    S3Credential,
    S3FileReader,
    get_s3_bucket,
)

logger = set_logger()

logger.info("Get credentials")
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
    s3_file_reader = S3FileReader(get_s3_bucket(s3_credential, project_name))
    project_id = find_project_id(project_name)

    for patient in new_patients:
        patient_object = Patient(project_name, patient)
        patient_object.insert_to_database(project_id)

        patient_id = find_patient_id(project_name, patient)
        count += run_each_patient(
            s3_file_reader, project_name, patient_id, patient
        )

    return count


def run_each_patient(
    s3_file_reader: S3FileReader,
    project_name: str,
    patient_id: int,
    folder_name: str,
):
    working_images = set(s3_file_reader.read(folder_name))
    existing_images = set(ExistingImages(project_name).get())
    target_images = working_images - existing_images
    for image in target_images:
        if "tiff" not in image:
            continue
        objects = extract_objects(image, project_name, folder_name)
        write_to_database(objects, project_name, patient_id)
    Database().conn.commit()
    return len(target_images)


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
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(run_each_project, project_name)
            for project_name in final_projects
        ]
        for future in concurrent.futures.as_completed(futures):
            logger.info(future.result())

    database.conn.commit()
    database.conn.close()


if __name__ == "__main__":
    main()
