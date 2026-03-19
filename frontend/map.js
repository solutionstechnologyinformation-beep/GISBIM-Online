// Inicializar mapa com Leaflet
var map = L.map('map').setView([-14, -52], 4);

// Camadas de Base
var baseLayers = {
    "road": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }),
    "satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EBP, and the GIS User Community'
    }),
    "3d": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        attribution: 'Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a> (<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)'
    })
};

// Adicionar camada inicial
baseLayers.road.addTo(map);

// Função para mudar a camada de base
function changeBaseLayer(layerKey) {
    // Remover todas as camadas de base
    Object.values(baseLayers).forEach(layer => {
        if (map.hasLayer(layer)) {
            map.removeLayer(layer);
        }
    });
    
    // Adicionar a nova camada
    if (baseLayers[layerKey]) {
        baseLayers[layerKey].addTo(map);
    }
}

// Variáveis globais
var pointsList = []; // Lista para armazenar pontos coletados
var polylines = []; // Lista para armazenar polylines
var polygons = []; // Lista para armazenar polígonos

// Estrutura para armazenar camadas de pontos por tipo
var pointLayers = {
    "bordo": L.layerGroup().addTo(map),
    "manilha": L.layerGroup().addTo(map),
    "pe": L.layerGroup().addTo(map),
    "crista": L.layerGroup().addTo(map),
    "outros": L.layerGroup().addTo(map),
    "ponto": L.layerGroup().addTo(map)
};

// Mapeamento de cores iniciais por tipo
var typeColors = {
    "bordo": "#ff0000",
    "manilha": "#00ff00",
    "pe": "#0000ff",
    "crista": "#ffff00",
    "outros": "#ff9900",
    "ponto": "#000000"
};

// Evento de clique no mapa para adicionar marcadores
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    var type = document.getElementById('pointType') ? document.getElementById('pointType').value : 'ponto';
    var color = document.getElementById('pointColor') ? document.getElementById('pointColor').value : typeColors[type];
    var description = document.getElementById('pointDesc') ? document.getElementById('pointDesc').value : '';
    
    addPointToMap(lat, lng, type, color, description);
    
    // Limpar campo de descrição após adicionar
    if (document.getElementById('pointDesc')) {
        document.getElementById('pointDesc').value = '';
    }
});

/**
 * Adiciona um ponto ao mapa e à lista global
 */
function addPointToMap(lat, lng, type, color, description) {
    // Atualizar cor padrão
    typeColors[type] = color;
    
    // Criar marcador circular com a cor escolhida
    var marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).bindPopup(`<strong>Tipo:</strong> ${type}<br><strong>Descrição:</strong> ${description || 'N/A'}<br><strong>Lat:</strong> ${lat.toFixed(6)}<br><strong>Lng:</strong> ${lng.toFixed(6)}`);
    
    // Armazenar descrição no marcador para facilitar o filtro
    marker.description = (description || '').toLowerCase();
    
    // Adicionar à camada correta e à lista de pontos
    pointLayers[type].addLayer(marker);
    pointsList.push({x: lng, y: lat, type: type, color: color, description: description || ''});
    
    updatePointsCount();
    console.log("Ponto adicionado:", type, color, description, {x: lng, y: lat});
}

/**
 * Filtra os pontos visíveis no mapa com base na descrição na aba lateral
 */
function filterPointsByDescription() {
    var filterText = document.getElementById('filterDescription').value.toLowerCase();
    var visibleCount = 0;
    
    Object.keys(pointLayers).forEach(type => {
        pointLayers[type].eachLayer(function(layer) {
            var desc = layer.description || '';
            if (desc.includes(filterText)) {
                if (!map.hasLayer(layer)) {
                    pointLayers[type].addLayer(layer);
                }
                visibleCount++;
            } else {
                pointLayers[type].removeLayer(layer);
            }
        });
    });
    
    updatePointsCount(visibleCount);
}

/**
 * Atualiza o contador de pontos visíveis na aba lateral
 */
function updatePointsCount(count) {
    var totalVisible = 0;
    if (count !== undefined) {
        totalVisible = count;
    } else {
        Object.keys(pointLayers).forEach(type => {
            totalVisible += pointLayers[type].getLayers().length;
        });
    }
    
    var countElement = document.getElementById('pointsCount');
    if (countElement) {
        countElement.innerText = `Pontos visíveis: ${totalVisible}`;
    }
}

