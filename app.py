from flask import Flask,render_template,request,redirect,session
from database import conectar
from database import obtenerusuarios
from database import insertar_estudiante
from dashprincipal import creartablero
import pandas as pd
import unicodedata
import mysql.connector


app = Flask(__name__)
server = app 
# CLAVE NECESARIA PARA USAR SESSION

app.secret_key = "40414732"

# crear dashboard
creartablero(app)

#evitar cache  en paginas protegidas
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache ,must-revalidate , max-age=0"
    response.headers["Pragma"]= "no-cache"
    response.headers["Expires"] = "0"

    return response

@app.route("/",methods=["GET","POST"])
def login():

    #verificar si el formulario fue enviado
    if request.method == "POST":
        #capturar los datos del formulario

        username = request.form["username"]
        password = request.form["password"]

        usuario = obtenerusuarios(username)

        #verificar si existe
        if usuario:

          if usuario["password"] == password:

              #creo la sesion del usuario
              session["username"] = usuario["username"]
              session["rol"] = usuario["rol"]

              return redirect("/dashprincipal")
          else:
              return "Contraseña incorrecta"
        else:
             return "Usuario no existe"

    return  render_template("login.html")
@app.route("/dashprincipal")
def dashprinci():
    if "username"  not in session:
        return redirect("/")

    return render_template("dashprinci.html", usuario=session["username"])

@app.route("/logout")
def logout():
   session.clear()
   return redirect("/")


@app.route("/registro_estudiante", methods=["GET","POST"])
def registroestudiante():
    if "username" not in session:
        return ("/")

    if request.method == "POST":

        nombre = request.form["txtnombre"]
        edad = request.form["txtedad"]
        carrera = request.form["txtcarrera"]
        notauno = float(request.form["txtnota1"])
        notados = float(request.form["txtnota2"])
        notatres = float(request.form["txtnota3"])
        #calcular el promedio
        promedio = round((notauno+notados+notatres)/ 3,2)


        #calcular el desempeño
        desempeno = calculardesempeño(promedio)

        #llamar la conexion
       # conn = conectar()
        #cursor =conn.cursor()

        insertar_estudiante(nombre,edad,carrera,notauno,notados,notatres,promedio,desempeno)

        return redirect("/dashprincipal")
    
    return  render_template("registro_estudiante.html")

#funcion para quitar acentos
def quitar(texto):
    if pd.isna(texto):
        return texto


    texto = str(texto)

    return ''.join(
            c for  c in unicodedata.normalize('NFD',texto)
            if unicodedata.category(c) != 'Mn'
        )

#clasificar el desempeño
def calculardesempeño(prom):
    if prom >=4.5:
            return "Excelente"
    elif prom >=4:
            return "Bueno"
    elif prom >=3:
            return "Regular"
    else:
            return "Bajo"


@app.route("/cargamasiva", methods=["GET","POST"])
def carga_masiva():
    if request.method == "POST":

       archivo = request.files["txtarchivo"]

       #leer archivo
       df = pd.read_excel(archivo)

       #limpiar nombres
       df["Nombre"] = df["Nombre"].astype(str).str.strip()#quitas espacio vacios
       df["Nombre"] = df["Nombre"].apply(quitar)#llamar la funcion de quitar acentos
       df["Nombre"]  = df["Nombre"].str.title()#1 es mayuscula

       #limpiar
       df["Carrera"] = df["Carrera"].astype(str).str.strip()#quitas espacio vacios
       df["Carrera"] = df["Carrera"].apply(quitar)#llamar la funcion de quitar acentos
       df["Carrera"]  = df["Carrera"].str.title()#1 es mayuscula


       #eliminar edades negativa
       df= df[df["Edad"]>=0]

       #validar las notas entre 0 y 5

       df = df[(df["Nota1"]>=0)&(df["Nota1"]<=5)&
               (df["Nota2"]>=0)&(df["Nota2"]<=5)&
               (df["Nota3"]>=0)&(df["Nota3"]<=5)
               ]
       #calcular el promedio
       df["Promedio"] = (df["Nota1"]+ df["Nota2"] + df["Nota3"]) / 3
       df["Promedio"] = df["Promedio"].round(2)

       #eliminar los promedios mayores a 5
       df = df[df["Promedio"] <= 5]

       #calcular desempeño
       df["Desempeño"] = df["Promedio"].apply(calculardesempeño)

       #eliminar duplicados
       df = df.drop_duplicates(subset=["Nombre","Carrera"])

       #insertar en la base de datos
       conn = conectar()
       cursor = conn.cursor()


       query = """INSERT INTO estudiantes(Nombre,Edad,Carrera,nota1,nota2,nota3,Promedio,Desempeño) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"""
       for _, row in df.iterrows():
            cursor.execute(query,(
                 row["Nombre"],
                 row["Edad"],
                 row["Carrera"],
                 row["Nota1"],
                 row["Nota2"],
                 row["Nota3"],
                 row["Promedio"],
                 row["Desempeño"]


            ))
       conn.commit()
       conn.close()

       #flash(f"Cargue exitoso. Se insertaron {len(df)} estudiantes")
       return redirect("/dashprincipal")
    return render_template("carga_masiva.html")
@app.route("/test-db")
def test_db():
    try:
        conn = conectar()
        return "Conexión exitosa 🚀"
    except Exception as e:
        return str(e)


if __name__ == "__main__":
    app.run(debug=True)