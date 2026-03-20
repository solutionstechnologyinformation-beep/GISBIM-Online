/**
 * Módulo de Importação em Lote
 * Responsável pela importação e conversão de múltiplas coordenadas
 */

const API_URL = getApiUrl();

/**
 * Faz upload e processa arquivo em lote
 */
async function uploadBatchFile() {
    try {
        const fileInput = document.getElementById('batchFile');
        const srcSystem = document.getElementById('batchSrcSystem').value;
        const dstSystem = document.getElementById('batchDstSystem').value;
        const srcZone = document.getElementById('batchSrcZone').value || null;
        const dstZone = document.getElementById('batchDstZone').value || null;
        
        if (!fileInput.files.length) {
            showBatchError('Selecione um arquivo');
            return;
        }
        
        if (!srcSystem || !dstSystem) {
            showBatchError('Selecione os sistemas de origem e destino');
            return;
        }
        
        const file = fileInput.files[0];
        
        // Validar extensão
        const ext = file.name.split('.').pop().toLowerCase();
        if (!['txt', 'csv'].includes(ext)) {
            showBatchError('Apenas arquivos TXT e CSV são suportados');
            return;
        }
        
        // Ler arquivo
        const fileContent = await readFileAsText(file);
        
        // Parse coordenadas
        const coordinates = parseCoordinatesFromFile(fileContent, ext);
        
        if (coordinates.length === 0) {
            showBatchError('Nenhuma coordenada válida encontrada no arquivo');
            return;
        }
        
        // Enviar para conversão em lote
        const response = await fetch(`${API_URL}/batch-convert`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                coordinates: coordinates,
                src_system: srcSystem,
                src_zone: srcZone,
                dst_system: dstSystem,
                dst_zone: dstZone
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            showBatchError(data.error || 'Erro ao processar arquivo');
            return;
        }
        
        // Exibir resultado
        displayBatchResult(data);
        
        // Adicionar pontos ao mapa
        data.results.forEach(result => {
            addPointToMap({
                name: result.name || `Ponto ${result.index}`,
                x: result.x,
                y: result.y,
                srcSystem: data.src_system,
                dstSystem: data.dst_system
            });
        });
        
        showBatchSuccess(`${data.successful} coordenadas convertidas com sucesso`);
        
    } catch (error) {
        showBatchError('Erro ao processar arquivo: ' + error.message);
    }
}

/**
 * Lê arquivo como texto
 */
function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsText(file);
    });
}

/**
 * Parse de coordenadas do arquivo
 */
function parseCoordinatesFromFile(content, format) {
    const coordinates = [];
    const lines = content.trim().split('\n');
    
    if (format === 'csv') {
        // Pular header
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line) continue;
            
            try {
                const parts = line.split(',');
                if (parts.length >= 3) {
                    const name = parts[0].trim();
                    const x = parseFloat(parts[1].trim());
                    const y = parseFloat(parts[2].trim());
                    
                    if (!isNaN(x) && !isNaN(y)) {
                        coordinates.push({ x, y, name });
                    }
                }
            } catch (e) {
                continue;
            }
        }
    } else if (format === 'txt') {
        // Parse TXT (espaço separado)
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            if (!line || line.startsWith('#')) continue;
            
            try {
                const parts = line.split(/\s+/);
                if (parts.length >= 2) {
                    const x = parseFloat(parts[0]);
                    const y = parseFloat(parts[1]);
                    const name = parts[2] || `Ponto ${i}`;
                    
                    if (!isNaN(x) && !isNaN(y)) {
                        coordinates.push({ x, y, name });
                    }
                }
            } catch (e) {
                continue;
            }
        }
    }
    
    return coordinates;
}

/**
 * Exibe resultado da importação em lote
 */
function displayBatchResult(data) {
    const resultBox = document.getElementById('batchResult');
    const resultContent = document.getElementById('batchResultContent');
    
    let html = '<div class="result-content">';
    
    // Resumo
    html += '<div class="result-item">';
    html += '<label>Total de Coordenadas</label>';
    html += `<value>${data.total}</value>`;
    html += '</div>';
    
    html += '<div class="result-item">';
    html += '<label>Convertidas com Sucesso</label>';
    html += `<value style="color: green;">${data.successful}</value>`;
    html += '</div>';
    
    html += '<div class="result-item">';
    html += '<label>Erros</label>';
    html += `<value style="color: red;">${data.failed}</value>`;
    html += '</div>';
    
    // Tabela de resultados
    if (data.results.length > 0) {
        html += '<div style="grid-column: 1/-1; margin-top: 1rem;">';
        html += '<h4>Coordenadas Convertidas</h4>';
        html += '<table style="width: 100%; border-collapse: collapse; font-size: 0.9rem;">';
        html += '<tr style="background: #f0f0f0; border-bottom: 2px solid #667eea;">';
        html += '<th style="padding: 0.5rem; text-align: left;">Nome</th>';
        html += '<th style="padding: 0.5rem; text-align: left;">X</th>';
        html += '<th style="padding: 0.5rem; text-align: left;">Y</th>';
        html += '</tr>';
        
        data.results.forEach(result => {
            html += '<tr style="border-bottom: 1px solid #e0e0e0;">';
            html += `<td style="padding: 0.5rem;">${result.name}</td>`;
            html += `<td style="padding: 0.5rem; font-family: monospace;">${result.x.toFixed(6)}</td>`;
            html += `<td style="padding: 0.5rem; font-family: monospace;">${result.y.toFixed(6)}</td>`;
            html += '</tr>';
        });
        
        html += '</table>';
        html += '</div>';
    }
    
    // Erros
    if (data.errors.length > 0) {
        html += '<div style="grid-column: 1/-1; margin-top: 1rem;">';
        html += '<h4>Erros</h4>';
        html += '<ul style="padding-left: 1.5rem;">';
        data.errors.forEach(error => {
            html += `<li style="color: red; margin-bottom: 0.3rem;">${error}</li>`;
        });
        html += '</ul>';
        html += '</div>';
    }
    
    html += '</div>';
    
    resultContent.innerHTML = html;
    resultBox.style.display = 'block';
}

/**
 * Exibe mensagem de erro de lote
 */
function showBatchError(message) {
    const resultBox = document.getElementById('batchResult');
    const resultContent = document.getElementById('batchResultContent');
    
    resultContent.innerHTML = `<div class="error-message">${message}</div>`;
    resultBox.style.display = 'block';
}

/**
 * Exibe mensagem de sucesso de lote
 */
function showBatchSuccess(message) {
    const resultBox = document.getElementById('batchResult');
    const resultContent = document.getElementById('batchResultContent');
    
    resultContent.innerHTML = `<div class="success-message">${message}</div>`;
    resultBox.style.display = 'block';
}

/**
 * Baixa modelo de arquivo TXT
 */
function downloadTemplate() {
    const template = `# Modelo de arquivo TXT para importação em lote
# Formato: X Y Nome (separados por espaço)
# Exemplo:
-52.5 -14.5 Ponto1
-52.6 -14.6 Ponto2
-52.7 -14.7 Ponto3
`;
    
    const dataBlob = new Blob([template], { type: 'text/plain' });
    const url = URL.createObjectURL(dataBlob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = 'modelo_coordenadas.txt';
    link.click();
    
    URL.revokeObjectURL(url);
}