/**
 * Aplicar filtro de cores aos pontos de um tipo específico
 */
function applyFilters() {
    var type = document.getElementById('pointType').value;
    var color = document.getElementById('pointColor').value;
    
    // Atualizar cor padrão para o tipo
    typeColors[type] = color;
    
    // Atualizar marcadores existentes daquele tipo
    pointLayers[type].eachLayer(function(layer) {
        layer.setStyle({fillColor: color});
    });
    
    // Atualizar cores na lista de pontos para exportação futura
    pointsList.forEach(p => {
        if (p.type === type) p.color = color;
    });
    
    console.log(`Filtro aplicado: Tipo "${type}" agora é ${color}`);
}

/**
 * Conectar pontos de um tipo específico com uma polyline
 */
function connectPoints() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 2) {
        alert(`Necessário ao menos 2 pontos do tipo "${type}" para ligar.`);
        return;
    }
    
    var latlngs = filteredPoints.map(p => [p.y, p.x]);
    var color = document.getElementById('pointColor').value;
    
    var polyline = L.polyline(latlngs, {
        color: color,
        weight: 3,
        opacity: 0.7,
        dashArray: '5, 10'
    }).addTo(map);
    
    polylines.push(polyline);
    console.log(`Pontos do tipo "${type}" ligados com ${filteredPoints.length} pontos`);
}

/**
 * Fechar polígono (criar mancha) a partir de pontos de um tipo específico
 */
function closePolygon() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 3) {
        alert(`Necessário ao menos 3 pontos do tipo "${type}" para fechar polígono.`);
        return;
    }
    
    var latlngs = filteredPoints.map(p => [p.y, p.x]);
    var color = document.getElementById('pointColor').value;
    
    var polygon = L.polygon(latlngs, {
        color: color,
        fillColor: color,
        fillOpacity: 0.4,
        weight: 2
    }).addTo(map);
    
    polygons.push(polygon);
    console.log(`Polígono (mancha) criado para o tipo "${type}" com ${filteredPoints.length} pontos`);
}

/**
 * Exportar dados em diferentes formatos
 */
async function exportData() {
    const format = document.getElementById('exportFormat').value;
    
    if (pointsList.length === 0) {
        alert("Nenhum ponto para exportar. Clique no mapa para adicionar pontos.");
        return;
    }
    
    try {
        const response = await fetch('/export_full', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({format: format, points: pointsList})
        });
        
        const result = await response.json();
        
        if (result.url) {
            window.location.href = result.url;
            console.log(`Arquivo exportado em formato ${format}`);
        } else {
            alert(result.error || "Erro ao exportar");
        }
    } catch (error) {
        alert(`Erro ao exportar: ${error.message}`);
        console.error(error);
    }
}

/**
 * Limpar todos os pontos, polylines e polígonos do mapa
 */
function clearMap() {
    // Limpar pontos
    pointsList = [];
    Object.keys(pointLayers).forEach(type => {
        pointLayers[type].clearLayers();
    });
    
    // Limpar polylines
    polylines.forEach(polyline => map.removeLayer(polyline));
    polylines = [];
    
    // Limpar polígonos
    polygons.forEach(polygon => map.removeLayer(polygon));
    polygons = [];
    
    updatePointsCount();
    console.log("Mapa limpo");
}

/**
 * Remover o último ponto adicionado
 */
function undoLastPoint() {
    if (pointsList.length === 0) {
        alert("Nenhum ponto para remover.");
        return;
    }
    
    var lastPoint = pointsList.pop();
    
    // Remover o marcador da camada
    var layerToRemove = null;
    pointLayers[lastPoint.type].eachLayer(function(layer) {
        if (layer.getLatLng().lat === lastPoint.y && layer.getLatLng().lng === lastPoint.x) {
            layerToRemove = layer;
        }
    });
    
    if (layerToRemove) {
        pointLayers[lastPoint.type].removeLayer(layerToRemove);
    }
    
    updatePointsCount();
    console.log(`Último ponto removido: ${lastPoint.type} em (${lastPoint.y}, ${lastPoint.x})`);
}

console.log("Map.js carregado com sucesso");
