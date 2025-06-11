from sqlalchemy.orm import Session

# Importamos nuestros modelos y schemas
from . import models, schemas, auth

# --- Funciones CRUD para User ---

def get_user_by_email(db: Session, email: str):
    """
    Busca y devuelve un usuario por su email.
    Lo usaremos para comprobar si un email ya está registrado.
    """
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """
    Crea un nuevo usuario en la base de datos.
    """
    # ¡IMPORTANTE! Aquí es donde ciframos la contraseña.
    # Usaremos una función que crearemos en el siguiente paso en auth.py.
    hashed_password = auth.get_password_hash(user.password)
    
    # Creamos un objeto de modelo SQLAlchemy con los datos
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    
    # Añadimos el objeto a la sesión de la base de datos
    db.add(db_user)
    # Confirmamos los cambios para guardarlos permanentemente
    db.commit()
    # Refrescamos el objeto para que contenga los datos nuevos de la BD (como el id)
    db.refresh(db_user)
    
    return db_user


# --- Funciones CRUD para Evaluation ---

def get_evaluations_by_user(db: Session, user_id: int, limit: int = 3):
    """
    Obtiene las últimas evaluaciones de un usuario específico.
    El límite por defecto es 3, cumpliendo con el requisito.
    """
    return db.query(models.Evaluation)\
             .filter(models.Evaluation.owner_id == user_id)\
             .order_by(models.Evaluation.evaluated_at.desc())\
             .limit(limit)\
             .all()

def create_user_evaluation(db: Session, evaluation: schemas.EvaluationCreate, user_id: int):
    """
    Guarda una nueva evaluación y la asocia con un usuario.
    """
    # Creamos el objeto de modelo SQLAlchemy
    db_evaluation = models.Evaluation(
        score=evaluation.score,
        recommendations=evaluation.recommendations,
        puesto=evaluation.puesto,      # <-- AÑADE ESTA LÍNEA
        detalles=evaluation.detalles,  # <-- AÑADE ESTA LÍNEA
        owner_id=user_id
    )

    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)

    return db_evaluation