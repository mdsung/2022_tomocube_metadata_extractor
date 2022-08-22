import logging
from dataclasses import dataclass

from src.database import Database
from src.patient import Patient
from src.type import CellType

logger = logging.getLogger()


@dataclass
class Cell:
    cell_type: CellType
    cell_number: int
    patient: Patient
    project: str

    def insert_to_database(self, project_name: str, patient_id: int):
        logger.info(
            f"Inserting Cell to database - {project_name}|{self.patient.google_drive_parent_name}|{self.cell_type.name}|{self.cell_number}"
        )

        sql = f"""INSERT INTO {project_name}_cell(cell_type, cell_number, patient_id) 
            SELECT '{self.cell_type.name}', {self.cell_number}, {patient_id} FROM DUAL
            WHERE NOT EXISTS(
                SELECT * 
                FROM {project_name}_cell 
                WHERE cell_type = '{self.cell_type.name}' 
                AND cell_number = {self.cell_number} 
                AND patient_id = {patient_id})"""
        Database().execute_sql(sql)
