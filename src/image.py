import datetime
import re
from dataclasses import dataclass
from enum import Enum, auto

from src.database import Database
from src.gdrive import Credentials, GDriveReader
from src.project import Project


class ImageType(Enum):
    BRIGHT_FIELD = auto()
    MIP = auto()
    HOLOTOMOGRAPHY = auto()


class CellType(Enum):
    WBC = auto()
    CD4 = auto()
    CD8 = auto()
    monocyte = auto()
    PBMC = auto()
    RBC = auto()


@dataclass
class Patient:
    google_parent_id: str
    project: Project

    def insert_to_database(self, database: Database, project: Project):
        project_id = find_project_id(self.project)
        sql = f"INSERT INTO {self.project.name}_patient(google_drive_parent_id, project_id) SELECT '{self.google_parent_id}', {project_id} WHERE NOT EXISTS(SELECT * FROM {self.project.name}_patient WHERE google_drive_parent_id = '{self.google_parent_id}')"

        database.execute_sql(sql)


@dataclass
class Cell:
    cell_type: CellType
    cell_number: int
    patient: Patient
    project: Project

    def insert_to_database(self, database: Database, project: Project):
        patient_id = find_patient_id(project, self.patient)

        try:
            sql = f"INSERT INTO {project.name}_cell(cell_type, cell_number, patient_id) SELECT '{self.cell_type.name}', {self.cell_number}, {patient_id} WHERE NOT EXISTS(SELECT * FROM {project.name}_cell WHERE cell_type = '{self.cell_type.name}' AND cell_number = {self.cell_number} AND patient_id = {patient_id})"
            database.execute_sql(sql)
        except AttributeError as e:
            print(self)
            raise AttributeError(e) from e


@dataclass
class Image:
    file_name: str
    google_drive_id: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    patient: Patient
    cell: Cell

    def insert_to_database(self, database: Database, project: Project):
        patient_id = find_patient_id(project, self.patient)

        try:
            sql = f"INSERT INTO {project.name}_image(file_name, google_drive_file_id, create_date, image_type, patient_id, cell_id) SELECT '{self.file_name}', '{self.google_drive_id}', '{self.shoot_datetime}', '{self.image_type.name}', {patient_id}, cell_id FROM {project.name}_cell WHERE cell_type = '{self.cell.cell_type.name}' AND cell_number = {self.cell.cell_number} AND patient_id = {patient_id} AND NOT EXISTS(SELECT * FROM {project.name}_image WHERE file_name = '{self.file_name}')"
            database.execute_sql(sql)
        except AttributeError as e:
            print(self)
            raise AttributeError from e


def find_project_id(project: Project) -> int:
    database = Database()
    sql = f"SELECT project_id FROM project WHERE name = '{project.name}'"
    result = database.execute_sql(sql)[0]["project_id"]  # type:ignore
    database.conn.close()
    del database
    return result


def find_patient_id(project: Project, patient: Patient) -> int:
    database = Database()
    sql = f"SELECT patient_id FROM {project.name}_patient WHERE google_drive_parent_id = '{patient.google_parent_id}'"
    result = database.execute_sql(sql)[0]["patient_id"]  # type:ignore
    database.conn.close()
    del database
    return result


def parse_shoot_time(filename: str) -> datetime.datetime:
    return datetime.datetime.strptime(filename[:14], "%Y%m%d.%H%M%S")


def parse_image_type(filename: str) -> ImageType:
    if "MIP" in filename:
        return ImageType.MIP
    elif ("Brightfield" in filename) or ("BF" in filename):
        return ImageType.BRIGHT_FIELD
    elif "Tomogram" in filename:
        return ImageType.HOLOTOMOGRAPHY


def parse_cell_type(file_name: str) -> CellType:
    cell_type_str = file_name[20:].split("-")[0]

    if cell_type_str.lower() == "default":
        return CellType.WBC
    elif cell_type_str.lower() == "buffycoat":
        return CellType.WBC
    elif cell_type_str.lower() == "buffycoatlysis":
        return CellType.WBC
    elif cell_type_str.lower() == "mono_negative":
        return CellType.PBMC

    for cell_type in CellType:
        if cell_type.name.lower() in cell_type_str.lower():
            return cell_type


def parse_cell_number(file_name: str) -> int:
    return int(re.findall("[0-9]{3}", file_name.split(".")[3])[0])


def read_all_images_in_the_project(credentials: Credentials, project: Project):
    reader = GDriveReader(
        credentials, project.google_drive_folder_id, folder=True
    )
    database = Database()

    google_file_id_list = [
        data_dict.get("google_drive_file_id")
        for data_dict in database.execute_sql(
            f"SELECT google_drive_file_id FROM {project.name}_image"
        )
    ]

    for date_folder in reader.read():
        image_reader = GDriveReader(credentials, date_folder["id"], image=True)
        for image in image_reader.read():
            if image["id"] in google_file_id_list:
                continue
            objects = _extract_objects(image, project)
            for obj in objects:
                obj.insert_to_database(database, project)

    database.conn.close()
    del database


def _extract_objects(image, project):
    file_name = image["name"]
    google_drive_id = image["id"]
    google_parent_id = image["parents"][0]
    shoot_datetime = parse_shoot_time(file_name)
    image_type = parse_image_type(file_name)
    cell_type = parse_cell_type(file_name)
    cell_number = parse_cell_number(file_name)

    patient_object = Patient(google_parent_id, project)
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
