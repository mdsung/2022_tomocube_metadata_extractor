from dataclasses import dataclass

from src.gdrive import Credentials, GDriveReader


@dataclass
class Project:
    google_drive_folder_id: str
    name: str

    @classmethod
    def from_metadata(cls, d):
        return cls(d["id"], d["name"])


def get_tomocube_projects(
    credentials: Credentials, raw_data_folder_id: str
) -> list[Project]:
    reader = GDriveReader(credentials, raw_data_folder_id, folder=True)
    return [
        Project.from_metadata(project)
        for project in reader.read()
        if "tomocube" in project["name"]
    ]
