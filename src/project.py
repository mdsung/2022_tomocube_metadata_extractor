from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.database import Database

# from src.gdrive import Credentials, GDriveReader
from src.s3 import S3Credential, get_s3_resource


@dataclass
class Project:
    name: str
    google_drive_folder_id: Optional[str] = None

    @classmethod
    def from_metadata(cls, d: dict[str, str]) -> Project:
        return cls(d["name"], d["id"])

    def insert_to_database(self, database: Database):
        logger = logging.getLogger()
        logger.info(f'Inserting project "{self.name}" to database')

        sql = f"""INSERT INTO project(name, google_drive_folder_id) 
        SELECT '{self.name}', '{self.google_drive_folder_id}' 
        FROM DUAL WHERE NOT EXISTS(
            SELECT * FROM project WHERE name = '{self.name}'
            )"""
        database.execute_sql(sql)


class Projects(ABC):
    @abstractmethod
    def get(self):
        ...


# class GdriveWorkingProjects(Projects):
#     def get(self, credentials: Credentials, raw_data_folder_id: str):
#         reader = GDriveReader(credentials, raw_data_folder_id, folder=True)
#         return {
#             Project.from_metadata(project)
#             for project in reader.read()
#             if "tomocube" in project["name"]
#         }


class S3WorkingProjects(Projects):
    def get(self, credentials: S3Credential):
        resource = get_s3_resource(credentials)
        return {
            bucket.name.replace("-", "_")
            for bucket in resource.buckets.all()
            if "tomocube" in bucket.name.replace("-", "_")
        }


class ExistingProjects(Projects):
    def get(self, database) -> set[str]:
        return {
            d["name"]  # type:ignore
            for d in database.execute_sql("SELECT name FROM project")
        }


class TargetProjects(Projects):
    def get(self, filename) -> set[str]:
        return set(open(filename).read().splitlines())


class FinalProjects(Projects):
    def get(
        self, working_projects: set[str], target_projects: set[str]
    ) -> set[str]:
        return working_projects.intersection(target_projects)


def create_project_table(database):
    database.execute_sql_file("sql/create_project_table.sql")


def create_new_project(projects: set[str]) -> None:
    database = Database()
    for project_name in projects:
        create_project_table(project_name)
        Project(project_name).insert_to_database(database)
    database.conn.commit()
