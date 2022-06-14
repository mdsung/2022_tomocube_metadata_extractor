from enum import Enum, auto


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


IMAGE_TYPE_DICT = {
    "MIP": ImageType.MIP,
    "Brightfield": ImageType.BRIGHT_FIELD,
    "BF": ImageType.BRIGHT_FIELD,
    "Tomogram": ImageType.HOLOTOMOGRAPHY,
}


CELL_TYPE_DICT = (
    {
        "default": CellType.WBC,
        "buffycoat": CellType.WBC,
        "buffycoatlysis": CellType.WBC,
        "mono_negative": CellType.PBMC,
    }
    | {e.name: e for e in CellType}
    | {e.name.lower(): e for e in CellType}
)
