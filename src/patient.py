from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.database import Database
from src.project import Project
from src.s3 import S3Credential, S3FolderReader, get_s3_bucket
from src.type import CellType
from src.util import get_bucket_name_from_project_name


class Patients:
    def __init__(self, project_name: str) -> None:
        self.project_name = project_name

    @abstractmethod
    def get(self):
        ...


class ExistingPatients(Patients):
    def get(self) -> set[str]:
        database = Database()
        sql = f"""SELECT google_drive_parent_name name 
                FROM {self.project_name}_patient"""
        return {
            d["name"]  # type:ignore
            for d in database.execute_sql(sql)
        }


class WorkingPatients(Patients):
    def __init__(self, project_name: str, s3_credential: S3Credential) -> None:
        super().__init__(project_name)
        self.s3_credential = s3_credential

    def get(self) -> set[str]:
        bucket_name = get_bucket_name_from_project_name(self.project_name)
        bucket = get_s3_bucket(self.s3_credential, bucket_name)
        return set(S3FolderReader(bucket).read())


class NewPatients(Patients):
    def get(
        self, working_patients: set[str], existing_patients: set[str]
    ) -> set[str]:
        return working_patients - existing_patients


@dataclass
class Patient:
    google_parent_id: str
    project: Project
    google_drive_parent_name: Optional[str]

    def insert_to_database(
        self, project: Project, project_id: int, patient_id: int
    ):
        database = Database()
        sql = f"""INSERT INTO {self.project.name}_patient(google_drive_parent_id, project_id, google_drive_parent_name) 
                SELECT '{self.google_parent_id}', {project_id}, {self.google_drive_parent_name}
                WHERE NOT EXISTS(SELECT * FROM {self.project.name}_patient 
                WHERE google_drive_parent_id = '{self.google_parent_id}')"""
        database.execute_sql(sql)
        database.conn.close()


@dataclass
class Cell:
    cell_type: CellType
    cell_number: int
    patient: Patient
    project: Project

    def insert_to_database(
        self, project: Project, project_id: int, patient_id: int
    ):
        database = Database()
        try:
            sql = f"""INSERT INTO {project.name}_cell(cell_type, cell_number, patient_id) 
                SELECT '{self.cell_type.name}', {self.cell_number}, {patient_id} 
                WHERE NOT EXISTS(
                    SELECT * 
                    FROM {project.name}_cell 
                    WHERE cell_type = '{self.cell_type.name}' 
                    AND cell_number = {self.cell_number} 
                    AND patient_id = {patient_id})"""
            database.execute_sql(sql)
        except AttributeError as e:
            print(self)
            raise AttributeError(e) from e
        database.conn.close()
