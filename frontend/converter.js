// Determinar a URL da API dinamicamente
function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    return window.location.origin;
}

const API_URL = getApiUrl();
let epsgCodes = {}; // Armazena os códigos EPSG carregados da API
let convertedFileData = null; // Armazena os dados convertidos do arquivo para exportação

// Função para carregar os códigos EPSG da API
async function loadEpsgCodes() {
    try {
        const response = await fetch(`${API_URL}/epsg_codes`);
        if (!response.ok) {
            throw new Error(`Erro ao carregar códigos EPSG: ${response.statusText}`);
        }
        epsgCodes = await response.json();
        populateEpsgDropdowns(); // Popula os dropdowns inicialmente sem filtro
    } catch (error) {
        console.error("Erro ao carregar códigos EPSG:", error);
        showError(`Erro ao carregar sistemas de referência: ${error.message}`);
    }
}

// Função para popular os dropdowns de SRC e DST com base no filtro
function populateEpsgDropdowns(filterSystem = 'all') {
    const srcSelect = document.getElementById("src");
    const dstSelect = document.getElementById("dst");

    // Limpar opções existentes, exceto a primeira (placeholder)
    srcSelect.innerHTML = `<option value="">-- Selecione --</option>`;
    dstSelect.innerHTML = `<option value="">-- Selecione --</option>`;

    for (const systemName in epsgCodes) {
        if (filterSystem !== 'all' && systemName !== filterSystem) {
            continue;
        }
        const system = epsgCodes[systemName];
        const optgroup = document.createElement("optgroup");
        optgroup.label = systemName;

        for (const categoryName in system) {
            const category = system[categoryName];
            for (const description in category) {
                const code = category[description];
                const option = document.createElement("option");
                option.value = code;
                option.textContent = `${description} (EPSG:${code})`;
                optgroup.appendChild(option);
            }
        }
        // Adicionar o optgroup aos dois selects
        srcSelect.appendChild(optgroup.cloneNode(true));
        dstSelect.appendChild(optgroup.cloneNode(true));
    }
}

// Função para converter um único ponto
async function convertSingle() {
    try {
        const x = document.getElementById("x").value.trim();
        const y = document.getElementById("y").value.trim();
        const src = document.getElementById("src").value;
        const dst = document.getElementById("dst").value;

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
                dst: dst
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }

        const data = await response.json();

        const resultText = `
            <strong>Resultado da Conversão:</strong><br>
            X: ${data.x.toFixed(6)}<br>
            Y: ${data.y.toFixed(6)}<br>
            De: EPSG:${data.src} → Para: EPSG:${data.dst}
        `;
        
        document.getElementById("result").innerHTML = resultText;
        document.getElementById("result").style.color = 'green';

        // Adicionar marcadores no mapa
        if (typeof clearMarkers === 'function' && typeof addOriginalMarker === 'function' && typeof addConvertedMarker === 'function') {
            clearMarkers();
            addOriginalMarker(parseFloat(y), parseFloat(x));
            addConvertedMarker(data.y, data.x);
        }

        // Limpar resultados de arquivo se houver
        document.getElementById("fileResult").innerHTML = '';
        document.getElementById("downloadFileBtn").style.display = 'none';
        convertedFileData = null;

    } catch (error) {
        showError(`Erro de conexão: ${error.message}`);
    }
}

