var map = L.map('map').setView([-14,-52],4)

var osm = L.tileLayer(
'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
{
maxZoom:19
})

osm.addTo(map)
// Funções para as novas solicitações
var pointsList = []; // Lista para armazenar pontos coletados

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    
    // Armazenar ponto
    var type = document.getElementById('pointType') ? document.getElementById('pointType').value : 'ponto';
    pointsList.push({x: lng, y: lat, type: type});
    
    // Mostrar no console para debug
    console.log("Ponto adicionado:", lng, lat, type);
});

async function exportData() {
    const format = document.getElementById('exportFormat').value;
    const response = await fetch('/export_full', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({format: format, points: pointsList})
    });
    const result = await response.json();
    if (result.url) {
        window.location.href = result.url;
    } else {
        alert(result.error || "Erro ao exportar");
    }
}

function applyFilters() {
    const type = document.getElementById('pointType').value;
    const color = document.getElementById('pointColor').value;
    
    // Limpar camadas anteriores se necessário
    // Lógica simplificada: mudar cor dos marcadores existentes
    alert("Filtro aplicado para " + type + " com cor " + color);
}

function connectPoints() {
    if (pointsList.length < 2) {
        alert("Necessário ao menos 2 pontos para ligar.");
        return;
    }
    var latlngs = pointsList.map(p => [p.y, p.x]);
    var polyline = L.polyline(latlngs, {color: document.getElementById('pointColor').value}).addTo(map);
    alert("Pontos ligados!");
}

function closePolygon() {
    if (pointsList.length < 3) {
        alert("Necessário ao menos 3 pontos para fechar um polígono.");
        return;
    }
    var latlngs = pointsList.map(p => [p.y, p.x]);
    var polygon = L.polygon(latlngs, {
        color: document.getElementById('pointColor').value,
        fillColor: document.getElementById('pointColor').value,
        fillOpacity: 0.5
    }).addTo(map);
    alert("Polígono (mancha) criado!");
}

// Estrutura para armazenar camadas de pontos por tipo
var pointLayers = {
    "bordo": L.layerGroup().addTo(map),
    "manilha": L.layerGroup().addTo(map),
    "pe": L.layerGroup().addTo(map),
    "crista": L.layerGroup().addTo(map),
    "ponto": L.layerGroup().addTo(map)
};

// Mapeamento de cores iniciais
var typeColors = {
    "bordo": "#ff0000",
    "manilha": "#00ff00",
    "pe": "#0000ff",
    "crista": "#ffff00",
    "ponto": "#000000"
};

// Sobrescrever evento de clique para adicionar marcadores com tipo e cor
map.off('click'); // Remover anterior
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    var type = document.getElementById('pointType').value || 'ponto';
    var color = document.getElementById('pointColor').value || typeColors[type];
    
    // Criar marcador circular com a cor escolhida
    var marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).bindPopup("Tipo: " + type + "<br>Lat: " + lat.toFixed(6) + "<br>Lng: " + lng.toFixed(6));
    
    // Adicionar à camada correta e à lista de pontos
    pointLayers[type].addLayer(marker);
    pointsList.push({x: lng, y: lat, type: type, color: color});
    
    console.log("Ponto adicionado:", type, color);
});

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
    
    alert("Filtro aplicado: Tipo " + type + " agora é " + color);
}

function connectPoints() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 2) {
        alert("Necessário ao menos 2 pontos do tipo " + type + " para ligar.");
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
    
    alert("Pontos do tipo " + type + " ligados!");
}

function closePolygon() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 3) {
        alert("Necessário ao menos 3 pontos do tipo " + type + " para fechar polígono.");
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
    
    alert("Polígono (mancha) criado para o tipo " + type + "!");
}

// Funções para as novas solicitações
var pointsList = []; // Lista para armazenar pontos coletados

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    
    // Armazenar ponto
    var type = document.getElementById('pointType') ? document.getElementById('pointType').value : 'ponto';
    pointsList.push({x: lng, y: lat, type: type});
    
    // Mostrar no console para debug
    console.log("Ponto adicionado:", lng, lat, type);
});

async function exportData() {
    const format = document.getElementById('exportFormat').value;
    const response = await fetch('/export_full', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({format: format, points: pointsList})
    });
    const result = await response.json();
    if (result.url) {
        window.location.href = result.url;
    } else {
        alert(result.error || "Erro ao exportar");
    }
}

function applyFilters() {
    const type = document.getElementById('pointType').value;
    const color = document.getElementById('pointColor').value;
    
    // Limpar camadas anteriores se necessário
    // Lógica simplificada: mudar cor dos marcadores existentes
    alert("Filtro aplicado para " + type + " com cor " + color);
}

function connectPoints() {
    if (pointsList.length < 2) {
        alert("Necessário ao menos 2 pontos para ligar.");
        return;
    }
    var latlngs = pointsList.map(p => [p.y, p.x]);
    var polyline = L.polyline(latlngs, {color: document.getElementById('pointColor').value}).addTo(map);
    alert("Pontos ligados!");
}

function closePolygon() {
    if (pointsList.length < 3) {
        alert("Necessário ao menos 3 pontos para fechar um polígono.");
        return;
    }
    var latlngs = pointsList.map(p => [p.y, p.x]);
    var polygon = L.polygon(latlngs, {
        color: document.getElementById('pointColor').value,
        fillColor: document.getElementById('pointColor').value,
        fillOpacity: 0.5
    }).addTo(map);
    alert("Polígono (mancha) criado!");
}

// Estrutura para armazenar camadas de pontos por tipo
var pointLayers = {
    "bordo": L.layerGroup().addTo(map),
    "manilha": L.layerGroup().addTo(map),
    "pe": L.layerGroup().addTo(map),
    "crista": L.layerGroup().addTo(map),
    "ponto": L.layerGroup().addTo(map)
};

// Mapeamento de cores iniciais
var typeColors = {
    "bordo": "#ff0000",
    "manilha": "#00ff00",
    "pe": "#0000ff",
    "crista": "#ffff00",
    "ponto": "#000000"
};

// Sobrescrever evento de clique para adicionar marcadores com tipo e cor
map.off('click'); // Remover anterior
map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lng = e.latlng.lng;
    var type = document.getElementById('pointType').value || 'ponto';
    var color = document.getElementById('pointColor').value || typeColors[type];
    
    // Criar marcador circular com a cor escolhida
    var marker = L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: color,
        color: "#000",
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }).bindPopup("Tipo: " + type + "<br>Lat: " + lat.toFixed(6) + "<br>Lng: " + lng.toFixed(6));
    
    // Adicionar à camada correta e à lista de pontos
    pointLayers[type].addLayer(marker);
    pointsList.push({x: lng, y: lat, type: type, color: color});
    
    console.log("Ponto adicionado:", type, color);
});

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
    
    alert("Filtro aplicado: Tipo " + type + " agora é " + color);
}

function connectPoints() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 2) {
        alert("Necessário ao menos 2 pontos do tipo " + type + " para ligar.");
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
    
    alert("Pontos do tipo " + type + " ligados!");
}

function closePolygon() {
    var type = document.getElementById('pointType').value;
    var filteredPoints = pointsList.filter(p => p.type === type || type === 'all');
    
    if (filteredPoints.length < 3) {
        alert("Necessário ao menos 3 pontos do tipo " + type + " para fechar polígono.");
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
    
    alert("Polígono (mancha) criado para o tipo " + type + "!");
}
