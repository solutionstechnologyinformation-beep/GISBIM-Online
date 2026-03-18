let map = L.map("map").setView([-15.7942, -47.8825], 4); // Centro do Brasil

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; <a href=\"https://www.openstreetmap.org/copyright\">OpenStreetMap</a> contributors",
}).addTo(map);

let originalMarkers = L.featureGroup().addTo(map);
let convertedMarkers = L.featureGroup().addTo(map);
let spatialMarkers = L.featureGroup().addTo(map);

function addMarker(lat, lon, popupText, color = 'blue', group = 'original') {
    let marker;
    let iconUrl;

    // Definir ícones personalizados com base na cor
    switch (color) {
        case 'blue':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png';
            break;
        case 'red':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png';
            break;
        case 'green':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png';
            break;
        case 'purple':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-purple.png';
            break;
        case 'orange':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-orange.png';
            break;
        case 'darkblue':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-darkblue.png';
            break;
        case 'pink':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-pink.png';
            break;
        case 'cadetblue':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-cadetblue.png';
            break;
        case 'brown':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-brown.png';
            break;
        case 'gray':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-gray.png';
            break;
        case 'black':
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-black.png';
            break;
        default:
            iconUrl = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png'; // Padrão azul
    }

    const customIcon = L.icon({
        iconUrl: iconUrl,
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        iconSize: [25, 41],
        iconAnchor: [12, 41],
        popupAnchor: [1, -34],
        shadowSize: [41, 41]
    });

    marker = L.marker([lat, lon], { icon: customIcon }).addTo(map);
    marker.bindPopup(popupText).openPopup();

    if (group === 'original') {
        originalMarkers.addLayer(marker);
    } else if (group === 'converted') {
        convertedMarkers.addLayer(marker);
    } else if (group === 'spatial') {
        spatialMarkers.addLayer(marker);
    }
    map.setView([lat, lon], 10); // Ajusta o zoom para o último ponto adicionado
}

function clearMarkers() {
    originalMarkers.clearLayers();
    convertedMarkers.clearLayers();
    spatialMarkers.clearLayers();
}

function addOriginalMarker(lat, lon, popupText = 'Original') {
    addMarker(lat, lon, popupText, 'blue', 'original');
}

function addConvertedMarker(lat, lon, popupText = 'Convertido') {
    addMarker(lat, lon, popupText, 'red', 'converted');
}

function addSpatialMarker(lat, lon, popupText = 'KMZ/KML') {
    addMarker(lat, lon, popupText, 'purple', 'spatial');
}
