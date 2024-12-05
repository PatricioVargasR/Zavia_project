-- Tabla de roles (profesor, alumno, etc.)
CREATE TABLE Roles (
    id_role INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_role TEXT NOT NULL UNIQUE
);

-- Tabla de usuarios (común para profesores y alumnos)
CREATE TABLE Usuarios (
    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
    id_role INTEGER NOT NULL,
    contraseña TEXT NOT NULL,
    nombre TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    edad INTEGER CHECK (edad >= 0 AND edad <= 120),
    email TEXT NOT NULL UNIQUE,
    FOREIGN KEY (id_role) REFERENCES Roles(id_role)
);

-- Tabla de profesores
CREATE TABLE Profesores (
    id_profesor INTEGER PRIMARY KEY,
    role_activo INTEGER NOT NULL DEFAULT 1 CHECK (role_activo IN (0, 1)),
    FOREIGN KEY (id_profesor) REFERENCES Usuarios(id_usuario)
);

-- Tabla de alumnos
CREATE TABLE Alumnos (
    id_alumno INTEGER PRIMARY KEY,
    role_activo INTEGER NOT NULL DEFAULT 1 CHECK (role_activo IN (0, 1)),
    FOREIGN KEY (id_alumno) REFERENCES Usuarios(id_usuario)
);

-- Tabla de cursos
CREATE TABLE Cursos (
    id_curso INTEGER PRIMARY KEY AUTOINCREMENT,
    id_profesor INTEGER NOT NULL,
    fecha_creacion TEXT NOT NULL DEFAULT (datetime('now')),
    contenido_explicacion TEXT NOT NULL,
    contenido_descripcion TEXT NOT NULL,
    FOREIGN KEY (id_profesor) REFERENCES Profesores(id_profesor)
);

-- Relación entre alumnos y cursos
CREATE TABLE Cursos_Alumnos (
    id_curso INTEGER NOT NULL,
    id_alumno INTEGER NOT NULL,
    PRIMARY KEY (id_curso, id_alumno),
    FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso),
    FOREIGN KEY (id_alumno) REFERENCES Alumnos(id_alumno)
);

-- Tabla de preguntas
CREATE TABLE Preguntas (
    id_pregunta INTEGER PRIMARY KEY AUTOINCREMENT,
    texto_pregunta TEXT NOT NULL,
    tipo_contenido TEXT NOT NULL CHECK (tipo_contenido IN ('test', 'ejercicio'))
);

-- Tabla de respuestas
CREATE TABLE Respuestas (
    id_respuesta INTEGER PRIMARY KEY AUTOINCREMENT,
    id_pregunta INTEGER NOT NULL,
    texto_respuesta TEXT NOT NULL,
    es_correcta INTEGER NOT NULL CHECK (es_correcta IN (0, 1)),
    FOREIGN KEY (id_pregunta) REFERENCES Preguntas(id_pregunta) ON DELETE CASCADE
);

-- Relación entre preguntas y tests
CREATE TABLE Tests_Preguntas (
    id_test INTEGER NOT NULL,
    id_pregunta INTEGER NOT NULL,
    PRIMARY KEY (id_test, id_pregunta),
    FOREIGN KEY (id_test) REFERENCES Tests(id_test) ON DELETE CASCADE,
    FOREIGN KEY (id_pregunta) REFERENCES Preguntas(id_pregunta) ON DELETE CASCADE
);

-- Relación entre preguntas y ejercicios
CREATE TABLE Ejercicios_Preguntas (
    id_ejercicio INTEGER NOT NULL,
    id_pregunta INTEGER NOT NULL,
    PRIMARY KEY (id_ejercicio, id_pregunta),
    FOREIGN KEY (id_ejercicio) REFERENCES Ejercicios(id_ejercicio) ON DELETE CASCADE,
    FOREIGN KEY (id_pregunta) REFERENCES Preguntas(id_pregunta) ON DELETE CASCADE
);

-- Tabla de tests
CREATE TABLE Tests (
    id_test INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso INTEGER NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);

-- Tabla de ejercicios
CREATE TABLE Ejercicios (
    id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
    id_curso INTEGER NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);

-- Tabla de recursos
CREATE TABLE Recursos (
    id_recurso INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_recurso TEXT NOT NULL,
    link TEXT NOT NULL,
    fecha_subida TEXT NOT NULL DEFAULT (datetime('now')),
    id_curso INTEGER NOT NULL,
    FOREIGN KEY (id_curso) REFERENCES Cursos(id_curso)
);
