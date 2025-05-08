# db_config.py
import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',  # Tu usuario de MySQL
        password='',  # Tu contraseña de MySQL
        database='ferreteria'  # Nombre de tu base de datos
    )
    return connection
