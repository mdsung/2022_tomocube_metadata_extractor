import datetime
from dataclasses import dataclass
from enum import Enum, auto

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
    project_name: str


def parse_image_type(filename: str) -> ImageType:
    if "MIP" in filename:
        return ImageType.MIP
    elif "Brightfield" in filename:
        return ImageType.BRIGHT_FIELD
    elif "Tomogram" in filename:
        return ImageType.HOLOTOMOGRAPHY


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
                project.name,
            )
            for image in image_reader.read()
        )

        break
    return images
