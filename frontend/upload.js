/**
 * Processa o upload de um arquivo GeoJSON/JSON, extrai os pontos e os adiciona ao mapa.
 */
function uploadFile() {
    const fileInput = document.getElementById('fileInput');
    const uploadResult = document.getElementById('uploadResult');

    if (!fileInput.files || fileInput.files.length === 0) {
        uploadResult.innerHTML = '<strong style="color: red;">Por favor, selecione um arquivo.</strong>';
        return;
    }

    const file = fileInput.files[0];
    const allowedExtensions = ['.geojson', '.json'];
    const fileExtension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();

    if (!allowedExtensions.includes(fileExtension)) {
        uploadResult.innerHTML = `<strong style="color: red;">Formato de arquivo inválido. Por favor, envie um arquivo ${allowedExtensions.join(' ou ')}.</strong>`;
        return;
    }

    const reader = new FileReader();

    reader.onload = function(event) {
        try {
            const geojson = JSON.parse(event.target.result);
            let pointsAdded = 0;

            const processFeature = (feature) => {
                if (feature.geometry && feature.geometry.type === 'Point') {
                    const coords = feature.geometry.coordinates;
                    const props = feature.properties || {};

                    // Prioriza campos de descrição comuns
                    const description = props.description || props.desc || props.name || 'Ponto importado';
                    const type = props.type || 'importado';
                    const color = props.color || '#9A2EFE'; // Cor roxa para pontos importados

                    // GeoJSON: [lng, lat], Leaflet: [lat, lng]
                    const lat = coords[1];
                    const lng = coords[0];

                    if (typeof addPointToMap === 'function') {
                        addPointToMap(lat, lng, type, color, description);
                        pointsAdded++;
                    }
                }
            };

            if (geojson.type === 'FeatureCollection' && Array.isArray(geojson.features)) {
                geojson.features.forEach(processFeature);
            } else if (geojson.type === 'Feature') {
                processFeature(geojson);
            }

            if (pointsAdded > 0) {
                uploadResult.innerHTML = `<strong style="color: green;">${pointsAdded} ponto(s) adicionado(s) com sucesso!</strong>`;
                // Forçar a atualização da contagem e do filtro
                if (typeof filterPointsByDescription === 'function') {
                    filterPointsByDescription();
                }
            } else {
                uploadResult.innerHTML = '<strong style="color: orange;">Nenhum ponto válido encontrado no arquivo.</strong>';
            }

        } catch (error) {
            uploadResult.innerHTML = `<strong style="color: red;">Erro ao processar o arquivo:</strong> ${error.message}`;
            console.error("Erro no upload:", error);
        }
    };

    reader.onerror = function() {
        uploadResult.innerHTML = '<strong style="color: red;">Não foi possível ler o arquivo.</strong>';
    };

    reader.readAsText(file);
}
