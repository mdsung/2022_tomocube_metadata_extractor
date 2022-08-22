import concurrent.futures
import datetime
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.cell import Cell
from src.database import Database
from src.parser import (
    parse_cell_number,
    parse_cell_type,
    parse_image_type,
    parse_shoot_time,
)
from src.patient import Patient
from src.s3 import S3Credential, S3FileReader, get_s3_bucket
from src.type import CELL_TYPE_DICT, IMAGE_TYPE_DICT, ImageType
from src.util import get_bucket_name_from_project_name

logger = logging.getLogger()


def count_working_images(
    project_name: str, patient: str, credential: S3Credential
):
    bucket_name = get_bucket_name_from_project_name(project_name)
    bucket = get_s3_bucket(credential, bucket_name)
    s3_file_reader = S3FileReader(bucket)
    result = len(s3_file_reader.read(patient))
    logging.info(f"Counting working images-{patient} : {result}")
    return result


def count_existing_images(project_name: str, patient: str):
    database = Database()
    sql = f"""SELECT COUNT(*) count FROM {project_name}_image i
            LEFT JOIN {project_name}_patient p
            ON p.patient_id = i.patient_id
            WHERE google_drive_parent_name = '{patient}';
            """
    result = database.execute_sql(sql)[0]["count"]  # type: ignore
    logging.info(f"Counting existing images-{patient}: {result}")
    return result


@dataclass
class Image:
    file_name: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    patient: Patient
    cell: Cell

    def insert_to_database(self, project_name: str, patient_id: int):
        logger.info(
            f"Inserting image to database - {project_name}|{self.patient.google_drive_parent_name}|{self.file_name}"
        )
        sql = f"""INSERT INTO {project_name}_image(file_name, create_date, image_type, patient_id, cell_id) 
                SELECT '{self.file_name}', '{self.shoot_datetime}', '{self.image_type.name}', {patient_id}, cell_id 
                FROM {project_name}_cell 
                WHERE patient_id = {patient_id} 
                AND cell_type = '{self.cell.cell_type.name}' 
                AND cell_number = {self.cell.cell_number} 
                AND NOT EXISTS(
                    SELECT * 
                    FROM {project_name}_image 
                    WHERE file_name = '{self.file_name}')
                """
        Database().execute_sql(sql)


class Images(ABC):
    def __init__(self, project_name: str) -> None:
        self.project_name = project_name

    @abstractmethod
    def get(self):
        ...


class ExistingImages(Images):
    def get(self):
        database = Database()
        return {
            data_dict.get("file_name")
            for data_dict in database.execute_sql(
                f"SELECT file_name FROM {self.project_name}_image"
            )
        }


def extract_objects(image_name: str, project_name: str, data_folder_name: str):
    shoot_datetime = parse_shoot_time(image_name)
    image_type = parse_image_type(image_name, IMAGE_TYPE_DICT)
    cell_type = parse_cell_type(image_name, CELL_TYPE_DICT)
    cell_number = parse_cell_number(image_name)

    patient_object = Patient(project_name, data_folder_name)
    cell_object = Cell(cell_type, cell_number, patient_object, project_name)
    image_object = Image(
        image_name, shoot_datetime, image_type, patient_object, cell_object
    )
    return cell_object, image_object


def write_to_database(objects, project_name: str, patient_id: int) -> None:

    cell_object, image_object = objects

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        f1 = executor.submit(
            cell_object.insert_to_database, project_name, patient_id
        )
        f2 = executor.submit(
            image_object.insert_to_database, project_name, patient_id
        )
        f1.result()
        f2.result()
