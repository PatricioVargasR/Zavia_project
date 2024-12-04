from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db, Base, engine
from models import Usuario, Role, Curso, Alumno, Profesor
from schemas import UsuarioSchema, CursoSchema, RoleSchema
from utils import hash_password, verify_password

Base.metadata.create_all(bind=engine)

app = FastAPI()

# SIGNUP
@app.post("/signup")
def signup(user: UsuarioSchema, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = hash_password(user.contraseña)
    new_user = Usuario(**user.dict(), contraseña=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully", "user": new_user}

# LOGIN
@app.post("/login")
def login(email: str, contraseña: str, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if not user or not verify_password(contraseña, user.contraseña):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.id_usuario}

# CRUD for Cursos
@app.get("/cursos")
def get_cursos(db: Session = Depends(get_db)):
    return db.query(Curso).all()

@app.post("/cursos")
def create_curso(curso: CursoSchema, db: Session = Depends(get_db)):
    new_curso = Curso(**curso.dict())
    db.add(new_curso)
    db.commit()
    db.refresh(new_curso)
    return new_curso

@app.delete("/cursos/{id_curso}")
def delete_curso(id_curso: int, db: Session = Depends(get_db)):
    curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not curso:
        raise HTTPException(status_code=404, detail="Curso not found")
    db.delete(curso)
    db.commit()
    return {"message": "Curso deleted successfully"}

@app.put("/cursos/{id_curso}")
def update_curso(id_curso: int, curso: CursoSchema, db: Session = Depends(get_db)):
    db_curso = db.query(Curso).filter(Curso.id_curso == id_curso).first()
    if not db_curso:
        raise HTTPException(status_code=404, detail="Curso not found")
    for key, value in curso.dict(exclude_unset=True).items():
        setattr(db_curso, key, value)
    db.commit()
    db.refresh(db_curso)
    return db_curso

# DASHBOARD
@app.get("/dashboard/profesor/{id_profesor}")
def profesor_dashboard(id_profesor: int, db: Session = Depends(get_db)):
    cursos = db.query(Curso).filter(Curso.id_profesor == id_profesor).all()
    return {"cursos": cursos}

@app.get("/dashboard/alumno/{id_alumno}")
def alumno_dashboard(id_alumno: int, db: Session = Depends(get_db)):
    cursos = db.query(Curso).join(Alumno, Alumno.id_alumno == id_alumno).all()
    return {"cursos": cursos}
