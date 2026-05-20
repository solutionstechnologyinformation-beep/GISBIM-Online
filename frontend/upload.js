/**
 * Módulo de Upload de Arquivos Geoespaciais
 * Suporta: GeoJSON, JSON, CSV, KML, KMZ
 */

/**
 * Detecta o formato do arquivo pela extensão
 */
function detectFileFormat(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const supportedFormats = {
        'geojson': 'GeoJSON',
        'json': 'JSON',
        'csv': 'CSV',
        'kml': 'KML',
        'kmz': 'KMZ'
    };
    
    return supportedFormats[ext] || null;
}

/**
 * Processa o upload de um arquivo GeoJSON/JSON
 */
function uploadFile() {
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = '.geojson,.json,.csv,.kml,.kmz';
    
    fileInput.onchange = function(e) {
        const file = e.target.files[0];
        if (!file) return;
        
        const format = detectFileFormat(file.name);
        if (!format) {
            showUploadError(`Formato de arquivo não suportado: ${file.name}`);
            return;
        }
        
        // Enviar para o servidor
        uploadFileToServer(file);
    };
    
    fileInput.click();
}

/**
 * Envia arquivo para o servidor para processamento
 */
function uploadFileToServer(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    showUploadLoading(`Processando ${file.name}...`);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            showUploadError(`Erro ao processar arquivo: ${data.error}`);
            return;
        }
        
        if (!data.features || !Array.isArray(data.features)) {
            showUploadError('Nenhum ponto válido encontrado no arquivo');
            return;
        }
        
        // Processar features
        let pointsAdded = 0;
        data.features.forEach((feature, index) => {
            try {
                if (feature.coordinates && Array.isArray(feature.coordinates) && feature.coordinates.length >= 2) {
                    const [lng, lat] = feature.coordinates;
                    
                    // Validar coordenadas
                    if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
                        console.warn(`Ponto ${index + 1} tem coordenadas inválidas`);
                        return;
                    }
                    
                    const description = feature.name || feature.description || `Ponto ${index + 1}`;
                    const type = feature.type || 'importado';
                    
                    if (typeof addPointToMap === 'function') {
                        addPointToMap(lat, lng, type, '#9f7aea', description, {
                            sourceEPSG: '4326',
                            timestamp: new Date().toISOString()
                        });
                        pointsAdded++;
                    }
                }
            } catch (error) {
                console.error(`Erro ao processar ponto ${index + 1}:`, error);
            }
        });
        
        if (pointsAdded > 0) {
            showUploadSuccess(`✓ ${pointsAdded} ponto(s) importado(s) com sucesso!`);
            
            // Forçar atualização da contagem
            if (typeof filterPointsByDescription === 'function') {
                filterPointsByDescription();
            }
            
            // Centralizar mapa no primeiro ponto
            if (pointsList && pointsList.length > 0) {
                const firstPoint = pointsList[0];
                if (typeof map !== 'undefined') {
                    map.setView([firstPoint.y, firstPoint.x], 12);
                }
            }
        } else {
            showUploadError('Nenhum ponto válido foi importado');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showUploadError(`Erro ao importar arquivo: ${error.message}`);
    });
}

/**
 * Exibe mensagem de sucesso do upload
 */
function showUploadSuccess(message) {
    const resultBox = document.getElementById("result");
    if (resultBox) {
        resultBox.innerHTML = `<strong>${message}</strong>`;
        resultBox.className = 'result-box success';
    }
}

/**
 * Exibe mensagem de erro do upload
 */
function showUploadError(message) {
    const resultBox = document.getElementById("result");
    if (resultBox) {
        resultBox.innerHTML = `<strong>✗ Erro:</strong> ${message}`;
        resultBox.className = 'result-box error';
    }
}

/**
 * Exibe mensagem de carregamento do upload
 */
function showUploadLoading(message) {
    const resultBox = document.getElementById("result");
    if (resultBox) {
        resultBox.innerHTML = `<em>⏳ ${message}</em>`;
        resultBox.className = 'result-box info';
    }
}

/**
 * Processa arquivo local (sem enviar para servidor)
 * Útil para processamento no cliente
 */
