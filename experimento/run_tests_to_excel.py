import os
from pathlib import Path
import pandas as pd
import asyncio # Necesario para ejecutar funciones asíncronas
from typing import Dict, List, Tuple # Importar tipos para claridad

# Importa las funciones y clases necesarias de TU ARCHIVO main.py.
# Asegúrate de que main.py esté en el mismo directorio.
from main import (
    TFIDFSemanticAnalyzer,
    extraer_texto_pdf,
    extraer_texto_docx,
    procesar_archivo # Importamos procesar_archivo ya que es async y simulará el UploadFile
)

# --- CONFIGURACIÓN DE LA EJECUCIÓN ---
# Define la ruta a la carpeta que contiene tus CVs de FullStack.
# Asegúrate de que esta ruta sea correcta y relativa a donde ejecutas este script.
CVS_DIR = Path("CVs/IngenieroRedes") 

# El puesto para el cual se analizarán todos los CVs.
# Asegúrate de que este puesto exista en los textos ideales de tu main.py.
PUSTO_A_ANALIZAR = "Ingeniero de Redes"

# Lista de los nombres de tus archivos de CV que quieres analizar.
# Asegúrate de que estos nombres coincidan exactamente con los archivos en tu carpeta CVS_DIR.
CV_FILES = [
    "1.pdf", 
    "2.pdf", 
    "3.pdf", 
    "4.pdf", 
    "5.pdf", 
    
     
]

# --- Clase Mock para simular UploadFile de FastAPI ---
# `procesar_archivo` en tu `main.py` espera un objeto `UploadFile` (FastAPI).
# Esta clase simula el comportamiento mínimo de `UploadFile` que `procesar_archivo` necesita:
# tener un atributo `.filename` y un método `.read()` (que es asíncrono).
class MockUploadFile:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.filename = file_path.name
        self._content = None # Cachea el contenido una vez leído

    async def read(self):
        # Lee el contenido del archivo de forma síncrona/asíncrona.
        # Para archivos pequeños como CVs, esta lectura directa está bien.
        if self._content is None:
            with open(self.file_path, "rb") as f:
                self._content = f.read()
        return self._content

    def __repr__(self):
        return f"<MockUploadFile filename='{self.filename}'>"

