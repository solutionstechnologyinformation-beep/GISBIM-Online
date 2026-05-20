// Inicializar mapa com Leaflet
var map = L.map('map').setView([-14, -52], 4);

// Camadas de Base
var baseLayers = {
    "road": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }),
    "satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Esri'
    }),
    "terrain": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        attribution: 'OpenTopoMap'
    })
};

baseLayers.road.addTo(map);

function changeBaseLayer(layerKey) {
    Object.values(baseLayers).forEach(layer => { 
        if (map.hasLayer(layer)) map.removeLayer(layer); 
    });
    if (baseLayers[layerKey]) baseLayers[layerKey].addTo(map);
}

// Variáveis globais
var pointsList = [];
var additionalLayers = {};
var pointLayers = {
    "ponto": L.layerGroup().addTo(map),
    "estacao": L.layerGroup().addTo(map),
    "marco": L.layerGroup().addTo(map),
    "limite": L.layerGroup().addTo(map),
    "outro": L.layerGroup().addTo(map),
    "importado": L.layerGroup().addTo(map)
};

// Cores por tipo de ponto
var typeColors = {
    "ponto": "#2d3748",
    "estacao": "#4a5568",
    "marco": "#3182ce",
    "limite": "#ecc94b",
    "outro": "#a0aec0",
    "importado": "#9f7aea"
};

// Gerenciamento de Abas
function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

// Evento de clique no mapa
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    
    // Preencher campos de coordenadas ao clicar
    if(document.getElementById('x')) document.getElementById('x').value = lng.toFixed(6);
    if(document.getElementById('y')) document.getElementById('y').value = lat.toFixed(6);
    
    // Limpar seleção de dados ao clicar no vazio
    if (typeof showDataDetails === 'function') showDataDetails(null);
});

/**
 * Adiciona um ponto ao mapa
 */
function addPointToMap(lat, lng, type, color, description, extraData = {}) {
    var marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: color || typeColors[type] || "#000",
        color: "#fff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
    });

    // Dados do Ponto Geoespacial
    const pointData = {
        id: Date.now().toString(),
        lat: lat,
        lng: lng,
        type: type,
        description: description,
        sourceEPSG: extraData.sourceEPSG || '4326',
        timestamp: extraData.timestamp || new Date().toISOString()
    };

    marker.pointData = pointData;
    marker.description = (description || '').toLowerCase();

    marker.bindPopup(`<strong>${pointData.description}</strong><br>Tipo: ${pointData.type}<br>Lat: ${lat.toFixed(6)}, Lng: ${lng.toFixed(6)}`);
    
    marker.on('click', function(e) {
        L.DomEvent.stopPropagation(e);
        if (typeof showDataDetails === 'function') showDataDetails(this.pointData);
    });

    if (pointLayers[type]) {
        pointLayers[type].addLayer(marker);
    } else {
        pointLayers["outro"].addLayer(marker);
    }

    pointsList.push({x: lng, y: lat, type: type, description: description, pointData: pointData});
    updatePointsCount();
}

/**
 * Filtra pontos por descrição
 */
function filterPointsByDescription() {
    var filterText = document.getElementById('filterDescription').value.toLowerCase();
    var visibleCount = 0;
    
    Object.keys(pointLayers).forEach(type => {
        pointLayers[type].eachLayer(function(layer) {
            if ((layer.description || '').includes(filterText)) {
                if (!map.hasLayer(layer)) pointLayers[type].addLayer(layer);
                visibleCount++;
            } else {
                pointLayers[type].removeLayer(layer);
            }
        });
    });
    updatePointsCount(visibleCount);
}

/**
 * Atualiza a contagem de pontos visíveis
 */
function updatePointsCount(count) {
    var totalVisible = count !== undefined ? count : 0;
    if (count === undefined) {
        Object.keys(pointLayers).forEach(type => { 
            totalVisible += pointLayers[type].getLayers().length; 
        });
    }
    if (document.getElementById('pointsCount')) {
        document.getElementById('pointsCount').innerText = `Pontos visíveis: ${totalVisible}`;
    }
}

/**
 * Mostra detalhes do ponto selecionado
 */
