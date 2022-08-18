from dataclasses import dataclass
from typing import Optional

from src.database import Database
from src.project import Project
from src.type import CellType


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
