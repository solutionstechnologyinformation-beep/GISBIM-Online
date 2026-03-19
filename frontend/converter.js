const API_URL = getApiUrl();
let epsgCodes = {};
let convertedFileData = null;

function getApiUrl() {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:5000';
    }
    return window.location.origin;
}

async function loadEpsgCodes() {
    try {
        const response = await fetch(`${API_URL}/epsg_codes`);
        if (!response.ok) {
            throw new Error(`Erro ao carregar códigos EPSG: ${response.statusText}`);
        }
        epsgCodes = await response.json();
        populateEpsgDropdowns();
    } catch (error) {
        console.error("Erro ao carregar códigos EPSG:", error);
        showError(`Erro ao carregar sistemas de referência: ${error.message}`);
    }
}

function populateEpsgDropdowns(filterSystem = 'all') {
    const srcSelect = document.getElementById("src");
    const dstSelect = document.getElementById("dst");

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
        srcSelect.appendChild(optgroup.cloneNode(true));
        dstSelect.appendChild(optgroup.cloneNode(true));
    }
}

async function convertSingle() {
    try {
        const src = document.getElementById("src").value;
        const dst = document.getElementById("dst").value;
        const inputFormat = document.querySelector("input[name=\"inputFormat\"]:checked").value;
        const outputFormat = document.getElementById("coordinateFormat").value; // Usar o mesmo seletor para output

        let postData = { src, dst, input_format: inputFormat, output_format: outputFormat };

        if (inputFormat === "dd") {
            const x = document.getElementById("x").value;
            const y = document.getElementById("y").value;
            if (!x || !y || !src || !dst) {
                alert("Por favor, preencha todas as coordenadas e sistemas de referência.");
                return;
            }
            postData.x = parseFloat(x);
            postData.y = parseFloat(y);
        } else if (inputFormat === "dms") {
            const x_deg = document.getElementById("x_deg").value;
            const x_min = document.getElementById("x_min").value;
            const x_sec = document.getElementById("x_sec").value;
            const x_dir = document.getElementById("x_dir").value;
            const y_deg = document.getElementById("y_deg").value;
            const y_min = document.getElementById("y_min").value;
            const y_sec = document.getElementById("y_sec").value;
            const y_dir = document.getElementById("y_dir").value;

            if (!x_deg || !x_min || !x_sec || !x_dir || !y_deg || !y_min || !y_sec || !y_dir || !src || !dst) {
                alert("Por favor, preencha todos os campos de GMS e sistemas de referência.");
                return;
            }
            postData.x_deg = parseFloat(x_deg);
            postData.x_min = parseFloat(x_min);
            postData.x_sec = parseFloat(x_sec);
            postData.x_dir = x_dir;
            postData.y_deg = parseFloat(y_deg);
            postData.y_min = parseFloat(y_min);
            postData.y_sec = parseFloat(y_sec);
            postData.y_dir = y_dir;
        }

        clearMarkers();

        // Adicionar marcador original (apenas para DD, pois GMS precisa de conversão prévia para plotar)
        if (inputFormat === "dd") {
            addMarker(postData.y, postData.x, 'Original', 'blue');
        }

        fetch("/convert", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(postData),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.error) {
                alert("Erro: " + data.error);
                return;
            }

            let originalCoordDisplay = "";
            let convertedCoordDisplay = "";

            if (inputFormat === "dd") {
                originalCoordDisplay = `Original: ${postData.x}, ${postData.y} (EPSG:${src})`;
            } else if (inputFormat === "dms") {
                originalCoordDisplay = `Original: ${postData.x_deg}°${postData.x_min}'${postData.x_sec}" ${postData.x_dir}, ${postData.y_deg}°${postData.y_min}'${postData.y_sec}" ${postData.y_dir} (EPSG:${src})`;
                // Para plotar o original GMS, precisamos converter para DD primeiro
                const originalDD_X = dmsToDd(postData.x_deg, postData.x_min, postData.x_sec, postData.x_dir);
                const originalDD_Y = dmsToDd(postData.y_deg, postData.y_min, postData.y_sec, postData.y_dir);
                addMarker(originalDD_Y, originalDD_X, 'Original', 'blue');
            }

            if (outputFormat === "dd") {
                convertedCoordDisplay = `Convertido: ${data.x}, ${data.y} (EPSG:${dst})`;
                addMarker(data.y, data.x, 'Convertido', 'red');
            } else if (outputFormat === "dms") {
                convertedCoordDisplay = `Convertido: ${data.y_deg}°${data.y_min}'${data.y_sec}" ${data.y_dir}, ${data.x_deg}°${data.x_min}'${data.x_sec}" ${data.x_dir} (EPSG:${dst})`;
                // Para plotar o convertido GMS, precisamos converter para DD primeiro
                const convertedDD_X = dmsToDd(data.x_deg, data.x_min, data.x_sec, data.x_dir);
                const convertedDD_Y = dmsToDd(data.y_deg, data.y_min, data.y_sec, data.y_dir);
                addMarker(convertedDD_Y, convertedDD_X, 'Convertido', 'red');
            }

            document.getElementById("result").innerHTML = `
                <p>${originalCoordDisplay}</p>
                <p>${convertedCoordDisplay}</p>
            `;
        })
        .catch((error) => {
            console.error("Erro:", error);
            showError("Erro ao converter coordenadas.");
        });
    } catch (error) {
        showError(`Erro de conexão: ${error.message}`);
    }
}

