
import os

def update_map_js_filters():
    print("Implementando filtros de pontos e ligação de categorias no frontend...")
    file_path = "frontend/map.js"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    # Nova lógica para gerenciar marcadores por tipo e cor
    filter_logic = '''
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
'''
    with open(file_path, "a") as f:
        f.write(filter_logic)
    print("   Lógica de filtros e ligação de pontos adicionada ao map.js.")

if __name__ == "__main__":
    update_map_js_filters()
    print("Atualização de filtros concluída.")
