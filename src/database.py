import os

import pymysql
from dotenv import load_dotenv

load_dotenv()

MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_PORT = int(os.getenv("MYSQL_PORT"))
MYSQL_DB = os.getenv("MYSQL_DB")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD")
MYSQL_CHARSET = os.getenv("MYSQL_CHARSET")


class Database:
    def __init__(
        self,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        db=MYSQL_DB,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset=MYSQL_CHARSET,
    ):
        self.conn = self.create_connection(
            host, port, db, user, password, charset
        )
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def create_connection(self, host, port, db, user, password, charset):
        return pymysql.connect(
            host=host,
            port=port,
            db=db,
            user=user,
            password=password,
            charset=charset,
            connect_timeout=1000,
        )  # type: ignore

    def execute_sql(self, sql: str):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def is_table(self, table_name: str):
        sql = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = '{table_name}';"
        return self.execute_sql(sql)[0]["COUNT(*)"] > 0  # type: ignore

    def execute_sql_file(self, sql_file, project_name=None):
        with open(sql_file, "r") as f:
            sql = f.read()

        sql_commands = sql.split(";")

        for command in sql_commands:
            if command.strip() == "":
                continue
            if project_name is not None:
                command = command.replace("table_name", project_name)
            self.execute_sql(command)

        self.conn.commit()


if __name__ == "__main__":
    database = Database(
        MYSQL_HOST,
        MYSQL_PORT,
        MYSQL_DB,
        MYSQL_USER,
        MYSQL_PASSWORD,
        MYSQL_CHARSET,
    )
    database.execute_sql("SHOW TABLES;")
