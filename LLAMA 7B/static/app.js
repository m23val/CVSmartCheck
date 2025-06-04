// app.js - JavaScript corregido para CV SmartCheck Llama 2

// Función principal para cambiar entre pestañas
function openTab(event, tabId) {
    console.log('Abriendo tab:', tabId);
    
    // Ocultar todos los contenidos de pestañas
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(function(content) {
        content.classList.remove('active');
        content.style.display = 'none';
    });
    
    // Desactivar todos los botones de pestañas
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(function(button) {
        button.classList.remove('active');
    });
    
    // Mostrar el contenido seleccionado
    const selectedTab = document.getElementById(tabId);
    if (selectedTab) {
        selectedTab.classList.add('active');
        selectedTab.style.display = 'block';
        console.log('Tab mostrado:', tabId);
    } else {
        console.error('Tab no encontrado:', tabId);
    }
    
    // Activar el botón seleccionado
    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }
    
    // Prevenir comportamiento por defecto
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
}

// Inicialización principal cuando carga el DOM
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Iniciando CV SmartCheck - Llama 2 JavaScript');
    
    // Inicializar pestañas
    initializeTabs();
    
    // Inicializar formulario de carga
    initializeFileUpload();
    
    // Inicializar barras de progreso
    initializeProgressBars();
    
    // Inicializar barras de similitud semántica
    initializeSemanticBars();
    
    console.log('✅ JavaScript inicializado correctamente');
});

// Función para inicializar las pestañas
function initializeTabs() {
    console.log('🔧 Inicializando pestañas...');
    
    // Agregar event listeners a todos los botones de pestañas
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            const tabId = this.getAttribute('data-tab');
            console.log('Click en pestaña:', tabId);
            openTab(e, tabId);
        });
    });
    
    // Asegurar que la primera pestaña esté activa
    const firstTab = document.querySelector('.tab-btn.active');
    if (firstTab) {
        const tabId = firstTab.getAttribute('data-tab');
        console.log('Activando primera pestaña:', tabId);
        openTab(null, tabId);
    }
    
    console.log('✅ Pestañas inicializadas');
}

// Función para inicializar la carga de archivos
function initializeFileUpload() {
    console.log('📁 Inicializando carga de archivos...');
    
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileMessage = document.querySelector('.file-message');
    
    if (fileInput) {
        console.log("Configurando input de archivos para Llama 2");
        
        // Crear botón visible
        if (fileMessage) {
            fileMessage.innerHTML = '<div class="file-message-content"><span>Arrastra tu archivo aquí</span><div class="custom-file-button">Seleccionar archivo</div></div>';
            
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
    
    // Inicializar formulario con spinner de carga específico para Llama 2
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validar archivo
            if (fileInput && !fileInput.files.length) {
                alert('Por favor selecciona un archivo CV.');
                return;
            }
            
            // Validar puesto
            const puestoSelect = document.getElementById('puestoSelect');
            if (puestoSelect && (puestoSelect.value === "" || puestoSelect.selectedIndex === 0)) {
                alert('Por favor selecciona un puesto.');
                return;
            }
            
            // Mostrar modal con spinner específico para Llama 2
            showLoadingModal();
            
            // Enviar formulario después del modal
            setTimeout(() => {
                uploadForm.submit();
            }, 1000);
        });
    }
    
    console.log('✅ Carga de archivos inicializada');
}

// Función para mostrar modal de carga
function showLoadingModal() {
    const progressModal = document.getElementById('progressModal');
    if (progressModal) {
        const modalContent = progressModal.querySelector('.modal-content');
        if (modalContent) {
            modalContent.innerHTML = `
                <div class="spinner-container">
                    <div class="spinner"></div>
                    <div class="spinner-text">🦙 Analizando con Llama 2 7B...</div>
                    <div class="spinner-timer">Evaluación semántica: <span id="countdown">15</span> segundos</div>
                    <div class="spinner-note">El análisis semántico puede tomar varios minutos...</div>
                </div>
            `;
        }
        
        progressModal.style.display = 'flex';
        
        // Contador específico para Llama 2
        let segundosRestantes = 15;
        const countdownElement = document.getElementById('countdown');
        
        const contador = setInterval(function() {
            segundosRestantes--;
            
            if (countdownElement) {
                countdownElement.textContent = segundosRestantes;
            }
            
            const spinnerText = document.querySelector('.spinner-text');
            if (spinnerText) {
                if (segundosRestantes <= 12 && segundosRestantes > 8) {
                    spinnerText.textContent = '🦙 Procesando texto con IA...';
                } else if (segundosRestantes <= 8 && segundosRestantes > 4) {
                    spinnerText.textContent = '🦙 Evaluando similitud semántica...';
                } else if (segundosRestantes <= 4) {
                    spinnerText.textContent = '🦙 Generando recomendaciones...';
                }
            }
            
            if (segundosRestantes <= 0) {
                clearInterval(contador);
                // El formulario ya se envió, solo actualizar mensaje
                if (spinnerText) {
                    spinnerText.textContent = '🦙 Análisis en progreso...';
                }
                if (countdownElement) {
                    countdownElement.textContent = '∞';
                }
            }
        }, 1000);
    }
}

