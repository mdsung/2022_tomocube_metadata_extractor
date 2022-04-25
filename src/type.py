import datetime
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class Folder:
    id_: str
    name: str

    @classmethod
    def from_dict(cls, d):
        if d["mimeType"] != "application/vnd.google-apps.folder":
            return None
        return cls(d["id"], d["name"])



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
