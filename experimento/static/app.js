/**
 * Inicializar formulario con spinner de carga para modelo experimental
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
                            <div class="spinner-text">Analizando con modelo experimental TF-IDF...</div>
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
                            spinnerText.textContent = 'Calculando similitud TF-IDF...';
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
    
    // Inicializar barras de progreso
    const progressBars = document.querySelectorAll('.progress[data-puntos]');
    progressBars.forEach(function(bar) {
        const puntos = parseFloat(bar.dataset.puntos) || 0;
        const total = parseFloat(bar.dataset.total) || 1;
        const porcentaje = Math.round((puntos / total) * 100 * 10) / 10;
        bar.style.width = porcentaje + '%';
    });
    
    // Inicializar barras de similitud
    const similitudBars = document.querySelectorAll('.similitud-bar[data-similitud]');
    similitudBars.forEach(function(bar) {
        const similitud = parseFloat(bar.dataset.similitud) || 0;
        bar.style.width = similitud + '%';
    });
    
    // Sistema de tooltips para la tabla de resultados
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
        
        // Generar mensaje para el modelo experimental
        if (seccion === "Perfil") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica con el perfil ideal para este puesto. El modelo TF-IDF detecta poca similitud entre tu perfil actual y lo que los reclutadores buscan. Considera personalizarlo específicamente para este puesto.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media con el perfil ideal. El análisis experimental detecta cierta similitud, pero hay oportunidades para mejorar. Considera incluir más términos y habilidades relevantes para el puesto.";
            } else {
                mensaje = "Alta coherencia semántica con el perfil ideal para este puesto. El modelo experimental detecta una buena correlación entre tu perfil y lo que los reclutadores buscan. Excelente trabajo de personalización.";
            }
        } 
        else if (seccion === "Experiencia") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tu experiencia profesional. El análisis TF-IDF detecta poca similitud con lo esperado para este puesto. Considera reescribir tus responsabilidades y logros utilizando términos más relevantes.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tu experiencia. El modelo experimental detecta cierta similitud, pero hay espacio para mejorar. Enfatiza más los proyectos y logros relevantes para este puesto específico.";
            } else {
                mensaje = "Alta coherencia semántica en tu experiencia profesional. El análisis TF-IDF detecta una fuerte correlación con lo esperado para este puesto. Tu experiencia está bien enfocada y relevante.";
            }
        }
        else if (seccion === "Habilidades") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tus habilidades técnicas. El modelo experimental detecta poca similitud con las competencias clave para este puesto. Considera añadir más tecnologías y herramientas relevantes.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tus habilidades. El análisis TF-IDF detecta cierta similitud, pero puedes mejorar. Prioriza las habilidades más relevantes para este puesto específico.";
            } else {
                mensaje = "Alta coherencia semántica en tus habilidades. El modelo experimental detecta una fuerte correlación con las competencias clave para este puesto. Tu stack tecnológico está bien alineado con lo que buscan los reclutadores.";
            }
        }
        else if (seccion === "Educación") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tu formación académica. El análisis TF-IDF detecta poca similitud con lo esperado para este puesto. Considera destacar cursos o especializaciones más relevantes.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tu educación. El modelo experimental detecta cierta similitud, pero hay oportunidades para mejorar. Enfatiza las áreas de estudio más relevantes para este puesto.";
            } else {
                mensaje = "Alta coherencia semántica en tu educación. El análisis TF-IDF detecta una buena correlación entre tu formación y lo esperado para este puesto. Tu background académico complementa bien tus habilidades profesionales.";
            }
        }
        else if (seccion === "Certificados") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tus certificaciones. El modelo experimental detecta poca similitud con las certificaciones valoradas para este puesto. Considera obtener certificaciones más relevantes para el sector.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tus certificaciones. El análisis TF-IDF detecta cierta similitud, pero puedes mejorar. Prioriza certificaciones más reconocidas en la industria para este puesto.";
            } else {
                mensaje = "Alta coherencia semántica en tus certificaciones. El modelo experimental detecta una buena correlación con las certificaciones valoradas para este puesto. Tus credenciales validan bien tus conocimientos técnicos.";
            }
        }
        else if (seccion === "Idiomas") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tu sección de idiomas. El análisis TF-IDF detecta poca similitud con lo esperado. Considera especificar mejor tus niveles y competencias lingüísticas relevantes para este puesto.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tus idiomas. El modelo experimental detecta cierta similitud, pero puedes mejorar. Destaca mejor tus habilidades en inglés técnico u otros idiomas relevantes.";
            } else {
                mensaje = "Alta coherencia semántica en tu sección de idiomas. El análisis TF-IDF detecta una buena correlación con lo esperado para este puesto. Tu perfil lingüístico complementa bien tus habilidades técnicas.";
            }
        }
        else if (seccion === "Datos") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia semántica en tu información de contacto. El modelo experimental sugiere que faltan elementos importantes como perfiles profesionales o datos de contacto estructurados adecuadamente.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia semántica media en tu información de contacto. El análisis TF-IDF detecta los elementos básicos, pero podrías mejorar añadiendo más canales profesionales de contacto.";
            } else {
                mensaje = "Alta coherencia semántica en tu información de contacto. El modelo experimental detecta que tu información está bien estructurada y completa, facilitando el contacto por parte de los reclutadores.";
            }
        }
        else if (seccion === "Formato") {
            if (porcentaje < 40) {
                mensaje = "Baja coherencia estructural en el formato de tu CV. El análisis TF-IDF detecta una estructura que difiere significativamente de los estándares del sector. Considera mejorar la organización y presentación visual.";
            } else if (porcentaje < 70) {
                mensaje = "Coherencia estructural media en el formato. El modelo experimental detecta una estructura aceptable, pero mejorable. Trabaja en la consistencia visual y organización de secciones.";
            } else {
                mensaje = "Alta coherencia estructural en el formato. El análisis TF-IDF detecta una estructura clara y profesional que facilita la lectura y comprensión de tu CV por parte de los reclutadores.";
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