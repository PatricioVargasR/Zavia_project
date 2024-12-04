from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from hashlib import sha256
from typing import List, Optional

# Crear la conexión a la base de datos SQLite
DATABASE_URL = "sqlite:///./zabia.db"


# Crear la aplicación FastAPI
app = FastAPI()

# Modelos Pydantic
class Login(BaseModel):
    email: str
    contraseña: str

# Modelos Pydantic para la creación de usuarios
class Signup(BaseModel):
    id_role: int
    contraseña: str
    nombre: str
    apellidos: str
    edad: int
    email: str
    
class Curso(BaseModel):
    id_profesor: int
    contenido_explicacion: str

class CursoAlumno(BaseModel):
    id_curso: int
    id_alumno: int

class Pregunta(BaseModel):
    texto_pregunta: str
    tipo_contenido: str  # 'test' o 'ejercicio'

class Respuesta(BaseModel):
    id_pregunta: int
    texto_respuesta: str
    es_correcta: int  # 0 o 1

class Test(BaseModel):
    id_curso: int

class Ejercicio(BaseModel):
    id_curso: int

class Recurso(BaseModel):
    id_contenido: int
    tipo_contenido: str  # 'curso', 'test', 'ejercicio'
    id_curso: int


# Función para obtener la conexión de la base de datos
def get_db_connection():
    conn = sqlite3.connect("zabia.db")
    return conn

@app.post("/login")
def login(login_data: Login):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Buscar el usuario por email
    cursor.execute("SELECT * FROM Usuarios WHERE email = ?", (login_data.email,))
    usuario = cursor.fetchone()
    
    conn.close()
    
    # Verificar si el usuario existe
    if usuario is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    # Comparar la contraseña encriptada
    stored_password = usuario[2]  # La contraseña en la base de datos (encriptada)
    hashed_password = sha256(login_data.contraseña.encode('utf-8')).hexdigest()

    if stored_password != hashed_password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")
    
    return {"message": "Login exitoso"}

