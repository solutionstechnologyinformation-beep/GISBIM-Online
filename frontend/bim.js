/**
 * Módulo BIM para o GISBIM-Online
 * Lida com modelos 3D, Cronograma 4D e Gestão de Ativos
 */

// Estado global do BIM
var bimState = {
    models: [],
    timelineDate: new Date(),
    clashDetectionEnabled: false
};

// Funções de Gerenciamento de Abas
function openTab(tabId) {
    // Esconder todas as abas
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    // Desativar todos os botões
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    // Ativar a aba e o botão selecionados
    document.getElementById(tabId).classList.add('active');
    event.currentTarget.classList.add('active');
}

/**
 * Upload e Visualização de Modelos BIM (GLB/IFC)
 */
function uploadBIMModel() {
    const fileInput = document.getElementById('bimFileInput');
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Selecione um arquivo .glb ou .ifc");
        return;
    }

    const file = fileInput.files[0];
    const extension = file.name.split('.').pop().toLowerCase();

    if (extension !== 'glb' && extension !== 'ifc') {
        alert("Formato não suportado. Use .glb ou .ifc");
        return;
    }

    // Simulação de carregamento de modelo 3D no mapa
    // Em uma implementação real, usaríamos Three.js + IFC.js para renderizar sobre o Leaflet
    console.log(`Carregando modelo BIM: ${file.name}`);
    
    // Adicionar marcador especial no centro do mapa representando o modelo
    const center = map.getCenter();
    const modelMarker = L.marker(center, {
        draggable: true,
        icon: L.divIcon({
            className: 'bim-model-icon',
            html: `<div style="background:#4a5568; color:white; padding:5px; border-radius:5px; border:2px solid #fff;">🏗️ BIM: ${file.name}</div>`,
            iconSize: [120, 40]
        })
    }).addTo(map);

    modelMarker.bindPopup(`<strong>Modelo BIM:</strong> ${file.name}<br>Posicione o modelo arrastando este marcador.`);
    
    alert(`Modelo ${file.name} carregado! No ambiente real, o Three.js renderizaria o volume 3D nesta posição.`);
}

/**
 * Cronograma 4D - Slider Temporal
 */
function updateTimeline(value) {
    // Mapear valor 0-100 para datas (ex: de Jan/2024 a Dez/2024)
    const startDate = new Date(2024, 0, 1);
    const endDate = new Date(2024, 11, 31);
    const totalDays = (endDate - startDate) / (1000 * 60 * 60 * 24);
    
    const currentDays = (value / 100) * totalDays;
    const currentDate = new Date(startDate.getTime() + (currentDays * 24 * 60 * 60 * 1000));
    
    document.getElementById('timelineLabel').innerText = `Data: ${currentDate.toLocaleDateString('pt-BR')}`;
    
    // Filtrar pontos no mapa de acordo com a data de execução
    filterByDate(currentDate);
}

function filterByDate(date) {
    Object.keys(pointLayers).forEach(type => {
        pointLayers[type].eachLayer(function(layer) {
            if (layer.assetData && layer.assetData.installDate) {
                const installDate = new Date(layer.assetData.installDate);
                if (installDate <= date) {
                    if (!map.hasLayer(layer)) pointLayers[type].addLayer(layer);
                } else {
                    pointLayers[type].removeLayer(layer);
                }
            }
        });
    });
}

/**
 * Gestão de Metadados e Ficha do Ativo
 */
function showAssetDetails(assetData) {
    const detailsDiv = document.getElementById('assetDetails');
    if (!assetData) {
        detailsDiv.innerHTML = '<p class="hint">Selecione um ponto no mapa para ver os detalhes.</p>';
        return;
    }

    openTab('assetTab'); // Trocar para a aba de ativos

    detailsDiv.innerHTML = `
        <div class="asset-card">
            <h4>${assetData.description || 'Ativo Sem Nome'}</h4>
            <p><strong>Tipo:</strong> ${assetData.type}</p>
            <p><strong>Fabricante:</strong> ${assetData.manufacturer || 'N/A'}</p>
            <p><strong>Data Execução:</strong> ${assetData.installDate || 'N/A'}</p>
            <p><strong>Status:</strong> <span class="status-badge ${assetData.status}">${assetData.status}</span></p>
            <hr>
            <p><strong>Coordenadas:</strong><br>${assetData.lat.toFixed(6)}, ${assetData.lng.toFixed(6)}</p>
            <button class="btn-convert" onclick="editAsset('${assetData.id}')" style="font-size: 0.8rem; padding: 5px;">Editar Atributos</button>
        </div>
    `;
}

/**
 * Detecção de Conflitos (Clash Detection)
 */
function checkClashes() {
    const clashAlert = document.getElementById('clash-alert');
    let clashesFound = 0;
    const threshold = 0.0001; // Distância mínima (aprox 10 metros)

    // Comparar todos os pontos entre si
    for (let i = 0; i < pointsList.length; i++) {
        for (let j = i + 1; j < pointsList.length; j++) {
            const p1 = pointsList[i];
            const p2 = pointsList[j];
            
            const dist = Math.sqrt(Math.pow(p1.x - p2.x, 2) + Math.pow(p1.y - p2.y, 2));
            
            if (dist < threshold) {
                clashesFound++;
                console.warn(`Conflito entre ${p1.description} e ${p2.description}`);
            }
        }
    }

    if (clashesFound > 0) {
        clashAlert.style.display = 'block';
        clashAlert.innerText = `⚠️ ${clashesFound} Conflito(s) de Proximidade Detectado(s)!`;
        setTimeout(() => { clashAlert.style.display = 'none'; }, 5000);
    } else {
        alert("Nenhum conflito detectado entre os ativos atuais.");
    }
}

/**
 * Suporte a LiDAR
 */
function uploadLidar() {
    const file = document.getElementById('lidarFileInput').files[0];
    if (!file) return;
    
    alert(`Arquivo LiDAR ${file.name} carregado. Processando nuvem de pontos para visualização 3D...`);
}

console.log("Módulo BIM.js carregado com sucesso");
