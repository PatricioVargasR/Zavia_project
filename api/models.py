from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Role(Base):
    __tablename__ = "roles"
    id_role = Column(Integer, primary_key=True, index=True)
    nombre_role = Column(String, unique=True, nullable=False)

class Usuario(Base):
    __tablename__ = "usuarios"
    id_usuario = Column(Integer, primary_key=True, index=True)
    id_role = Column(Integer, ForeignKey("roles.id_role"), nullable=False)
    contraseña = Column(String, nullable=False)
    nombre = Column(String, nullable=False)
    apellidos = Column(String, nullable=False)
    edad = Column(Integer, nullable=False)
    email = Column(String, unique=True, nullable=False)
    role = relationship("Role")

class Profesor(Base):
    __tablename__ = "profesores"
    id_profesor = Column(Integer, ForeignKey("usuarios.id_usuario"), primary_key=True)
    role_activo = Column(Boolean, default=True)

class Alumno(Base):
    __tablename__ = "alumnos"
    id_alumno = Column(Integer, ForeignKey("usuarios.id_usuario"), primary_key=True)
    role_activo = Column(Boolean, default=True)

class Curso(Base):
    __tablename__ = "cursos"
    id_curso = Column(Integer, primary_key=True, index=True)
    id_profesor = Column(Integer, ForeignKey("profesores.id_profesor"), nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    contenido_explicacion = Column(Text, nullable=False)
    contenido_descripcion = Column(Text, nullable=False)

class Recurso(Base):
    __tablename__ = "recursos"
    
    id_recurso = Column(Integer, primary_key=True, index=True)
    nombre_recurso = Column(String, nullable=False)
    link = Column(String, nullable=False)
    fecha_subida = Column(DateTime, default=datetime.utcnow)
    id_curso = Column(Integer, ForeignKey("cursos.id_curso"), nullable=False)
    
    curso = relationship("Curso", back_populates="recursos")
