// Determinar a URL da API dinamicamente
function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    return window.location.origin;
}

const API_URL = getApiUrl();

/**
 * Converte Graus Minutos Segundos para Graus Decimais
 */
function dmsToDD(degrees, minutes, seconds, direction) {
    let dd = parseFloat(degrees) + parseFloat(minutes) / 60 + parseFloat(seconds) / 3600;
    if (direction === 'S' || direction === 'W') {
        dd *= -1;
    }
    return dd;
}

/**
 * Converte Graus Decimais para Graus Minutos Segundos
 */
function ddToDMS(dd) {
    const isNegative = dd < 0;
    dd = Math.abs(dd);
    const degrees = Math.floor(dd);
    const minutes = Math.floor((dd - degrees) * 60);
    const seconds = ((dd - degrees - minutes / 60) * 3600).toFixed(2);
    return { degrees, minutes, seconds, isNegative };
}

/**
 * Detecta o formato de entrada das coordenadas
 */
function detectCoordinateFormat(x, y) {
    const xNum = parseFloat(x);
    const yNum = parseFloat(y);
    
    // Validar se são números
    if (isNaN(xNum) || isNaN(yNum)) {
        return { format: 'invalid', message: 'Coordenadas devem ser números válidos' };
    }
    
    // Verificar se são Graus Decimais (DD)
    if (xNum >= -180 && xNum <= 180 && yNum >= -90 && yNum <= 90) {
        return { format: 'dd', message: 'Formato detectado: Graus Decimais (DD)' };
    }
    
    // Verificar se são UTM (valores grandes)
    if (xNum > 160000 && xNum < 840000 && yNum > 0 && yNum < 10000000) {
        return { format: 'utm', message: 'Formato detectado: UTM' };
    }
    
    return { format: 'unknown', message: 'Formato de coordenadas não reconhecido' };
}

/**
 * Valida coordenadas em Graus Decimais
 */
function validateDD(lat, lon) {
    if (isNaN(lat) || isNaN(lon)) {
        return { valid: false, message: 'Latitude e Longitude devem ser números' };
    }
    
    if (lat < -90 || lat > 90) {
        return { valid: false, message: 'Latitude deve estar entre -90 e 90' };
    }
    
    if (lon < -180 || lon > 180) {
        return { valid: false, message: 'Longitude deve estar entre -180 e 180' };
    }
    
    return { valid: true, message: 'Coordenadas DD válidas' };
}

/**
 * Valida coordenadas UTM
 */
function validateUTM(zone, easting, northing) {
    if (!Number.isInteger(zone) || zone < 1 || zone > 60) {
        return { valid: false, message: 'Zona UTM deve estar entre 1 e 60' };
    }
    
    if (easting < 160000 || easting > 840000) {
        return { valid: false, message: 'Easting deve estar entre 160000 e 840000' };
    }
    
    if (northing < 0 || northing > 10000000) {
        return { valid: false, message: 'Northing deve estar entre 0 e 10000000' };
    }
    
    return { valid: true, message: 'Coordenadas UTM válidas' };
}

/**
 * Formata coordenadas para exibição
 */
function formatCoordinates(x, y, format) {
    if (format === 'dd') {
        return `${y.toFixed(6)}°, ${x.toFixed(6)}°`;
    } else if (format === 'utm') {
        return `${x.toFixed(2)}m E, ${y.toFixed(2)}m N`;
    } else if (format === 'dms') {
        const xDMS = ddToDMS(x);
        const yDMS = ddToDMS(y);
        const xDir = xDMS.isNegative ? 'W' : 'E';
        const yDir = yDMS.isNegative ? 'S' : 'N';
        return `${yDMS.degrees}°${yDMS.minutes}'${yDMS.seconds}"${yDir}, ${xDMS.degrees}°${xDMS.minutes}'${xDMS.seconds}"${xDir}`;
    }
    return 'Formato desconhecido';
}

/**
 * Atualiza o preview antes/depois
 */
function updatePreview(beforeCoords, afterCoords) {
    const previewSection = document.getElementById('previewSection');
    const previewBefore = document.getElementById('previewBefore');
    const previewAfter = document.getElementById('previewAfter');
    
    if (previewSection && previewBefore && previewAfter) {
        previewSection.style.display = 'block';
        previewBefore.textContent = beforeCoords;
        previewAfter.textContent = afterCoords;
    }
}

/**
 * Função principal de conversão de coordenadas
 */
