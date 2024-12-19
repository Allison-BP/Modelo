import mysql.connector
from mysql.connector import Error
import os

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password=os.environ['DB_PASSWORD'],
            database=os.environ['DB']
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None