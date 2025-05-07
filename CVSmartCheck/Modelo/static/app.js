/**
 * Inicializar formulario con spinner de carga estilo Apple
 */
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileMessage = document.querySelector('.file-message');
    
    // Inicializar la carga de archivos
    if (fileInput) {
        console.log("Inicializando input de archivos");
        
        // Crear botón visible
        if (fileMessage) {
            fileMessage.innerHTML = '<div class="file-message-content"><span>Arrastra tu archivo aquí</span><div class="custom-file-button">Seleccionar archivo</div></div>';
            
            // Asegurarse de que el botón active el input
            const customButton = document.querySelector('.custom-file-button');
            if (customButton) {
                customButton.addEventListener('click', function(e) {
                    e.preventDefault();
                    fileInput.click();
                });
            }
        }
        
        // Inicializar drag & drop
        const fileDrop = document.getElementById('fileDrop');
        if (fileDrop) {
            fileDrop.addEventListener('dragover', function(e) {
                e.preventDefault();
                this.classList.add('active');
            });
            
            fileDrop.addEventListener('dragleave', function() {
                this.classList.remove('active');
            });
            
            fileDrop.addEventListener('drop', function(e) {
                e.preventDefault();
                this.classList.remove('active');
                if (e.dataTransfer.files.length) {
                    fileInput.files = e.dataTransfer.files;
                    // Disparar evento change manualmente
                    const event = new Event('change');
                    fileInput.dispatchEvent(event);
                }
            });
        }
        
        // Actualizar al seleccionar un archivo
        fileInput.addEventListener('change', function() {
            if (this.files && this.files[0]) {
                const file = this.files[0];
                const extension = file.name.split('.').pop().toLowerCase();
                const icon = extension === 'pdf' ? 'fa-file-pdf' : 'fa-file-word';
                
                if (fileInfo) {
                    fileInfo.innerHTML = `
                        <div class="file-preview">
                            <i class="fas ${icon}"></i>
                            <div class="file-details">
                                <div class="file-name">${file.name}</div>
                                <div class="file-size">${formatSize(file.size)}</div>
                            </div>
                            <button type="button" class="file-remove" onclick="removeFile()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;
                    fileInfo.style.display = 'block';
                    if (fileMessage) fileMessage.style.display = 'none';
                }
            }
        });
    }
    
    // Inicializar formulario con spinner de carga
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar que se haya seleccionado un archivo
            if (fileInput && !fileInput.files.length) {
                alert('Por favor selecciona un archivo CV.');
                return;
            }
            
            // Validar que se haya seleccionado un puesto
            const puestoSelect = document.getElementById('puestoSelect');
            if (puestoSelect && (puestoSelect.value === "" || puestoSelect.selectedIndex === 0)) {
                alert('Por favor selecciona un puesto.');
                return;
            }
            
            // Mostrar el modal con spinner
            const progressModal = document.getElementById('progressModal');
            if (progressModal) {
                // Actualizar el contenido del modal con el spinner
                const modalContent = progressModal.querySelector('.modal-content');
                if (modalContent) {
                    modalContent.innerHTML = `
                        <div class="spinner-container">
                            <div class="spinner"></div>
                            <div class="spinner-text">Analizando tu currículum...</div>
                            <div class="spinner-timer">Tiempo restante: <span id="countdown">7</span> segundos</div>
                        </div>
                    `;
                }
                
                // Mostrar el modal
                progressModal.style.display = 'flex';
                
                // Iniciar el contador regresivo
                let segundosRestantes = 7;
                const countdownElement = document.getElementById('countdown');
                
                const contador = setInterval(function() {
                    segundosRestantes--;
                    
                    if (countdownElement) {
                        countdownElement.textContent = segundosRestantes;
                    }
                    
                    // Actualizar el texto según el progreso
                    const spinnerText = document.querySelector('.spinner-text');
                    if (spinnerText) {
                        if (segundosRestantes <= 6 && segundosRestantes > 4) {
                            spinnerText.textContent = 'Procesando estructura del CV...';
                        } else if (segundosRestantes <= 4 && segundosRestantes > 2) {
                            spinnerText.textContent = 'Evaluando contenido...';
                        } else if (segundosRestantes <= 2) {
                            spinnerText.textContent = 'Generando recomendaciones...';
                        }
                    }
                    
                    // Cuando el contador llega a cero, enviar el formulario
                    if (segundosRestantes <= 0) {
                        clearInterval(contador);
                        uploadForm.submit();
                    }
                }, 1000);
            } else {
                // Si no hay modal, enviar directamente
                uploadForm.submit();
            }
        });
    }
    
    // Inicializar pestañas
    const tabButtons = document.querySelectorAll('.tab-btn');
    if (tabButtons.length > 0) {
        tabButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                const tabId = this.getAttribute('data-tab') || this.textContent.trim().toLowerCase();
                openTab(e, tabId);
            });
        });
    }
});

// Función para formatear el tamaño del archivo
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
}

// Función para eliminar el archivo
function removeFile() {
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileMessage = document.querySelector('.file-message');
    
    if (fileInput) fileInput.value = '';
    if (fileInfo) {
        fileInfo.innerHTML = '';
        fileInfo.style.display = 'none';
    }
    if (fileMessage) fileMessage.style.display = 'block';
}

// Función para cambiar de pestaña
function openTab(event, tabId) {
    // Ocultar todos los contenidos de pestañas
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(function(content) {
        content.classList.remove('active');
    });
    
    // Desactivar todos los botones de pestañas
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(function(button) {
        button.classList.remove('active');
    });
    
    // Mostrar el contenido de la pestaña seleccionada
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Activar el botón de la pestaña seleccionada
    if (event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
}

// Función para copiar una recomendación
function copiarRecomendacion(boton, texto) {
    // Usamos un textarea temporal para copiar texto con formato
    const textarea = document.createElement('textarea');
    textarea.value = texto;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    
    // Cambiar el ícono temporalmente
    const iconoOriginal = boton.innerHTML;
    boton.innerHTML = '<i class="fas fa-check"></i>';
    
    setTimeout(function() {
        boton.innerHTML = iconoOriginal;
    }, 2000);
}
// Sistema de tooltips para la tabla de resultados
document.addEventListener('DOMContentLoaded', function() {
    // Crear el tooltip como un elemento fijo en el DOM
    if (!document.getElementById('custom-tooltip')) {
        const tooltip = document.createElement('div');
        tooltip.id = 'custom-tooltip';
        tooltip.style.cssText = `
            position: absolute;
            width: 350px;
            padding: 16px;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: rgba(255, 255, 255, 0.95);
            font-size: 14px;
            z-index: 1000;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            opacity: 0;
            pointer-events: none;
            transition: all 0.2s ease;
            transform: translateY(10px);
            line-height: 1.5;
        `;
        document.body.appendChild(tooltip);
    }
    
    const tooltip = document.getElementById('custom-tooltip');
    
    // Función para mostrar los tooltips
    function showTooltip(seccion, puntos, elemento) {
        // Calcular porcentaje
        const [obtenidos, total] = puntos.split('/').map(n => parseInt(n.trim()));
        const porcentaje = (obtenidos / total) * 100;
        
        // Determinar icono y mensaje según la sección y puntuación
        let icono = '';
        let mensaje = '';
        let iconoColor = '';
        
        if (porcentaje < 40) {
            icono = '<i class="fas fa-exclamation-triangle"></i>';
            iconoColor = '#FF453A';
        } else if (porcentaje < 70) {
            icono = '<i class="fas fa-exclamation-circle"></i>';
            iconoColor = '#FFD60A';
        } else {
            icono = '<i class="fas fa-check-circle"></i>';
            iconoColor = '#30D158';
        }
        
        // Corrección para la sección Perfil
        if (seccion === "Perfil") {
            if (porcentaje < 40) {
                mensaje = "Tu perfil profesional necesita una mejora significativa. Añade un resumen claro de 3-5 líneas que destaque tus principales fortalezas y experiencia relevante para el puesto.";
            } else if (porcentaje < 70) {
                mensaje = "Tu perfil es básico pero funcional. Para mejorarlo, personalízalo según el puesto específico, destacando experiencias y habilidades directamente relevantes.";
            } else {
                mensaje = "Excelente perfil profesional. Comunica claramente tu propuesta de valor y está bien alineado con el puesto. Es conciso pero informativo, destacando tus fortalezas clave.";
                
                // Si tiene perfil excelente pero puntuación < 15, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        // Si tiene perfil realmente completo y bien estructurado (emojis, nombre, rol al inicio)
                        let perfilCompleto = tiene_emojis && 
                                            texto_cv.toLowerCase().includes("perfil") &&
                                            texto_cv.split('\n').slice(0, 5).join(' ').length > 100;
                        
                        if (perfilCompleto) {
                            // Actualizar a 15/15
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                puntosElement.textContent = "15 / 15";
                            }
                            
                            // Actualizar la barra de progreso
                            const progressElement = elemento.querySelector('.progress');
                            if (progressElement) {
                                progressElement.style.width = "100%";
                            }
                            
                            // Actualizar el mensaje de feedback
                            const feedbackElement = elemento.querySelector('td:nth-child(4)');
                            if (feedbackElement) {
                                feedbackElement.innerHTML = "✅ Excelente";
                            }
                            
                            // Cambiar el color de la fila a verde
                            elemento.classList.remove('bajo', 'medio');
                            elemento.classList.add('alto');
                        }
                    }, 100);
                }
            }
        } 
        // Corrección para la sección Educación
        else if (seccion === "Educación") {
            if (porcentaje < 40) {
                mensaje = "La sección de educación requiere más detalles. Incluye el nombre completo de las instituciones, titulaciones obtenidas, fechas precisas y cursos relevantes para el puesto.";
            } else if (porcentaje < 70) {
                mensaje = "Tu sección de educación contiene información básica pero podría ser más completa. Añade especialización, logros académicos destacados o proyectos relevantes.";
            } else {
                mensaje = "Muy buena sección de educación con detalles completos de tu formación. La información está bien estructurada y destaca aspectos relevantes para el puesto.";
                
                // Si tiene educación bien detallada pero puntuación < 15, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        const educacionCompleta = texto_cv.match(/universidad|máster|grado|licenciatura|ingenier[íi]a|doctorado/gi);
                        
                        if (educacionCompleta && educacionCompleta.length >= 2) {
                            // Actualizar a 15/15
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                puntosElement.textContent = "15 / 15";
                            }
                            
                            // Actualizar la barra de progreso
                            const progressElement = elemento.querySelector('.progress');
                            if (progressElement) {
                                progressElement.style.width = "100%";
                            }
                            
                            // Actualizar el mensaje de feedback
                            const feedbackElement = elemento.querySelector('td:nth-child(4)');
                            if (feedbackElement) {
                                feedbackElement.innerHTML = "✅ Excelente";
                            }
                            
                            // Cambiar el color de la fila a verde
                            elemento.classList.remove('bajo', 'medio');
                            elemento.classList.add('alto');
                        }
                    }, 100);
                }
            }
        }
        // Corrección para la sección Educación
        else if (seccion === "Habilidades") {
            if (porcentaje < 40) {
                mensaje = "Tu sección de habilidades necesita una mejora importante. Organiza las habilidades por categorías (técnicas, herramientas, metodologías) y asegúrate de incluir aquellas más relevantes para el puesto.";
            } else if (porcentaje < 70) {
                mensaje = "Tu sección de habilidades está presente pero podría optimizarse. Prioriza las habilidades más relevantes para el puesto y considera agruparlas por categorías para mejorar la legibilidad.";
            } else {
                mensaje = "Excelente sección de habilidades, bien organizada y completa. Las habilidades listadas son altamente relevantes para el puesto y la categorización facilita la lectura.";
                
                // Si tiene habilidades bien organizadas pero puntuación < 15, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        const habilidadesCompletas = texto_cv.match(/lenguajes|frameworks|librerías|herramientas|tecnologías|stack|skills/gi);
                        const tieneViñetas = texto_cv.match(/•|✓|✅|✔|■|◆|★|►|-\s/g);
                        
                        if (habilidadesCompletas && habilidadesCompletas.length >= 2 && tieneViñetas && tieneViñetas.length > 5) {
                            // Actualizar a 15/15
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                puntosElement.textContent = "15 / 15";
                            }
                            
                            // Actualizar la barra de progreso
                            const progressElement = elemento.querySelector('.progress');
                            if (progressElement) {
                                progressElement.style.width = "100%";
                            }
                            
                            // Actualizar el mensaje de feedback
                            const feedbackElement = elemento.querySelector('td:nth-child(4)');
                            if (feedbackElement) {
                                feedbackElement.innerHTML = "✅ Excelente";
                            }
                            
                            // Cambiar el color de la fila a verde
                            elemento.classList.remove('bajo', 'medio');
                            elemento.classList.add('alto');
                        }
                    }, 100);
                }
            }
        }
        else if (seccion === "Experiencia") {
            if (porcentaje < 40) {
                mensaje = "La sección de experiencia profesional necesita más detalle. Estructura cada posición con: cargo, empresa, fechas, responsabilidades clave y logros medibles. Utiliza verbos de acción y cuantifica resultados.";
            } else if (porcentaje < 70) {
                mensaje = "Tu experiencia profesional está descrita de manera básica. Mejora enfocándote en resultados y logros cuantificables en lugar de solo responsabilidades. Destaca proyectos exitosos y contribuciones.";
            } else {
                mensaje = "Experiencia profesional muy bien detallada con logros cuantificables. La estructura es clara y la progresión profesional evidente. Demuestra claramente tu capacidad para generar resultados.";
                
                // Si tiene experiencia bien detallada pero puntuación < 15, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        const tieneEmpresas = texto_cv.match(/S\.A\.|S\.L\.|Inc\.|Ltd\.|LLC|GmbH|Corp/g);
                        const tieneFechas = texto_cv.match(/20\d\d\s*[-–]\s*(20\d\d|presente|actualidad|actual|present)/gi);
                        const tieneLogros = texto_cv.match(/\d+%|reduc|aument|implement|desarroll|liderad/gi);
                        
                        if ((tieneEmpresas || tieneFechas) && tieneLogros && tieneLogros.length > 2) {
                            // Actualizar a 15/15 o al menos mejorar a 14/15
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                const puntosActuales = parseInt(puntosElement.textContent);
                                if (puntosActuales < 14) {
                                    puntosElement.textContent = "14 / 15";
                                    
                                    // Actualizar la barra de progreso
                                    const progressElement = elemento.querySelector('.progress');
                                    if (progressElement) {
                                        progressElement.style.width = "93%";
                                    }
                                    
                                    // Actualizar el mensaje de feedback
                                    const feedbackElement = elemento.querySelector('td:nth-child(4)');
                                    if (feedbackElement) {
                                        feedbackElement.innerHTML = "✅ Muy bueno";
                                    }
                                    
                                    // Cambiar el color de la fila a verde
                                    elemento.classList.remove('bajo', 'medio');
                                    elemento.classList.add('alto');
                                }
                            }
                        }
                    }, 100);
                }
            }
        }
        else if (seccion === "Certificados") {
            if (porcentaje < 40) {
                mensaje = "Faltan certificaciones relevantes que validen tus conocimientos técnicos. Incluye certificaciones actuales relacionadas con el puesto, especificando la institución emisora y fecha de obtención.";
            } else if (porcentaje < 70) {
                mensaje = "Has incluido algunas certificaciones, pero considera obtener otras más específicas y actuales para el puesto. Las certificaciones técnicas recientes aumentan significativamente tu competitividad.";
            } else {
                mensaje = "Excelentes certificaciones, actualizadas y altamente relevantes para el puesto. Demuestran compromiso con el desarrollo profesional y validación formal de tus conocimientos técnicos.";
                
                // Si tiene certificaciones pero puntuación baja, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        const tieneCertificaciones = texto_cv.match(/certificad[oa]|certific|curso|diploma|AWS|Microsoft|Google|Cisco|Oracle|Udemy|Coursera/gi);
                        
                        if (tieneCertificaciones && tieneCertificaciones.length >= 2) {
                            // Mejora a 8/10 o 9/10 según cantidad
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                const puntosActuales = parseInt(puntosElement.textContent);
                                if (puntosActuales < 8) {
                                    // Si tiene varias certificaciones, aumentar a 8/10
                                    puntosElement.textContent = "8 / 10";
                                    
                                    // Actualizar la barra de progreso
                                    const progressElement = elemento.querySelector('.progress');
                                    if (progressElement) {
                                        progressElement.style.width = "80%";
                                    }
                                    
                                    // Actualizar el mensaje de feedback
                                    const feedbackElement = elemento.querySelector('td:nth-child(4)');
                                    if (feedbackElement) {
                                        feedbackElement.innerHTML = "✅ Bueno: Complementa con más certificaciones";
                                    }
                                    
                                    // Cambiar el color de la fila a verde
                                    elemento.classList.remove('bajo', 'medio');
                                    elemento.classList.add('alto');
                                }
                            }
                        }
                    }, 100);
                }
            }
        }
        else if (seccion === "Idiomas") {
            if (porcentaje < 40) {
                mensaje = "La sección de idiomas necesita mejoras. Añade todos los idiomas que dominas con su nivel específico según marcos reconocidos (A1-C2). El dominio de inglés es especialmente importante en roles técnicos.";
            } else if (porcentaje < 70) {
                mensaje = "Tu sección de idiomas es adecuada pero podría mejorar. Especifica más claramente tu nivel en cada idioma y considera mencionar experiencias prácticas de uso (ej: 'Experiencia en documentación técnica en inglés').";
            } else {
                mensaje = "Tu sección de idiomas está por un buen camino pero no olvides especificar mucho mas tu nivel de idioma ";
                
                // Si tiene idiomas bien especificados pero puntuación baja, mejorar
                if (porcentaje >= 70 && porcentaje < 95) {
                    setTimeout(() => {
                        const tieneIdiomasDetallados = texto_cv.match(/inglés|english|español|spanish|nivel|level|B1|B2|C1|C2|fluent|fluido|nativo|native|avanzado|advanced/gi);
                        const tieneCertificacion = texto_cv.match(/TOEFL|IELTS|Cambridge|DELE|DALF|Goethe/gi);
                        
                        if (tieneIdiomasDetallados && tieneIdiomasDetallados.length >= 3) {
                            // Mejorar a 8/10 o más según detalle
                            const puntosElement = elemento.querySelector('td:nth-child(2)');
                            if (puntosElement) {
                                const puntosActuales = parseInt(puntosElement.textContent);
                                let nuevaPuntuacion = 8;
                                
                                // Si además tiene certificaciones de idiomas, subir a 9/10
                                if (tieneCertificacion) {
                                    nuevaPuntuacion = 9;
                                }
                                
                                if (puntosActuales < nuevaPuntuacion) {
                                    puntosElement.textContent = nuevaPuntuacion + " / 10";
                                    
                                    // Actualizar la barra de progreso
                                    const progressElement = elemento.querySelector('.progress');
                                    if (progressElement) {
                                        progressElement.style.width = (nuevaPuntuacion * 10) + "%";
                                    }
                                    
                                    // Actualizar el mensaje de feedback
                                    const feedbackElement = elemento.querySelector('td:nth-child(4)');
                                    if (feedbackElement) {
                                        feedbackElement.innerHTML = "✅ Muy buena sección de idiomas con niveles claramente especificados. El dominio lingüístico demostrado es adecuado para las exigencias del puesto y potencia tu perfil internacional.";
                                    }
                                    
                                    // Cambiar el color de la fila a verde
                                    elemento.classList.remove('bajo', 'medio');
                                    elemento.classList.add('alto');
                                }
                            }
                        }
                    }, 100);
                }
            }
        }

        // Sección de Datos con evaluación MÁS ESTRICTA
        // Modifica esta parte en app.js - función showTooltip
        else if (seccion === "Datos") {
            // Calcular la puntuación real (0-100%)
            const porcentajeReal = (obtenidos / total) * 100;
            
            // Determinar el mensaje basado en la puntuación real
            if (porcentajeReal >= 90) {
                mensaje = "Información de contacto completa y bien presentada. Incluye todos los canales profesionales relevantes y facilita múltiples vías para que los reclutadores te contacten.";
                icono = '<i class="fas fa-check-circle"></i>';
                iconoColor = '#30D158';
            } else if (porcentajeReal >= 80) {
                mensaje = "Muy buena información de contacto, casi completa. Contiene los elementos esenciales y algún perfil profesional. Para ser excelente, considera añadir más vías de contacto profesional.";
                icono = '<i class="fas fa-check-circle"></i>';
                iconoColor = '#30D158';
            } else if (porcentajeReal >= 70) {
                mensaje = "Buena información de contacto con datos esenciales. Considera añadir más enlaces a perfiles profesionales como LinkedIn, GitHub o portafolio personal.";
                icono = '<i class="fas fa-check-circle"></i>';
                iconoColor = '#30D158';
            } else if (porcentajeReal >= 60) {
                mensaje = "Información de contacto básica pero suficiente. Añade perfiles profesionales online (LinkedIn, GitHub) para facilitar que los reclutadores conozcan mejor tu experiencia y proyectos.";
                icono = '<i class="fas fa-exclamation-circle"></i>';
                iconoColor = '#FFD60A';
            } else if (porcentajeReal >= 40) {
                mensaje = "La información de contacto es incompleta. Asegúrate de incluir al menos tu nombre completo, email profesional, teléfono y algún perfil en redes profesionales como LinkedIn.";
                icono = '<i class="fas fa-exclamation-circle"></i>';
                iconoColor = '#FFD60A';
            } else {
                mensaje = "La información de contacto es insuficiente. Asegúrate de incluir email profesional, teléfono, ubicación, LinkedIn actualizado y GitHub para roles técnicos. Esta información debe ser fácilmente visible.";
                icono = '<i class="fas fa-exclamation-triangle"></i>';
                iconoColor = '#FF453A';
            }
            
            // CORRECCIÓN: Verificar manualmente el contenido del CV para mostrar tooltip correcto
            // Extraer el texto del CV desde la vista previa si está disponible
            const previewContainer = document.querySelector('.preview-container pre');
            if (previewContainer) {
                const textoCV = previewContainer.textContent || '';
                
                // Detectar elementos básicos y profesionales
                const tieneNombreCompleto = /[A-Z][a-z]+\s+[A-Z][a-z]+(\s+[A-Z][a-z]+)?/.test(textoCV);
                const tieneEmail = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(textoCV);
                const tieneTelefono = /(\+\d{1,3}[ -]?)?(\(\d{1,3}\)[ -]?)?\d{3}[ -]?\d{3,4}[ -]?\d{3,4}/.test(textoCV);
                const tieneLinkedIn = /linkedin\.com\/in\/[a-zA-Z0-9_-]+/.test(textoCV.toLowerCase());
                const tieneGitHub = /github\.com\/[a-zA-Z0-9_-]+/.test(textoCV.toLowerCase());
                const tieneWeb = /(portfolio|portafolio|web|website|sitio|blog)[:;\s]+[a-zA-Z0-9][a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/.test(textoCV.toLowerCase());
                const tieneUbicacion = /(ciudad|ubicación|location|dirección|address|city)[:;]?\s*[A-Z][a-zA-Z]+|[📍🌍🌎🌏🏙️]\s*[A-Z][a-zA-Z]+/.test(textoCV);
                // Contar perfiles profesionales
                const perfilesCount = [tieneLinkedIn, tieneGitHub, tieneWeb].filter(Boolean).length;
                
                // Si solo tiene email y teléfono, mostrar mensaje básico aunque el puntaje sea alto
                if (tieneNombreCompleto && tieneEmail && tieneTelefono && perfilesCount === 0 && porcentajeReal > 60) {
                    mensaje = "Información de contacto básica pero suficiente. Añade perfiles profesionales online (LinkedIn, GitHub) para facilitar que los reclutadores conozcan mejor tu experiencia y proyectos.";
                    iconoColor = '#FFD60A';
                    icono = '<i class="fas fa-exclamation-circle"></i>';
                }
                // Si falta email o teléfono, mostrar mensaje de error aunque el puntaje sea alto
                else if ((!tieneEmail || !tieneTelefono || !tieneUbicacion) && porcentajeReal > 40) {
                    mensaje = "La información de contacto es incompleta. Asegúrate de incluir al menos tu nombre completo, email profesional, teléfono, dirección o ubicación y algún perfil en redes profesionales como LinkedIn.";
                    iconoColor = '#FFD60A';
                    icono = '<i class="fas fa-exclamation-circle"></i>';
                }
            }
        }
        else if (seccion === "Formato") {
            if (porcentaje < 40) {
                mensaje = "El formato de tu CV necesita una mejora significativa. Utiliza una estructura clara con secciones bien definidas, viñetas para facilitar la lectura, espaciado consistente, y no más de 2 páginas.";
            } else if (porcentaje < 70) {
                mensaje = "El formato de tu CV es funcional pero mejorable. Trabaja en la consistencia visual (espaciado, fuentes, estilo), uso de viñetas para facilitar el escaneo rápido, y priorización visual de la información más relevante.";
            } else {
                mensaje = "Excelente formato, profesional y bien estructurado. Es visualmente atractivo y prioriza eficazmente la información más relevante. La consistencia visual facilita la lectura.";
                
                // CORRECCIÓN: Si tiene un buen formato en general (≥ 70%), pero puntuación baja, mejorar visualmente
                if (porcentaje >= 70 && porcentaje < 90 && tiene_emojis) {
                    setTimeout(() => {
                        // Actualizar visualmente la puntuación a un mejor valor
                        const puntosElement = elemento.querySelector('td:nth-child(2)');
                        if (puntosElement) {
                            // Si la puntuación es < 8, actualizar a 8/10
                            if (parseInt(puntosElement.textContent) < 8) {
                                puntosElement.textContent = "8 / 10";
                                
                                // Actualizar la barra de progreso
                                const progressElement = elemento.querySelector('.progress');
                                if (progressElement) {
                                    progressElement.style.width = "80%";
                                }
                                
                                // Actualizar el mensaje de feedback
                                const feedbackElement = elemento.querySelector('td:nth-child(4)');
                                if (feedbackElement) {
                                    feedbackElement.innerHTML = "✅ Muy bueno: Formato profesional y moderno";
                                }
                                
                                // Cambiar el color de la fila a verde
                                elemento.classList.remove('bajo', 'medio');
                                elemento.classList.add('alto');
                            }
                        }
                    }, 100); // Pequeño retraso para asegurar que los elementos estén disponibles
                }
            }
        }
        
        // Actualizar contenido del tooltip con diseño similar a la imagen
        tooltip.innerHTML = `
            <div style="display: flex; align-items: flex-start; margin-bottom: 10px;">
                <span style="color: ${iconoColor}; font-size: 18px; margin-right: 10px;">${icono}</span>
                <div style="font-weight: 500; font-size: 16px;">${seccion}</div>
            </div>
            <div style="color: rgba(255, 255, 255, 0.85); line-height: 1.6; font-size: 14px;">
                ${mensaje}
            </div>
        `;
        
        // Posicionar tooltip alineado con la fila y ligeramente por encima
        const rect = elemento.getBoundingClientRect();
        
        // Calcular posición óptima (siempre a la derecha)
        let leftPos = rect.right + 20;

        // Comprobar el ancho de la ventana para confirmar que hay espacio
        const windowWidth = window.innerWidth;
        const tableRect = document.querySelector('.tabla-resultados').getBoundingClientRect();
        const availableSpace = windowWidth - tableRect.right;

        console.log('Espacio disponible a la derecha:', availableSpace, 'px');

        // Forzar que siempre aparezca a la derecha si hay al menos 100px disponibles
        if (availableSpace >= 100) {
            // Hay espacio suficiente, colocar a la derecha con margen
            leftPos = rect.right + 20;
        } else {
            // Si realmente no hay espacio, entonces mostrar a la izquierda
            leftPos = rect.left - 370;
            
            // Como última opción, si no hay espacio ni a la izquierda, centrar debajo
            if (leftPos < 10) {
                leftPos = Math.max(20, (tableRect.left + tableRect.right - 350) / 2);
                const offsetY = rect.height + 10; // Mostrar debajo con margen
                tooltip.style.top = `${rect.bottom + window.scrollY + 10}px`;
            }
        }

        // Posicionar el tooltip ligeramente más arriba que la fila
        const offsetY = -10; // Ajusta este valor para subirlo más o menos

        tooltip.style.left = `${leftPos}px`;
        tooltip.style.top = `${rect.top + window.scrollY + offsetY}px`;

        // Mostrar tooltip con animación
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }
    
    // Función para ocultar el tooltip
    function hideTooltip() {
        const tooltip = document.getElementById('custom-tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
            tooltip.style.transform = 'translateY(10px)';
        }
    }
    
    // Añadir eventos a las filas de la tabla
    const filas = document.querySelectorAll('.tabla-resultados tbody tr');
    
    filas.forEach(fila => {
        // Hacer que el cursor cambie al pasar sobre la fila
        fila.style.cursor = 'pointer';
        
        fila.addEventListener('mouseenter', function() {
            const seccion = this.querySelector('td:first-child strong').textContent;
            const puntos = this.querySelector('td:nth-child(2)').textContent;
            showTooltip(seccion, puntos, this);
            
            // Resaltar la fila
            this.style.backgroundColor = 'rgba(255, 255, 255, 0.08)';
        });
        
        fila.addEventListener('mouseleave', function() {
            hideTooltip();
            this.style.backgroundColor = '';
        });
    });
    
    // Ocultar tooltip al hacer scroll
    window.addEventListener('scroll', hideTooltip);
});

// Función adicional para manejar la interacción táctil (para dispositivos móviles)
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si el dispositivo es táctil
    const isTouchDevice = 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    
    if (isTouchDevice) {
        // Añadir clases específicas para dispositivos táctiles
        document.body.classList.add('touch-device');
        
        // Cambiar comportamiento para mostrar tooltips en dispositivos táctil
        const filas = document.querySelectorAll('.tabla-resultados tbody tr');
        
        filas.forEach(fila => {
            // Eliminar eventos de hover en dispositivos táctiles
            fila.classList.add('touch-row');
            
            // Modificar el evento click para dispositivos táctiles
            const existingClickHandler = fila.onclick;
            fila.onclick = null;
            
            fila.addEventListener('click', function(e) {
                // En dispositivos táctiles, mostrar directamente el modal completo
                mostrarModalDetallado(this);
                
                // Prevenir la propagación del evento
                e.stopPropagation();
            });
        });
    }
});