function showDataDetails(pointData) {
    const detailsDiv = document.getElementById('dataDetails');
    if (!detailsDiv) return;
    
    if (!pointData) {
        detailsDiv.innerHTML = '<p class="hint">Selecione um ponto no mapa para ver os detalhes.</p>';
        return;
    }

    openTab('dataTab');

    detailsDiv.innerHTML = `
        <div class="data-card">
            <h4>${pointData.description || 'Ponto Sem Nome'}</h4>
            <p><strong>Tipo:</strong> ${pointData.type}</p>
            <p><strong>Sistema de Referência:</strong> EPSG:${pointData.sourceEPSG}</p>
            <p><strong>Coordenadas:</strong><br>Latitude: ${pointData.lat.toFixed(6)}<br>Longitude: ${pointData.lng.toFixed(6)}</p>
            <p><strong>Data:</strong> ${new Date(pointData.timestamp).toLocaleString('pt-BR')}</p>
        </div>
    `;
}

/**
 * Alterna visibilidade de camadas adicionais
 */
function toggleLayer() {
    const layerSelect = document.getElementById('layerSelect');
    const selectedLayer = layerSelect.value;
    const layerInfo = document.getElementById('layerInfo');
    
    // Remover todas as camadas adicionais
    Object.keys(additionalLayers).forEach(key => {
        if (map.hasLayer(additionalLayers[key])) {
            map.removeLayer(additionalLayers[key]);
        }
    });
    
    if (!selectedLayer) {
        layerInfo.innerHTML = '';
        return;
    }
    
    // Adicionar camada selecionada
    if (selectedLayer === 'ibge_municipios') {
        layerInfo.innerHTML = '<p class="info">Carregando municípios do IBGE...</p>';
        // Aqui seria feita a chamada para carregar dados do IBGE
        // Por enquanto, apenas informativo
    } else if (selectedLayer === 'ibge_estados') {
        layerInfo.innerHTML = '<p class="info">Carregando estados do IBGE...</p>';
    } else if (selectedLayer === 'mapbiomas') {
        layerInfo.innerHTML = '<p class="info">Carregando camada de uso do solo do MapBiomas...</p>';
    }
}

/**
 * Limpa todos os pontos do mapa
 */
function clearMap() {
    pointsList = [];
    Object.keys(pointLayers).forEach(type => pointLayers[type].clearLayers());
    updatePointsCount();
    if (typeof showDataDetails === 'function') showDataDetails(null);
}

/**
 * Exporta os dados como GeoJSON
 */
function exportData() {
    if (pointsList.length === 0) {
        alert('Nenhum ponto para exportar');
        return;
    }
    
    const features = pointsList.map(point => ({
        type: 'Feature',
        geometry: {
            type: 'Point',
            coordinates: [point.x, point.y]
        },
        properties: {
            description: point.description,
            type: point.type,
            sourceEPSG: point.pointData.sourceEPSG,
            timestamp: point.pointData.timestamp
        }
    }));
    
    const geojson = {
        type: 'FeatureCollection',
        features: features
    };
    
    const dataStr = JSON.stringify(geojson, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `gis_export_${new Date().toISOString().split('T')[0]}.geojson`;
    link.click();
    URL.revokeObjectURL(url);
}

/**
 * Abre diálogo de importação de arquivo
 */
function importFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.geojson,.json,.csv,.kml,.kmz';
    input.onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            uploadFileToServer(file);
        }
    };
    input.click();
}

/**
 * Envia arquivo para o servidor para processamento
 */
function uploadFileToServer(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert('Erro ao processar arquivo: ' + data.error);
            return;
        }
        
        if (data.features && Array.isArray(data.features)) {
            data.features.forEach((feature, index) => {
                if (feature.coordinates && feature.coordinates.length === 2) {
                    const [lng, lat] = feature.coordinates;
                    const description = feature.name || feature.description || `Ponto ${index + 1}`;
                    addPointToMap(lat, lng, 'importado', typeColors.importado, description);
                }
            });
            alert(`${data.features.length} ponto(s) importado(s) com sucesso!`);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao importar arquivo: ' + error.message);
    });
}

console.log("Map.js (GIS Edition) carregado com sucesso");
