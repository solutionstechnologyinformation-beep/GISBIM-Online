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
    "3d": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
        maxZoom: 17,
        attribution: 'OpenTopoMap'
    })
};

baseLayers.road.addTo(map);

function changeBaseLayer(layerKey) {
    Object.values(baseLayers).forEach(layer => { if (map.hasLayer(layer)) map.removeLayer(layer); });
    if (baseLayers[layerKey]) baseLayers[layerKey].addTo(map);
}

// Variáveis globais
var pointsList = [];
var pointLayers = {
    "pilar": L.layerGroup().addTo(map),
    "viga": L.layerGroup().addTo(map),
    "tubulacao": L.layerGroup().addTo(map),
    "eletrica": L.layerGroup().addTo(map),
    "outros": L.layerGroup().addTo(map),
    "importado": L.layerGroup().addTo(map)
};

// Cores por tipo BIM
var typeColors = {
    "pilar": "#2d3748",
    "viga": "#4a5568",
    "tubulacao": "#3182ce",
    "eletrica": "#ecc94b",
    "outros": "#a0aec0",
    "importado": "#9f7aea"
};

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    
    // Preencher campos de coordenadas ao clicar
    if(document.getElementById('x')) document.getElementById('x').value = lng.toFixed(6);
    if(document.getElementById('y')) document.getElementById('y').value = lat.toFixed(6);
    
    // Limpar seleção de ativo ao clicar no vazio
    if (typeof showAssetDetails === 'function') showAssetDetails(null);
});

function addPointToMap(lat, lng, type, color, description, extraData = {}) {
    var marker = L.circleMarker([lat, lng], {
        radius: 10,
        fillColor: color || typeColors[type] || "#000",
        color: "#fff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
    });

    // Dados do Ativo (BIM)
    const assetData = {
        id: Date.now().toString(),
        lat: lat,
        lng: lng,
        type: type,
        description: description,
        manufacturer: extraData.manufacturer || document.getElementById('assetManufacturer')?.value || '',
        installDate: extraData.installDate || document.getElementById('assetInstallDate')?.value || new Date().toISOString().split('T')[0],
        status: extraData.status || document.getElementById('assetStatus')?.value || 'planejado'
    };

    marker.assetData = assetData;
    marker.description = (description || '').toLowerCase();

    marker.bindPopup(`<strong>${assetData.description}</strong><br>Status: ${assetData.status}`);
    
    marker.on('click', function(e) {
        L.DomEvent.stopPropagation(e);
        if (typeof showAssetDetails === 'function') showAssetDetails(this.assetData);
    });

    if (pointLayers[type]) {
        pointLayers[type].addLayer(marker);
    } else {
        pointLayers["outros"].addLayer(marker);
    }

    pointsList.push({x: lng, y: lat, type: type, description: description, assetData: assetData});
    updatePointsCount();
}

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

function updatePointsCount(count) {
    var totalVisible = count !== undefined ? count : 0;
    if (count === undefined) {
        Object.keys(pointLayers).forEach(type => { totalVisible += pointLayers[type].getLayers().length; });
    }
    if (document.getElementById('pointsCount')) document.getElementById('pointsCount').innerText = `Ativos visíveis: ${totalVisible}`;
}

function clearMap() {
    pointsList = [];
    Object.keys(pointLayers).forEach(type => pointLayers[type].clearLayers());
    updatePointsCount();
    if (typeof showAssetDetails === 'function') showAssetDetails(null);
}

console.log("Map.js (BIM Edition) carregado");
