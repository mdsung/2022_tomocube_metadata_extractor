import concurrent.futures
import datetime
from dataclasses import dataclass

from src.database import Database
from src.gdrive import Credentials, GDriveReader
from src.parser import (
    find_patient_id,
    find_project_id,
    parse_cell_number,
    parse_cell_type,
    parse_image_type,
    parse_shoot_time,
)
from src.project import Project
from src.type import CELL_TYPE_DICT, IMAGE_TYPE_DICT, CellType, ImageType


@dataclass
class Patient:
    google_parent_id: str
    project: Project
    google_drive_parent_name: str

    def insert_to_database(
        self, project: Project, project_id: int, patient_id: int
    ):
        database = Database()
        sql = f"""INSERT INTO {self.project.name}_patient(google_drive_parent_id, project_id, google_drive_parent_name) 
                SELECT '{self.google_parent_id}', {project_id}, {self.google_drive_parent_name}
                WHERE NOT EXISTS(SELECT * FROM {self.project.name}_patient 
                WHERE google_drive_parent_id = '{self.google_parent_id}')"""
        database.execute_sql(sql)
        database.conn.close()


@dataclass
class Cell:
    cell_type: CellType
    cell_number: int
    patient: Patient
    project: Project

    def insert_to_database(
        self, project: Project, project_id: int, patient_id: int
    ):
        database = Database()
        try:
            sql = f"""INSERT INTO {project.name}_cell(cell_type, cell_number, patient_id) 
                SELECT '{self.cell_type.name}', {self.cell_number}, {patient_id} 
                WHERE NOT EXISTS(
                    SELECT * 
                    FROM {project.name}_cell 
                    WHERE cell_type = '{self.cell_type.name}' 
                    AND cell_number = {self.cell_number} 
                    AND patient_id = {patient_id})"""
            database.execute_sql(sql)
        except AttributeError as e:
            print(self)
            raise AttributeError(e) from e
        database.conn.close()


@dataclass
class Image:
    file_name: str
    google_drive_id: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    patient: Patient
    cell: Cell

    def insert_to_database(
        self, project: Project, project_id: int, patient_id: int
    ):
        database = Database()
        try:
            sql = f"""INSERT INTO {project.name}_image(file_name, google_drive_file_id, create_date, image_type, patient_id, cell_id) 
                    SELECT '{self.file_name}', '{self.google_drive_id}', '{self.shoot_datetime}', '{self.image_type.name}', {patient_id}, cell_id 
                    FROM {project.name}_cell 
                    WHERE patient_id = {patient_id} 
                    AND cell_type = '{self.cell.cell_type.name}' 
                    AND cell_number = {self.cell.cell_number} 
                    AND NOT EXISTS(
                        SELECT * 
                        FROM {project.name}_image 
                        WHERE file_name = '{self.file_name}')
                    """
            database.execute_sql(sql)
        except AttributeError as e:
            print(self)
            raise AttributeError from e
        database.conn.close()


def read_all_images_in_the_project(credentials: Credentials, project: Project):
    count = 0
    google_file_id_list = _extract_exist_images(project)

    reader = GDriveReader(
        credentials, project.google_drive_folder_id, folder=True
    )
    for data_folder in reader.read():
        image_reader = GDriveReader(credentials, data_folder["id"], image=True)
        project_id = find_project_id(project)
        patient_id = find_patient_id(project, data_folder["id"])

        for image in image_reader.read():
            if image["id"] in google_file_id_list:
                continue
            objects = _extract_objects(image, project, data_folder["name"])
            _write_to_database(objects, project, project_id, patient_id)
            count += len(objects)

    return {"Updated Image": count}


def _extract_exist_images(project: Project) -> list[str]:
    database = Database()
    return [
        data_dict.get("google_drive_file_id")
        for data_dict in database.execute_sql(
            f"SELECT google_drive_file_id FROM {project.name}_image"
        )
    ]


def _extract_objects(image, project, data_folder_name):
    file_name = image["name"]
    google_drive_id = image["id"]
    google_parent_id = image["parents"][0]

    shoot_datetime = parse_shoot_time(file_name)
    image_type = parse_image_type(file_name, IMAGE_TYPE_DICT)
    cell_type = parse_cell_type(file_name, CELL_TYPE_DICT)
    cell_number = parse_cell_number(file_name)

    patient_object = Patient(google_parent_id, project, data_folder_name)
    cell_object = Cell(cell_type, cell_number, patient_object, project)
    image_object = Image(
        file_name,
        google_drive_id,
        shoot_datetime,
        image_type,
        patient_object,
        cell_object,
    )
    return patient_object, cell_object, image_object


def _write_to_database(objects, project, project_id, patient_id) -> None:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(
                obj.insert_to_database, project, project_id, patient_id
            )
            for obj in objects
        ]
        for future in concurrent.futures.as_completed(futures):
            future.result()
