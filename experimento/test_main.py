import pytest
from fastapi.testclient import TestClient # Importa el cliente de pruebas de FastAPI
import os
from pathlib import Path
import re # Módulo para expresiones regulares
import pandas as pd # Para leer el archivo Excel
from typing import Dict # Para la anotación de tipos
import pytest_asyncio # Para manejar fixtures y tests asíncronos

# Importa tu aplicación FastAPI y el analizador semántico desde main.py
# Asegúrate de que main.py esté en el mismo directorio.
from main import app, semantic_analyzer 

# --- Configuración General para las Pruebas ---
# Define la ruta a la carpeta que contiene tus CVs reales de FullStack.
# Asegúrate de que esta ruta sea correcta y relativa al directorio desde donde ejecutas pytest.
TEST_CVS_DIR = Path("CVs/IngenieroRedes") 

# Define el puesto para el cual se analizarán los CVs en estas pruebas.
# Este valor DEBE coincidir con el puesto que usaste cuando generaste tu 'resultados_cv_fullstack_generado.xlsx'.
PUSTO_DE_PRUEBA = "Ingeniero de Redes"

# --- Cargar los casos de prueba desde tu archivo de resultados Excel generado ---
# ¡IMPORTANTE! Este es el nombre del archivo Excel que genera el script `generar_excel_resultados.py`.
# Asegúrate de que este archivo esté en el mismo directorio que test_main.py.
EXCEL_GENERATED_RESULTS_PATH = "resultados_cv_IngenieroRedes.xlsx" 

# Lista que contendrá los casos de prueba cargados dinámicamente desde el Excel.
TEST_CASES = []

try:
    # Intenta leer el archivo Excel usando pandas.
    df_results = pd.read_excel(EXCEL_GENERATED_RESULTS_PATH)
    print(f"✅ Se cargaron los resultados de prueba desde '{EXCEL_GENERATED_RESULTS_PATH}'.")
    print(f"Número de filas (CVs) cargadas en Excel: {len(df_results)}") 
    print(f"Columnas detectadas en el Excel: {df_results.columns.tolist()}") 

    if not df_results.empty:
        # Itera sobre cada fila del DataFrame (cada CV analizado previamente).
        for index, row in df_results.iterrows():
            # Extrae el nombre del archivo del CV de la columna "Nombre CV".
            filename = str(row["Nombre CV"]) 
            # Extrae la puntuación total del CV de la columna "Puntuación Total".
            total_score = int(row["Puntuación Total"]) 
            
            # Inicializa un diccionario para almacenar los niveles esperados de cada sección.
            expected_section_levels = {}
            # Itera sobre todas las columnas del DataFrame para encontrar las columnas de "Nivel".
            for col_name in df_results.columns:
                if " - Nivel" in col_name:
                    # Extrae el nombre de la sección (ej. "Experiencia" de "Experiencia - Nivel").
                    section_name = col_name.replace(" - Nivel", "")
                    # Almacena el nivel esperado para esa sección (ej. "Alto", "Medio").
                    expected_section_levels[section_name] = str(row[col_name]) 
            
            # Añade un nuevo caso de prueba a la lista TEST_CASES.
            TEST_CASES.append({
                "filename": filename,
                "puesto": PUSTO_DE_PRUEBA,
                "expected_total_score_min": total_score,
                "expected_total_score_max": total_score,
                "expected_section_levels": expected_section_levels
            })
        print(f"Número de casos de prueba generados en TEST_CASES: {len(TEST_CASES)}") 
    else:
        print("⚠️ El DataFrame cargado desde el archivo Excel está vacío. No se generaron casos de prueba para ejecutar.")

except FileNotFoundError:
    print(f"❌ Error: El archivo de resultados '{EXCEL_GENERATED_RESULTS_PATH}' no se encontró en el directorio actual. Asegúrate de que haya sido generado por 'generar_excel_resultados.py' y esté en la misma carpeta que test_main.py.")
except Exception as e:
    print(f"❌ Error al leer o procesar el archivo de resultados '{EXCEL_GENERATED_RESULTS_PATH}': {e}")


# --- Fixture de Pytest para el Cliente de Prueba Asíncrono ---
@pytest_asyncio.fixture(scope="module") 
def client():
    """
    Crea y proporciona un cliente de prueba para la aplicación FastAPI.
    Usa TestClient de FastAPI para simular las solicitudes.
    """
    return TestClient(app) 

