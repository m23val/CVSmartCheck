from fastapi import APIRouter, Request, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Importamos las herramientas de nuestros otros módulos
from .. import core_logic, schemas, crud, auth, models
from ..database import get_db
from .. import models
from .. import core_logic


# --- CONFIGURACIÓN DEL ROUTER ---
router = APIRouter(
    tags=["Evaluations"] # Etiqueta para la documentación de la API
)

# Configuración de los templates HTML para que FastAPI sepa dónde encontrarlos
templates = Jinja2Templates(directory="templates")


# --- DEFINICIÓN DE RUTAS ---

@router.get("/", response_class=HTMLResponse)
# REEMPLAZA LA FUNCIÓN EXISTENTE EN app/routers/evaluations.py

@router.get("/", response_class=HTMLResponse)
async def mostrar_formulario_principal(
    request: Request,
    user: models.User = Depends(auth.get_current_user_optional)
):
    """
    Ruta para mostrar la página principal.
    Muestra una vista si el usuario está logueado, y otra si no.
    """
    return templates.TemplateResponse("index.html", {
        "request": request,
        "user": user  # Pasamos el usuario (o None) al template
    })

# REEMPLAZA LA FUNCIÓN procesar_cv_endpoint EN app/routers/evaluations.py

@router.post("/subir")
async def procesar_cv_endpoint(
    request: Request,
    archivo: UploadFile = File(...),
    puesto: str = Form(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    Endpoint para subir y procesar el CV.
    Esta ruta ahora devuelve los resultados en formato JSON.
    """
    if not archivo.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de archivo no válido. Solo se aceptan PDF y DOCX."
        )

    try:
        texto_cv = await core_logic.procesar_archivo(archivo)
        
        # Primero analizamos con BERT
        metricas_bert = core_logic.analizar_cv_con_bert(texto_cv, puesto)
        
        # Luego evaluamos, pasando las métricas de BERT
        puntaje, detalles = await core_logic.evaluar_cv(texto_cv, puesto, metricas_bert)
        
        recomendaciones = core_logic.recommendation_engine.generar_recomendaciones(texto_cv, puesto)

        evaluation_data = schemas.EvaluationCreate(
            score=puntaje, 
            recommendations=[str(r) for r in recomendaciones],
            puesto=puesto,      # <-- AÑADE ESTO
            detalles=detalles   # <-- AÑADE ESTO
        )
        crud.create_user_evaluation(db=db, evaluation=evaluation_data, user_id=current_user.id)

        # Devolvemos todo en el JSON, incluyendo las métricas para la UI
        return {
            "resultado": puntaje,
            "detalles": detalles,
            "nombre": archivo.filename,
            "contenido_cv": texto_cv[:10000],
            "recomendaciones": recomendaciones,
            "puesto": puesto,
            "user": {"email": current_user.email}, # Pasamos solo los datos seguros del usuario
            "metricas_bert": list(metricas_bert.values())
        }

    except Exception as e:
        import traceback
        traceback.print_exc() # Imprime el error detallado en la consola del servidor
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error procesando el archivo: {e}"
        )
