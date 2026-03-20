/**
 * Módulo de Mapa - Leaflet
 * Responsável pela visualização de coordenadas no mapa
 */

let map;
let pointsMarkers = [];
let currentLayer = 'road';

// Camadas base disponíveis
const baseLayers = {
    road: L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }),
    satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Esri',
        maxZoom: 18
    })
};

// Inicializar mapa ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
});

/**
 * Inicializa o mapa Leaflet
 */
function initializeMap() {
    // Criar mapa centrado no Brasil
    map = L.map('map').setView([-14, -52], 4);
    
    // Adicionar camada base padrão (Estrada)
    baseLayers.road.addTo(map);
    
    // Adicionar controle de zoom
    L.control.zoom({ position: 'topright' }).addTo(map);
}

/**
 * Altera a camada base do mapa
 */
function changeBaseLayer(layerName) {
    // Remover camada atual
    if (currentLayer && baseLayers[currentLayer]) {
        map.removeLayer(baseLayers[currentLayer]);
    }
    
    // Adicionar nova camada
    if (baseLayers[layerName]) {
        baseLayers[layerName].addTo(map);
        currentLayer = layerName;
    }
}

/**
 * Adiciona um ponto ao mapa
 */
function addPointToMap(pointData) {
    if (!map) {
        console.error('Mapa não inicializado');
        return;
    }
    
    try {
        // Extrair coordenadas
        let lat, lng;
        
        if (pointData.y !== undefined && pointData.x !== undefined) {
            // Se as coordenadas forem geográficas (DD)
            lat = pointData.y;
            lng = pointData.x;
        } else {
            console.error('Coordenadas inválidas');
            return;
        }
        
        // Validar coordenadas
        if (isNaN(lat) || isNaN(lng) || lat < -90 || lat > 90 || lng < -180 || lng > 180) {
            console.error('Coordenadas fora do intervalo válido');
            return;
        }
        
        // Criar marcador
        const marker = L.circleMarker([lat, lng], {
            radius: 6,
            fillColor: '#667eea',
            color: '#764ba2',
            weight: 2,
            opacity: 0.8,
            fillOpacity: 0.7
        });
        
        // Adicionar popup
        const popupContent = `
            <div style="font-size: 12px;">
                <strong>${pointData.name || 'Ponto'}</strong><br>
                Latitude: ${lat.toFixed(6)}<br>
                Longitude: ${lng.toFixed(6)}<br>
                ${pointData.srcSystem ? `Origem: ${pointData.srcSystem}` : ''}<br>
                ${pointData.dstSystem ? `Destino: ${pointData.dstSystem}` : ''}
            </div>
        `;
        
        marker.bindPopup(popupContent);
        marker.addTo(map);
        
        // Armazenar marcador
        pointsMarkers.push({
            marker: marker,
            data: pointData
        });
        
        // Adicionar à lista de pontos
        addPointToList(pointData, pointsMarkers.length - 1);
        
        // Centralizar mapa no ponto
        map.setView([lat, lng], 12);
        
    } catch (error) {
        console.error('Erro ao adicionar ponto ao mapa:', error);
    }
}

/**
 * Adiciona um ponto à lista de pontos na sidebar
 */
function addPointToList(pointData, index) {
    const pointsList = document.getElementById('pointsList');
    
    if (!pointsList) return;
    
    const pointItem = document.createElement('div');
    pointItem.className = 'point-item';
    pointItem.innerHTML = `
        <div class="point-item-name">${pointData.name || `Ponto ${index + 1}`}</div>
        <div class="point-item-coords">
            ${pointData.y.toFixed(4)}, ${pointData.x.toFixed(4)}
        </div>
    `;
    
    // Clicar no item para centralizar no ponto
    pointItem.addEventListener('click', function() {
        if (pointsMarkers[index]) {
            const marker = pointsMarkers[index].marker;
            map.setView(marker.getLatLng(), 12);
            marker.openPopup();
        }
    });
    
    pointsList.appendChild(pointItem);
}

/**
 * Limpa todos os pontos do mapa
 */
function clearAllPoints() {
    // Remover marcadores do mapa
    pointsMarkers.forEach(item => {
        map.removeLayer(item.marker);
    });
    
    // Limpar array
    pointsMarkers = [];
    
    // Limpar lista
    const pointsList = document.getElementById('pointsList');
    if (pointsList) {
        pointsList.innerHTML = '';
    }
}

/**
 * Exporta os pontos como GeoJSON
 */
function exportPointsAsGeoJSON() {
    const features = pointsMarkers.map(item => {
        return {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [item.data.x, item.data.y]
            },
            properties: {
                name: item.data.name,
                srcSystem: item.data.srcSystem,
                dstSystem: item.data.dstSystem
            }
        };
    });
    
    const geojson = {
        type: 'FeatureCollection',
        features: features
    };
    
    return geojson;
}

/**
 * Baixa os pontos como arquivo GeoJSON
 */
function downloadPointsAsGeoJSON() {
    const geojson = exportPointsAsGeoJSON();
    const dataStr = JSON.stringify(geojson, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'coordenadas.geojson';
    link.click();
    
    URL.revokeObjectURL(url);
}

/**
 * Baixa os pontos como arquivo CSV
 */
function downloadPointsAsCSV() {
    let csv = 'Nome,Latitude,Longitude,Sistema Origem,Sistema Destino\n';
    
    pointsMarkers.forEach(item => {
        csv += `"${item.data.name || 'Ponto'}",${item.data.y},${item.data.x},"${item.data.srcSystem || ''}","${item.data.dstSystem || ''}"\n`;
    });
    
    const dataBlob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'coordenadas.csv';
    link.click();
    
    URL.revokeObjectURL(url);
}
