import datetime
from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class ImageLabel:
    label_id: int
    status: str
    bright_field: int  # image_id
    mip: int  # image_id
    holotomography: int  # image_id
    cell_type: str
    quality: int
