import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Importamos las herramientas de nuestros otros módulos
from . import crud, models, schemas
from .database import get_db

# Cargar variables de entorno del .env
load_dotenv()

# --- Configuración de Seguridad ---
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# --- Configuración para Hashing de Contraseñas ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token") # Lo mantenemos para la documentación

def verify_password(plain_password, hashed_password):
    """Verifica si una contraseña en texto plano coincide con una hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Genera el hash de una contraseña en texto plano."""
    return pwd_context.hash(password)

def authenticate_user(db: Session, email: str, password: str):
    """Busca un usuario por email y verifica su contraseña."""
    user = crud.get_user_by_email(db, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# --- Funciones para Tokens JWT ---

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un nuevo token de acceso."""
    to_encode = data.copy()
    expire_time = ACCESS_TOKEN_EXPIRE_MINUTES
    expire = datetime.now(timezone.utc) + timedelta(minutes=expire_time)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# === FUNCIÓN CORREGIDA PARA OBTENER EL USUARIO (PARA RUTAS PROTEGIDAS) ===
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """
    Dependencia para obtener el usuario actual. Ahora busca el token
    primero en las cookies, que es como lo estamos usando para la navegación.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = request.cookies.get("access_token")
    if token is None:
        raise credentials_exception
        
    try:
        # El token en la cookie es "Bearer <token>", así que lo separamos
        token_data = token.split(" ")[1]
        payload = jwt.decode(token_data, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except (JWTError, IndexError):
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
        
    return user

# === FUNCIÓN CORREGIDA PARA OBTENER EL USUARIO (PARA PÁGINAS PÚBLICAS) ===
async def get_current_user_optional(request: Request, db: Session = Depends(get_db)):
    """
    Dependencia para obtener el usuario actual si existe, pero no da error si no.
    Ideal para la página principal.
    """
    try:
        return await get_current_user(request=request, db=db)
    except HTTPException:
        return None
