
from db_config import get_db_connection
from flask import Flask, request, jsonify
class Venta:
    def __init__(self):
        pass

    def agregar_venta(self, id_producto, cantidad_vendida, total_venta, id_usuario):
        """Agrega una nueva venta a la base de datos."""
        db = get_db_connection()
        cursor = db.cursor()

        query = '''
            INSERT INTO ventas (id_producto, cantidad_vendida, total_venta, id_usuario)
            VALUES (%s, %s, %s, %s)
        '''

        cursor.execute(query, (id_producto, cantidad_vendida, total_venta, id_usuario))
        db.commit()  # Confirmar cambios en la base de datos
        cursor.close()  # Cerrar el cursor
        db.close()  # Cerrar la conexión a la base de datos

    def obtener_ventas(self):
        """Obtiene todas las ventas de la base de datos."""
        db = get_db_connection()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM ventas')
        rows = cursor.fetchall()

        ventas = []
        column_names = [desc[0] for desc in cursor.description]
        for row in rows:
            ventas.append(dict(zip(column_names, row)))

        cursor.close()
        db.close()
        return ventas