function processFileLocally(file) {
    const reader = new FileReader();
    const format = detectFileFormat(file.name);
    
    if (!format) {
        showUploadError(`Formato não suportado: ${format}`);
        return;
    }
    
    reader.onload = function(event) {
        try {
            const content = event.target.result;
            
            if (format === 'geojson' || format === 'json') {
                processGeoJSON(content);
            } else if (format === 'csv') {
                processCSV(content);
            } else if (format === 'kml') {
                processKML(content);
            }
        } catch (error) {
            showUploadError(`Erro ao processar arquivo: ${error.message}`);
        }
    };
    
    reader.onerror = function() {
        showUploadError('Não foi possível ler o arquivo');
    };
    
    reader.readAsText(file);
}

/**
 * Processa arquivo GeoJSON
 */
function processGeoJSON(content) {
    try {
        const geojson = JSON.parse(content);
        let pointsAdded = 0;
        
        const processFeature = (feature) => {
            if (feature.geometry && feature.geometry.type === 'Point') {
                const coords = feature.geometry.coordinates;
                if (coords && coords.length >= 2) {
                    const [lng, lat] = coords;
                    const props = feature.properties || {};
                    const description = props.description || props.desc || props.name || 'Ponto importado';
                    const type = props.type || 'importado';
                    
                    if (typeof addPointToMap === 'function') {
                        addPointToMap(lat, lng, type, '#9f7aea', description);
                        pointsAdded++;
                    }
                }
            }
        };
        
        if (geojson.type === 'FeatureCollection' && Array.isArray(geojson.features)) {
            geojson.features.forEach(processFeature);
        } else if (geojson.type === 'Feature') {
            processFeature(geojson);
        }
        
        if (pointsAdded > 0) {
            showUploadSuccess(`✓ ${pointsAdded} ponto(s) adicionado(s)`);
        } else {
            showUploadError('Nenhum ponto válido encontrado');
        }
    } catch (error) {
        showUploadError(`Erro ao processar GeoJSON: ${error.message}`);
    }
}

/**
 * Processa arquivo CSV
 */
function processCSV(content) {
    try {
        const lines = content.trim().split('\n');
        let pointsAdded = 0;
        
        // Pular header
        for (let i = 1; i < lines.length; i++) {
            const parts = lines[i].split(',');
            if (parts.length >= 3) {
                try {
                    const name = parts[0].trim();
                    const lat = parseFloat(parts[1].trim());
                    const lng = parseFloat(parts[2].trim());
                    
                    if (!isNaN(lat) && !isNaN(lng)) {
                        if (typeof addPointToMap === 'function') {
                            addPointToMap(lat, lng, 'importado', '#9f7aea', name);
                            pointsAdded++;
                        }
                    }
                } catch (e) {
                    console.warn(`Erro ao processar linha ${i + 1}`);
                }
            }
        }
        
        if (pointsAdded > 0) {
            showUploadSuccess(`✓ ${pointsAdded} ponto(s) importado(s) do CSV`);
        } else {
            showUploadError('Nenhum ponto válido encontrado no CSV');
        }
    } catch (error) {
        showUploadError(`Erro ao processar CSV: ${error.message}`);
    }
}

/**
 * Processa arquivo KML (parsing básico)
 */
function processKML(content) {
    try {
        const coordsPattern = /<coordinates>(.*?)<\/coordinates>/g;
        let pointsAdded = 0;
        let match;
        
        while ((match = coordsPattern.exec(content)) !== null) {
            const coordsStr = match[1].trim();
            const coordsList = coordsStr.split(/\s+/);
            
            coordsList.forEach(coord => {
                const parts = coord.split(',');
                if (parts.length >= 2) {
                    try {
                        const lng = parseFloat(parts[0]);
                        const lat = parseFloat(parts[1]);
                        
                        if (!isNaN(lat) && !isNaN(lng)) {
                            if (typeof addPointToMap === 'function') {
                                addPointToMap(lat, lng, 'importado', '#9f7aea', `Ponto ${pointsAdded + 1}`);
                                pointsAdded++;
                            }
                        }
                    } catch (e) {
                        console.warn('Erro ao processar coordenada KML');
                    }
                }
            });
        }
        
        if (pointsAdded > 0) {
            showUploadSuccess(`✓ ${pointsAdded} ponto(s) importado(s) do KML`);
        } else {
            showUploadError('Nenhum ponto válido encontrado no KML');
        }
    } catch (error) {
        showUploadError(`Erro ao processar KML: ${error.message}`);
    }
}

console.log("Upload.js (GIS Edition) carregado com sucesso");
