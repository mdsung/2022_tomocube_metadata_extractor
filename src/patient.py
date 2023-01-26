import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from src.database import Database
from src.s3 import S3Credential, S3FolderReader, get_s3_bucket
from src.util import get_bucket_name_from_project_name

logger = logging.getLogger()


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
        return (
            working_patients
            - existing_patients
            - {
                "processed",
            }
        )


@dataclass
class Patient:
    project_name: str
    google_drive_parent_name: str
    google_parent_id: Optional[str] = None

    def insert_to_database(self, project_id: int):
        logger.info(
            f"Inserting patient {self.google_drive_parent_name} to database"
        )

        sql = f"""INSERT INTO {self.project_name}_patient(
                    project_id, 
                    google_drive_parent_id,
                    google_drive_parent_name
                ) 
                SELECT {project_id}, NULL, '{self.google_drive_parent_name}' FROM DUAL
                WHERE NOT EXISTS(
                    SELECT * 
                    FROM {self.project_name}_patient 
                    WHERE google_drive_parent_name = '{self.google_drive_parent_name}')
                """
        Database().execute_sql(sql)
