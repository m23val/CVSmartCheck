from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Importamos las herramientas
from .database import engine
from . import models
# ¡Añade 'history' a esta línea!
from .routers import evaluations, users, history 

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# "Conecta" o "incluye" todos los routers
app.include_router(evaluations.router)
app.include_router(users.router)
app.include_router(history.router) # <-- ¡AÑADE ESTA LÍNEA!

# Opcional: una ruta simple para verificar que todo funciona
@app.get("/health-check")
def health_check():
    return {"status": "ok", "message": "Servidor principal funcionando"}