import mysql.connector
import os
import pandas as pd
def conectar():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        port=int(os.getenv("MYSQLPORT")),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE")
    )

#obtener usuarios
def obtenerusuarios(username):
    try:
        conn = conectar()
        if conn is None:
            return None

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE username=%s", (username,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario

    except Exception as e:
        print("Error obtenerusuarios:", e)
        return None
#obtener los estudiantes
def  obtenerestudiantes():
     conn = conectar()
     query = "SELECT * FROM estudiantes"
     df = pd.read_sql(query,conn)
     conn.close()

     return df

#registrar estudiante 
def insertar_estudiante(nombre,edad,carrera,nota1,nota2,nota3,promedio,desempeno):
     coon = conectar()
     cursor = coon.cursor()

     query = """INSERT INTO estudiantes(Nombre,Edad,Carrera,nota1,nota2,nota3,Promedio,Desempeño)values(%s,%s,%s,%s,%s,%s,%s,%s)"""
     cursor.execute(query,(nombre,edad,carrera,nota1,nota2,nota3,promedio,desempeno))
     
     coon.commit()
     coon.close()


if __name__ == "__main__":
    coon = conectar()
    print("Conexion exitosa")
    coon.close()