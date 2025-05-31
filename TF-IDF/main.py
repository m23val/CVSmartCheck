from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import tempfile
from pathlib import Path
import re
from typing import List, Dict, Tuple, Set
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

app = FastAPI()

# Crear directorios si no existen
os.makedirs("static", exist_ok=True)
os.makedirs("templates", exist_ok=True)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ===== MODELO EXPERIMENTAL DE ANÁLISIS SEMÁNTICO CORREGIDO =====
class TFIDFSemanticAnalyzer:
    """
    Implementación experimental CORREGIDA de análisis semántico para CVs
    utilizando TF-IDF y similitud coseno con evaluación más justa.
    """
    
    def __init__(self):
        """Inicializa el analizador con criterios más realistas"""
        # Textos ideales SIMPLIFICADOS y más accesibles
        self.textos_ideales = {
            "Desarrollador Full Stack": {
                "perfil": "desarrollador programador software web frontend backend aplicaciones tecnología sistemas",
                "experiencia": "desarrollo programación proyectos aplicaciones web software sistemas experiencia trabajo",
                "habilidades": "javascript html css react angular vue node python java php sql base datos git",
                "educacion": "ingeniería sistemas informática programación universidad instituto estudios tecnología",
                "certificados": "certificación curso capacitación formación desarrollo programación tecnología",
                "idiomas": "inglés español comunicación técnico internacional documentación",
                "datos": "contacto email teléfono linkedin github portafolio información personal",
                "formato": "organizado estructurado claro profesional secciones información completa"
            },
            "Administrador de Bases de Datos (DBA)": {
                "perfil": "administrador base datos sql servidor gestión análisis sistemas información",
                "experiencia": "administración base datos sql servidor gestión análisis proyectos sistemas",
                "habilidades": "sql mysql postgresql oracle mongodb base datos consultas servidor administración",
                "educacion": "ingeniería sistemas informática base datos universidad instituto estudios",
                "certificados": "certificación sql base datos administración oracle mysql postgresql",
                "idiomas": "inglés español técnico comunicación documentación internacional",
                "datos": "contacto email teléfono linkedin información profesional",
                "formato": "estructurado organizado profesional secciones información técnica"
            },
            "Ingeniero DevOps": {
                "perfil": "devops automatización infraestructura cloud contenedores deployment sistemas",
                "experiencia": "devops automatización infraestructura cloud deployment sistemas proyectos",
                "habilidades": "docker kubernetes aws azure terraform ansible jenkins git linux automatización",
                "educacion": "ingeniería sistemas informática cloud devops universidad instituto",
                "certificados": "certificación aws azure kubernetes docker devops cloud infraestructura",
                "idiomas": "inglés español técnico internacional cloud documentación",
                "datos": "contacto email linkedin github portafolio técnico información",
                "formato": "técnico estructurado métricas proyectos infraestructura organizado"
            },
            "Científico de Datos / ML Engineer": {
                "perfil": "datos análisis estadística machine learning python ciencia investigación",
                "experiencia": "análisis datos estadística machine learning python proyectos investigación",
                "habilidades": "python r sql pandas numpy machine learning estadística análisis visualización tableau power bi excel",
                "educacion": "ingeniería sistemas matemáticas estadística ciencia datos universidad",
                "certificados": "certificación análisis datos python machine learning estadística coursera",
                "idiomas": "inglés español científico técnico análisis comunicación",
                "datos": "contacto email linkedin github proyectos datos información",
                "formato": "analítico cuantificado métricas proyectos datos organizado estructurado"
            },
            "Desarrollador de Aplicaciones Móviles": {
                "perfil": "móvil mobile aplicaciones ios android desarrollo programación apps",
                "experiencia": "desarrollo móvil aplicaciones ios android mobile programación proyectos",
                "habilidades": "swift kotlin java react native flutter ios android mobile desarrollo programación",
                "educacion": "ingeniería desarrollo software móvil programación universidad instituto",
                "certificados": "certificación ios android mobile desarrollo swift kotlin programación",
                "idiomas": "inglés español técnico móvil documentación internacional",
                "datos": "contacto email portafolio apps github linkedin información",
                "formato": "móvil apps desarrolladas proyectos portafolio organizado profesional"
            }
        }
        
        # Palabras clave EXPANDIDAS con mayor cobertura
        self.palabras_clave = {
            "Desarrollador Full Stack": [
                # Lenguajes de programación
                "javascript", "js", "typescript", "python", "java", "php", "html", "css", "sql",
                # Frameworks y bibliotecas
                "react", "angular", "vue", "node", "express", "django", "flask", "laravel",
                # Conceptos generales
                "desarrollo", "programación", "web", "frontend", "backend", "fullstack", "full stack",
                "api", "rest", "base de datos", "bases de datos", "git", "github", "software"
            ],
            "Administrador de Bases de Datos (DBA)": [
                # Sistemas de BD
                "sql", "mysql", "postgresql", "oracle", "mongodb", "redis", "sqlite",
                # Conceptos de BD
                "base de datos", "bases de datos", "bd", "database", "consultas", "queries",
                "administración", "gestión", "servidor", "server", "backup", "recovery",
                # Análisis y optimización
                "análisis", "optimización", "performance", "índices", "reporting", "datos", "data"
            ],
            "Ingeniero DevOps": [
                # Herramientas principales
                "docker", "kubernetes", "terraform", "ansible", "jenkins", "git",
                # Cloud providers
                "aws", "azure", "gcp", "google cloud", "cloud", "nube",
                # Conceptos DevOps
                "devops", "automatización", "ci/cd", "deployment", "infraestructura",
                "contenedores", "containers", "pipeline", "monitoreo", "linux", "scripting"
            ],
            "Científico de Datos / ML Engineer": [
                # Lenguajes
                "python", "r", "sql", "scala",
                # Bibliotecas de datos
                "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly",
                # Machine Learning
                "machine learning", "ml", "tensorflow", "pytorch", "scikit-learn", "keras",
                # Conceptos generales
                "análisis", "datos", "data", "estadística", "statistics", "visualización",
                "ciencia de datos", "data science", "big data", "tableau", "power bi", "excel"
            ],
            "Desarrollador de Aplicaciones Móviles": [
                # Lenguajes móviles
                "swift", "kotlin", "java", "dart", "objective-c",
                # Frameworks
                "react native", "flutter", "ionic", "xamarin",
                # Plataformas
                "ios", "android", "mobile", "móvil", "app", "aplicación",
                # Herramientas
                "xcode", "android studio", "firebase", "desarrollo móvil", "programación móvil"
            ]
        }
        
        print("✅ Analizador semántico TF-IDF CORREGIDO inicializado")
    
    def extraer_secciones_cv(self, texto_completo):
        """Extrae secciones del CV de manera más inteligente y flexible"""
        secciones = {}
        texto_lower = texto_completo.lower()
        
        # Patrones de detección MÁS SIMPLES y EFECTIVOS
        patrones_seccion = {
            "perfil": [
                r"(?:perfil|resumen|objetivo|presentación|sobre mí|summary).*?(?=\n.*?(?:experiencia|habilidades|educación|formación)|\Z)",
                r"^(.{100,400}?)(?=\n.*?(?:experiencia|habilidades|educación)|\Z)"  # Primeros párrafos como perfil
            ],
            "habilidades": [
                r"(?:habilidades|competencias|skills|conocimientos|tecnologías|lenguajes).*?(?=\n.*?(?:experiencia|educación|certificados|idiomas)|\Z)",
                r"(?:python|javascript|java|sql|html|css|react|angular).*?(?=\n.*?(?:experiencia|educación)|\Z)"
            ],
            "experiencia": [
                r"(?:experiencia|laboral|profesional|trabajo|proyectos|práticas).*?(?=\n.*?(?:educación|formación|habilidades)|\Z)",
                r"(?:desarrollador|ingeniero|analista|programador|especialista).*?(?=\n.*?(?:educación|habilidades)|\Z)"
            ],
            "educacion": [
                r"(?:educación|formación|estudios|universidad|instituto|grado|máster|licenciatura).*?(?=\n.*?(?:experiencia|certificados|habilidades)|\Z)",
                r"(?:ingeniería|carrera|bachillerato).*?(?=\n.*?(?:experiencia|certificados)|\Z)"
            ],
            "certificados": [
                r"(?:certificados|certificaciones|cursos|diplomas|capacitación).*?(?=\n.*?(?:idiomas|referencias|habilidades)|\Z)",
                r"(?:coursera|udemy|edx|certificación|curso).*?(?=\n.*?(?:idiomas|referencias)|\Z)"
            ],
            "idiomas": [
                r"(?:idiomas|lenguajes|languages).*?(?=\n.*?(?:referencias|contacto)|\Z)",
                r"(?:inglés|español|francés|alemán|nativo|intermedio|avanzado|c1|b2).*?(?=\n.*?(?:referencias|contacto)|\Z)"
            ],
            "datos": [
                r"(?:contacto|información|datos|email|teléfono|linkedin|github).*?(?=\n.*?(?:perfil|resumen)|\Z)",
                r"(?:@|linkedin\.com|github\.com|\+\d+).*?(?=\n|\Z)"
            ]
        }
        
        # Extraer cada sección usando múltiples patrones
        for seccion, patrones in patrones_seccion.items():
            contenido_encontrado = ""
            
            for patron in patrones:
                matches = re.findall(patron, texto_completo, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if isinstance(match, tuple):
                        match = match[0] if match[0] else match[1] if len(match) > 1 else ""
                    if match and len(match.strip()) > 20:
                        contenido_encontrado += match.strip() + "\n"
            
            # Si encontramos contenido específico, usarlo; sino, usar texto completo
            if contenido_encontrado.strip():
                secciones[seccion] = contenido_encontrado.strip()
                print(f"  ✅ {seccion}: {len(secciones[seccion])} chars (específico)")
            else:
                secciones[seccion] = texto_completo
                print(f"  📄 {seccion}: {len(secciones[seccion])} chars (general)")
        
        # Formato siempre usa texto completo
        secciones["formato"] = texto_completo
        
        return secciones
    
    def calcular_similitud_tfidf(self, texto1, texto2):
        """Calcula similitud TF-IDF con parámetros MÁS GENEROSOS"""
        try:
            if not texto1 or not texto2:
                return 0.4  # Base más alta
                
            t1 = str(texto1).lower().strip()
            t2 = str(texto2).lower().strip()
            
            if len(t1) < 10 or len(t2) < 10:
                return 0.4  # Textos muy cortos
                
            if t1 == t2:
                return 0.8  # Textos idénticos
                
            try:
                # Vectorizer MÁS PERMISIVO
                vectorizer = TfidfVectorizer(
                    analyzer='word',
                    ngram_range=(1, 2),  # Solo 1-2 gramas
                    stop_words=['de', 'la', 'el', 'en', 'y', 'a', 'con', 'para', 'por'],
                    max_features=500,    # Menos features para mayor generalización
                    min_df=1,           # Aceptar palabras que aparecen solo una vez
                    lowercase=True,
                    token_pattern=r'\b\w+\b'  # Patrón más simple
                )
                
                tfidf_matrix = vectorizer.fit_transform([t1, t2])
                similitud = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
                
                # TRANSFORMACIÓN PARA PUNTUACIONES MÁS ALTAS
                # Aplicar función sigmoidea desplazada para aumentar puntuaciones
                similitud_ajustada = 0.3 + (similitud * 0.6)  # Mínimo 30%, máximo 90%
                
                return max(0.3, min(0.9, float(similitud_ajustada)))
                
            except Exception as e:
                print(f"    ⚠️ Error TF-IDF interno: {e}")
                return 0.5
                
        except Exception as e:
            print(f"    ⚠️ Error TF-IDF: {e}")
            return 0.5
    
    def calcular_similitud_keywords(self, texto_seccion, puesto_clave):
        """Calcula similitud por palabras clave con MÁXIMA FLEXIBILIDAD y reconocimiento de habilidades transferibles"""
        try:
            if not texto_seccion or puesto_clave not in self.palabras_clave:
                return 0.4  # Base más alta
            
            texto_lower = str(texto_seccion).lower()
            keywords_for_puesto = self.palabras_clave[puesto_clave]
            
            if not keywords_for_puesto:
                return 0.4
            
            # BÚSQUEDA SÚPER FLEXIBLE de keywords
            encontradas = 0
            palabras_encontradas = []
            puntos_bonus = 0
            
            for keyword in keywords_for_puesto:
                # Búsqueda exacta
                if keyword.lower() in texto_lower:
                    encontradas += 1
                    palabras_encontradas.append(keyword)
                # Búsqueda de variaciones comunes
                elif self._buscar_variaciones(keyword, texto_lower):
                    encontradas += 1
                    palabras_encontradas.append(f"{keyword}*")
            
            # RECONOCIMIENTO DE HABILIDADES TRANSFERIBLES
            # Si es Full Stack, reconocer habilidades de programación general
            if puesto_clave == "Desarrollador Full Stack":
                habilidades_transferibles = [
                    "python", "programación", "desarrollo", "sql", "base de datos", "bases de datos",
                    "mongodb", "postgresql", "mysql", "git", "github", "análisis", "algoritmos",
                    "pandas", "numpy", "api", "web", "dashboard", "visualización", "estadística"
                ]
                
                for habilidad in habilidades_transferibles:
                    if habilidad in texto_lower and habilidad not in [k.lower() for k in palabras_encontradas]:
                        puntos_bonus += 1
                        palabras_encontradas.append(f"💡{habilidad}")
            
            # Si es Data Science, reconocer más habilidades específicas
            elif "Datos" in puesto_clave or "ML" in puesto_clave:
                habilidades_transferibles = [
                    "análisis", "estadística", "visualización", "dashboard", "reporting",
                    "predicción", "modelos", "algoritmos", "clustering", "regresión", "clasificación"
                ]
                
                for habilidad in habilidades_transferibles:
                    if habilidad in texto_lower and habilidad not in [k.lower() for k in palabras_encontradas]:
                        puntos_bonus += 1
                        palabras_encontradas.append(f"💡{habilidad}")
            
            encontradas_total = encontradas + puntos_bonus
            
            if encontradas_total > 0:
                print(f"    🎯 Keywords: {encontradas}/{len(keywords_for_puesto)} directas + {puntos_bonus} transferibles")
                print(f"    📋 Encontradas: {', '.join(palabras_encontradas[:10])}")
            
            # CÁLCULO SÚPER GENEROSO con habilidades transferibles
            proporcion_base = encontradas / len(keywords_for_puesto)
            bonus_transferible = min(0.4, puntos_bonus * 0.05)  # Max 40% bonus
            
            similitud_total = proporcion_base + bonus_transferible
            
            # BOOST según cantidad total de keywords encontradas
            if encontradas_total >= 8:
                similitud = min(0.95, similitud_total + 0.25)  # Boost enorme
            elif encontradas_total >= 5:
                similitud = min(0.85, similitud_total + 0.2)   # Gran boost
            elif encontradas_total >= 3:
                similitud = min(0.75, similitud_total + 0.15)  # Boost medio
            elif encontradas_total >= 1:
                similitud = min(0.65, similitud_total + 0.1)   # Boost pequeño
            else:
                similitud = 0.2  # Mínimo más alto
            
            return round(similitud, 3)
            
        except Exception as e:
            print(f"    ⚠️ Error keywords: {e}")
            return 0.5
    
    def _buscar_variaciones(self, keyword, texto):
        """Busca variaciones comunes de las palabras clave con MAYOR COBERTURA"""
        variaciones = {
            "javascript": ["js", "ecmascript", "node", "nodejs", "react", "angular", "vue"],
            "bases de datos": ["bd", "database", "sql", "mysql", "postgresql", "mongodb", "redis"],
            "base de datos": ["bd", "database", "sql", "mysql", "postgresql", "mongodb", "redis"],
            "machine learning": ["ml", "aprendizaje automático", "ia", "inteligencia artificial"],
            "desarrollo": ["development", "dev", "programación", "coding", "software"],
            "programación": ["programming", "desarrollo", "dev", "coding", "software"],
            "análisis": ["analysis", "analítica", "analytics", "data analysis"],
            "react": ["reactjs", "react.js", "frontend"],
            "angular": ["angularjs", "frontend"],
            "full stack": ["fullstack", "full-stack"],
            "python": ["py", "pandas", "numpy", "django", "flask"],
            "sql": ["mysql", "postgresql", "sqlite", "oracle", "base de datos"],
            "web": ["frontend", "backend", "javascript", "html", "css"],
            "frontend": ["front-end", "react", "angular", "vue", "javascript"],
            "backend": ["back-end", "servidor", "api", "node", "python"],
            "git": ["github", "gitlab", "control de versiones", "versionado"],
            "api": ["rest", "restful", "endpoint", "web service"],
            "html": ["markup", "web", "frontend"],
            "css": ["styles", "styling", "frontend", "web"]
        }
        
        if keyword in variaciones:
            encontradas = [var for var in variaciones[keyword] if var in texto]
            if encontradas:
                return True
        
        # Búsqueda adicional de términos relacionados
        terminos_relacionados = {
            "desarrollo": ["proyecto", "implementé", "desarrollé", "creé", "construí"],
            "programación": ["código", "script", "algoritmo", "función", "método"],
            "análisis": ["analizar", "analizando", "estudió", "investigó", "examinó"],
            "experiencia": ["trabajé", "colaboré", "participé", "realicé", "ejecuté"]
        }
        
        if keyword in terminos_relacionados:
            return any(termino in texto for termino in terminos_relacionados[keyword])
        
        return False
    
    def analizar_cv(self, texto_cv, puesto):
        """Análisis completo del CV con criterios CORREGIDOS Y JUSTOS"""
        resultados = {}
        
        print(f"\n🔄 ANÁLISIS EXPERIMENTAL CORREGIDO")
        print(f"📋 Puesto: {puesto}")
        print(f"📄 CV: {len(texto_cv)} caracteres")
        
        # Buscar puesto con MAYOR FLEXIBILIDAD
        puesto_clave = self._encontrar_puesto_clave(puesto)
        print(f"🎯 Usando perfil: '{puesto_clave}'")
        
        textos_ideales = self.textos_ideales[puesto_clave]
        
        # Extraer secciones
        secciones_cv = self.extraer_secciones_cv(texto_cv)
        
        # Analizar cada sección con criterios MEJORADOS
        for seccion, texto_ideal in textos_ideales.items():
            texto_seccion = secciones_cv.get(seccion, texto_cv)
            
            print(f"\n  📊 Analizando {seccion.upper()}:")
            
            # Calcular métricas
            sim_tfidf = self.calcular_similitud_tfidf(texto_seccion, texto_ideal)
            sim_keywords = self.calcular_similitud_keywords(texto_seccion, puesto_clave)
            
            # Combinar métricas con PESOS MÁS FAVORABLES A KEYWORDS
            sim_combinada = (sim_tfidf * 0.3) + (sim_keywords * 0.7)  # 70% peso a keywords
            
            # Criterios de nivel MUCHO MÁS JUSTOS
            if sim_combinada >= 0.6:
                nivel = "Alto"
                ajuste = 4
            elif sim_combinada >= 0.4:
                nivel = "Medio"
                ajuste = 2
            elif sim_combinada >= 0.2:
                nivel = "Bajo"
                ajuste = 1
            else:
                nivel = "Bajo"
                ajuste = 0
            
            resultados[seccion] = {
                "similitud_tfidf": round(sim_tfidf, 3),
                "similitud_keywords": round(sim_keywords, 3),
                "similitud_combinada": round(sim_combinada, 3),
                "nivel": nivel,
                "ajuste_puntos": ajuste
            }
            
            print(f"    ✅ TF-IDF: {sim_tfidf:.1%} | Keywords: {sim_keywords:.1%} | Combined: {sim_combinada:.1%} → {nivel}")
        
        return resultados
    
    def _encontrar_puesto_clave(self, puesto):
        """Encuentra el puesto clave con mayor flexibilidad"""
        # Mapeo de términos comunes
        mapeo_puestos = {
            "full stack": "Desarrollador Full Stack",
            "fullstack": "Desarrollador Full Stack",
            "frontend": "Desarrollador Full Stack",
            "backend": "Desarrollador Full Stack",
            "web": "Desarrollador Full Stack",
            "dba": "Administrador de Bases de Datos (DBA)",
            "base de datos": "Administrador de Bases de Datos (DBA)",
            "bases de datos": "Administrador de Bases de Datos (DBA)",
            "devops": "Ingeniero DevOps",
            "datos": "Científico de Datos / ML Engineer",
            "data": "Científico de Datos / ML Engineer",
            "machine learning": "Científico de Datos / ML Engineer",
            "ml": "Científico de Datos / ML Engineer",
            "móvil": "Desarrollador de Aplicaciones Móviles",
            "mobile": "Desarrollador de Aplicaciones Móviles",
            "ios": "Desarrollador de Aplicaciones Móviles",
            "android": "Desarrollador de Aplicaciones Móviles"
        }
        
        puesto_lower = puesto.lower()
        
        # Buscar match directo
        if puesto in self.textos_ideales:
            return puesto
        
        # Buscar por mapeo
        for termino, puesto_mapeado in mapeo_puestos.items():
            if termino in puesto_lower:
                return puesto_mapeado
        
        # Buscar coincidencias parciales
        for puesto_existente in self.textos_ideales.keys():
            palabras_existente = puesto_existente.lower().split()
            palabras_busqueda = puesto_lower.split()
            
            if any(palabra in puesto_lower for palabra in palabras_existente) or \
               any(palabra in puesto_existente.lower() for palabra in palabras_busqueda):
                return puesto_existente
        
        # Default
        return "Desarrollador Full Stack"

# Inicializar analizador
semantic_analyzer = TFIDFSemanticAnalyzer()

# === Funciones de procesamiento de archivos ===
def extraer_texto_pdf(ruta: str) -> str:
    """Extrae texto de PDF"""
    try:
        import pypdf
        with open(ruta, 'rb') as file:
            reader = pypdf.PdfReader(file)
            texto = ""
            for page in reader.pages:
                if page.extract_text():
                    texto += page.extract_text() + "\n"
            return texto.strip()
    except ImportError:
        try:
            import PyPDF2
            with open(ruta, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                texto = ""
                for page in reader.pages:
                    if page.extract_text():
                        texto += page.extract_text() + "\n"
                return texto.strip()
        except ImportError:
            return "Error: Instala pypdf con 'pip install pypdf'"
    except Exception as e:
        return f"Error procesando PDF: {str(e)}"

def extraer_texto_docx(ruta: str) -> str:
    """Extrae texto de DOCX"""
    try:
        from docx import Document
        doc = Document(ruta)
        texto = ""
        for para in doc.paragraphs:
            if para.text.strip():
                texto += para.text + "\n"
        return texto.strip()
    except ImportError:
        return "Error: Instala python-docx con 'pip install python-docx'"
    except Exception as e:
        return f"Error procesando DOCX: {str(e)}"

async def procesar_archivo(archivo: UploadFile) -> str:
    """Procesa archivo subido"""
    try:
        print(f"🔄 Procesando: {archivo.filename}")
        
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir / archivo.filename
        
        content = await archivo.read()
        if not content:
            return "Archivo vacío"
        
        with open(temp_file, "wb") as f:
            f.write(content)
        
        if archivo.filename.lower().endswith('.pdf'):
            texto = extraer_texto_pdf(str(temp_file))
        elif archivo.filename.lower().endswith('.docx'):
            texto = extraer_texto_docx(str(temp_file))
        else:
            texto = "Formato no soportado"
        
        # Limpiar archivos temporales
        try:
            temp_file.unlink()
            temp_dir.rmdir()
        except:
            pass
        
        print(f"✅ Extraído: {len(texto)} caracteres")
        return texto
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return f"Error: {str(e)}"

# === Rutas de la aplicación ===
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
        "puesto": ""
    })

