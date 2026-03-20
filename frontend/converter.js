/**
 * Conversor de Coordenadas - Frontend
 * Responsável pela conversão de coordenadas entre sistemas de referência
 */

const API_URL = getApiUrl();

function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    return window.location.origin;
}

// Inicializar ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    loadSystems();
});

/**
 * Carrega os sistemas de referência disponíveis
 */
async function loadSystems() {
    try {
        const response = await fetch(`${API_URL}/api/systems`);
        const data = await response.json();
        
        if (data.systems) {
            // Preencher selects de sistema
            const srcSystemSelect = document.getElementById('srcSystem');
            const dstSystemSelect = document.getElementById('dstSystem');
            const batchSrcSystemSelect = document.getElementById('batchSrcSystem');
            const batchDstSystemSelect = document.getElementById('batchDstSystem');
            
            data.systems.forEach(system => {
                const option = document.createElement('option');
                option.value = system;
                option.textContent = system;
                
                srcSystemSelect.appendChild(option.cloneNode(true));
                dstSystemSelect.appendChild(option.cloneNode(true));
                batchSrcSystemSelect.appendChild(option.cloneNode(true));
                batchDstSystemSelect.appendChild(option.cloneNode(true));
            });
        }
    } catch (error) {
        console.error('Erro ao carregar sistemas:', error);
    }
}

/**
 * Atualiza as zonas UTM de origem
 */
async function updateSrcZones() {
    const system = document.getElementById('srcSystem').value;
    const hemisphere = document.getElementById('srcHemisphere').value;
    const zoneSelect = document.getElementById('srcZone');
    
    if (!system) {
        zoneSelect.innerHTML = '<option value="">Selecione...</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/zones?hemisphere=${hemisphere}`);
        const data = await response.json();
        
        zoneSelect.innerHTML = '<option value="">Selecione...</option>';
        if (data.zones) {
            data.zones.forEach(zone => {
                const option = document.createElement('option');
                option.value = zone;
                option.textContent = zone;
                zoneSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar zonas:', error);
    }
}

/**
 * Atualiza as zonas UTM de destino
 */
async function updateDstZones() {
    const system = document.getElementById('dstSystem').value;
    const hemisphere = document.getElementById('dstHemisphere').value;
    const zoneSelect = document.getElementById('dstZone');
    
    if (!system) {
        zoneSelect.innerHTML = '<option value="">Selecione...</option>';
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/api/zones?hemisphere=${hemisphere}`);
        const data = await response.json();
        
        zoneSelect.innerHTML = '<option value="">Selecione...</option>';
        if (data.zones) {
            data.zones.forEach(zone => {
                const option = document.createElement('option');
                option.value = zone;
                option.textContent = zone;
                zoneSelect.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Erro ao carregar zonas:', error);
    }
}

/**
 * Alterna a visibilidade dos inputs de zona UTM de origem
 */
function toggleSrcInputs() {
    const type = document.getElementById('srcType').value;
    const zoneContainer = document.getElementById('srcZoneContainer');
    
    if (type === 'utm') {
        zoneContainer.style.display = 'grid';
        updateSrcZones();
    } else {
        zoneContainer.style.display = 'none';
    }
}

/**
 * Alterna a visibilidade dos inputs de zona UTM de destino
 */
function toggleDstInputs() {
    const type = document.getElementById('dstType').value;
    const zoneContainer = document.getElementById('dstZoneContainer');
    
    if (type === 'utm') {
        zoneContainer.style.display = 'grid';
        updateDstZones();
    } else {
        zoneContainer.style.display = 'none';
    }
}

/**
 * Converte coordenadas entre sistemas de referência
 */
async function convertCoordinates() {
    try {
        // Validar entradas
        const srcSystem = document.getElementById('srcSystem').value;
        const srcType = document.getElementById('srcType').value;
        const srcX = parseFloat(document.getElementById('srcX').value);
        const srcY = parseFloat(document.getElementById('srcY').value);
        const dstSystem = document.getElementById('dstSystem').value;
        const dstType = document.getElementById('dstType').value;
        
        if (!srcSystem || !dstSystem || isNaN(srcX) || isNaN(srcY)) {
            showError('Por favor, preencha todos os campos obrigatórios');
            return;
        }
        
        let srcZone = null;
        let dstZone = null;
        
        if (srcType === 'utm') {
            srcZone = document.getElementById('srcZone').value;
            if (!srcZone) {
                showError('Selecione a zona UTM de origem');
                return;
            }
        }
        
        if (dstType === 'utm') {
            dstZone = document.getElementById('dstZone').value;
            if (!dstZone) {
                showError('Selecione a zona UTM de destino');
                return;
            }
        }
        
        // Fazer requisição ao backend
        const response = await fetch(`${API_URL}/convert/system`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                x: srcX,
                y: srcY,
                src_system: srcSystem,
                src_zone: srcZone,
                dst_system: dstSystem,
                dst_zone: dstZone
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showError(data.error || 'Erro ao converter coordenadas');
            return;
        }
        
        // Exibir resultado
        displayResult(data);
        
        // Adicionar ponto ao mapa
        addPointToMap({
            name: `${srcSystem} → ${dstSystem}`,
            x: data.x,
            y: data.y,
            srcSystem: srcSystem,
            dstSystem: dstSystem
        });
        
    } catch (error) {
        showError('Erro ao processar conversão: ' + error.message);
    }
}

/**
 * Exibe o resultado da conversão
 */
function displayResult(data) {
    const resultBox = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    let html = '<div class="result-content">';
    
    // Coordenadas de origem
    html += '<div class="result-item">';
    html += '<label>Coordenada X</label>';
    html += `<value>${data.x.toFixed(6)}</value>`;
    html += '</div>';
    
    html += '<div class="result-item">';
    html += '<label>Coordenada Y</label>';
    html += `<value>${data.y.toFixed(6)}</value>`;
    html += '</div>';
    
    // Sistema e zona de origem
    html += '<div class="result-item">';
    html += '<label>Sistema de Origem</label>';
    html += `<value>${data.src_system}${data.src_zone ? ' - ' + data.src_zone : ''}</value>`;
    html += '</div>';
    
    // Sistema e zona de destino
    html += '<div class="result-item">';
    html += '<label>Sistema de Destino</label>';
    html += `<value>${data.dst_system}${data.dst_zone ? ' - ' + data.dst_zone : ''}</value>`;
    html += '</div>';
    
    // Código EPSG
    html += '<div class="result-item">';
    html += '<label>EPSG Origem</label>';
    html += `<value>${data.src_epsg}</value>`;
    html += '</div>';
    
    html += '<div class="result-item">';
    html += '<label>EPSG Destino</label>';
    html += `<value>${data.dst_epsg}</value>`;
    html += '</div>';
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    resultBox.style.display = 'block';
}

/**
 * Exibe mensagem de erro
 */
function showError(message) {
    const resultBox = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = `<div class="error-message">${message}</div>`;
    resultBox.style.display = 'block';
}

/**
 * Exibe mensagem de sucesso
 */
function showSuccess(message) {
    const resultBox = document.getElementById('result');
    const resultContent = document.getElementById('resultContent');
    
    resultContent.innerHTML = `<div class="success-message">${message}</div>`;
    resultBox.style.display = 'block';
}
