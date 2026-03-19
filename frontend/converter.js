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

async function convert() {
    try {
        // Obter valores dos inputs
        const x = document.getElementById("x").value.trim();
        const y = document.getElementById("y").value.trim();
        const src = document.getElementById("src").value;
        const dst = document.getElementById("dst").value;

        // Validar campos
        if (!x || !y) {
            showError('Por favor, preencha as coordenadas X e Y');
            return;
        }

        // Validar se são números
        if (isNaN(parseFloat(x)) || isNaN(parseFloat(y))) {
            showError('Coordenadas X e Y devem ser números válidos');
            return;
        }

        // Validar se os sistemas de referência foram selecionados
        if (!src || !dst) {
            showError('Por favor, selecione os sistemas de referência de origem e destino');
            return;
        }

        // Mostrar mensagem de carregamento
        showLoading();

        // Fazer requisição à API
        const response = await fetch(`${API_URL}/convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                x: parseFloat(x),
                y: parseFloat(y),
                src: src,
                dst: dst
            })
        });

        // Processar resposta
        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }

        const data = await response.json();

        // Exibir resultado com mais precisão
        const resultText = `
            <strong>Resultado da Conversão:</strong><br>
            X: ${data.x.toFixed(6)}<br>
            Y: ${data.y.toFixed(6)}<br>
            De: EPSG:${data.src} → Para: EPSG:${data.dst}
        `;
        
        document.getElementById("result").innerHTML = resultText;
        document.getElementById("result").style.color = 'green';

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
    document.getElementById('ddInputs').style.display = (mode === 'dd' || mode === 'utm') ? 'block' : 'none';
    document.getElementById('dmsInputs').style.display = (mode === 'dms') ? 'block' : 'none';
    
    if (mode === 'utm') {
        document.querySelector('label[for="x"]').innerText = "Easting (X):";
        document.querySelector('label[for="y"]').innerText = "Northing (Y):";
    } else {
        document.querySelector('label[for="x"]').innerText = "Longitude (X):";
        document.querySelector('label[for="y"]').innerText = "Latitude (Y):";
    }
}

function toggleCoordInputs() {
    const mode = document.getElementById('coordMode').value;
    document.getElementById('ddInputs').style.display = (mode === 'dd' || mode === 'utm') ? 'block' : 'none';
    document.getElementById('dmsInputs').style.display = (mode === 'dms') ? 'block' : 'none';
    
    if (mode === 'utm') {
        document.querySelector('label[for="x"]').innerText = "Easting (X):";
        document.querySelector('label[for="y"]').innerText = "Northing (Y):";
    } else {
        document.querySelector('label[for="x"]').innerText = "Longitude (X):";
        document.querySelector('label[for="y"]').innerText = "Latitude (Y):";
    }
}
