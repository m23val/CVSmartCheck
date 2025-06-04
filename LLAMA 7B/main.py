# main_enhanced.py - Versión mejorada con análisis semántico avanzado
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import requests
import tempfile
from pathlib import Path
import re
import uvicorn
from typing import Dict, List
import numpy as np
from collections import Counter
import time

app = FastAPI()
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class Llama2SemanticAnalyzerEnhanced:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.modelo_disponible = self.verificar_llama2()
        
        # Configuración de análisis semántico avanzado
        self.semantic_weights = {
            "coherencia_contextual": 0.25,     # Coherencia del contexto
            "relevancia_tecnica": 0.25,        # Relevancia técnica específica
            "densidad_informacion": 0.20,      # Densidad de información útil
            "especificidad_dominio": 0.15,     # Especificidad del dominio
            "modernidad_tecnologica": 0.15     # Actualidad tecnológica
        }
        
        # Mapas semánticos por puesto (expandidos)
        self.semantic_maps = {
            "desarrollador_full_stack": {
                "tecnologias_core": ["javascript", "typescript", "react", "node.js", "python", "html", "css"],
                "frameworks": ["express", "django", "flask", "vue", "angular", "next.js", "nuxt"],
                "bases_datos": ["mongodb", "postgresql", "mysql", "redis", "elasticsearch"],
                "herramientas": ["git", "docker", "kubernetes", "aws", "azure", "jenkins", "webpack"],
                "conceptos": ["api rest", "microservicios", "responsive", "spa", "pwa", "graphql"]
            },
            "cientifico_datos": {
                "lenguajes": ["python", "r", "sql", "scala", "julia", "matlab"],
                "ml_libs": ["scikit-learn", "tensorflow", "pytorch", "keras", "xgboost", "lightgbm"],
                "data_tools": ["pandas", "numpy", "matplotlib", "seaborn", "plotly", "jupyter"],
                "big_data": ["spark", "hadoop", "kafka", "airflow", "dask", "ray"],
                "estadistica": ["regresión", "clasificación", "clustering", "deep learning", "nlp", "cv"]
            }
        }
        
        # Perfiles ideales mejorados con más contexto semántico
        self.perfiles_ideales_enhanced = {
            "Desarrollador Full Stack": {
                "perfil": """Desarrollador full stack senior con dominio completo del ciclo de desarrollo. 
                Experiencia sólida en arquitecturas modernas, desarrollo frontend/backend, y deployment. 
                Capaz de diseñar, implementar y escalar aplicaciones web complejas usando tecnologías actuales.""",
                
                "habilidades": """Dominio avanzado de JavaScript/TypeScript, React/Vue, Node.js, Python. 
                Experiencia con bases de datos relacionales y NoSQL. Conocimiento profundo de APIs REST/GraphQL, 
                microservicios, contenedores Docker, CI/CD, y plataformas cloud.""",
                
                "experiencia": """Desarrollo end-to-end de aplicaciones web escalables. Implementación de 
                arquitecturas microservicios, integración de APIs, optimización de rendimiento, 
                trabajo colaborativo en equipos ágiles, mentoring técnico.""",
                
                "educacion": """Ingeniería en Sistemas, Ciencias de la Computación o equivalente. 
                Formación continua en tecnologías emergentes, certificaciones cloud, 
                contribuciones open source."""
            }
        }
    
    def verificar_llama2(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                modelos = response.json().get("models", [])
                return any("llama2:7b" in modelo.get("name", "") for modelo in modelos)
        except:
            pass
        return False
    
    def analizar_cv_semantico_avanzado(self, texto_cv: str, puesto: str) -> Dict:
        """Análisis semántico multi-dimensional mejorado"""
        if not self.modelo_disponible:
            raise Exception("Llama 2 no disponible")
        
        print(f"🦙 Iniciando análisis semántico avanzado para: {puesto}")
        
        # 1. Análisis de coherencia contextual con Llama 2
        coherencia_results = self.evaluar_coherencia_contextual(texto_cv, puesto)
        
        # 2. Análisis de densidad semántica
        densidad_results = self.calcular_densidad_semantica(texto_cv, puesto)
        
        # 3. Análisis de especificidad técnica
        especificidad_results = self.evaluar_especificidad_tecnica(texto_cv, puesto)
        
        # 4. Evaluación de modernidad tecnológica
        modernidad_results = self.evaluar_modernidad_tecnologica(texto_cv, puesto)
        
        # 5. Combinar todas las métricas
        puntuacion_final = self.combinar_metricas_avanzadas({
            "coherencia": coherencia_results,
            "densidad": densidad_results,
            "especificidad": especificidad_results,
            "modernidad": modernidad_results
        })
        
        # 6. Extraer secciones del CV para análisis detallado
        secciones_cv = self.extraer_secciones_cv(texto_cv)
        resultados_secciones = {}
        
        for seccion, contenido in secciones_cv.items():
            resultado_seccion = self.analizar_seccion_semantica(contenido, seccion, puesto)
            resultados_secciones[seccion] = resultado_seccion
        
        return {
            "puntuacion_global": puntuacion_final,
            "metricas_avanzadas": {
                "coherencia_contextual": coherencia_results,
                "densidad_semantica": densidad_results,
                "especificidad_tecnica": especificidad_results,
                "modernidad_tecnologica": modernidad_results
            },
            "analisis_secciones": resultados_secciones,
            "recomendaciones_semanticas": self.generar_recomendaciones_avanzadas(
                puntuacion_final, texto_cv, puesto
            )
        }
    
    def evaluar_coherencia_contextual(self, texto: str, puesto: str) -> Dict:
        """Evalúa la coherencia contextual usando Llama 2 - PROMPT OPTIMIZADO"""
        
        # Prompt más corto para mayor velocidad
        prompt = f"""Evalúa CV para {puesto}:

    {texto[:800]}

    Responde solo números 0-100:
    CONSISTENCIA: [número]
    ALINEACIÓN: [número]
    PROGRESIÓN: [número]
    INTEGRACIÓN: [número]

    CONSISTENCIA:"""

        print(f"🧠 Evaluando coherencia contextual...")
        respuesta = self.generar_respuesta(prompt)
        return self.parsear_metricas_coherencia(respuesta)

    # Y optimiza calcular_densidad_semantica:
    def calcular_densidad_semantica(self, texto: str, puesto: str) -> Dict:
        """Calcula densidad de información semánticamente relevante - OPTIMIZADO"""
        
        # Prompt más corto
        prompt = f"""Evalúa densidad técnica para {puesto}:

    {texto[:800]}

    DENSIDAD_TÉCNICA: [0-100]
    RELEVANCIA_CONTENIDO: [0-100]
    ESPECIFICIDAD_DATOS: [0-100]

    DENSIDAD_TÉCNICA:"""

        respuesta_llama = self.generar_respuesta(prompt)
        metricas_llama = self.parsear_densidad_respuesta(respuesta_llama)
        
        # Obtener mapa semántico para el puesto
        mapa_semantico = self.obtener_mapa_semantico(puesto)
        analisis_keywords = self.analizar_keywords_avanzado(texto, mapa_semantico)
        
        # Combinar resultados
        densidad_final = (
            metricas_llama.get("densidad_tecnica", 60) * 0.6 +
            analisis_keywords.get("cobertura_semantica", 60) * 0.4
        )
        
        return {
            "densidad_final": densidad_final,
            "metricas_llama": metricas_llama,
            "analisis_keywords": analisis_keywords
        }
    
    def calcular_densidad_semantica(self, texto: str, puesto: str) -> Dict:
        """Calcula densidad de información semánticamente relevante"""
        
        # Obtener mapa semántico para el puesto
        mapa_semantico = self.obtener_mapa_semantico(puesto)
        
        # Análisis con Llama 2
        prompt = f"""Evalúa la densidad de información técnica relevante en este CV para {puesto}.

TEXTO:
{texto[:1200]}

Evalúa:
1. DENSIDAD_TÉCNICA: ¿Cuánta información técnica útil contiene? (0-100)
2. RELEVANCIA_CONTENIDO: ¿Qué porcentaje del contenido es relevante? (0-100)
3. ESPECIFICIDAD_DATOS: ¿Qué tan específicos son los datos técnicos? (0-100)

DENSIDAD_TÉCNICA:"""

        respuesta_llama = self.generar_respuesta(prompt)
        metricas_llama = self.parsear_densidad_respuesta(respuesta_llama)
        
        # Análisis complementario de keywords
        analisis_keywords = self.analizar_keywords_avanzado(texto, mapa_semantico)
        
        # Combinar resultados
        densidad_final = (
            metricas_llama.get("densidad_tecnica", 50) * 0.6 +
            analisis_keywords.get("cobertura_semantica", 50) * 0.4
        )
        
        return {
            "densidad_final": densidad_final,
            "metricas_llama": metricas_llama,
            "analisis_keywords": analisis_keywords
        }
    
    def evaluar_especificidad_tecnica(self, texto: str, puesto: str) -> Dict:
        """Evalúa qué tan específico y detallado es el contenido técnico"""
        prompt = f"""Evalúa la especificidad técnica de este CV para {puesto}.

CV:
{texto[:1000]}

Analiza:
1. DETALLE_TÉCNICO: ¿Qué tan detalladas son las descripciones técnicas? (0-100)
2. MÉTRICAS_CUANTIFICABLES: ¿Incluye métricas y resultados específicos? (0-100)
3. PROFUNDIDAD_CONOCIMIENTO: ¿Demuestra conocimiento profundo vs superficial? (0-100)
4. APLICACIÓN_PRÁCTICA: ¿Describe aplicaciones prácticas específicas? (0-100)

DETALLE_TÉCNICO:"""

        respuesta = self.generar_respuesta(prompt)
        return self.parsear_especificidad_respuesta(respuesta)
    
    def evaluar_modernidad_tecnologica(self, texto: str, puesto: str) -> Dict:
        """Evalúa qué tan actualizadas son las tecnologías mencionadas"""
        prompt = f"""Evalúa la modernidad tecnológica del CV para {puesto}.

CV:
{texto[:1000]}

Evalúa:
1. TECNOLOGÍAS_ACTUALES: ¿Menciona tecnologías actuales y relevantes? (0-100)
2. TENDENCIAS_INDUSTRIA: ¿Está alineado con tendencias de la industria? (0-100)
3. EVOLUCIÓN_TECNOLÓGICA: ¿Muestra adaptación a cambios tecnológicos? (0-100)

TECNOLOGÍAS_ACTUALES:"""

        respuesta = self.generar_respuesta(prompt)
        return self.parsear_modernidad_respuesta(respuesta)
    
    def analizar_seccion_semantica(self, contenido: str, seccion: str, puesto: str) -> Dict:
        """Análisis semántico específico por sección - CON CORRECCIÓN PARA FORMATO"""
        
        # CASO ESPECIAL: Análisis de FORMATO sin Llama 2
        if seccion.lower() == "formato":
            return self.analizar_formato_cv(contenido)
        
        # Para el resto de secciones, usar Llama 2 como antes
        prompt = f"""Evalúa sección "{seccion}" para {puesto}:

    {contenido[:600]}

    Responde solo números 0-100:
    COMPLETITUD: [número]
    RELEVANCIA: [número]  
    CALIDAD: [número]

    COMPLETITUD:"""

        print(f"🔍 Analizando sección: {seccion} (prompt: {len(prompt)} chars)")
        
        respuesta = self.generar_respuesta(prompt)
        
        if not respuesta or "Error" in respuesta:
            print(f"❌ Error en análisis de {seccion}: {respuesta}")
            return {
                "puntuacion_seccion": 60.0,
                "metricas_detalle": {
                    "completitud": 60,
                    "relevancia_seccion": 60,
                    "calidad_informacion": 60,
                    "explicacion_seccion": f"Análisis de {seccion} con valores por defecto"
                },
                "nivel": "Medio",
                "explicacion": f"Sección {seccion} evaluada"
            }
        
        # Parsear con función corregida
        metricas = self.parsear_respuesta_seccion(respuesta)
        
        # Calcular puntuación promedio
        puntuacion_seccion = (
            metricas.get("completitud", 60) +
            metricas.get("relevancia_seccion", 60) +
            metricas.get("calidad_informacion", 60)
        ) / 3
        
        # Determinar nivel
        if puntuacion_seccion >= 80:
            nivel = "Alto"
        elif puntuacion_seccion >= 60:
            nivel = "Medio"
        else:
            nivel = "Bajo"
        
        print(f"✅ {seccion}: {puntuacion_seccion:.1f}% ({nivel})")
        
        return {
            "puntuacion_seccion": round(puntuacion_seccion, 1),
            "metricas_detalle": metricas,
            "nivel": nivel,
            "explicacion": metricas.get("explicacion_seccion", "Análisis completado")
        }
    def analizar_formato_cv(self, contenido_cv: str) -> Dict:
        """Análisis específico del formato del CV sin usar Llama 2"""
        
        print("📋 Analizando formato del CV...")
        
        texto = contenido_cv.lower()
        puntuacion = 0
        criterios_cumplidos = []
        
        # Criterio 1: Estructura de secciones (25 puntos)
        secciones_esperadas = ["perfil", "habilidades", "experiencia", "educación", "certificados", "idiomas", "contacto"]
        secciones_encontradas = 0
        
        for seccion in secciones_esperadas:
            if seccion in texto or seccion.replace("ó", "o") in texto:
                secciones_encontradas += 1
        
        if secciones_encontradas >= 6:
            puntuacion += 25
            criterios_cumplidos.append("✅ Estructura completa de secciones")
        elif secciones_encontradas >= 4:
            puntuacion += 18
            criterios_cumplidos.append("⚠️ Estructura básica de secciones")
        else:
            criterios_cumplidos.append("❌ Estructura de secciones incompleta")
        
        # Criterio 2: Información de contacto (20 puntos)
        contactos = ["email", "teléfono", "linkedin", "github", "@", "+", "telefono"]
        contactos_encontrados = sum(1 for contacto in contactos if contacto in texto)
        
        if contactos_encontrados >= 3:
            puntuacion += 20
            criterios_cumplidos.append("✅ Información de contacto completa")
        elif contactos_encontrados >= 2:
            puntuacion += 15
            criterios_cumplidos.append("⚠️ Información de contacto básica")
        else:
            criterios_cumplidos.append("❌ Información de contacto insuficiente")
        
        # Criterio 3: Organización y legibilidad (20 puntos)
        # Verificar uso de bullets, numeración, espaciado
        indicadores_organizacion = ["•", "-", "*", "1.", "2.", "\n\n", ":**"]
        organizacion_encontrada = sum(1 for ind in indicadores_organizacion if ind in contenido_cv)
        
        if organizacion_encontrada >= 4:
            puntuacion += 20
            criterios_cumplidos.append("✅ Excelente organización visual")
        elif organizacion_encontrada >= 2:
            puntuacion += 15
            criterios_cumplidos.append("⚠️ Organización aceptable")
        else:
            criterios_cumplidos.append("❌ Organización visual mejorable")
        
        # Criterio 4: Longitud apropiada (15 puntos)
        palabras = len(contenido_cv.split())
        
        if 300 <= palabras <= 800:
            puntuacion += 15
            criterios_cumplidos.append("✅ Longitud óptima del CV")
        elif 200 <= palabras <= 1000:
            puntuacion += 12
            criterios_cumplidos.append("⚠️ Longitud aceptable")
        else:
            if palabras < 200:
                criterios_cumplidos.append("❌ CV demasiado corto")
            else:
                criterios_cumplidos.append("❌ CV demasiado extenso")
        
        # Criterio 5: Consistencia (10 puntos)
        # Verificar que no hay errores obvios de formato
        lineas = contenido_cv.split('\n')
        lineas_con_contenido = [l for l in lineas if len(l.strip()) > 0]
        
        if len(lineas_con_contenido) >= 10:  # CV con suficiente contenido estructurado
            puntuacion += 10
            criterios_cumplidos.append("✅ Formato consistente")
        else:
            criterios_cumplidos.append("❌ Formato inconsistente")
        
        # Criterio 6: Fechas y datos específicos (10 puntos)
        indicadores_fechas = ["2020", "2021", "2022", "2023", "2024", "2025", "presente"]
        fechas_encontradas = sum(1 for fecha in indicadores_fechas if fecha in texto)
        
        if fechas_encontradas >= 2:
            puntuacion += 10
            criterios_cumplidos.append("✅ Información temporal presente")
        else:
            criterios_cumplidos.append("❌ Falta información temporal")
        
        # Determinar nivel basado en puntuación
        if puntuacion >= 80:
            nivel = "Alto"
            explicacion = "Formato excelente del CV"
        elif puntuacion >= 60:
            nivel = "Medio"
            explicacion = "Formato aceptable del CV"
        else:
            nivel = "Bajo"
            explicacion = "Formato del CV necesita mejoras"
        
        # Generar explicación detallada
        explicacion_detallada = f"Formato evaluado: {puntuacion}/100. " + " | ".join(criterios_cumplidos[:2])
        
        print(f"📋 Formato del CV: {puntuacion}/100 ({nivel})")
        print(f"📊 Criterios: {len(criterios_cumplidos)} evaluados")
        
        return {
            "puntuacion_seccion": float(puntuacion),
            "metricas_detalle": {
                "completitud": puntuacion,
                "relevancia_seccion": puntuacion,
                "calidad_informacion": puntuacion,
                "explicacion_seccion": explicacion_detallada
            },
            "nivel": nivel,
            "explicacion": explicacion
        }

    def parsear_metricas_coherencia(self, respuesta: str) -> Dict:
        """Parsea métricas de coherencia contextual - VERSIÓN CORREGIDA"""
        print(f"🔍 Parsing coherencia: '{respuesta[:150]}...'")
        
        metricas = {"consistencia": 50, "alineacion": 50, "progresion": 50, "integracion": 50}
        
        # Buscar cada métrica
        for metrica in ["consistencia", "alineacion", "progresion", "integracion"]:
            patron = rf"{metrica}:\s*(\d{{1,3}})"
            match = re.search(patron, respuesta, re.IGNORECASE)
            if match:
                valor = int(match.group(1))
                if 0 <= valor <= 100:
                    metricas[metrica] = valor
                    print(f"✅ {metrica}: {valor}")
                    continue
            
            # Heurística si no encuentra números
            respuesta_lower = respuesta.lower()
            if any(word in respuesta_lower for word in ['excelente', 'muy bueno', 'alto', 'óptimo']):
                metricas[metrica] = 85
                print(f"🎯 {metrica}: 85 (heurística ALTO)")
            elif any(word in respuesta_lower for word in ['bueno', 'aceptable', 'medio']):
                metricas[metrica] = 70
                print(f"🎯 {metrica}: 70 (heurística MEDIO)")
            elif any(word in respuesta_lower for word in ['malo', 'bajo', 'pobre']):
                metricas[metrica] = 30
                print(f"🎯 {metrica}: 30 (heurística BAJO)")
        
        # Buscar explicación
        explicacion = "Análisis de coherencia completado"
        if "explicación:" in respuesta.lower():
            explicacion = respuesta.lower().split("explicación:")[1].strip()[:120]
        
        metricas["explicacion"] = explicacion
        return metricas
    
    def parsear_respuesta_seccion(self, respuesta: str) -> Dict:
        """Parsea respuesta de análisis por sección - VERSIÓN CORREGIDA"""
        print(f"🔍 Parsing sección: '{respuesta[:100]}...'")
        
        metricas = {
            "completitud": 50,
            "relevancia_seccion": 50,
            "calidad_informacion": 50,
            "explicacion_seccion": "Análisis completado"
        }
        
        if not respuesta or len(respuesta.strip()) < 5 or "Error" in respuesta:
            print("⚠️ Respuesta inválida para sección")
            return metricas
        
        # Buscar números en la respuesta
        numeros = re.findall(r'\b(\d{1,3})\b', respuesta)
        numeros_validos = [int(n) for n in numeros if 0 <= int(n) <= 100]
        
        print(f"🔢 Números encontrados: {numeros_validos}")
        
        if len(numeros_validos) >= 3:
            metricas["completitud"] = numeros_validos[0]
            metricas["relevancia_seccion"] = numeros_validos[1] 
            metricas["calidad_informacion"] = numeros_validos[2]
            print(f"✅ Usando números: {numeros_validos[:3]}")
        elif len(numeros_validos) >= 1:
            valor = numeros_validos[0]
            metricas["completitud"] = valor
            metricas["relevancia_seccion"] = valor
            metricas["calidad_informacion"] = valor
            print(f"✅ Valor único: {valor}")
        else:
            # Heurística basada en palabras clave
            respuesta_lower = respuesta.lower()
            
            if any(word in respuesta_lower for word in ['excelente', 'muy bueno', 'alto', 'óptimo', 'perfecto']):
                valor = 85
                print(f"🎯 Heurística ALTA: {valor}")
            elif any(word in respuesta_lower for word in ['bueno', 'aceptable', 'medio', 'adecuado']):
                valor = 72
                print(f"🎯 Heurística MEDIA: {valor}")
            elif any(word in respuesta_lower for word in ['malo', 'bajo', 'insuficiente', 'pobre']):
                valor = 35
                print(f"🎯 Heurística BAJA: {valor}")
            else:
                valor = 65
                print(f"🎯 Heurística DEFAULT: {valor}")
            
            metricas["completitud"] = valor
            metricas["relevancia_seccion"] = valor
            metricas["calidad_informacion"] = valor
        
        # Buscar explicación
        if "explicación" in respuesta.lower():
            partes = respuesta.lower().split("explicación")
            if len(partes) > 1:
                explicacion = partes[1].strip()
                if explicacion.startswith(':'):
                    explicacion = explicacion[1:].strip()
                metricas["explicacion_seccion"] = explicacion[:100]
        
        return metricas
    
    def parsear_densidad_respuesta(self, respuesta: str) -> Dict:
        """Parsea respuesta de análisis de densidad"""
        metricas = {"densidad_tecnica": 50, "relevancia_contenido": 50, "especificidad_datos": 50}
        
        for metrica in ["densidad_tecnica", "relevancia_contenido", "especificidad_datos"]:
            metrica_buscar = metrica.replace("_", "_")
            patron = rf"{metrica_buscar}:\s*(\d{{1,3}})"
            match = re.search(patron, respuesta, re.IGNORECASE)
            if match:
                valor = int(match.group(1))
                if 0 <= valor <= 100:
                    metricas[metrica] = valor
        
        return metricas
    
    def parsear_especificidad_respuesta(self, respuesta: str) -> Dict:
        """Parsea respuesta de análisis de especificidad"""
        metricas = {
            "detalle_tecnico": 50,
            "metricas_cuantificables": 50,
            "profundidad_conocimiento": 50,
            "aplicacion_practica": 50
        }
        
        for metrica in metricas.keys():
            patron = rf"{metrica.replace('_', '_')}:\s*(\d{{1,3}})"
            match = re.search(patron, respuesta, re.IGNORECASE)
            if match:
                valor = int(match.group(1))
                if 0 <= valor <= 100:
                    metricas[metrica] = valor
        
        return metricas
    
    def parsear_modernidad_respuesta(self, respuesta: str) -> Dict:
        """Parsea respuesta de análisis de modernidad"""
        metricas = {
            "tecnologias_actuales": 50,
            "tendencias_industria": 50,
            "evolucion_tecnologica": 50
        }
        
        for metrica in metricas.keys():
            patron = rf"{metrica.replace('_', '_')}:\s*(\d{{1,3}})"
            match = re.search(patron, respuesta, re.IGNORECASE)
            if match:
                valor = int(match.group(1))
                if 0 <= valor <= 100:
                    metricas[metrica] = valor
        
        return metricas
    
    def combinar_metricas_avanzadas(self, todas_metricas: Dict) -> float:
        """Combina todas las métricas para una puntuación final"""
        coherencia = todas_metricas.get("coherencia", {})
        densidad = todas_metricas.get("densidad", {})
        especificidad = todas_metricas.get("especificidad", {})
        modernidad = todas_metricas.get("modernidad", {})
        
        puntuacion_coherencia = self.extraer_puntuacion_principal(coherencia)
        puntuacion_densidad = densidad.get("densidad_final", 50)
        puntuacion_especificidad = self.extraer_puntuacion_principal(especificidad)
        puntuacion_modernidad = self.extraer_puntuacion_principal(modernidad)
        
        puntuacion_final = (
            puntuacion_coherencia * self.semantic_weights["coherencia_contextual"] +
            puntuacion_densidad * self.semantic_weights["densidad_informacion"] +
            puntuacion_especificidad * self.semantic_weights["especificidad_dominio"] +
            puntuacion_modernidad * self.semantic_weights["modernidad_tecnologica"] +
            65 * self.semantic_weights["relevancia_tecnica"]  # Base score mejorado
        )
        
        return min(100, max(0, puntuacion_final))
    
    def generar_recomendaciones_avanzadas(self, puntuacion: float, texto: str, puesto: str) -> List[str]:
        """Genera recomendaciones basadas en el análisis semántico completo"""
        recomendaciones = []
        
        if puntuacion < 70:
            prompt_principal = f"""Para un CV de {puesto} con {puntuacion:.1f}% de coherencia semántica, da 3 recomendaciones específicas para mejorar. Máximo 60 palabras cada una.

CV:
{texto[:1000]}

Recomendación 1:"""
            
            respuesta = self.generar_respuesta(prompt_principal)
            recomendaciones_texto = self.extraer_recomendaciones_multiples(respuesta)
            recomendaciones.extend(recomendaciones_texto)
        
        mapa_semantico = self.obtener_mapa_semantico(puesto)
        analisis_keywords = self.analizar_keywords_avanzado(texto, mapa_semantico)
        categorias_bajas = self.identificar_categorias_bajas(analisis_keywords)
        
        for categoria in categorias_bajas[:2]:
            prompt_categoria = f"""Para {puesto}, la categoría "{categoria}" tiene baja cobertura. Da una recomendación específica de 40 palabras."""
            
            recomendacion = self.generar_respuesta(prompt_categoria)
            if len(recomendacion.strip()) > 15:
                recomendaciones.append(f"🔧 {categoria.title()}: {recomendacion.strip()}")
        
        return recomendaciones[:4]
    
    def obtener_mapa_semantico(self, puesto: str) -> Dict:
        """Obtiene el mapa semántico correspondiente al puesto"""
        puesto_lower = puesto.lower()
        
        if any(term in puesto_lower for term in ["full stack", "desarrollador", "frontend", "backend"]):
            return self.semantic_maps.get("desarrollador_full_stack", {})
        elif any(term in puesto_lower for term in ["datos", "data", "machine learning", "científico"]):
            return self.semantic_maps.get("cientifico_datos", {})
        else:
            return self.semantic_maps.get("desarrollador_full_stack", {})
    
    def analizar_keywords_avanzado(self, texto: str, mapa_semantico: Dict) -> Dict:
        """Análisis avanzado de keywords semánticas"""
        texto_lower = texto.lower()
        resultados = {}
        
        total_keywords = 0
        total_encontradas = 0
        
        for categoria, keywords in mapa_semantico.items():
            encontradas = []
            for keyword in keywords:
                if keyword.lower() in texto_lower:
                    encontradas.append(keyword)
            
            cobertura = (len(encontradas) / len(keywords)) * 100 if keywords else 0
            
            resultados[categoria] = {
                "encontradas": encontradas,
                "total": len(keywords),
                "cobertura": cobertura
            }
            
            total_keywords += len(keywords)
            total_encontradas += len(encontradas)
        
        cobertura_general = (total_encontradas / total_keywords) * 100 if total_keywords > 0 else 0
        
        return {
            "por_categoria": resultados,
            "cobertura_semantica": cobertura_general,
            "total_encontradas": total_encontradas,
            "total_keywords": total_keywords
        }
    
    def identificar_categorias_bajas(self, analisis_keywords: Dict) -> List[str]:
        """Identifica categorías con baja cobertura semántica"""
        categorias_bajas = []
        
        for categoria, datos in analisis_keywords.get("por_categoria", {}).items():
            if datos.get("cobertura", 0) < 40:
                categorias_bajas.append(categoria)
        
        categorias_bajas.sort(key=lambda cat: 
            analisis_keywords["por_categoria"][cat].get("cobertura", 0))
        
        return categorias_bajas
    
    def extraer_puntuacion_principal(self, metricas: Dict) -> float:
        """Extrae la puntuación principal de un conjunto de métricas - CORREGIDA"""
        if not metricas:
            return 65.0  # Default mejorado
        
        valores_numericos = [v for v in metricas.values() if isinstance(v, (int, float)) and v != 50]
        
        if valores_numericos:
            return sum(valores_numericos) / len(valores_numericos)
        else:
            return 65.0
    
    def extraer_recomendaciones_multiples(self, respuesta: str) -> List[str]:
        """Extrae múltiples recomendaciones de una respuesta"""
        recomendaciones = []
        
        lineas = respuesta.split('\n')
        
        for linea in lineas:
            linea = linea.strip()
            if len(linea) > 30 and any(char.isalpha() for char in linea):
                linea_limpia = re.sub(r'^[\d\.\-\*\s]+', '', linea).strip()
                if len(linea_limpia) > 20:
                    recomendaciones.append(f"🦙 {linea_limpia}")
        
        return recomendaciones[:3]
    
    def determinar_nivel(self, puntuacion: float) -> str:
        """Determina el nivel basado en la puntuación"""
        if puntuacion >= 80:
            return "Alto"
        elif puntuacion >= 60:
            return "Medio"
        else:
            return "Bajo"
    
    def extraer_secciones_cv(self, texto_cv: str) -> Dict[str, str]:
        """Extrae secciones del CV"""
        secciones = {}
        
        patrones = {
            "perfil": r"(?:perfil|resumen|objetivo).*?(?=\n.*?(?:experiencia|habilidades|educación)|\Z)",
            "habilidades": r"(?:habilidades|competencias|skills).*?(?=\n.*?(?:experiencia|educación|certificados)|\Z)",
            "experiencia": r"(?:experiencia|laboral|proyectos).*?(?=\n.*?(?:educación|habilidades|certificados)|\Z)",
            "educacion": r"(?:educación|formación|universidad|estudios).*?(?=\n.*?(?:experiencia|certificados|idiomas)|\Z)",
            "certificados": r"(?:certificados|certificaciones|cursos).*?(?=\n.*?(?:idiomas|contacto)|\Z)",
            "idiomas": r"(?:idiomas|lenguajes|languages).*?(?=\n.*?(?:contacto|referencias)|\Z)",
            "datos": r"(?:contacto|email|teléfono|linkedin|github).*?(?=\n.*?(?:perfil|resumen)|\Z)"
        }
        
        for seccion, patron in patrones.items():
            match = re.search(patron, texto_cv, re.IGNORECASE | re.DOTALL)
            if match:
                secciones[seccion] = match.group(0)
            else:
                secciones[seccion] = texto_cv[:500]
        
        secciones["formato"] = texto_cv
        return secciones
    
    def generar_respuesta(self, prompt: str) -> str:
        """Genera respuesta usando Llama 2 - SIN TIMEOUT, ESPERA LO NECESARIO"""
        try:
            # Optimizar prompt para que sea más rápido
            prompt_optimizado = prompt[:1000]  # Limitar a 1000 caracteres
            
            payload = {
                "model": "llama2:7b",
                "prompt": prompt_optimizado,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "top_p": 0.9,
                    "max_tokens": 200,     # Reducido para ser más rápido
                    "num_ctx": 1024,       # Contexto reducido = más rápido
                    "num_predict": 150,    # Predicciones limitadas
                    "repeat_penalty": 1.1
                }
            }
            
            print(f"🦙 Llamando a Llama 2... (sin timeout, esperando respuesta)")
            print(f"📝 Prompt length: {len(prompt_optimizado)} chars")
            
            # SIN TIMEOUT - espera lo que sea necesario
            response = requests.post(
                self.ollama_url, 
                json=payload
                # ← NO timeout parameter = espera infinito
            )
            
            if response.status_code == 200:
                result = response.json().get("response", "").strip()
                
                if result:
                    print(f"✅ Llama 2 respondió exitosamente: '{result[:100]}...'")
                    return result
                else:
                    print("⚠️ Llama 2 devolvió respuesta vacía")
                    return "Error: Respuesta vacía de Llama 2"
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"Response: {response.text}")
                return f"Error HTTP: {response.status_code}"
                
        except requests.exceptions.ConnectionError as e:
            print(f"❌ Error de conexión: {e}")
            return "Error: No se puede conectar a Ollama. ¿Está corriendo 'ollama serve'?"
            
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            return f"Error: {str(e)}"