@app.post("/signup/")
def signup(user_data: Signup):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si el email ya está registrado
    cursor.execute("SELECT * FROM Usuarios WHERE email = ?", (user_data.email,))
    existing_user = cursor.fetchone()

    if existing_user:
        conn.close()
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    # Encriptar la contraseña (usando sha256 en este ejemplo, pero es preferible usar bcrypt en producción)
    hashed_password = sha256(user_data.contraseña.encode('utf-8')).hexdigest()

    # Insertar los nuevos datos del usuario en la tabla Usuarios
    cursor.execute('''
        INSERT INTO Usuarios (id_role, contraseña, nombre, apellidos, edad, email)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_data.id_role, hashed_password, user_data.nombre, user_data.apellidos, user_data.edad, user_data.email))

    # Obtener el id_usuario del nuevo registro
    user_id = cursor.lastrowid

    # Dependiendo del rol, insertar en la tabla Profesores o Alumnos
    if user_data.id_role == 1:  # Si el rol es 1 (por ejemplo, profesor)
        cursor.execute('''
            INSERT INTO Profesores (id_profesor)
            VALUES (?)
        ''', (user_id,))
    elif user_data.id_role == 2:  # Si el rol es 2 (por ejemplo, alumno)
        cursor.execute('''
            INSERT INTO Alumnos (id_alumno)
            VALUES (?)
        ''', (user_id,))
    
    conn.commit()
    conn.close()

    return {"message": "Usuario registrado exitosamente"}



# Endpoint para obtener todos los cursos
@app.get("/cursos", response_model=List[dict])
def get_cursos():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Cursos")
    cursos = cursor.fetchall()
    
    conn.close()
    
    return [{"id_curso": curso[0], "id_profesor": curso[1], "fecha_creacion": curso[2], "contenido_explicacion": curso[3]} for curso in cursos]

# Endpoint para obtener un curso específico por ID
@app.get("/curso/{curso_id}", response_model=dict)
def get_curso(curso_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = ?", (curso_id,))
    curso = cursor.fetchone()
    
    conn.close()
    
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    return {"id_curso": curso[0], "id_profesor": curso[1], "fecha_creacion": curso[2], "contenido_explicacion": curso[3]}

# Endpoint para crear un nuevo curso
@app.post("/cursos", response_model=dict)
def create_curso(curso: Curso):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Insertar el nuevo curso
    cursor.execute(
        "INSERT INTO Cursos (id_profesor, contenido_explicacion) VALUES (?, ?)",
        (curso.id_profesor, curso.contenido_explicacion)
    )
    
    curso_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_curso": curso_id, "id_profesor": curso.id_profesor, "contenido_explicacion": curso.contenido_explicacion}

# Endpoint para actualizar un curso
@app.put("/curso/{curso_id}", response_model=dict)
def update_curso(curso_id: int, curso: Curso):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si el curso existe
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = ?", (curso_id,))
    existing_curso = cursor.fetchone()
    
    if existing_curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Actualizar el curso
    cursor.execute(
        "UPDATE Cursos SET id_profesor = ?, contenido_explicacion = ? WHERE id_curso = ?",
        (curso.id_profesor, curso.contenido_explicacion, curso_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"id_curso": curso_id, "id_profesor": curso.id_profesor, "contenido_explicacion": curso.contenido_explicacion}

# Endpoint para eliminar un curso
@app.delete("/curso/{curso_id}")
def delete_curso(curso_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si el curso existe
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = ?", (curso_id,))
    existing_curso = cursor.fetchone()
    
    if existing_curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Eliminar el curso
    cursor.execute("DELETE FROM Cursos WHERE id_curso = ?", (curso_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Curso eliminado con éxito"}

# Endpoint para asignar un alumno a un curso (POST)
@app.post("/curso/{curso_id}/alumno")
def asignar_alumno(curso_id: int, alumno: CursoAlumno):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si el curso existe
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = ?", (curso_id,))
    curso = cursor.fetchone()
    
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Verificar si el alumno existe
    cursor.execute("SELECT * FROM Alumnos WHERE id_alumno = ?", (alumno.id_alumno,))
    alumno_existente = cursor.fetchone()
    
    if alumno_existente is None:
        raise HTTPException(status_code=404, detail="Alumno no encontrado")
    
    # Asignar el alumno al curso
    cursor.execute(
        "INSERT INTO Cursos_Alumnos (id_curso, id_alumno) VALUES (?, ?)",
        (curso_id, alumno.id_alumno)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": f"Alumno {alumno.id_alumno} asignado al curso {curso_id}"}

# Endpoint para eliminar un alumno de un curso
@app.delete("/curso/{curso_id}/alumno/{alumno_id}")
def eliminar_alumno(curso_id: int, alumno_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Verificar si el curso existe
    cursor.execute("SELECT * FROM Cursos WHERE id_curso = ?", (curso_id,))
    curso = cursor.fetchone()
    
    if curso is None:
        raise HTTPException(status_code=404, detail="Curso no encontrado")
    
    # Verificar si el alumno está asignado al curso
    cursor.execute(
        "SELECT * FROM Cursos_Alumnos WHERE id_curso = ? AND id_alumno = ?",
        (curso_id, alumno_id)
    )
    asignacion = cursor.fetchone()
    
    if asignacion is None:
        raise HTTPException(status_code=404, detail="El alumno no está asignado a este curso")
    
    # Eliminar la asignación del alumno
    cursor.execute(
        "DELETE FROM Cursos_Alumnos WHERE id_curso = ? AND id_alumno = ?",
        (curso_id, alumno_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": f"Alumno {alumno_id} eliminado del curso {curso_id}"}




@app.get("/preguntas", response_model=List[dict])
def get_preguntas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Preguntas")
    preguntas = cursor.fetchall()
    
    conn.close()
    
    return [{"id_pregunta": pregunta[0], "texto_pregunta": pregunta[1], "tipo_contenido": pregunta[2]} for pregunta in preguntas]

@app.get("/pregunta/{pregunta_id}", response_model=dict)
def get_pregunta(pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    pregunta = cursor.fetchone()
    
    conn.close()
    
    if pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    return {"id_pregunta": pregunta[0], "texto_pregunta": pregunta[1], "tipo_contenido": pregunta[2]}

@app.post("/preguntas", response_model=dict)
def create_pregunta(pregunta: Pregunta):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO Preguntas (texto_pregunta, tipo_contenido) VALUES (?, ?)",
        (pregunta.texto_pregunta, pregunta.tipo_contenido)
    )
    
    pregunta_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_pregunta": pregunta_id, "texto_pregunta": pregunta.texto_pregunta, "tipo_contenido": pregunta.tipo_contenido}

@app.put("/pregunta/{pregunta_id}", response_model=dict)
def update_pregunta(pregunta_id: int, pregunta: Pregunta):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    existing_pregunta = cursor.fetchone()
    
    if existing_pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    cursor.execute(
        "UPDATE Preguntas SET texto_pregunta = ?, tipo_contenido = ? WHERE id_pregunta = ?",
        (pregunta.texto_pregunta, pregunta.tipo_contenido, pregunta_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"id_pregunta": pregunta_id, "texto_pregunta": pregunta.texto_pregunta, "tipo_contenido": pregunta.tipo_contenido}

@app.delete("/pregunta/{pregunta_id}")
def delete_pregunta(pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    existing_pregunta = cursor.fetchone()
    
    if existing_pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    cursor.execute("DELETE FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Pregunta eliminada con éxito"}


@app.post("/test/{test_id}/pregunta/{pregunta_id}", response_model=dict)
def asignar_pregunta_a_test(test_id: int, pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Tests WHERE id_test = ?", (test_id,))
    test = cursor.fetchone()
    if test is None:
        raise HTTPException(status_code=404, detail="Test no encontrado")
    
    cursor.execute("SELECT * FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    pregunta = cursor.fetchone()
    if pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    cursor.execute(
        "INSERT INTO Tests_Preguntas (id_test, id_pregunta) VALUES (?, ?)",
        (test_id, pregunta_id)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Pregunta asignada al test correctamente", "id_test": test_id, "id_pregunta": pregunta_id}

# Eliminar una relación entre una pregunta y un test
@app.delete("/test/{test_id}/pregunta/{pregunta_id}")
def eliminar_pregunta_de_test(test_id: int, pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Tests_Preguntas WHERE id_test = ? AND id_pregunta = ?", (test_id, pregunta_id))
    test_pregunta = cursor.fetchone()
    if test_pregunta is None:
        raise HTTPException(status_code=404, detail="Relación entre test y pregunta no encontrada")
    
    cursor.execute("DELETE FROM Tests_Preguntas WHERE id_test = ? AND id_pregunta = ?", (test_id, pregunta_id))
    conn.commit()
    conn.close()
    
    return {"message": "Relación eliminada correctamente entre test y pregunta"}

# Obtener todas las preguntas asociadas a un test
@app.get("/test/{test_id}/preguntas", response_model=List[dict])
def obtener_preguntas_de_test(test_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Preguntas.* FROM Preguntas INNER JOIN Tests_Preguntas ON Preguntas.id_pregunta = Tests_Preguntas.id_pregunta WHERE Tests_Preguntas.id_test = ?", (test_id,))
    preguntas = cursor.fetchall()
    
    conn.close()
    
    return [{"id_pregunta": pregunta[0], "texto_pregunta": pregunta[1], "tipo_contenido": pregunta[2]} for pregunta in preguntas]


# Asignar una pregunta a un ejercicio
@app.post("/ejercicio/{ejercicio_id}/pregunta/{pregunta_id}", response_model=dict)
def asignar_pregunta_a_ejercicio(ejercicio_id: int, pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Ejercicios WHERE id_ejercicio = ?", (ejercicio_id,))
    ejercicio = cursor.fetchone()
    if ejercicio is None:
        raise HTTPException(status_code=404, detail="Ejercicio no encontrado")
    
    cursor.execute("SELECT * FROM Preguntas WHERE id_pregunta = ?", (pregunta_id,))
    pregunta = cursor.fetchone()
    if pregunta is None:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    cursor.execute(
        "INSERT INTO Ejercicios_Preguntas (id_ejercicio, id_pregunta) VALUES (?, ?)",
        (ejercicio_id, pregunta_id)
    )
    conn.commit()
    conn.close()
    
    return {"message": "Pregunta asignada al ejercicio correctamente", "id_ejercicio": ejercicio_id, "id_pregunta": pregunta_id}

# Eliminar una relación entre una pregunta y un ejercicio
@app.delete("/ejercicio/{ejercicio_id}/pregunta/{pregunta_id}")
def eliminar_pregunta_de_ejercicio(ejercicio_id: int, pregunta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Ejercicios_Preguntas WHERE id_ejercicio = ? AND id_pregunta = ?", (ejercicio_id, pregunta_id))
    ejercicio_pregunta = cursor.fetchone()
    if ejercicio_pregunta is None:
        raise HTTPException(status_code=404, detail="Relación entre ejercicio y pregunta no encontrada")
    
    cursor.execute("DELETE FROM Ejercicios_Preguntas WHERE id_ejercicio = ? AND id_pregunta = ?", (ejercicio_id, pregunta_id))
    conn.commit()
    conn.close()
    
    return {"message": "Relación eliminada correctamente entre ejercicio y pregunta"}

# Obtener todas las preguntas asociadas a un ejercicio
@app.get("/ejercicio/{ejercicio_id}/preguntas", response_model=List[dict])
def obtener_preguntas_de_ejercicio(ejercicio_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT Preguntas.* FROM Preguntas INNER JOIN Ejercicios_Preguntas ON Preguntas.id_pregunta = Ejercicios_Preguntas.id_pregunta WHERE Ejercicios_Preguntas.id_ejercicio = ?", (ejercicio_id,))
    preguntas = cursor.fetchall()
    
    conn.close()
    
    return [{"id_pregunta": pregunta[0], "texto_pregunta": pregunta[1], "tipo_contenido": pregunta[2]} for pregunta in preguntas]


@app.get("/respuestas", response_model=List[dict])
def get_respuestas():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Respuestas")
    respuestas = cursor.fetchall()
    
    conn.close()
    
    return [{"id_respuesta": respuesta[0], "id_pregunta": respuesta[1], "texto_respuesta": respuesta[2], "es_correcta": respuesta[3]} for respuesta in respuestas]

@app.get("/respuesta/{respuesta_id}", response_model=dict)
def get_respuesta(respuesta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Respuestas WHERE id_respuesta = ?", (respuesta_id,))
    respuesta = cursor.fetchone()
    
    conn.close()
    
    if respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    
    return {"id_respuesta": respuesta[0], "id_pregunta": respuesta[1], "texto_respuesta": respuesta[2], "es_correcta": respuesta[3]}

@app.post("/respuestas", response_model=dict)
def create_respuesta(respuesta: Respuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO Respuestas (id_pregunta, texto_respuesta, es_correcta) VALUES (?, ?, ?)",
        (respuesta.id_pregunta, respuesta.texto_respuesta, respuesta.es_correcta)
    )
    
    respuesta_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_respuesta": respuesta_id, "id_pregunta": respuesta.id_pregunta, "texto_respuesta": respuesta.texto_respuesta, "es_correcta": respuesta.es_correcta}

@app.put("/respuesta/{respuesta_id}", response_model=dict)
def update_respuesta(respuesta_id: int, respuesta: Respuesta):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Respuestas WHERE id_respuesta = ?", (respuesta_id,))
    existing_respuesta = cursor.fetchone()
    
    if existing_respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    
    cursor.execute(
        "UPDATE Respuestas SET texto_respuesta = ?, es_correcta = ? WHERE id_respuesta = ?",
        (respuesta.texto_respuesta, respuesta.es_correcta, respuesta_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"id_respuesta": respuesta_id, "id_pregunta": respuesta.id_pregunta, "texto_respuesta": respuesta.texto_respuesta, "es_correcta": respuesta.es_correcta}

@app.delete("/respuesta/{respuesta_id}")
def delete_respuesta(respuesta_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM Respuestas WHERE id_respuesta = ?", (respuesta_id,))
    existing_respuesta = cursor.fetchone()
    
    if existing_respuesta is None:
        raise HTTPException(status_code=404, detail="Respuesta no encontrada")
    
    cursor.execute("DELETE FROM Respuestas WHERE id_respuesta = ?", (respuesta_id,))
    
    conn.commit()
    conn.close()
    
    return {"message": "Respuesta eliminada con éxito"}

# --- ENDPOINTS: TESTS Y EJERCICIOS ---

@app.post("/tests", response_model=dict)
def create_test(test: Test):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO Tests (id_curso) VALUES (?)",
        (test.id_curso,)
    )
    
    test_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_test": test_id, "id_curso": test.id_curso}

@app.post("/ejercicios", response_model=dict)
def create_ejercicio(ejercicio: Ejercicio):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO Ejercicios (id_curso) VALUES (?)",
        (ejercicio.id_curso,)
    )
    
    ejercicio_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_ejercicio": ejercicio_id, "id_curso": ejercicio.id_curso}

# --- ENDPOINTS: RECURSOS ---

@app.post("/recursos", response_model=dict)
def create_recurso(recurso: Recurso):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO Recursos (id_contenido, tipo_contenido, id_curso) VALUES (?, ?, ?)",
        (recurso.id_contenido, recurso.tipo_contenido, recurso.id_curso)
    )
    
    recurso_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id_recurso": recurso_id, "id_contenido": recurso.id_contenido, "tipo_contenido": recurso.tipo_contenido, "id_curso": recurso.id_curso}