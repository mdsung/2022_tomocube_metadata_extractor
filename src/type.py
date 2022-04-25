import datetime
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Project:
    project_id: int
    project_name: str
    start_date: datetime.datetime


class ImageType(Enum):
    BRIGHT_FIELD = auto()
    MIP = auto()
    HOLOTOMOGRAPHY = auto()


@dataclass
class Image:
    image_id: int
    file_name: str
    google_drive_id: str
    shoot_datetime: datetime.datetime
    image_type: ImageType
    project_id: int


@dataclass
class ImageLabel:
    label_id: int
    status: str
    bright_field: int  # image_id
    mip: int  # image_id
    holotomography: int  # image_id
    cell_type: str
    quality: int
