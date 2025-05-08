# movimiento.py
from db_config import get_db_connection

class Movimiento:
    def registrar(self, id_producto, tipo, cantidad, usuario):
        db = get_db_connection()
        cursor = db.cursor()
        query = '''
            INSERT INTO movimientos_stock (id_producto, tipo_movimiento, cantidad, usuario)
            VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(query, (id_producto, tipo, cantidad, usuario))
        db.commit()
        cursor.close()
        db.close()
