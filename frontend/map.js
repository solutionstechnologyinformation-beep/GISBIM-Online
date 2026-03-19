// Inicializar mapa com Leaflet
var map = L.map('map').setView([-14, -52], 4);

// Adicionar camada de tiles do OpenStreetMap
var osm = L.tileLayer(
    'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    { maxZoom: 19 }
);
osm.addTo(map);

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
    }).bindPopup(`<strong>Tipo:</strong> ${type}<br><strong>Lat:</strong> ${lat.toFixed(6)}<br><strong>Lng:</strong> ${lng.toFixed(6)}`);
    
    // Adicionar à camada correta e à lista de pontos
    pointLayers[type].addLayer(marker);
    pointsList.push({x: lng, y: lat, type: type, color: color});
    
    console.log("Ponto adicionado:", type, color, {x: lng, y: lat});
});

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
    
    console.log(`Último ponto removido: ${lastPoint.type} em (${lastPoint.y}, ${lastPoint.x})`);
}

console.log("Map.js carregado com sucesso");
