from pydantic import BaseModel
from typing import List, Tuple, Optional
from datetime import datetime

# --- Schemas para Evaluation ---

class EvaluationBase(BaseModel):
    score: int
    # Usamos List[str] porque las recomendaciones son una lista de textos
    recommendations: List[str]
    puesto: str
    detalles: List[Tuple] # Los detalles son una lista de tuplas/listas

class EvaluationCreate(EvaluationBase):
    # Para crear una evaluación, solo necesitamos el score y las recomendaciones.
    # El resto (id, fecha, owner_id) se genera automáticamente.
    pass

class Evaluation(EvaluationBase):
    # Este es el schema que usaremos para LEER una evaluación desde la BD.
    # Incluirá todos los datos que queremos mostrar.
    id: int
    owner_id: int
    evaluated_at: datetime

    class Config:
        # Esta línea mágica le dice a Pydantic que puede leer los datos
        # incluso si son un modelo de SQLAlchemy (un objeto ORM), no solo un diccionario.
        from_attributes = True


# --- Schemas para User ---

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    # Para crear un usuario, necesitamos el email y la contraseña.
    password: str

class User(UserBase):
    # Este es el schema que usaremos para LEER un usuario.
    # Fíjate que NO incluye la contraseña por seguridad.
    id: int
    created_at: datetime
    # Aquí le decimos que un usuario puede tener una lista de evaluaciones
    # que se ajustan al schema 'Evaluation'.
    evaluations: List[Evaluation] = []

    class Config:
        from_attributes = True