// Función para inicializar barras de progreso
function initializeProgressBars() {
    console.log('📊 Inicializando barras de progreso...');
    
    const progressBars = document.querySelectorAll('.progress[data-puntos]');
    progressBars.forEach(function(bar) {
        const puntos = parseFloat(bar.dataset.puntos) || 0;
        const total = parseFloat(bar.dataset.total) || 1;
        const porcentaje = Math.round((puntos / total) * 100);
        
        // Animación suave
        setTimeout(() => {
            bar.style.width = porcentaje + '%';
            bar.style.transition = 'width 1s ease-out';
        }, 300);
    });
    
    console.log('✅ Barras de progreso inicializadas');
}

// Función para inicializar barras de similitud semántica
function initializeSemanticBars() {
    console.log('🧠 Inicializando barras semánticas...');
    
    setTimeout(() => {
        document.querySelectorAll('.llama-bar').forEach(function(bar) {
            const similitud = bar.dataset.similitud || 0;
            bar.style.width = similitud + '%';
            bar.style.transition = 'width 1.5s ease-out';
        });
        
        document.querySelectorAll('.similitud-bar').forEach(function(bar) {
            const similitud = bar.dataset.similitud || 0;
            bar.style.width = similitud + '%';
            bar.style.transition = 'width 1.5s ease-out';
        });
    }, 500);
    
    console.log('✅ Barras semánticas inicializadas');
}

// Funciones auxiliares
function formatSize(bytes) {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
}

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
    
    console.log('📁 Archivo removido');
}

// Función para exportar resultados
function exportarResultados() {
    console.log('💾 Exportando resultados...');
    
    try {
        const resultados = {
            archivo: document.querySelector('.resultado-header h2')?.textContent || 'CV',
            timestamp: new Date().toISOString(),
            puntuacion_total: document.querySelector('.puntaje-number')?.textContent || '0',
            puntuacion_semantica: document.querySelector('.semantic-score-value')?.textContent || '0',
            detalles: extractTableData(),
            recomendaciones: extractRecommendations()
        };
        
        const blob = new Blob([JSON.stringify(resultados, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `analisis_semantico_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        console.log('✅ Resultados exportados');
    } catch (error) {
        console.error('❌ Error al exportar:', error);
        alert('Error al exportar resultados');
    }
}

// Funciones auxiliares para exportación
function extractTableData() {
    const rows = document.querySelectorAll('.tabla-resultados tbody tr');
    const data = [];
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 4) {
            data.push({
                seccion: cells[0].textContent.trim(),
                puntuacion: cells[1].textContent.trim(),
                evaluacion: cells[3].textContent.trim()
            });
        }
    });
    
    return data;
}

function extractRecommendations() {
    const recoElements = document.querySelectorAll('.reco-contenido p');
    const recommendations = [];
    
    recoElements.forEach(elem => {
        if (elem.textContent.trim()) {
            recommendations.push(elem.textContent.trim());
        }
    });
    
    return recommendations;
}

// Event listeners globales
window.addEventListener('load', function() {
    console.log('🌟 Página completamente cargada');
    
    // Verificar que todo esté funcionando
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    console.log(`📋 Pestañas encontradas: ${tabButtons.length} botones, ${tabContents.length} contenidos`);
    
    if (tabButtons.length === 0) {
        console.warn('⚠️ No se encontraron pestañas en la página');
    }
});

// Manejo de errores globales
window.addEventListener('error', function(e) {
    console.error('❌ Error JavaScript:', e.error);
});

console.log('📁 app.js cargado correctamente - CV SmartCheck Llama 2');