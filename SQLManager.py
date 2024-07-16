import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

class SQLManager:
    def __init__(self):
        self.host = os.getenv("HOST")
        self.user = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.database = os.getenv("DATABASE")
        self.table = os.getenv("TABLE")
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            self.cursor = self.connection.cursor()
            # print("Connected to MySQL database!")

        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")

    def execute_and_commit_query(self, query, values=None):
        try:
            if values:
                self.cursor.execute(query, values)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            return 1

        except mysql.connector.Error:
            self.connection.rollback()
            return 0

    def fetch_all(self, query, values=None):
        """Executes a query and returns the fetched data."""
        if values:
                self.cursor.execute(query, values)
        else:
            self.cursor.execute(query)
        return self.cursor.fetchall()

    def close_connection(self):
        if self.connection:
            self.cursor.close()
            self.connection.close()
            # print("Connection closed!")

    def create_table(self):
        try:
            print('verificando tabla')
            # verificamos si la tabla existe
            self.cursor.execute(
               f"""
                SELECT
                    count(TABLE_NAME) as count
                    FROM
                    information_schema.TABLES
                    WHERE TABLE_NAME = "{self.table}"
                """
            )
            exists = self.cursor.fetchone()[0]
            self.cursor.reset()
            if exists == 0:
                try:  # Crear tabla
                    print("Creando tabla")
                    self.cursor.execute(
                        f"""
                        CREATE TABLE {self.table} (
                            isbn VARCHAR(20) NOT NULL,
                            nombre TEXT,
                            fecha_publicacion DATE,
                            editorial TEXT,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            PRIMARY KEY(isbn)
                        );
                        """
                    )
                except Exception as e:
                    print(e)
        except Exception as e:
            print(e)