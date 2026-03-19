// Determinar a URL da API dinamicamente
function getApiUrl() {
    // Em produção, usar URL relativa; em desenvolvimento, usar localhost
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    // Em produção, usar o mesmo domínio
    return window.location.origin;
}

const API_URL = getApiUrl();

// Funções de conversão de coordenadas
function dmsToDD(degrees, minutes, seconds, direction) {
    let dd = parseFloat(degrees) + parseFloat(minutes) / 60 + parseFloat(seconds) / 3600;
    if (direction === 'S' || direction === 'W') {
        dd *= -1;
    }
    return dd;
}

function ddToDMS(dd) {
    const isNegative = dd < 0;
    dd = Math.abs(dd);
    const degrees = Math.floor(dd);
    const minutes = Math.floor((dd - degrees) * 60);
    const seconds = ((dd - degrees - minutes / 60) * 3600).toFixed(2);
    return { degrees, minutes, seconds, isNegative };
}

async function convert() {
    try {
        const coordMode = document.getElementById('coordMode').value;
        let x, y;
        
        if (coordMode === 'dd' || coordMode === 'utm') {
            x = document.getElementById('x').value.trim();
            y = document.getElementById('y').value.trim();
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
        }
        
        const src = document.getElementById('src').value;
        const dst = document.getElementById('dst').value;
        const description = document.getElementById('pointDesc') ? document.getElementById('pointDesc').value : '';
        const type = document.getElementById('pointType') ? document.getElementById('pointType').value : 'ponto';
        const color = document.getElementById('pointColor') ? document.getElementById('pointColor').value : '#ff0000';
        
        if (!x || !y) {
            showError('Por favor, preencha as coordenadas X e Y');
            return;
        }
        
        if (isNaN(parseFloat(x)) || isNaN(parseFloat(y))) {
            showError('Coordenadas X e Y devem ser números válidos');
            return;
        }
        
        if (!src || !dst) {
            showError('Por favor, selecione os sistemas de referência de origem e destino');
            return;
        }
        
        showLoading();
        
        const response = await fetch(`${API_URL}/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                x: parseFloat(x),
                y: parseFloat(y),
                src: src,
                dst: dst,
                mode: coordMode
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }
        
        const data = await response.json();
        
        // Adicionar o ponto ao mapa (sempre em WGS84 para o Leaflet)
        // Se o destino for 4326, usamos o resultado. Se não, a API deve retornar o WGS84 também?
        // Na verdade, a API /convert retorna as coordenadas no sistema de destino.
        // O Leaflet precisa de 4326.
        
        let latForMap, lngForMap;
        if (data.dst === "4326") {
            latForMap = data.y;
            lngForMap = data.x;
        } else {
            // Se o destino não for WGS84, precisamos converter para WGS84 para exibir no mapa
            // Vamos assumir que a API pode nos dar o WGS84 ou fazemos outra chamada.
            // Por simplicidade, se o usuário quer ver no mapa, o ideal é que o destino seja 4326.
            // Mas vamos tentar pegar o ponto original se for 4326.
            if (data.src === "4326") {
                latForMap = parseFloat(y);
                lngForMap = parseFloat(x);
            } else {
                // Caso complexo: nem origem nem destino são 4326. 
                // Para este MVP, vamos alertar ou tentar converter para 4326.
                const resWgs84 = await fetch(`${API_URL}/convert`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({x: parseFloat(x), y: parseFloat(y), src: src, dst: "4326", mode: coordMode})
                });
                const dataWgs84 = await resWgs84.json();
                latForMap = dataWgs84.y;
                lngForMap = dataWgs84.x;
            }
        }
        
        if (typeof addPointToMap === 'function') {
            addPointToMap(latForMap, lngForMap, type, color, description);
            map.setView([latForMap, lngForMap], 15);
        }

        // Formatar resultado de acordo com o modo de saída
        let resultText = `<strong>Resultado da Conversão:</strong><br>`;
        resultText += `De: EPSG:${data.src} → Para: EPSG:${data.dst}<br>`;
        
        if (coordMode === 'dd' || coordMode === 'utm') {
            resultText += `X: ${data.x.toFixed(6)}<br>`;
            resultText += `Y: ${data.y.toFixed(6)}<br>`;
        } else if (coordMode === 'dms') {
            const xDMS = ddToDMS(data.x);
            const yDMS = ddToDMS(data.y);
            resultText += `X: ${xDMS.degrees}° ${xDMS.minutes}' ${xDMS.seconds}" ${xDMS.isNegative ? 'W' : 'E'}<br>`;
            resultText += `Y: ${yDMS.degrees}° ${yDMS.minutes}' ${yDMS.seconds}" ${yDMS.isNegative ? 'S' : 'N'}<br>`;
        }
        
        document.getElementById('result').innerHTML = resultText;
        document.getElementById('result').style.color = 'green';
        
        // Limpar campos
        if (document.getElementById('pointDesc')) document.getElementById('pointDesc').value = '';
        
    } catch (error) {
        showError(`Erro de conexão: ${error.message}`);
    }
}

function showError(message) {
    document.getElementById("result").innerHTML = `<strong style="color: red;">Erro:</strong> ${message}`;
    document.getElementById("result").style.color = 'red';
}

function showLoading() {
    document.getElementById("result").innerHTML = '<em>Convertendo...</em>';
    document.getElementById("result").style.color = 'gray';
}

// Permitir converter ao pressionar Enter
document.addEventListener('DOMContentLoaded', function() {
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
});

function toggleCoordInputs() {
    const mode = document.getElementById('coordMode').value;
    const ddInputs = document.getElementById('ddInputs');
    const dmsInputs = document.getElementById('dmsInputs');
    
    if (ddInputs) ddInputs.style.display = (mode === 'dd' || mode === 'utm') ? 'block' : 'none';
    if (dmsInputs) dmsInputs.style.display = (mode === 'dms') ? 'block' : 'none';
    
    if (mode === 'utm') {
        const xLabel = document.querySelector('label[for="x"]');
        const yLabel = document.querySelector('label[for="y"]');
        if (xLabel) xLabel.innerText = "Easting (X):";
        if (yLabel) yLabel.innerText = "Northing (Y):";
    } else {
        const xLabel = document.querySelector('label[for="x"]');
        const yLabel = document.querySelector('label[for="y"]');
        if (xLabel) xLabel.innerText = "Longitude (X):";
        if (yLabel) yLabel.innerText = "Latitude (Y):";
    }
}
