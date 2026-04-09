import mysql.connector
import os
import pandas as pd
def conectar():
    try:
        conexion = mysql.connector.connect(
            host=os.getenv("MYSQLHOST") or "maglev.proxy.rlwy.net",
            port=int(os.getenv("MYSQLPORT") or 31545),
            user=os.getenv("MYSQLUSER") or "root",
            password=os.getenv("MYSQLPASSWORD") or "MNHUmsbIpnxZJTYNvyuRSqgQwaOeWTDt",
            database=os.getenv("MYSQLDATABASE") or "railway"
        )
        return conexion
    except Exception as e:
        print("Error de conexión:", e)
        return None

#obtener usuarios
def  obtenerusuarios(username):
     #conectar a la base bd
        conn = conectar()
        cursor = conn.cursor(dictionary=True)
        #buscar el usuario en la bd
        cursor.execute("SELECT * FROM usuarios WHERE username=%s",(username,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario
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