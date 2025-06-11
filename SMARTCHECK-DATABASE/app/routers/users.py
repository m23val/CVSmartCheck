from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importamos todas nuestras herramientas de los otros archivos
from .. import auth, crud, models, schemas
from ..database import get_db

# Creamos un router.
# El prefijo hará que todas las rutas aquí empiecen con /users
# La etiqueta 'users' agrupará estas rutas en la documentación de la API
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Ruta para registrar un nuevo usuario.
    """
    # Primero, comprobamos si ya existe un usuario con ese email
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        # Si existe, lanzamos un error HTTP 400
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Si no existe, llamamos a nuestra función CRUD para crear el usuario
    # Esta función se encargará de hashear la contraseña y guardarla
    return crud.create_user(db=db, user=user)


@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Ruta para iniciar sesión. Devuelve un token de acceso.
    FastAPI usa la clase OAuth2PasswordRequestForm para recibir el 'username' y 'password'
    en un formulario.
    """
    # Verificamos al usuario. En nuestro caso, el 'username' será el email.
    user = auth.authenticate_user(db, email=form_data.username, password=form_data.password)
    if not user:
        # Si las credenciales son incorrectas, lanzamos un error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Si las credenciales son correctas, creamos un token de acceso
    access_token = auth.create_access_token(
        data={"sub": user.email}
    )
    
    # Devolvemos el token
    return {"access_token": access_token, "token_type": "bearer"}