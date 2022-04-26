import datetime
from dataclasses import dataclass
from enum import Enum, auto

from src.database import Database
from src.gdrive import Credentials, GDriveReader
from src.project import Project


class ImageType(Enum):
    BRIGHT_FIELD = auto()
    MIP = auto()
    HOLOTOMOGRAPHY = auto()


@dataclass
class Image:
    file_name: str
    google_drive_id: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    project: Project

    def insert_to_database(self, database: Database):
        project_id = self.find_project_id(database, self.project)

        try:
            sql = f"INSERT INTO {self.project.name}(file_name, google_drive_file_id, create_date, image_type, project_id) SELECT '{self.file_name}', '{self.google_drive_id}', '{self.shoot_datetime}', '{self.image_type.name}',{project_id}  FROM DUAL WHERE NOT EXISTS(SELECT * FROM {self.project.name} WHERE file_name = '{self.file_name}')"
        except AttributeError:
            print(self.project)
            print(self.file_name)

        else:
            database.execute_sql(sql)

    def find_project_id(self, database: Database, project: Project) -> int:
        sql = f"SELECT project_id FROM project WHERE name = '{project.name}'"
        return database.execute_sql(sql)[0]["project_id"]


def parse_image_type(filename: str) -> ImageType:
    if "MIP" in filename:
        return ImageType.MIP
    elif ("Brightfield" in filename) or ("BF" in filename):
        return ImageType.BRIGHT_FIELD
    elif "Tomogram" in filename:
        return ImageType.HOLOTOMOGRAPHY


def is_project_in_database(database, project_name):
    return database.is_table(project_name)


def create_project_table(database, project_name):
    database.execute_sql_file("sql/create_each_project_table.sql", project_name)


def get_images(credentials: Credentials, project: Project) -> list[Image]:
    """
    [{'id': '1XYyxLOeXriq1u7a00Z79FfjMMFaeQkA_', 'name': '20220422.195937.460.CD4_2-007_RI MIP.tiff', 'mimeType': 'image/tiff'}]
    """
    images = []
    reader = GDriveReader(
        credentials, project.google_drive_folder_id, folder=True
    )
    for date_folder in reader.read():
        image_reader = GDriveReader(credentials, date_folder["id"], image=True)
        images.extend(
            Image(
                image["name"],
                image["id"],
                datetime.datetime.strptime(image["name"][:14], "%Y%m%d.%H%M%S"),
                parse_image_type(image["name"]),
                project,
            )
            for image in image_reader.read()
        )

    return images


def create_image_table(credentials, database: Database, project: Project):
    images = get_images(credentials, project)
    print(project.name)

    if not is_project_in_database(database, project.name):
        create_project_table(database, project.name)

    for image in images:
        image.insert_to_database(database)

    database.conn.commit()

    return images