# --- Función de Prueba Principal ---
@pytest.mark.asyncio 
@pytest.mark.parametrize("test_case", TEST_CASES, ids=[tc["filename"] for tc in TEST_CASES])
async def test_IngenieroRedes_cv_analysis(client: TestClient, test_case: Dict):
    """
    Prueba el análisis de un CV específico para el puesto de Desarrollador Full Stack.
    Simula la subida de un archivo CV a la API y verifica los resultados en la respuesta HTML
    contra las expectativas cargadas desde el archivo Excel.
    """
    cv_filename = test_case["filename"]
    cv_path = TEST_CVS_DIR / cv_filename 
    puesto_seleccionado = test_case["puesto"]

    assert cv_path.is_file(), \
        f"Error: El archivo de CV '{cv_filename}' no se encontró en '{TEST_CVS_DIR}'. Asegúrate de que tus CVs originales estén en la ruta correcta y que el nombre en el Excel sea exacto."

    with open(cv_path, "rb") as f:
        files = {"archivo": (cv_filename, f.read(), "application/octet-stream")}
        data = {"puesto": puesto_seleccionado}

        print(f"\n--- Ejecutando prueba para CV: {cv_filename}, Puesto: {puesto_seleccionado} ---")
        response = client.post("/analizar", files=files, data=data) 

    assert response.status_code == 200, \
        f"La solicitud a la API falló para '{cv_filename}'. " \
        f"Código de estado HTTP: {response.status_code}. Respuesta del servidor: {response.text}"

    html_content = response.text 

    assert "id=\"resultadoContainer\"" in html_content, \
        f"La sección de resultados (id='resultadoContainer') no se encontró en el HTML para '{cv_filename}'. " \
        f"Revisa si hubo un error en la plantilla HTML o en la lógica de Jinja2. " \
        f"Contenido HTML (inicio): {html_content[:500]}..." 
    assert "Resultados Experimentales para:" in html_content, \
        f"El encabezado 'Resultados Experimentales para:' no se encontró en el HTML para '{cv_filename}'."

    match_total_score = re.search(r'<div class="puntaje-number">(\d+)</div>', html_content)
    
    assert match_total_score, \
        f"No se pudo extraer la puntuación total del HTML para '{cv_filename}'. " \
        f"Asegúrate de que la clase 'puntaje-number' exista en el HTML y contenga solo el número. " \
        f"HTML (parte relevante): {html_content[max(0, html_content.find('<div class=\"puntaje-number\">')-50):html_content.find('</div>')+50]}" 
    
    actual_total_score = int(match_total_score.group(1)) 

    print(f"  Puntuación Total Obtenida: {actual_total_score}")
    print(f"  Puntuación Total Esperada (según Excel): {test_case['expected_total_score_min']} - {test_case['expected_total_score_max']}")

    assert test_case["expected_total_score_min"] <= actual_total_score <= test_case["expected_total_score_max"], \
        f"FALLO: La puntuación total para '{cv_filename}' ({actual_total_score}) NO está en el rango esperado. " \
        f"Esperado: [{test_case['expected_total_score_min']}-{test_case['expected_total_score_max']}]"

    for section_name, expected_level in test_case["expected_section_levels"].items():
        # ¡CORRECCIÓN FINAL! Ajustamos el regex para capturar el contenido de la CUARTA <td>
        # re.escape() asegura que caracteres especiales en section_name no rompan el regex.
        # \s*<td>.*?</td>\s* se usa dos veces para saltar las celdas de "puntos" y "progreso".
        # Luego, (\s*(.*?)\s*) captura el contenido de la cuarta <td>.
        section_pattern = rf"<td><strong>{re.escape(section_name)}</strong></td>\s*<td>.*?</td>\s*<td>.*?</td>\s*<td>\s*(.*?)\s*</td>" 
        match_section_coherence = re.search(section_pattern, html_content, re.IGNORECASE | re.DOTALL)

        assert match_section_coherence, \
            f"No se encontró el mensaje de coherencia para la sección '{section_name}' en el HTML para '{cv_filename}'. " \
            f"Revisa la estructura HTML de tu tabla de resultados o el patrón regex. " \
            f"HTML relevante: {html_content[max(0, html_content.find(f'<td><strong>{section_name}</strong>')) : html_content.find('</tbody>') + 100]}"
        
        actual_coherence_message_raw = match_section_coherence.group(1).strip()
        
        actual_level = ""
        if "Excelente coherencia" in actual_coherence_message_raw:
            actual_level = "Alto"
        elif "Coherencia aceptable" in actual_coherence_message_raw:
            actual_level = "Medio"
        elif "Coherencia básica" in actual_coherence_message_raw:
            actual_level = "Bajo"
        elif "Baja o nula coherencia" in actual_coherence_message_raw:
            actual_level = "Muy Bajo" 
        else:
            # Si no se mapea, aún se puede intentar extraer el nivel directamente del HTML si la estructura lo permite.
            # Por ahora, se mantendrá como Desconocido si no hay match directo con los mensajes esperados.
            # Podríamos buscar el "nivel" que se pasa en el JSON de metricas_semanticas si fuera accesible.
            # Pero dado que estamos parseando HTML, nos basamos en los mensajes.
            # El mensaje de depuración anterior mostraba '8 / 10', que no contenía las frases.
            # La regex corregida debería capturar '⚠️ Coherencia aceptable [TF-IDF: 30%]'.
            # Si aún así no coincide, podría ser un problema de caché o de que el HTML no siempre imprime el mismo nivel de mensaje.
            actual_level = "Desconocido" 
        
        print(f"  - Sección '{section_name}': Nivel Obtenido='{actual_level}', Nivel Esperado='{expected_level}'")
        
        assert actual_level == expected_level, \
            f"FALLO: El nivel para la sección '{section_name}' en '{cv_filename}' no es el esperado. " \
            f"Esperado: '{expected_level}', Obtenido: '{actual_level}' (Mensaje en HTML: '{actual_coherence_message_raw}')"