# Inicializar el analizador
llama2_analyzer = Llama2SemanticAnalyzerEnhanced()

# Funciones de procesamiento de archivos
def extraer_texto_pdf(ruta: str) -> str:
    try:
        import pypdf
        with open(ruta, 'rb') as file:
            reader = pypdf.PdfReader(file)
            return "\n".join(page.extract_text() for page in reader.pages if page.extract_text()).strip()
    except ImportError:
        return "Error: pip install pypdf"
    except Exception as e:
        return f"Error PDF: {str(e)}"

def extraer_texto_docx(ruta: str) -> str:
    try:
        from docx import Document
        doc = Document(ruta)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip()).strip()
    except ImportError:
        return "Error: pip install python-docx"
    except Exception as e:
        return f"Error DOCX: {str(e)}"

async def procesar_archivo(archivo: UploadFile) -> str:
    try:
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / archivo.filename
        
        content = await archivo.read()
        with open(temp_file, "wb") as f:
            f.write(content)
        
        if archivo.filename.lower().endswith('.pdf'):
            texto = extraer_texto_pdf(str(temp_file))
        elif archivo.filename.lower().endswith('.docx'):
            texto = extraer_texto_docx(str(temp_file))
        else:
            texto = "Formato no soportado"
        
        try:
            temp_file.unlink()
            temp_dir.rmdir()
        except:
            pass
        
        return texto
    except Exception as e:
        return f"Error: {str(e)}"