# --- Función Principal para Ejecutar el Análisis y Recolectar Resultados ---
async def ejecutar_analisis_y_recolectar_resultados():
    """
    Ejecuta el análisis de CV para cada archivo en la lista, utilizando
    las funciones y la lógica de puntuación de main.py, y recolecta los resultados
    en un formato adecuado para Pandas/Excel.
    """
    # Instancia el analizador semántico de tu main.py.
    # Esto carga los textos ideales y palabras clave tal como están definidos en tu main.py.
    analyzer = TFIDFSemanticAnalyzer() 
    
    all_cv_results = [] # Lista para almacenar los resultados procesados de cada CV

    print(f"--- Iniciando análisis masivo para el puesto: {PUSTO_A_ANALIZAR} ---")

    for cv_filename in CV_FILES:
        cv_path = CVS_DIR / cv_filename # Construye la ruta completa al archivo CV
        
        print(f"\nAnalizando CV: {cv_filename}")
        
        # Verifica si el archivo CV existe antes de intentar procesarlo
        if not cv_path.is_file():
            print(f"ERROR: Archivo no encontrado: {cv_path}. Saltando este CV.")
            # Añade una entrada de error al registro de resultados
            all_cv_results.append({
                "Nombre CV": cv_filename, 
                "Puesto Analizado": PUSTO_A_ANALIZAR, 
                "Puntuación Total": 0, "Puntuación Máxima Posible": 0, "Promedio por Sección": 0.0,
                "Estado": f"ERROR: Archivo no encontrado - {cv_path}"
            })
            continue # Pasa al siguiente CV

        try:
            # 1. Simula la subida del archivo usando MockUploadFile y procesar_archivo de main.py
            mock_file = MockUploadFile(cv_path)
            texto_cv_extraido = await procesar_archivo(mock_file) # await porque procesar_archivo es async

            # Valida el texto extraído (simulando la validación en la ruta /analizar de main.py)
            if len(texto_cv_extraido.strip()) < 50: # Este umbral es el de tu main.py original
                raise ValueError("Texto insuficiente o ilegible en el archivo del CV.")
            
            # 2. Llama al método `analizar_cv` de tu TFIDFSemanticAnalyzer
            # Este método devuelve las métricas RAW (sim_tfidf, sim_keywords, sim_combinada, nivel, ajuste_puntos)
            metricas_raw = analyzer.analizar_cv(texto_cv_extraido, PUSTO_A_ANALIZAR)

            # --- 3. REPLICAR LA LÓGICA DE PUNTUACIÓN Y VISUALIZACIÓN DE LA RUTA /ANALIZAR DE MAIN.PY ---
            # Para que los resultados en el Excel sean idénticos a los que ves en la UI de tu app,
            # replicamos aquí la lógica de conversión de métricas_raw a puntuaciones_ui de main.py.

            resultados_ui_simulados: List[Tuple[str, int, int, str]] = [] # (seccion, puntuacion, puntuacion_base, mensaje)
            puntuacion_total_calculada = 0
            
            # Definir el orden de las secciones tal como aparecen en tu main.py original para el bucle
            # (formato se procesa al final, pero es parte de los resultados).
            # En tu main.py original, 'formato' es la última sección en textos_ideales.items()
            # y se procesa en el bucle principal.
            orden_secciones_original_main_py = [
                "perfil", "experiencia", "habilidades", "educacion", 
                "certificados", "idiomas", "datos", "formato"
            ]

            # Puntuación base por sección en la UI (de tu main.py)
            puntuacion_base_seccion_ui = 10 
            
            # El main.py original no tiene la sección "proyectos" en `textos_ideales` ni en el bucle principal de `analizar_cv`.
            # Sin embargo, la imprimías en la UI y la incluías en el test_main.py.
            # Para la estricta replicación del main.py original que me pasaste:
            # replicamos el bucle `for seccion, texto_ideal in textos_ideales.items():`

            # El `analizar_cv` de tu main.py original NO devuelve `proyectos` por defecto
            # si no está en `textos_ideales`.
            # Así que los resultados serán para las 8 secciones que SÍ analiza el main.py original.
            
            # Recreamos la iteración sobre las métricas que el `analizar_cv` de main.py devuelve
            # para generar los puntos de UI y el total/promedio.

            for seccion_key in orden_secciones_original_main_py:
                # Si por alguna razón la sección no fue procesada por analizar_cv (ej. no está en textos_ideales)
                if seccion_key not in metricas_raw:
                    continue # Saltar y no incluir en los resultados

                datos = metricas_raw[seccion_key] # Accede a los datos de la métrica RAW
                
                # Extrae los valores de similitud y nivel de la métrica RAW
                factor_similitud = float(datos["similitud_combinada"])
                nivel_coherencia = datos["nivel"] # Nivel viene directamente de analizar_cv
                
                # ESCALA DE PUNTUACIÓN GENEROSA (DE TU MAIN.PY ORIGINAL)
                puntuacion_actual_seccion_ui = 0
                if factor_similitud >= 0.6:       # Alto
                    puntuacion_actual_seccion_ui = min(10, 9 + round(factor_similitud))      # 9-10 puntos
                elif factor_similitud >= 0.4:     # Medio
                    puntuacion_actual_seccion_ui = min(9, 7 + round(factor_similitud * 2))   # 7-9 puntos  
                elif factor_similitud >= 0.2:     # Bajo
                    puntuacion_actual_seccion_ui = min(7, 5 + round(factor_similitud * 3))   # 5-7 puntos
                else:                   # Muy bajo (en tu original, también lo llamaba "Bajo" aquí)
                    puntuacion_actual_seccion_ui = max(3, round(factor_similitud * 10))      # 3-5 puntos
                
                # Mensaje de coherencia (replicado de tu main.py original)
                mensaje_coherencia_simulado = ""
                if nivel_coherencia == "Alto":
                    mensaje_coherencia_simulado = "✅ Excelente coherencia semántica"
                elif nivel_coherencia == "Medio":
                    mensaje_coherencia_simulado = "⚠️ Coherencia aceptable"
                else: # Aquí tu main.py original agrupa "Bajo" y "Muy Bajo" si sim_combinada < 0.4
                    mensaje_coherencia_simulado = "❌ Coherencia básica"
                
                mensaje_coherencia_simulado += f" [TF-IDF: {int(datos['similitud_tfidf']*100)}%]"

                # Añade los resultados formateados para la fila del Excel
                resultados_ui_simulados.append((
                    seccion_key.capitalize(), # Nombre de la sección capitalizado
                    puntuacion_actual_seccion_ui, # La puntuación de 1-10 para la UI
                    puntuacion_base_seccion_ui,   # Siempre 10
                    mensaje_coherencia_simulado,
                    round(factor_similitud * 100), # Similitud combinada en %
                    round(float(datos["similitud_tfidf"]) * 100), # Similitud TF-IDF en %
                    round(float(datos["similitud_keywords"]) * 100), # Similitud Keywords en %
                    nivel_coherencia # Nivel (Alto, Medio, Bajo)
                ))
                puntuacion_total_calculada += puntuacion_actual_seccion_ui
            
            # Cálculo de la Puntuación Total y Promedio (de tu main.py original)
            # Tu main.py original calcula `puntaje_total/8`. Esto asume 8 secciones.
            # Las 8 secciones son: perfil, experiencia, habilidades, educacion, certificados, idiomas, datos, formato.
            # Contamos las secciones que realmente se procesaron para el promedio.
            num_secciones_evaluadas = len(resultados_ui_simulados) # Deberían ser 8 si todo se extrajo bien
            if num_secciones_evaluadas == 0: num_secciones_evaluadas = 1 # Evitar división por cero

            promedio_por_seccion_simulado = round(puntuacion_total_calculada / num_secciones_evaluadas, 1)

            # --- Almacena todos los resultados para el DataFrame ---
            cv_data_para_df = {
                "Nombre CV": cv_filename,
                "Puesto Analizado": PUSTO_A_ANALIZAR,
                "Puntuación Total": puntuacion_total_calculada,
                # La puntuación máxima era implícitamente 80 en el original (8 secciones * 10 puntos)
                "Puntuación Máxima Posible": 8 * puntuacion_base_seccion_ui, 
                "Promedio por Sección": promedio_por_seccion_simulado,
                "Estado": "OK" # Estado inicial, se cambia si hay error
            }

            # Agrega los detalles de cada sección como columnas separadas para el DataFrame
            for seccion_tuple in resultados_ui_simulados:
                seccion_nombre_limpio = seccion_tuple[0] # Ej: "Perfil"
                cv_data_para_df[f"{seccion_nombre_limpio} - Puntuación"] = seccion_tuple[1]
                cv_data_para_df[f"{seccion_nombre_limpio} - Sim. Combinada (%)"] = seccion_tuple[4]
                cv_data_para_df[f"{seccion_nombre_limpio} - Sim. TF-IDF (%)"] = seccion_tuple[5]
                cv_data_para_df[f"{seccion_nombre_limpio} - Sim. Keywords (%)"] = seccion_tuple[6]
                cv_data_para_df[f"{seccion_nombre_limpio} - Nivel"] = seccion_tuple[7]

            all_cv_results.append(cv_data_para_df)

        except Exception as e:
            print(f"ERROR: Fallo al procesar {cv_filename}: {e}")
            # Si hay un error, registra un CV de datos de error para el Excel
            error_details = str(e)
            all_cv_results.append({
                "Nombre CV": cv_filename, 
                "Puesto Analizado": PUSTO_A_ANALIZAR, 
                "Puntuación Total": 0, 
                "Puntuación Máxima Posible": 8 * puntuacion_base_seccion_ui, # Mantén el máximo aunque haya error
                "Promedio por Sección": 0.0,
                "Estado": f"ERROR: {error_details}"
            })

    return all_cv_results

