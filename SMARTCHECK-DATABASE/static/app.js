// =================================================================================
// CV SMARTCHECK - app.js FINAL Y COMPLETO (VERSIÓN CORREGIDA)
// Este archivo controla toda la interactividad de la aplicación.
// Incluye la lógica de autenticación y la renderización dinámica de vistas,
// reutilizando toda la lógica original de UI (tooltips, tabs, etc.).
// =================================================================================

document.addEventListener('DOMContentLoaded', () => {

    // --- ESTADO INICIAL Y SELECTORES ---
    const mainContainer = document.getElementById('main-container');
    const token = getTokenFromCookie();

    // --- LÓGICA DE INICIO ---
    // Al cargar la página, decidimos qué vista mostrar
    if (token) {
        renderizarVistaLogueada();
    } else {
        inicializarVistaPublica();
    }

    // =============================================================================
    // --- SECCIÓN 1: LÓGICA DE AUTENTICACIÓN (LOGIN, REGISTER, LOGOUT) ---
    // =============================================================================

    function inicializarVistaPublica() {
        const showLoginBtn = document.getElementById('showLoginBtn');
        const showRegisterBtn = document.getElementById('showRegisterBtn');
        const ctaButton = document.querySelector('.cta-button');
        if (showLoginBtn) showLoginBtn.addEventListener('click', () => openAuthModal('login'));
        if (showRegisterBtn) showRegisterBtn.addEventListener('click', () => openAuthModal('register'));
        

        if (ctaButton) ctaButton.addEventListener('click', (e) => {
            e.preventDefault(); // Evita que el enlace #auth-section se active
            openAuthModal('login');
        });
        // === FIN DE LA LÍNEA A AÑADIR ===
        
        console.log("Listeners para login, registro y CTA asignados.");

    }

    async function handleRegister(e) {
        e.preventDefault();
        const errorElement = document.getElementById('register-error');
        const successElement = document.getElementById('register-success');
        errorElement.textContent = '';
        successElement.textContent = '';

        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;

        try {
            const response = await fetch('/users/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await response.json();
            if (!response.ok) {
                errorElement.textContent = data.detail || 'Error en el registro.';
            } else {
                successElement.textContent = '¡Registro exitoso! Ahora puedes iniciar sesión.';
                e.target.reset();
            }
        } catch (error) {
            errorElement.textContent = 'No se pudo conectar con el servidor.';
        }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const errorElement = document.getElementById('login-error');
        errorElement.textContent = '';
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;

        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        try {
            const response = await fetch('/users/token', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            if (!response.ok) {
                errorElement.textContent = data.detail || 'Email o contraseña incorrectos.';
            } else {
                document.cookie = `access_token=Bearer ${data.access_token}; path=/; max-age=1800; SameSite=Lax`;
                window.location.reload();
            }
        } catch (error) {
            errorElement.textContent = 'No se pudo conectar con el servidor.';
        }
    }

    function handleLogout() {
        document.cookie = 'access_token=; path=/; max-age=0;';
        window.location.reload();
    }

    function getTokenFromCookie() {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; access_token=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
        return null;
    }


    // =============================================================================
    // --- SECCIÓN 2: LÓGICA DE LA VISTA DE USUARIO LOGUEADO ---
    // =============================================================================

    function renderizarVistaLogueada() {
        const uploadSection = document.getElementById('upload-section');
        if (!uploadSection) return;

        // HTML REUTILIZADO: Formulario de subida completo de tu index.html original
        const formHTML = `
            <form id="uploadForm" method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="puestoSelect"><i class="fas fa-briefcase"></i> Selecciona el puesto deseado</label>
                    <div class="select-wrapper">
                        <select name="puesto" required id="puestoSelect">
                            <option value="" disabled selected>-- Selecciona un puesto --</option>
                            <option value="Desarrollador Full Stack">Desarrollador Full Stack</option>
                            <option value="Ingeniero DevOps">Ingeniero DevOps</option>
                            <option value="Especialista en Ciberseguridad">Especialista en Ciberseguridad</option>
                            <option value="Ingeniero de Datos">Ingeniero de Datos</option>
                            <option value="Científico de Datos / Machine Learning Engineer">Científico de Datos / ML Engineer</option>
                            <option value="Administrador de Bases de Datos (DBA)">Administrador de Bases de Datos (DBA)</option>
                            <option value="Arquitecto de Software">Arquitecto de Software</option>
                            <option value="Ingeniero de Redes">Ingeniero de Redes</option>
                            <option value="Desarrollador de Aplicaciones Móviles">Desarrollador de Aplicaciones Móviles</option>
                            <option value="Ingeniero de Inteligencia Artificial / Deep Learning">Ingeniero de IA / Deep Learning</option>
                            <option value="Ingeniero Cloud">Ingeniero Cloud</option>
                            <option value="Ingeniero de Pruebas Automatizadas">Ingeniero de Pruebas Automatizadas</option>
                            <option value="Consultor en Arquitectura Cloud">Consultor en Arquitectura Cloud</option>
                            <option value="Administrador de Sistemas Linux/Unix">Administrador de Sistemas Linux/Unix</option>
                            <option value="Especialista en Blockchain">Especialista en Blockchain</option>
                            <option value="Ingeniero de Automatización">Ingeniero de Automatización</option>
                            <option value="Desarrollador Front-End">Desarrollador Front-End</option>
                            <option value="Ingeniero de Integración / API">Ingeniero de Integración / API</option>
                            <option value="Ingeniero de Big Data">Ingeniero de Big Data</option>
                            <option value="Ingeniero IoT">Ingeniero IoT</option>
                        </select>
                    </div>
                </div>
                <div class="form-group">
                    <label for="fileInput"><i class="fas fa-file-upload"></i> Sube tu currículum (.pdf, .docx)</label>
                    <div class="file-drop-area" id="fileDrop">
                        <span class="file-message">Arrastra tu archivo aquí o haz clic para seleccionar</span>
                        <input type="file" name="archivo" accept=".pdf,.docx" required id="fileInput">
                    </div>
                    <div class="file-info" id="fileInfo"></div>
                </div>
                <button type="submit" class="submit-btn">
                    <span class="btn-text"><i class="fas fa-rocket"></i> Evaluar CV</span>
                </button>
            </form>
        `;
        uploadSection.innerHTML = formHTML;

        // LÓGICA REUTILIZADA de tu app.js original para el formulario
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', handleCvUpload);
            inicializarLogicaDeArchivos();
        }

        const logoutButton = document.getElementById('logoutButton');
        if(logoutButton) {
            logoutButton.addEventListener('click', handleLogout);
        }
    }


    function openAuthModal(mode) {
        const authModal = document.getElementById('authModal');
        const authModalContent = document.getElementById('authModalContent');
        if (!authModal || !authModalContent) return;

        let formHTML = '';
        if (mode === 'login') {
            formHTML = `
                <div class="modal-header">
                    <h3><i class="fas fa-sign-in-alt"></i> Iniciar Sesión</h3>
                    <button class="modal-close" id="closeAuthModal">&times;</button>
                </div>
                <form id="loginForm">
                    <div class="form-group"><label for="login-email">Email</label><input type="email" id="login-email" required autocomplete="username"></div>
                    <div class="form-group"><label for="login-password">Contraseña</label><input type="password" id="login-password" required autocomplete="current-password"></div>
                    <button type="submit" class="submit-btn">Entrar</button>
                    <p id="login-error" class="error-text"></p>
                </form>
            `;
        } else {
            formHTML = `
                <div class="modal-header">
                    <h3><i class="fas fa-user-plus"></i> Registrarse</h3>
                    <button class="modal-close" id="closeAuthModal">&times;</button>
                </div>
                <form id="registerForm">
                    <div class="form-group"><label for="register-email">Email</label><input type="email" id="register-email" required></div>
                    <div class="form-group"><label for="register-password">Contraseña</label><input type="password" id="register-password" required></div>
                    <button type="submit" class="submit-btn secondary">Crear Cuenta</button>
                    <p id="register-error" class="error-text"></p>
                    <p id="register-success" class="success-text"></p>
                </form>
            `;
        }
        
        authModalContent.innerHTML = formHTML;
        authModal.classList.add('active');

        // Asignar listeners a los nuevos elementos del modal
        document.getElementById('closeAuthModal')?.addEventListener('click', () => authModal.classList.remove('active'));
        if (mode === 'login') {
            document.getElementById('loginForm')?.addEventListener('submit', handleLogin);
        } else {
            document.getElementById('registerForm')?.addEventListener('submit', handleRegister);
        }
    }


    async function handleCvUpload(event) {
        event.preventDefault();
        // LÓGICA REUTILIZADA: El modal de carga
        mainContainer.innerHTML = `
            <div id="progressModal" class="modal" style="display: flex;">
                <div class="modal-content">
                    <div class="spinner-container">
                        <div class="spinner"></div>
                        <div class="spinner-text">Analizando tu currículum...</div>
                    </div>
                </div>
            </div>`;

        const token = getTokenFromCookie();
        if (!token) {
            alert("Tu sesión ha expirado. Por favor, inicia sesión de nuevo.");
            window.location.reload();
            return;
        }

        const formData = new FormData(event.target);

        try {
            const response = await fetch('/subir', {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });

            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.detail || 'Ocurrió un error en el servidor.');
            }
            mostrarResultados(data);
        } catch (error) {
            mainContainer.innerHTML = `<div class="error-container glass-panel"><div class="error-message"><h3>Error</h3><p>${error.message}</p></div></div>`;
        }
    }

    function mostrarResultados(datos) {
        const detallesHTML = datos.detalles.map(item => {
            const [seccion, puntos, total, comentario] = item;
            const porcentaje = total > 0 ? (puntos / total) * 100 : 0;
            let claseFila = 'bajo';
            if (porcentaje >= 85) claseFila = 'alto';
            else if (porcentaje >= 60) claseFila = 'medio';
            
            return `
                <tr class="${claseFila}">
                    <td><strong>${seccion}</strong></td>
                    <td>${puntos} / ${total}</td>
                    <td>
                        <div class="progress-container">
                            <div class="progress" style="width: ${porcentaje}%"></div>
                        </div>
                    </td>
                    <td>${comentario}</td>
                </tr>
            `;
        }).join('');

        const recomendacionesHTML = datos.recomendaciones.map((rec, index) => `
            <div class="reco-seccion glass-panel">
                <div class="reco-header">
                    <div class="reco-seccion-titulo">Recomendación ${index + 1}</div>
                    <div class="reco-indicador"></div>
                </div>
                <div class="reco-contenido"><p>${rec}</p></div>
            </div>
        `).join('');
        
        let bertMetricsHTML = '';
        if (datos.metricas_bert && datos.metricas_bert.length > 0) {
            const bertRows = datos.metricas_bert.map(metrica => {
                const similitud = metrica.similitud || 0;
                const ajuste = metrica.ajuste || 0;
                const nivel = metrica.nivel || 'N/A';
                const seccion = metrica.seccion || 'N/A';
                return `
                <tr>
                    <td><strong>${seccion}</strong></td>
                    <td>
                        <div class="similitud-container">
                            <div class="similitud-bar" style="width:${similitud}%"></div>
                            <span class="similitud-text">${similitud}%</span>
                        </div>
                    </td>
                    <td>${nivel}</td>
                    <td class="ajuste-bert ${ ajuste > 0 ? 'positivo' : ajuste < 0 ? 'negativo' : ''}">
                        ${ ajuste > 0 ? '+' : '' }${ajuste}
                    </td>
                </tr>
            `}).join('');

            bertMetricsHTML = `
                <div class="bert-metrics glass-panel">
                    <h3><i class="fas fa-brain"></i> Análisis Semántico con BERT</h3>
                    <p class="bert-intro">El modelo BERT evalúa la calidad semántica y relevancia contextual del contenido para el puesto seleccionado.</p>
                    <table class="bert-table">
                        <thead>
                            <tr><th>Sección</th><th>Similitud Semántica</th><th>Nivel</th><th>Ajuste</th></tr>
                        </thead>
                        <tbody>${bertRows}</tbody>
                    </table>
                </div>
            `;
        }

        const resultadosHTML = `
            <div id="resultadoContainer" class="resultado-container animate-in">
                <div class="resultado-header">
                    <h2><i class="fas fa-chart-line"></i> Resultados para: ${datos.nombre}</h2>
                    <div class="puntaje-container">
                        <div class="puntaje-circle ${datos.resultado < 50 ? 'bajo' : datos.resultado < 85 ? 'medio' : 'alto'}">
                            <div class="puntaje-number">${datos.resultado}</div>
                            <div class="puntaje-label">Puntos</div>
                        </div>
                    </div>
                </div>

                <div class="tabs-container">
                    <div class="tabs">
                        <button class="tab-btn active" data-tab="detalles"><i class="fas fa-list-alt"></i> Detalles</button>
                        <button class="tab-btn" data-tab="recomendaciones"><i class="fas fa-lightbulb"></i> Recomendaciones</button>
                        <button class="tab-btn" data-tab="preview"><i class="fas fa-eye"></i> Vista previa</button>
                    </div>

                    <div id="detalles" class="tab-content active">
                        <div class="tabla-resultados glass-panel">
                            <table>
                                <thead>
                                    <tr>
                                        <th><i class="fas fa-tag"></i> Sección</th>
                                        <th><i class="fas fa-check"></i> Puntos</th>
                                        <th><i class="fas fa-chart-bar"></i> Progreso</th>
                                        <th><i class="fas fa-comment"></i> Comentario</th>
                                    </tr>
                                </thead>
                                <tbody>${detallesHTML}</tbody>
                            </table>
                        </div>
                        ${bertMetricsHTML}
                    </div>

                    <div id="recomendaciones" class="tab-content">
                        <div class="recomendaciones-container">
                            <h3>Recomendaciones para <span class="highlight">${datos.puesto}</span></h3>
                            <div class="recomendaciones-secciones">${recomendacionesHTML}</div>
                        </div>
                    </div>

                    <div id="preview" class="tab-content">
                        <div class="preview-container glass-panel">
                            <h3><i class="fas fa-file-alt"></i> Contenido extraído del CV</h3>
                            <pre>${datos.contenido_cv}</pre>
                        </div>
                    </div>
                </div>

                <div class="actions">
                    <button class="action-btn" id="evaluarOtroBtn"><i class="fas fa-redo"></i> Evaluar otro CV</button>
                    <button class="action-btn secondary" onclick="window.print()"><i class="fas fa-print"></i> Imprimir resultados</button>
                </div>
            </div>
        `;
        mainContainer.innerHTML = resultadosHTML;

        // LÓGICA REUTILIZADA: Ahora que el HTML existe, activamos sus funcionalidades
        inicializarLogicaResultados();
    }


    // =============================================================================
    // --- SECCIÓN 3: FUNCIONES REUTILIZADAS DE TU ANTIGUO app.js ---
    // =============================================================================

    function inicializarLogicaDeArchivos() {
        const fileInput = document.getElementById('fileInput');
        const fileInfo = document.getElementById('fileInfo');
        const fileDrop = document.getElementById('fileDrop');
        if (!fileInput || !fileDrop) return;
        
        const updateFileInfo = () => {
             if (fileInput.files && fileInput.files[0]) {
                const file = fileInput.files[0];
                const icon = file.name.endsWith('.pdf') ? 'fa-file-pdf' : 'fa-file-word';
                fileInfo.innerHTML = `<div class="file-preview"><i class="fas ${icon}"></i><div class="file-details"><div class="file-name">${file.name}</div><div class="file-size">${formatSize(file.size)}</div></div></div>`;
                fileInfo.style.display = 'block';
            }
        };

        fileDrop.addEventListener('dragover', (e) => { e.preventDefault(); fileDrop.classList.add('active'); });
        fileDrop.addEventListener('dragleave', () => fileDrop.classList.remove('active'));
        fileDrop.addEventListener('drop', (e) => {
            e.preventDefault();
            fileDrop.classList.remove('active');
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileInfo();
            }
        });
        fileInput.addEventListener('change', updateFileInfo);
    }

    function inicializarLogicaResultados() {
        const tabButtons = document.querySelectorAll('.tab-btn');
        tabButtons.forEach(btn => {
            if(btn) btn.addEventListener('click', (e) => openTab(e, btn.dataset.tab));
        });

        if (!document.getElementById('custom-tooltip')) {
            const tooltip = document.createElement('div');
            tooltip.id = 'custom-tooltip';
            tooltip.className = 'custom-tooltip'; // Usamos una clase para estilos
            document.body.appendChild(tooltip);
        }
        
        const tooltip = document.getElementById('custom-tooltip');

        document.querySelectorAll('.tabla-resultados tbody tr').forEach(fila => {
            fila.addEventListener('mouseenter', function() {
                const seccion = this.querySelector('td:first-child strong').textContent;
                const puntos = this.querySelector('td:nth-child(2)').textContent;
                showTooltip(seccion, puntos, this, tooltip);
            });
            fila.addEventListener('mouseleave', () => hideTooltip(tooltip));
        });
        
        const evaluarOtroBtn = document.getElementById('evaluarOtroBtn');
        if (evaluarOtroBtn) {
            evaluarOtroBtn.addEventListener('click', renderizarVistaLogueada);
        }
    }
    
    function formatSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    function openTab(event, tabId) {
        const TABS = document.querySelectorAll('.tab-content');
        const BUTTONS = document.querySelectorAll('.tab-btn');
        
        TABS.forEach(c => { if(c) c.classList.remove('active') });
        BUTTONS.forEach(b => { if(b) b.classList.remove('active') });
        
        const tabToShow = document.getElementById(tabId);
        if(tabToShow) tabToShow.classList.add('active');
        
        if(event.currentTarget) event.currentTarget.classList.add('active');
    }

    function showTooltip(seccion, puntos, elemento, tooltip) {
        if (!tooltip) return;
        const [obtenidos, total] = puntos.split('/').map(n => parseInt(n.trim()));
        const porcentaje = total > 0 ? (obtenidos / total) * 100 : 0;
        
        let icono = '';
        let mensaje = '';
        let iconoColor = '';

        if (porcentaje < 40) { icono = '<i class="fas fa-exclamation-triangle"></i>'; iconoColor = '#FF453A'; }
        else if (porcentaje < 70) { icono = '<i class="fas fa-exclamation-circle"></i>'; iconoColor = '#FFD60A'; }
        else { icono = '<i class="fas fa-check-circle"></i>'; iconoColor = '#30D158'; }
        
        const mensajes = {
            "Perfil": {
                bajo: "Tu perfil profesional necesita una mejora significativa. Añade un resumen claro de 3-5 líneas que destaque tus principales fortalezas y experiencia relevante para el puesto.",
                medio: "Tu perfil es básico pero funcional. Para mejorarlo, personalízalo según el puesto específico, destacando experiencias y habilidades directamente relevantes.",
                alto: "Excelente perfil profesional. Comunica claramente tu propuesta de valor y está bien alineado con el puesto. Es conciso pero informativo, destacando tus fortalezas clave."
            },
            "Educación": {
                bajo: "La sección de educación requiere más detalles. Incluye el nombre completo de las instituciones, titulaciones obtenidas, fechas precisas y cursos relevantes para el puesto.",
                medio: "Tu sección de educación contiene información básica pero podría ser más completa. Añade especialización, logros académicos destacados o proyectos relevantes.",
                alto: "Muy buena sección de educación con detalles completos de tu formación. La información está bien estructurada y destaca aspectos relevantes para el puesto."
            },
            "Habilidades": {
                bajo: "Tu sección de habilidades necesita una mejora importante. Organiza las habilidades por categorías y asegúrate de incluir aquellas más relevantes para el puesto.",
                medio: "Tu sección de habilidades está presente pero podría optimizarse. Prioriza las habilidades más relevantes para el puesto y considera agruparlas por categorías.",
                alto: "Excelente sección de habilidades, bien organizada y completa, con tecnologías alineadas al puesto."
            },
            "Experiencia": {
                bajo: "La sección de experiencia profesional necesita más detalle. Estructura cada posición con cargo, empresa, fechas y, lo más importante, logros medibles.",
                medio: "Tu experiencia está descrita de manera básica. Mejora enfocándote en resultados y logros cuantificables en lugar de solo listar responsabilidades.",
                alto: "Experiencia profesional muy bien detallada con logros cuantificables y estructura clara."
            },
            "Certificados": {
                bajo: "Faltan certificaciones relevantes. Incluye certificaciones actuales, especificando institución y fecha.",
                medio: "Certificaciones básicas presentes. Considera añadir certificaciones más relevantes y actuales.",
                alto: "Excelentes certificaciones, actualizadas y muy relevantes para el puesto."
            },
             "Idiomas": {
                bajo: "Falta información detallada sobre idiomas. Añade todos los idiomas que dominas con niveles específicos (A1-C2 o básico/intermedio/avanzado/nativo).",
                medio: "Información básica de idiomas presente. Es importante detallar mejor tus niveles en cada idioma y destacar tu dominio del inglés técnico.",
                alto: "Excelente sección de idiomas con niveles claramente especificados según estándares reconocidos."
            },
             "Datos": {
                bajo: "La información de contacto es insuficiente. Asegúrate de incluir email, teléfono, LinkedIn actualizado y GitHub para roles técnicos.",
                medio: "Información de contacto básica pero suficiente. Añade perfiles profesionales online para facilitar que los reclutadores conozcan mejor tu experiencia.",
                alto: "Información de contacto completa y bien presentada, facilitando múltiples vías para que los reclutadores te contacten."
            },
             "Formato": {
                bajo: "El formato de tu CV necesita una mejora significativa. Utiliza una estructura clara con secciones bien definidas, viñetas y espaciado consistente.",
                medio: "Formato aceptable pero mejorable. Trabaja en la consistencia visual y en facilitar la lectura rápida de la información clave.",
                alto: "Excelente formato, profesional y bien estructurado. Es visualmente atractivo y prioriza eficazmente la información más relevante."
            }
        };

        const mensajesSeccion = mensajes[seccion];
        if (mensajesSeccion) {
            if (porcentaje < 40) mensaje = mensajesSeccion.bajo;
            else if (porcentaje < 70) mensaje = mensajesSeccion.medio;
            else mensaje = mensajesSeccion.alto;
        } else {
            mensaje = "Análisis general de esta sección.";
        }

        tooltip.innerHTML = `
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <span style="color: ${iconoColor}; font-size: 18px; margin-right: 10px;">${icono}</span>
                <div style="font-weight: 500; font-size: 16px;">${seccion}</div>
            </div>
            <div style="color: rgba(255, 255, 255, 0.85); line-height: 1.6; font-size: 14px;">${mensaje}</div>`;
        
        const rect = elemento.getBoundingClientRect();
        tooltip.style.left = `${rect.right + 15}px`;
        tooltip.style.top = `${rect.top + window.scrollY}px`;
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
        tooltip.style.display = 'block';
    }

    function hideTooltip(tooltip) {
        if(tooltip) {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(10px)';
        }
    }

        // AÑADE ESTO DENTRO DEL 'DOMContentLoaded' EN app.js

function inicializarAcordeonHistorial() {
    const accordionItems = document.querySelectorAll('.accordion-item');

    accordionItems.forEach(item => {
        const header = item.querySelector('.accordion-header');
        if(header) {
            header.addEventListener('click', () => {
                const content = item.querySelector('.accordion-content');
                
                if (item.classList.contains('active')) {
                    item.classList.remove('active');
                    content.style.maxHeight = null;
                    content.style.padding = "0 20px";
                } else {
                    item.classList.add('active');
                    content.style.padding = "0 20px 20px";
                    content.style.maxHeight = content.scrollHeight + "px";
                }
            });
        }
    });
}

// Llama a la nueva función al iniciar
inicializarAcordeonHistorial();

});
