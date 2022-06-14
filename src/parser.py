import datetime
import re

from src.database import Database
from src.project import Project
from src.type import CELL_TYPE_DICT, IMAGE_TYPE_DICT, CellType, ImageType


def find_project_id(project: Project) -> int:
    database = Database()
    sql = f"SELECT project_id FROM project WHERE name = '{project.name}'"
    result = database.execute_sql(sql)[0]["project_id"]  # type:ignore
    database.conn.close()
    return result


def find_patient_id(project: Project, google_parent_id: str) -> int:
    database = Database()
    sql = f"SELECT patient_id FROM {project.name}_patient WHERE google_drive_parent_id = '{google_parent_id}'"
    result = database.execute_sql(sql)[0]["patient_id"]  # type:ignore
    database.conn.close()
    return result


def parse_shoot_time(filename: str) -> datetime.datetime:
    return datetime.datetime.strptime(filename[:14], "%Y%m%d.%H%M%S")


def parse_image_type(
    filename: str, image_type_dict: dict[str, ImageType] = IMAGE_TYPE_DICT
) -> ImageType:
    for key, value in image_type_dict.items():
        if key in filename:
            return value
    raise ValueError(f"{filename} is not a valid image type")


def parse_cell_type(
    file_name: str, cell_type_dict: dict[str, CellType] = CELL_TYPE_DICT
) -> CellType:
    cell_type_str = file_name[20:].split("-")[0].lower()
    for key, value in cell_type_dict.items():
        if key in cell_type_str:
            return value
    raise ValueError(f"{cell_type_str} is not a valid cell type")


def parse_cell_number(file_name: str) -> int:
    return int(re.findall("[0-9]{3}", file_name.split(".")[3])[0])