# --- Función para guardar los resultados en Excel ---
async def guardar_resultados_en_excel(results: List[Dict], output_excel_path: str):
    """
    Guarda la lista de resultados de análisis de CV en un archivo Excel.
    """
    if not results:
        print("No hay resultados para exportar al Excel.")
        return

    df = pd.DataFrame(results)

    # Definir el orden de las columnas para el Excel de salida.
    # Esto asegura que el Excel sea consistente y legible.
    # Las columnas se construirán dinámicamente para incluir todas las secciones.
    
    # Columnas principales
    ordered_columns_final = [
        "Nombre CV", "Puesto Analizado", "Puntuación Total", 
        "Puntuación Máxima Posible", "Promedio por Sección"
    ]

    # Orden predefinido para las secciones detalladas
    secciones_detalladas_orden = [
        "Perfil", "Experiencia", "Habilidades", "Proyectos", # Proyectos no estaba en textos_ideales original, pero si se extrajo, se incluye.
        "Educacion", "Certificados", "Idiomas", "Datos", "Formato"
    ]
    
    # Añadir columnas de detalles de sección en el orden deseado
    for sec in secciones_detalladas_orden:
        # Asegúrate de que estas columnas existan en el DataFrame antes de intentar agregarlas
        if f"{sec} - Puntuación" in df.columns:
            ordered_columns_final.append(f"{sec} - Puntuación")
            ordered_columns_final.append(f"{sec} - Sim. Combinada (%)")
            ordered_columns_final.append(f"{sec} - Sim. TF-IDF (%)")
            ordered_columns_final.append(f"{sec} - Sim. Keywords (%)")
            ordered_columns_final.append(f"{sec} - Nivel")
    
    # Finalmente, añade la columna de Estado
    ordered_columns_final.append("Estado")

    # Filtra las columnas del DataFrame para que coincidan con el orden deseado
    # y solo incluye las que realmente existen en el DataFrame (manejo de errores/secciones faltantes).
    final_cols = [col for col in ordered_columns_final if col in df.columns]
    df = df[final_cols]

    # Guarda el DataFrame en un archivo Excel.
    try:
        df.to_excel(output_excel_path, index=False)
        print(f"\n¡Análisis completado y resultados exportados a '{output_excel_path}'!")
    except Exception as e:
        print(f"ERROR: No se pudo exportar a Excel '{output_excel_path}': {e}")


