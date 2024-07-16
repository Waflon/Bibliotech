from SQLManager import SQLManager

db = SQLManager()

class CRUD :
    def __init__(self):
        self.db_manager = SQLManager()
    def nueva_entrada(self, isbn, nombre, fecha_publicacion, editorial):
        self.db_manager.connect()
        self.cursor = self.db_manager.cursor
        print(self.cursor)
        sql = f"INSERT INTO {self.db_manager.table} (isbn, nombre, fecha_publicacion, editorial) VALUES (%s, %s, %s, %s)"
        val = (isbn, nombre, fecha_publicacion, editorial)
        result = self.cursor.execute(sql, val)
        self.db_manager.connection.commit()

        if result == 1:
            return {"status": 200}
        return {"status": 500}