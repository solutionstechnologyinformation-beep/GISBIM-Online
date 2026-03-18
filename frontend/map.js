var map = L.map("map").setView([-14,-52],4);

var osm = L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom:19
    }
);

osm.addTo(map);

let originalMarkers = L.featureGroup().addTo(map);
let convertedMarkers = L.featureGroup().addTo(map);
let spatialMarkers = L.featureGroup().addTo(map);

function addOriginalMarker(lat, lon) {
    const marker = L.marker([lat, lon], {icon: L.divIcon({className: 'original-marker', html: '<div style="background-color: blue; width: 10px; height: 10px; border-radius: 50%; border: 1px solid white;"></div>'})}).bindPopup(`Original: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    originalMarkers.addLayer(marker);
    return marker;
}

function addConvertedMarker(lat, lon) {
    const marker = L.marker([lat, lon], {icon: L.divIcon({className: 'converted-marker', html: '<div style="background-color: red; width: 10px; height: 10px; border-radius: 50%; border: 1px solid white;"></div>'})}).bindPopup(`Convertido: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    convertedMarkers.addLayer(marker);
    return marker;
}

function addSpatialMarker(lat, lon) {
    const marker = L.marker([lat, lon], {icon: L.divIcon({className: 'spatial-marker', html: '<div style="background-color: purple; width: 10px; height: 10px; border-radius: 50%; border: 1px solid white;"></div>'})}).bindPopup(`Espacial: ${lat.toFixed(6)}, ${lon.toFixed(6)}`);
    spatialMarkers.addLayer(marker);
    return marker;
}

function clearMarkers() {
    originalMarkers.clearLayers();
    convertedMarkers.clearLayers();
}

function clearAllSpatialMarkers() {
    originalMarkers.clearLayers();
    convertedMarkers.clearLayers();
    spatialMarkers.clearLayers();
}

map.on("click", function(e) {
    document.getElementById("x").value = e.latlng.lng.toFixed(6);
    document.getElementById("y").value = e.latlng.lat.toFixed(6);
    clearAllSpatialMarkers(); // Limpa todos os marcadores ao clicar no mapa
    addOriginalMarker(e.latlng.lat, e.latlng.lng);
});