async function convertFile() {
    const fileInput = document.getElementById("fileUpload");
    const src = document.getElementById("src").value;
    const dst = document.getElementById("dst").value;
    const inputFileFormat = document.getElementById("inputFileFormat").value;
    const fileResultDiv = document.getElementById("fileResult");
    const downloadBtn = document.getElementById("downloadFileBtn");
    const downloadKmlBtn = document.getElementById("downloadKmlBtn");
    const downloadDxfBtn = document.getElementById("downloadDxfBtn");

    fileResultDiv.innerHTML = '';
    downloadBtn.style.display = 'none';
    downloadKmlBtn.style.display = 'none';
    downloadDxfBtn.style.display = 'none';
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
    formData.append('input_file_format', inputFileFormat);

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
        convertedFileData = data;

        if (typeof clearMarkers === 'function' && typeof addMarker === 'function') {
            clearMarkers();
            const categories = {}; // Para agrupar pontos por descrição e atribuir cores
            const colors = ['green', 'purple', 'orange', 'darkblue', 'pink', 'cadetblue', 'brown', 'gray', 'olive', 'teal']; // Cores para categorias
            let colorIndex = 0;

            data.slice(0, 5).forEach(point => {
                let original_y_plot, original_x_plot;
                let converted_y_plot, converted_x_plot;
                let description = "";

                if (inputFileFormat === "pnec") {
                    original_y_plot = point.original_y;
                    original_x_plot = point.original_x;
                    converted_y_plot = point.converted_y;
                    converted_x_plot = point.converted_x;
                    description = point.descricao || "";
                } else {
                    original_y_plot = point.original_y;
                    original_x_plot = point.original_x;
                    converted_y_plot = point.converted_y;
                    converted_x_plot = point.converted_x;
                }

                // Atribuir cor baseada na descrição
                let categoryColor = 'gray'; // Cor padrão
                if (description) {
                    if (!categories[description]) {
                        categories[description] = colors[colorIndex % colors.length];
                        colorIndex++;
                    }
                    categoryColor = categories[description];
                }

                addMarker(original_y_plot, original_x_plot, `Original ${point.ponto || ''} (${description})`, categoryColor);
                addMarker(converted_y_plot, converted_x_plot, `Convertido ${point.ponto || ''} (${description})`, 'red'); // Convertido sempre vermelho
            });
        }

        if (data.length > 0) {
            let tableHtml;
            if (inputFileFormat === "pnec") {
                tableHtml = '<table class="results-table"><thead><tr><th>Ponto</th><th>Original N</th><th>Original E</th><th>Cota</th><th>Descrição</th><th>Convertido N</th><th>Convertido E</th></tr></thead><tbody>';
            } else {
                tableHtml = '<table class="results-table"><thead><tr><th>Original X</th><th>Original Y</th><th>Convertido X</th><th>Convertido Y</th></tr></thead><tbody>';
            }
            data.slice(0, 10).forEach(row => {
                if (inputFileFormat === "pnec") {
                    tableHtml += `<tr>\n                        <td>${row.ponto}</td>\n                        <td>${row.original_y.toFixed(6)}</td>\n                        <td>${row.original_x.toFixed(6)}</td>\n                        <td>${row.cota !== null ? row.cota : ''}</td>\n                        <td>${row.descricao !== null ? row.descricao : ''}</td>\n                        <td>${row.converted_y.toFixed(6)}</td>\n                        <td>${row.converted_x.toFixed(6)}</td>\n                    </tr>`;
                } else {
                    tableHtml += `<tr><td>${row.original_x.toFixed(6)}</td><td>${row.original_y.toFixed(6)}</td><td>${row.converted_x.toFixed(6)}</td><td>${row.converted_y.toFixed(6)}</td></tr>`;
                }
            });
            if (data.length > 10) {
                tableHtml += `<tr><td colspan="${inputFileFormat === 'pnec' ? 7 : 4}">... e mais ${data.length - 10} linhas. Clique em 'Baixar Resultados' para ver tudo.</td></tr>`;
            }
            tableHtml += '</tbody></table>';
            fileResultDiv.innerHTML = `<strong>Conversão de Arquivo Concluída!</strong><br>${tableHtml}`;
            fileResultDiv.style.color = 'green';
            downloadBtn.style.display = 'inline-block';
            downloadKmlBtn.style.display = 'inline-block';
            downloadDxfBtn.style.display = 'inline-block';
        } else {
            showError('Nenhuma coordenada válida foi convertida.', fileResultDiv);
        }

    } catch (error) {
        showError(`Erro de conexão ao converter arquivo: ${error.message}`, fileResultDiv);
    }
}

