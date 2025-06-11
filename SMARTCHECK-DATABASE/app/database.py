import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

# Lee la URL de la base de datos desde las variables de entorno
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# Crea el "motor" de SQLAlchemy. Este es el punto de entrada principal
# a la base de datos para SQLAlchemy.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Cada instancia de SessionLocal será una sesión de base de datos.
# Esta clase es la que usaremos para interactuar con la BD.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Usaremos esta clase Base para que nuestros modelos de la base de datos
# (que crearemos en models.py) hereden de ella.
Base = declarative_base()

# Función de dependencia para obtener la sesión de la base de datos en las rutas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()