# Rutas de la aplicación
@app.get("/", response_class=HTMLResponse)
async def mostrar_formulario(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "resultado": None,
        "error": None,
        "detalles": [],
        "recomendaciones": [],
        "contenido_cv": "",
        "nombre": "",
        "puesto": "",
        "llama2_disponible": llama2_analyzer.modelo_disponible
    })

@app.post("/analizar", response_class=HTMLResponse)
async def analizar_cv_llama2_enhanced(request: Request, archivo: UploadFile = File(...), puesto: str = Form(...)):
    try:
        print(f"\n🦙 INICIANDO ANÁLISIS SEMÁNTICO AVANZADO")
        print(f"📋 Puesto: {puesto}")
        print(f"📄 Archivo: {archivo.filename}")
        
        if not llama2_analyzer.modelo_disponible:
            raise ValueError("Llama 2 no disponible. Ejecuta: ollama pull llama2:7b")
        
        if not puesto or puesto.startswith("--"):
            raise ValueError("Selecciona un puesto válido")
        
        if not archivo.filename.lower().endswith((".pdf", ".docx")):
            raise ValueError("Solo PDF o DOCX")
        
        texto = await procesar_archivo(archivo)
        if len(texto.strip()) < 50:
            raise ValueError("Texto insuficiente")
        
        # Análisis semántico avanzado
        resultados_avanzados = llama2_analyzer.analizar_cv_semantico_avanzado(texto, puesto)
        
        # Convertir resultados para la UI
        resultados_ui = []
        mapeo_secciones = {
            "perfil": "Perfil",
            "habilidades": "Habilidades", 
            "experiencia": "Experiencia",
            "educacion": "Educación",
            "certificados": "Certificados",
            "idiomas": "Idiomas",
            "datos": "Datos",
            "formato": "Formato"
        }
        
        # Procesar resultados por sección
        for seccion_key, datos in resultados_avanzados["analisis_secciones"].items():
            seccion_nombre = mapeo_secciones.get(seccion_key, seccion_key.capitalize())
            puntuacion = datos["puntuacion_seccion"]
            nivel = datos["nivel"]
            explicacion = datos["explicacion"]
            
            if nivel == "Alto":
                mensaje = f"✅ Excelente coherencia semántica ({puntuacion:.1f}%): {explicacion}"
            elif nivel == "Medio":
                mensaje = f"⚠️ Coherencia semántica aceptable ({puntuacion:.1f}%): {explicacion}"
            else:
                mensaje = f"❌ Baja coherencia semántica ({puntuacion:.1f}%): {explicacion}"
            
            resultados_ui.append((seccion_nombre, round(puntuacion/10), 10, mensaje))
        
        puntaje_total = sum(p for _, p, _, _ in resultados_ui)
        
        # Métricas semánticas avanzadas para la UI
        metricas_avanzadas = []
        puntuacion_global = resultados_avanzados["puntuacion_global"]
        
        for seccion_key, datos in resultados_avanzados["analisis_secciones"].items():
            seccion_nombre = mapeo_secciones.get(seccion_key, seccion_key.capitalize())
            puntuacion_seccion = datos["puntuacion_seccion"]
            nivel = datos["nivel"]
            
            metricas_avanzadas.append({
                "seccion": seccion_nombre,
                "similitud": round(puntuacion_seccion),
                "nivel": nivel,
                "ajuste": round(puntuacion_seccion - 70, 1)  # Diferencia respecto a baseline
            })
        
        print(f"🎯 ANÁLISIS SEMÁNTICO AVANZADO COMPLETADO")
        print(f"📊 Puntuación global: {puntuacion_global:.1f}%")
        print(f"📈 Secciones analizadas: {len(resultados_avanzados['analisis_secciones'])}")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "resultado": puntaje_total,
            "detalles": resultados_ui,
            "nombre": archivo.filename,
            "contenido_cv": texto[:15000] + ("..." if len(texto) > 15000 else ""),
            "recomendaciones": resultados_avanzados["recomendaciones_semanticas"],
            "puesto": puesto,
            "metricas_semanticas": metricas_avanzadas,
            "puntuacion_global_semantica": round(puntuacion_global, 1),
            "modo_experimental": True,
            "llama2_disponible": True,
            "analisis_avanzado": True
        })
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return templates.TemplateResponse("index.html", {
            "request": request,
            "error": f"Error: {str(e)}",
            "resultado": None,
            "detalles": [],
            "recomendaciones": [],
            "contenido_cv": "",
            "nombre": "",
            "puesto": "",
            "llama2_disponible": llama2_analyzer.modelo_disponible
        })

if __name__ == "__main__":
    print("🦙 Iniciando servidor Llama 2 semántico avanzado en puerto 8002...")
    uvicorn.run(app, host="127.0.0.1", port=8002, reload=True)