function downloadResults() {
    if (!convertedFileData) {
        alert('Nenhum dado para baixar.');
        return;
    }

    let csvContent;
    if (convertedFileData[0] && 'ponto' in convertedFileData[0]) {
        csvContent = "Ponto,Original_N,Original_E,Cota,Descricao,Convertido_N,Convertido_E\n";
        convertedFileData.forEach(row => {
            csvContent += `${row.ponto},${row.original_y},${row.original_x},${row.cota !== null ? row.cota : ''},${row.descricao !== null ? row.descricao : ''},${row.converted_y},${row.converted_x}\n`;
        });
    } else {
        csvContent = "Original_X,Original_Y,Convertido_X,Convertido_Y\n";
        convertedFileData.forEach(row => {
            csvContent += `${row.original_x},${row.original_y},${row.converted_x},${row.converted_y}\n`;
        });
    }

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'coordenadas_convertidas.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

async function downloadKml() {
    if (!convertedFileData) {
        alert('Nenhum dado para baixar.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/export_kml`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: convertedFileData,
                input_file_format: document.getElementById("inputFileFormat").value
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'coordenadas_convertidas.kml';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Erro ao baixar KML:", error);
        showError(`Erro ao baixar KML: ${error.message}`);
    }
}

async function downloadDxf() {
    if (!convertedFileData) {
        alert('Nenhum dado para baixar.');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/export_dxf`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                data: convertedFileData,
                input_file_format: document.getElementById("inputFileFormat").value
            }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`);
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'coordenadas_convertidas.dxf';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);

    } catch (error) {
        console.error("Erro ao baixar DXF:", error);
        showError(`Erro ao baixar DXF: ${error.message}`);
    }
}

function showError(message, targetDiv = null) {
    const div = targetDiv || document.getElementById("result");
    div.innerHTML = `<p style="color: red;">${message}</p>`;
    div.style.color = 'red';
}

function showLoading(targetDiv) {
    targetDiv.innerHTML = `<p style="color: blue;">Processando... Por favor, aguarde.</p>`;
    targetDiv.style.color = 'blue';
}

document.addEventListener("DOMContentLoaded", () => {
    loadEpsgCodes();

    document.getElementById("downloadKmlBtn").addEventListener("click", downloadKml);
    document.getElementById("downloadDxfBtn").addEventListener("click", downloadDxf);

    // Evento para alternar entre inputs DD e GMS
    document.querySelectorAll("input[name=\"inputFormat\"]").forEach(radio => {
        radio.addEventListener("change", (event) => {
            if (event.target.value === "dd") {
                document.getElementById("ddInputs").style.display = "block";
                document.getElementById("dmsInputs").style.display = "none";
            } else {
                document.getElementById("ddInputs").style.display = "none";
                document.getElementById("dmsInputs").style.display = "block";
            }
        });
    });

    // Adicionar evento de clique no mapa
    map.on("click", function (e) {
        // Apenas preenche se o formato de entrada for DD
        if (document.querySelector("input[name=\"inputFormat\"]:checked").value === "dd") {
            document.getElementById("x").value = e.latlng.lng.toFixed(6);
            document.getElementById("y").value = e.latlng.lat.toFixed(6);
        } else {
            showError("Para preencher do mapa, alterne para o formato de entrada Graus Decimais (DD).");
        }
    });
});

// Função auxiliar para converter GMS para DD no frontend (para plotagem)
function dmsToDd(degrees, minutes, seconds, direction) {
    let dd = parseFloat(degrees) + parseFloat(minutes) / 60 + parseFloat(seconds) / (60 * 60);
    if (direction === "S" || direction === "W") {
        dd = dd * -1;
    }
    return dd;
}

async function viewSpatialFile() {
    const fileInput = document.getElementById("spatialFileUpload");
    const resultDiv = document.getElementById("spatialFileResult");

    if (!fileInput.files.length) {
        showError('Por favor, selecione um arquivo espacial para visualizar.', resultDiv);
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    showLoading(resultDiv);

    try {
        const response = await fetch(`${API_URL}/upload_spatial_file`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            showError(errorData.error || `Erro ${response.status}: ${response.statusText}`, resultDiv);
            return;
        }

        const data = await response.json();

        if (data.error) {
            showError(data.error, resultDiv);
            return;
        }

        if (data.features && data.features.length > 0) {
            if (typeof clearMarkers === 'function') {
                clearMarkers();
            }
            
            data.features.forEach(feature => {
                if (feature.type === 'Point') {
                    const [lon, lat] = feature.coordinates;
                    if (typeof addSpatialMarker === 'function') {
                        addSpatialMarker(lat, lon, 'Ponto do Arquivo Espacial');
                    } else if (typeof addMarker === 'function') {
                        addMarker(lat, lon, 'Ponto do Arquivo Espacial', 'purple', 'spatial');
                    }
                }
            });
            
            resultDiv.innerHTML = `<p style="color: green;">Visualização concluída! ${data.features.length} pontos adicionados ao mapa.</p>`;
        } else {
            showError('Nenhuma geometria válida encontrada no arquivo para visualização.', resultDiv);
        }

    } catch (error) {
        showError(`Erro de conexão ao processar arquivo espacial: ${error.message}`, resultDiv);
    }
}