// Função para converter um arquivo
async function convertFile() {
    const fileInput = document.getElementById("fileUpload");
    const src = document.getElementById("src").value;
    const dst = document.getElementById("dst").value;
    const fileResultDiv = document.getElementById("fileResult");
    const downloadBtn = document.getElementById("downloadFileBtn");

    fileResultDiv.innerHTML = '';
    downloadBtn.style.display = 'none';
    convertedFileData = null;

    if (!fileInput.files.length) {
        showError('Por favor, selecione um arquivo para converter.', fileResultDiv);
        return;
    }

    if (!src || !dst) {
        showError('Por favor, selecione os sistemas de referência de origem e destino.', fileResultDiv);
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('src', src);
    formData.append('dst', dst);

    showLoading(fileResultDiv);

    try {
        const response = await fetch(`${API_URL}/convert_file`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`, fileResultDiv);
            return;
        }

        const data = await response.json();
        convertedFileData = data; // Armazena os dados para exportação

        // Adicionar marcadores no mapa para os primeiros pontos convertidos do arquivo
        if (typeof clearMarkers === 'function' && typeof addOriginalMarker === 'function' && typeof addConvertedMarker === 'function') {
            clearMarkers();
            data.slice(0, 5).forEach(point => { // Mostra os primeiros 5 pontos
                addOriginalMarker(point.original_y, point.original_x);
                addConvertedMarker(point.converted_y, point.converted_x);
            });
        }

        if (data.length > 0) {
            let tableHtml = '<table class="results-table"><thead><tr><th>Original X</th><th>Original Y</th><th>Convertido X</th><th>Convertido Y</th></tr></thead><tbody>';
            data.slice(0, 10).forEach(row => { // Mostrar apenas as primeiras 10 linhas na tela
                tableHtml += `<tr><td>${row.original_x.toFixed(6)}</td><td>${row.original_y.toFixed(6)}</td><td>${row.converted_x.toFixed(6)}</td><td>${row.converted_y.toFixed(6)}</td></tr>`;
            });
            if (data.length > 10) {
                tableHtml += `<tr><td colspan="4">... e mais ${data.length - 10} linhas. Clique em 'Baixar Resultados' para ver tudo.</td></tr>`;
            }
            tableHtml += '</tbody></table>';
            fileResultDiv.innerHTML = `<strong>Conversão de Arquivo Concluída!</strong><br>${tableHtml}`;
            fileResultDiv.style.color = 'green';
            downloadBtn.style.display = 'inline-block';
        } else {
            showError('Nenhuma coordenada válida foi convertida.', fileResultDiv);
        }

    } catch (error) {
        showError(`Erro de conexão ao converter arquivo: ${error.message}`, fileResultDiv);
    }
}

// Função para baixar os resultados convertidos
function downloadResults() {
    if (!convertedFileData) {
        alert('Nenhum dado para baixar.');
        return;
    }

    let csvContent = "original_x,original_y,converted_x,converted_y\n";
    convertedFileData.forEach(row => {
        csvContent += `${row.original_x},${row.original_y},${row.converted_x},${row.converted_y}\n`;
    });

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'coordenadas_convertidas.csv';
    link.click();
    URL.revokeObjectURL(link.href);
}

// Funções de feedback visual
function showError(message, targetDiv = null) {
    const resultDiv = targetDiv || document.getElementById("result");
    resultDiv.innerHTML = `<strong style="color: red;">Erro:</strong> ${message}`;
    resultDiv.style.color = 'red';
}

function showLoading(targetDiv = null) {
    const resultDiv = targetDiv || document.getElementById("result");
    resultDiv.innerHTML = '<em>Processando...</em>';
    resultDiv.style.color = 'gray';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    loadEpsgCodes(); // Carregar os códigos EPSG ao iniciar a página

    const systemFilter = document.getElementById("systemFilter");
    if (systemFilter) {
        systemFilter.addEventListener("change", function() {
            populateEpsgDropdowns(this.value);
        });
    }

    const xInput = document.getElementById("x");
    const yInput = document.getElementById("y");
    
    if (xInput) {
        xInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') convertSingle();
        });
    }
    
    if (yInput) {
        yInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') convertSingle();
        });
    }

    const downloadFileBtn = document.getElementById('downloadFileBtn');
    if (downloadFileBtn) {
        downloadFileBtn.addEventListener("click", downloadResults);
    }
});

// Função para visualizar arquivo espacial (KMZ/KML)
async function viewSpatialFile() {
    const fileInput = document.getElementById("spatialFileUpload");
    const spatialFileResultDiv = document.getElementById("spatialFileResult");

    spatialFileResultDiv.innerHTML = "";

    if (!fileInput.files.length) {
        showError("Por favor, selecione um arquivo espacial para visualizar.", spatialFileResultDiv);
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    showLoading(spatialFileResultDiv);

    try {
        const response = await fetch(`${API_URL}/upload_spatial_file`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`, spatialFileResultDiv);
            return;
        }

        const data = await response.json();

        if (data.features && data.features.length > 0) {
            // Limpar marcadores existentes e adicionar os novos
            if (typeof clearAllSpatialMarkers === 'function' && typeof addSpatialMarker === 'function') {
                clearAllSpatialMarkers();
                data.features.forEach(feature => {
                    if (feature.type === 'Point') {
                        addSpatialMarker(feature.coordinates[1], feature.coordinates[0]); // lat, lng
                    }
                });
                spatialFileResultDiv.innerHTML = `<strong style="color: green;">Arquivo espacial carregado e visualizado no mapa!</strong>`;
                spatialFileResultDiv.style.color = 'green';
            } else {
                showError("Funções de mapa não disponíveis para visualização.", spatialFileResultDiv);
            }
        } else {
            showError("Nenhuma geometria válida encontrada no arquivo espacial.", spatialFileResultDiv);
        }

    } catch (error) {
        showError(`Erro de conexão ao visualizar arquivo espacial: ${error.message}`, spatialFileResultDiv);
    }
}
