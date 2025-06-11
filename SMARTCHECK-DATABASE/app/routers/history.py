from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List

# Importamos las herramientas de nuestros otros módulos
from .. import crud, auth, models, schemas
from ..database import get_db

router = APIRouter(
    tags=["History"],
    prefix="/history" # Añadimos un prefijo para todas las rutas de este archivo
)

templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_user_history(
    request: Request, 
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Obtiene las últimas 3 evaluaciones del usuario logueado y
    renderiza la página del historial.
    """
    # Usamos la función CRUD que ya habíamos creado
    evaluations = crud.get_evaluations_by_user(db=db, user_id=current_user.id, limit=3)
    
    # Pasamos los datos al nuevo template 'history.html'
    return templates.TemplateResponse("history.html", {
        "request": request,
        "user": current_user,
        "evaluations": evaluations
    })

