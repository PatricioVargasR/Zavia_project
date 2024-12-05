INSERT INTO Usuarios (id_role, contraseña, nombre, apellidos, edad, email) VALUES
(1, 'password123', 'Carlos', 'Pérez', 40, 'carlos.perez@ejemplo.com'),
(1, 'profesor123', 'María', 'Gómez', 35, 'maria.gomez@ejemplo.com'),
(2, 'alumno456', 'Juan', 'Martínez', 20, 'juan.martinez@ejemplo.com'),
(2, 'alumno789', 'Ana', 'López', 22, 'ana.lopez@ejemplo.com'),
(2, 'alumno101', 'Luis', 'Hernández', 19, 'luis.hernandez@ejemplo.com');

INSERT INTO Profesores (id_profesor, role_activo) VALUES 
(1, 1), 
(2, 1);

INSERT INTO Alumnos (id_alumno, role_activo) VALUES 
(3, 1), 
(4, 1), 
(5, 1);

INSERT INTO Cursos (id_profesor, contenido_explicacion, contenido_descripcion) VALUES
(1, 'Introducción a la programación en Python', 'Este curso está diseñado para aquellos que desean aprender los fundamentos de la programación usando Python. Se cubrirán conceptos como variables, estructuras de control, funciones y manejo de datos. Ideal para principiantes que buscan iniciar su camino en el desarrollo de software.'),
(2, 'Curso avanzado de matemáticas discretas', 'En este curso, los estudiantes explorarán los temas más complejos de las matemáticas discretas, como teoría de grafos, combinatoria avanzada, y lógica matemática. Perfecto para aquellos interesados en áreas como la informática, la inteligencia artificial y la teoría de la computación.'),
(1, 'Conceptos básicos de bases de datos', 'Este curso proporciona una introducción al mundo de las bases de datos. Los estudiantes aprenderán sobre el modelo relacional, el lenguaje SQL, el diseño de bases de datos y la normalización. Un curso esencial para futuros desarrolladores y administradores de bases de datos.'),
(2, 'Fundamentos de redes de computadoras', 'En este curso, los estudiantes aprenderán los conceptos fundamentales de redes de computadoras, incluyendo arquitectura de redes, protocolos, direcciones IP, y seguridad en redes. Ideal para aquellos que buscan comprender cómo las computadoras se comunican entre sí en un entorno de red.'),
(1, 'Desarrollo web con HTML y CSS', 'Este curso está enfocado en enseñar a los estudiantes cómo crear páginas web utilizando HTML y CSS. Se cubrirán temas como la estructura básica de una página web, el diseño responsivo y las mejores prácticas para construir sitios web modernos y accesibles.');

INSERT INTO Cursos_Alumnos (id_curso, id_alumno) VALUES
(1, 3),
(1, 4),
(2, 5),
(3, 3),
(4, 4);

INSERT INTO Preguntas (texto_pregunta, tipo_contenido) VALUES
('¿Qué es una variable en Python?', 'test'),
('¿Cuál es la sintaxis correcta para un bucle for?', 'test'),
('Define el concepto de conjunto en matemáticas', 'ejercicio'),
('¿Qué es una dirección IP?', 'test'),
('Escribe un ejemplo de una regla CSS', 'ejercicio');

INSERT INTO Respuestas (id_pregunta, texto_respuesta, es_correcta) VALUES
(1, 'Un contenedor para almacenar datos', 1),
(1, 'Una función matemática', 0),
(2, 'for i in range(5):', 1),
(2, 'loop while true:', 0),
(3, 'Un conjunto es una colección de elementos únicos.', 1),
(4, 'Una dirección única asignada a un dispositivo en una red.', 1),
(5, 'color: blue;', 1),
(5, 'import blue;', 0);

INSERT INTO Tests (id_curso) VALUES
(1), 
(3), 
(4);

INSERT INTO Tests_Preguntas (id_test, id_pregunta) VALUES
(1, 1), 
(1, 2), 
(2, 4);

INSERT INTO Ejercicios (id_curso) VALUES
(2), 
(3);

INSERT INTO Ejercicios_Preguntas (id_ejercicio, id_pregunta) VALUES
(1, 3), 
(2, 5);

INSERT INTO Recursos (id_contenido, tipo_contenido, id_curso) VALUES
(1, 'curso', 1),
(2, 'test', 1),
(3, 'ejercicio', 2),
(4, 'curso', 3),
(5, 'test', 4);