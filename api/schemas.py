from pydantic import BaseModel
from typing import Optional

class RoleSchema(BaseModel):
    id_role: Optional[int]
    nombre_role: str

    class Config:
        orm_mode = True

class UsuarioSchema(BaseModel):
    id_usuario: Optional[int]
    id_role: int
    nombre: str
    apellidos: str
    edad: int
    email: str
    contraseña: str 

    class Config:
        orm_mode = True

class CursoSchema(BaseModel):
    id_curso: Optional[int]
    id_profesor: int
    contenido_explicacion: str
    contenido_descripcion: str

    class Config:
        orm_mode = True
class RecursoSchema(BaseModel):
    id_recurso: Optional[int]
    nombre_recurso: str
    link: str
    id_curso: int

    class Config:
        orm_mode = True
