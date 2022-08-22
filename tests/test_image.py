import pytest
from src.image import (
    CELL_TYPE_DICT,
    CellType,
    parse_cell_number,
    parse_cell_type,
)


def test_cell_type_dict():
    assert CELL_TYPE_DICT["CD4"] == CellType.CD4
    assert CELL_TYPE_DICT["CD8"] == CellType.CD8
    assert CELL_TYPE_DICT["cd4"] == CellType.CD4
    assert CELL_TYPE_DICT["cd8"] == CellType.CD8


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("20220422.194719.911.CD4_2-004_RI MIP.tiff", "CD4"),
        ("20220422.183553.770.monocyte_2-040_Brightfield.tiff", "monocyte"),
        ("20220425.134542.163.CD4-018_RI Tomogram.tiff", "CD4"),
        ("20220425.130529.035.CD8-052_RI Tomogram.tiff", "CD8"),
    ],
)
def test_parse_cell_type(filename, expected):
    print(parse_cell_type(filename))
    assert parse_cell_type(filename).name == expected


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("20220422.194719.911.CD4_2-004_RI MIP.tiff", 4),
        ("20220422.183553.770.monocyte_2-040_Brightfield.tiff", 40),
        ("20220425.134542.163.CD4-018_RI Tomogram.tiff", 18),
        ("20220425.130529.035.CD8-052_RI Tomogram.tiff", 52),
    ],
)
def test_parse_cell_number(filename, expected):
    assert parse_cell_number(filename) == expected