async function convert() {
    try {
        const coordMode = document.getElementById('coordMode').value;
        const sourceEPSG = document.getElementById('sourceEPSG').value;
        let x, y;
        let formatBefore = '';
        
        // Extrair coordenadas de acordo com o modo
        if (coordMode === 'dd') {
            x = parseFloat(document.getElementById('x').value);
            y = parseFloat(document.getElementById('y').value);
            formatBefore = 'dd';
        } else if (coordMode === 'utm') {
            const zone = parseInt(document.getElementById('utmZone').value);
            const hemisphere = document.getElementById('utmHemisphere').value;
            const easting = parseFloat(document.getElementById('utmEasting').value);
            const northing = parseFloat(document.getElementById('utmNorthing').value);
            
            // Validar UTM
            const utmValidation = validateUTM(zone, easting, northing);
            if (!utmValidation.valid) {
                showError(utmValidation.message);
                return;
            }
            
            x = easting;
            y = northing;
            formatBefore = 'utm';
        } else if (coordMode === 'dms') {
            const xd = parseFloat(document.getElementById('xd').value) || 0;
            const xm = parseFloat(document.getElementById('xm').value) || 0;
            const xs = parseFloat(document.getElementById('xs').value) || 0;
            const xdir = document.getElementById('xdir').value;
            
            const yd = parseFloat(document.getElementById('yd').value) || 0;
            const ym = parseFloat(document.getElementById('ym').value) || 0;
            const ys = parseFloat(document.getElementById('ys').value) || 0;
            const ydir = document.getElementById('ydir').value;
            
            x = dmsToDD(xd, xm, xs, xdir);
            y = dmsToDD(yd, ym, ys, ydir);
            formatBefore = 'dms';
        }
        
        // Validação básica
        if (isNaN(x) || isNaN(y)) {
            showError('Coordenadas X e Y devem ser números válidos');
            return;
        }
        
        // Detectar formato se não especificado
        if (!sourceEPSG) {
            const detection = detectCoordinateFormat(x, y);
            if (detection.format === 'invalid') {
                showError(detection.message);
                return;
            }
        }
        
        const description = document.getElementById('pointDesc')?.value || '';
        const type = document.getElementById('pointType')?.value || 'ponto';
        
        showLoading();
        
        // Chamar API de conversão
        const response = await fetch(`${API_URL}/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                x: x,
                y: y,
                src: sourceEPSG,
                dst: '4326',  // Sempre converter para WGS84 para o mapa
                mode: coordMode
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }
        
        const data = await response.json();
        
        // Extrair coordenadas convertidas
        let latForMap = data.y;
        let lngForMap = data.x;
        
        // Validar coordenadas convertidas
        const validation = validateDD(latForMap, lngForMap);
        if (!validation.valid) {
            showError('Coordenadas convertidas inválidas: ' + validation.message);
            return;
        }
        
        // Atualizar preview
        const beforeCoords = formatCoordinates(x, y, formatBefore);
        const afterCoords = formatCoordinates(lngForMap, latForMap, 'dd');
        updatePreview(beforeCoords, afterCoords);
        
        // Adicionar ponto ao mapa
        if (typeof addPointToMap === 'function') {
            addPointToMap(latForMap, lngForMap, type, '#2d3748', description, {
                sourceEPSG: sourceEPSG,
                timestamp: new Date().toISOString()
            });
            map.setView([latForMap, lngForMap], 15);
        }
        
        // Formatar resultado
        let resultText = `<strong>✓ Conversão Realizada com Sucesso</strong><br>`;
        resultText += `De: EPSG:${data.src} → Para: EPSG:${data.dst}<br>`;
        resultText += `Latitude: ${latForMap.toFixed(6)}°<br>`;
        resultText += `Longitude: ${lngForMap.toFixed(6)}°<br>`;
        
        if (description) {
            resultText += `Descrição: ${description}`;
        }
        
        showSuccess(resultText);
        
        // Limpar campos
        if (document.getElementById('pointDesc')) {
            document.getElementById('pointDesc').value = '';
        }
        
    } catch (error) {
        showError(`Erro de conexão: ${error.message}`);
        console.error('Erro:', error);
    }
}

/**
 * Exibe mensagem de erro
 */
function showError(message) {
    const resultBox = document.getElementById("result");
    resultBox.innerHTML = `<strong>✗ Erro:</strong> ${message}`;
    resultBox.className = 'result-box error';
}

/**
 * Exibe mensagem de sucesso
 */
function showSuccess(message) {
    const resultBox = document.getElementById("result");
    resultBox.innerHTML = message;
    resultBox.className = 'result-box success';
}

/**
 * Exibe mensagem de carregamento
 */
function showLoading() {
    const resultBox = document.getElementById("result");
    resultBox.innerHTML = '<em>⏳ Convertendo coordenadas...</em>';
    resultBox.className = 'result-box info';
}

/**
 * Alterna visibilidade dos grupos de entrada de coordenadas
 */
function toggleCoordInputs() {
    const mode = document.getElementById('coordMode').value;
    const ddInputs = document.getElementById('ddInputs');
    const utmInputs = document.getElementById('utmInputs');
    const dmsInputs = document.getElementById('dmsInputs');
    
    // Esconder todos
    if (ddInputs) ddInputs.style.display = 'none';
    if (utmInputs) utmInputs.style.display = 'none';
    if (dmsInputs) dmsInputs.style.display = 'none';
    
    // Mostrar o selecionado
    if (mode === 'dd' && ddInputs) {
        ddInputs.style.display = 'block';
    } else if (mode === 'utm' && utmInputs) {
        utmInputs.style.display = 'block';
    } else if (mode === 'dms' && dmsInputs) {
        dmsInputs.style.display = 'block';
    }
}

/**
 * Inicialização ao carregar a página
 */
document.addEventListener('DOMContentLoaded', function() {
    // Permitir converter ao pressionar Enter
    const xInput = document.getElementById("x");
    const yInput = document.getElementById("y");
    
    if (xInput) {
        xInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') convert();
        });
    }
    
    if (yInput) {
        yInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') convert();
        });
    }
    
    // Inicializar visibilidade dos inputs
    toggleCoordInputs();
});

console.log("Converter.js (GIS Edition) carregado com sucesso");
