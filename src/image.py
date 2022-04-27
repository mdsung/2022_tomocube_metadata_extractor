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


@dataclass
class Patient:
    google_parent_id: str
    project: Project


@dataclass
class Cell:
    cell_type: CellType
    cell_number: int
    patient: Patient


@dataclass
class Image:
    file_name: str
    google_drive_id: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    cell: Cell

    def insert_to_database(self, database: Database):
        project_id = self.find_project_id(database, self.project)

        try:
            sql = f"INSERT INTO {self.project.name}(file_name, google_drive_file_id, google_drive_parent_id, create_date, image_type, project_id) SELECT '{self.file_name}', '{self.google_drive_id}', '{self.google_parent_id}', '{self.shoot_datetime}', '{self.image_type.name}',{project_id}  FROM DUAL WHERE NOT EXISTS(SELECT * FROM {self.project.name} WHERE file_name = '{self.file_name}')"
        except AttributeError:
            print(self.project)
            print(self.file_name)

        else:
            database.execute_sql(sql)


def find_project_id(project: Project) -> int:
    database = Database()
    sql = f"SELECT project_id FROM project WHERE name = '{project.name}'"
    result = database.execute_sql(sql)[0]["project_id"]
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
    for cell_type in CellType:
        if cell_type.name.lower() in cell_type_str.lower():
            return cell_type


def parse_cell_number(file_name: str) -> int:
    return int(re.findall("[0-9]{3}", file_name.split(".")[3])[0])


def read_all_images_in_the_project(credentials: Credentials, project: Project):
    reader = GDriveReader(
        credentials, project.google_drive_folder_id, folder=True
    )

    for date_folder in reader.read():
        image_reader = GDriveReader(credentials, date_folder["id"], image=True)
        for image in image_reader.read():
            file_name = image["name"]
            print(file_name)
            google_drive_id = image["id"]
            google_parent_id = image["parents"][0]
            shoot_datetime = parse_shoot_time(file_name)
            image_type = parse_image_type(file_name)
            cell_type = parse_cell_type(file_name)
            cell_number = parse_cell_number(file_name)
            project_name = project.name

            patient_object = Patient(google_parent_id, project)
            cell_object = Cell(cell_type, cell_number, patient_object)
            image_object = Image(
                file_name,
                google_drive_id,
                shoot_datetime,
                image_type,
                cell_object,
            )
            return patient_object, cell_object, image_object


# def insert_image(credentials, database: Database, project: Project):
#     images = get_images(credentials, project)

#     if not is_project_in_database(database, project.name):
#         create_project_table(database, project.name)

#     for image in images:
#         image.insert_to_database(database)

#     database.conn.commit()

#     return images