@app.post("/analizar", response_class=HTMLResponse)
async def analizar_cv_experimental(request: Request, archivo: UploadFile = File(...), puesto: str = Form(...)):
    try:
        print(f"\n🚀 INICIANDO ANÁLISIS CORREGIDO")
        print(f"📋 Puesto: {puesto}")
        print(f"📄 Archivo: {archivo.filename}")
        
        # Validaciones
        if not puesto or puesto.startswith("--"):
            raise ValueError("Selecciona un puesto válido")
        
        if not archivo.filename.lower().endswith((".pdf", ".docx")):
            raise ValueError("Solo PDF o DOCX")
        
        # Procesar archivo
        texto = await procesar_archivo(archivo)
        if len(texto.strip()) < 50:
            raise ValueError("Texto insuficiente en el archivo")
        
        # Análisis semántico
        print("\n🧠 INICIANDO ANÁLISIS SEMÁNTICO CORREGIDO...")
        metricas = semantic_analyzer.analizar_cv(texto, puesto)
        
        # Convertir para UI con PUNTUACIÓN CORREGIDA
        resultados_ui = []
        for seccion, datos in metricas.items():
            puntuacion_base = 10
            factor = datos["similitud_combinada"]
            
            # ESCALA DE PUNTUACIÓN MUCHO MÁS GENEROSA
            if factor >= 0.6:       # Alto
                puntuacion = min(10, 9 + round(factor))      # 9-10 puntos
            elif factor >= 0.4:     # Medio
                puntuacion = min(9, 7 + round(factor * 2))   # 7-9 puntos  
            elif factor >= 0.2:     # Bajo
                puntuacion = min(7, 5 + round(factor * 3))   # 5-7 puntos
            else:                   # Muy bajo
                puntuacion = max(3, round(factor * 10))      # 3-5 puntos
            
            nivel = datos["nivel"]
            if nivel == "Alto":
                mensaje = "✅ Excelente coherencia semántica"
            elif nivel == "Medio":
                mensaje = "⚠️ Coherencia aceptable"
            else:
                mensaje = "❌ Coherencia básica"
            
            mensaje += f" [TF-IDF: {int(datos['similitud_tfidf']*100)}%]"
            
            resultados_ui.append((
                seccion.capitalize(),
                puntuacion,
                puntuacion_base,
                mensaje
            ))
        
        # Puntuación total
        puntaje_total = sum(p for _, p, _, _ in resultados_ui)
        
        # Recomendaciones mejoradas
        recomendaciones = []
        secciones_bajas = sorted(metricas.items(), key=lambda x: x[1]["similitud_combinada"])[:2]
        
        for seccion, datos in secciones_bajas:
            if datos["similitud_combinada"] < 0.5:
                if seccion == "habilidades":
                    recomendaciones.append(f"Amplía tu sección de habilidades técnicas para {puesto}. Incluye más tecnologías específicas del área.")
                elif seccion == "experiencia":
                    recomendaciones.append(f"Destaca proyectos y logros más relacionados con {puesto}. Cuantifica tus resultados.")
                elif seccion == "perfil":
                    recomendaciones.append(f"Personaliza tu perfil profesional para {puesto}, destacando competencias clave del área.")
        
        if len(recomendaciones) < 2:
            recomendaciones.append(f"Tu CV muestra buena compatibilidad con {puesto}. Continúa desarrollando proyectos en esta área.")
        
        # Métricas para visualización
        metricas_ui = []
        for seccion, datos in metricas.items():
            metricas_ui.append({
                "seccion": seccion.capitalize(),
                "similitud": round(datos["similitud_combinada"] * 100),
                "nivel": datos["nivel"],
                "ajuste": datos["ajuste_puntos"]
            })
        
        print(f"\n🎯 ANÁLISIS COMPLETADO")
        print(f"📊 Puntuación total: {puntaje_total}/80")
        print(f"📈 Promedio: {puntaje_total/8:.1f}/10")
        
        return templates.TemplateResponse("index.html", {
            "request": request,
            "resultado": puntaje_total,
            "detalles": resultados_ui,
            "nombre": archivo.filename,
            "contenido_cv": texto[:15000] + ("..." if len(texto) > 15000 else ""),
            "recomendaciones": recomendaciones,
            "puesto": puesto,
            "metricas_semanticas": metricas_ui,
            "modo_experimental": True
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
            "puesto": ""
        })

@app.middleware("http")
async def add_headers(request: Request, call_next):
    print(f"🌐 {request.method} {request.url}")
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache" 
    response.headers["Expires"] = "0"
    return response