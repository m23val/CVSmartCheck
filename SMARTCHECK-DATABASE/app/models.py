from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Importamos la Base declarativa que creamos en database.py
from .database import Base

class User(Base):
    # Nombre de la tabla en la base de datos
    __tablename__ = "users"

    # Columnas de la tabla 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Esta es una "relación", no una columna.
    # Le dice a SQLAlchemy que puede encontrar todas las evaluaciones
    # que pertenecen a este usuario a través del atributo 'evaluations'.
    # 'back_populates' conecta esta relación con la del modelo Evaluation.
    evaluations = relationship("Evaluation", back_populates="owner")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    recommendations = Column(JSON, nullable=False)
    evaluated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # --- LÍNEAS A AÑADIR ---
    puesto = Column(String, nullable=False)
    detalles = Column(JSON, nullable=False)
    # --- FIN DE LÍNEAS A AÑADIR ---
    
    # Esta es la clave foránea que conecta esta evaluación con un usuario.
    # Le dice a la base de datos que cada evaluación DEBE pertenecer a un usuario.
    owner_id = Column(Integer, ForeignKey("users.id"))

    # La otra parte de la relación. Nos permite acceder al usuario
    # propietario de esta evaluación a través del atributo 'owner'.
    owner = relationship("User", back_populates="evaluations")