# --- Bloque de ejecución principal del script ---
# Esto se ejecuta cuando corres el script directamente.
if __name__ == "__main__":
    # Define la ruta de salida para el archivo Excel.
    # Este será el NUEVO Excel que contendrá los resultados actuales.
    output_excel_file = "resultados_cv_IngenieroRedes.xlsx" 
    
    # Ejecuta la función asíncrona principal.
    asyncio.run(ejecutar_analisis_y_recolectar_resultados())
    
    # Luego de recolectar, puedes cargar y guardar en excel.
    # Note: La función `ejecutar_analisis_y_recolectar_resultados` ya devuelve `all_cv_results`.
    # Podemos pasar esos resultados directamente a `guardar_resultados_en_excel`.
    # Sin embargo, el diseño actual está pensado para que los resultados
    # se guarden al final de la ejecución de `main`.
    # Si quisieras que `guardar_resultados_en_excel` también sea async, necesitarías await.
    # Simplifiquemos: llamamos a guardar_resultados_en_excel con los resultados.

    # Esta línea necesita los resultados.
    # Deberíamos modificar `ejecutar_analisis_y_recolectar_resultados` para que retorne `all_cv_results`
    # y luego pasárselo a `guardar_resultados_en_excel`.

    # CORRECCIÓN EN EL FLUJO DE EJECUCIÓN PRINCIPAL:
    final_results = asyncio.run(ejecutar_analisis_y_recolectar_resultados())
    if final_results:
        asyncio.run(guardar_resultados_en_excel(final_results, output_excel_file))
    else:
        print("No se generaron resultados para exportar.")

