from dataclasses import dataclass

from src.database import Database
from src.gdrive import Credentials, GDriveReader


@dataclass
class Project:
    google_drive_folder_id: str
    name: str

    @classmethod
    def from_metadata(cls, d):
        return cls(d["id"], d["name"])

    def insert_to_database(self, database: Database):
        sql = f"INSERT INTO project(name, google_drive_folder_id) SELECT '{self.name}', '{self.google_drive_folder_id}' FROM DUAL WHERE NOT EXISTS(SELECT * FROM project WHERE name = '{self.name}')"
        database.execute_sql(sql)


def get_projects(
    credentials: Credentials, raw_data_folder_id: str
) -> list[Project]:
    reader = GDriveReader(credentials, raw_data_folder_id, folder=True)
    return [
        Project.from_metadata(project)
        for project in reader.read()
        if "tomocube" in project["name"]
    ]


def is_project_in_database(database):
    return database.is_table("project")


def create_project_table(database):
    database.execute_sql_file("sql/create_project_list_table.sql")


def create_project_database(credentials, database, folder_raw_data_id):
    tomocube_projects = get_projects(credentials, folder_raw_data_id)

    if not is_project_in_database(database):
        create_project_table(database)

    projects = []
    for project in tomocube_projects:
        project.insert_to_database(database)
        projects.append(project)
    database.conn.commit()

    return projects
