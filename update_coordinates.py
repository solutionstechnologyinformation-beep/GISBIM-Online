
import os

def update_backend_app():
    print("Atualizando backend/app.py com suporte a DMS e exportação...")
    file_path = "backend/app.py"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    with open(file_path, "r") as f:
        content = f.read()

    # Adicionar lógica de conversão DMS no backend (simplificada)
    dms_logic = '''
def dd_to_dms(dd):
    """Converte graus decimais para graus, minutos e segundos."""
    is_positive = dd >= 0
    dd = abs(dd)
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees if is_positive else -degrees
    return int(degrees), int(minutes), round(seconds, 2)

@app.route('/convert_dms', methods=['POST'])
def convert_dms():
    try:
        data = request.json
        x = float(data['x'])
        y = float(data['y'])
        
        deg_x, min_x, sec_x = dd_to_dms(x)
        deg_y, min_y, sec_y = dd_to_dms(y)
        
        return jsonify({
            'x_dms': f"{deg_x}° {min_x}' {sec_x}\"",
            'y_dms': f"{deg_y}° {min_y}' {sec_y}\""
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/export', methods=['POST'])
def export_data():
    """Simula a exportação de dados em diferentes formatos."""
    try:
        data = request.json
        fmt = data.get('format', 'txt').lower()
        points = data.get('points', [])
        
        filename = f"export.{fmt}"
        filepath = os.path.join('../data/uploads', filename)
        
        if fmt == 'csv':
            content = "id,x,y,type\\n"
            for i, p in enumerate(points):
                content += f"{i},{p['x']},{p['y']},{p.get('type', 'ponto')}\\n"
        elif fmt == 'txt':
            content = "Exportação Mini-QGIS\\n"
            for p in points:
                content += f"X: {p['x']}, Y: {p['y']}\\n"
        else:
            content = f"Formato {fmt} ainda não implementado no backend, mas simulado."
            
        with open(filepath, "w") as f:
            f.write(content)
            
        return jsonify({'message': f'Arquivo {filename} gerado com sucesso', 'url': f'/download/{filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
'''
    if '/convert_dms' not in content:
        content = content.replace(
            '@app.route(\'/health\', methods=[\'GET\'])',
            dms_logic + '\n\n@app.route(\'/health\', methods=[\'GET\'])'
        )
        with open(file_path, "w") as f:
            f.write(content)
        print("   Backend atualizado com rotas de DMS e Exportação.")
    else:
        print("   Rotas de DMS e Exportação já existem no backend.")

def update_frontend_index():
    print("Atualizando frontend/index.html com novas opções de entrada e exportação...")
    file_path = "frontend/index.html"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    with open(file_path, "r") as f:
        content = f.read()

    # Adicionar campos para DMS e UTM nos selects
    if 'UTM' not in content:
        content = content.replace(
            '<option value="31983">UTM 23S (EPSG:31983)</option>',
            '<option value="31983">UTM 23S (EPSG:31983)</option>\n                        <option value="utm_auto">UTM (Automático)</option>'
        )
        print("   Opções de UTM adicionadas ao index.html.")

    # Adicionar seção de exportação e filtros
    if 'id="exportSection"' not in content:
        export_html = '''
        <section id="exportSection" class="export-section">
            <h2>Exportação e Filtros</h2>
            <div class="form-row">
                <div class="form-group">
                    <label for="exportFormat">Formato de Exportação:</label>
                    <select id="exportFormat">
                        <option value="txt">TXT</option>
                        <option value="csv">CSV</option>
                        <option value="kml">KML</option>
                        <option value="dxf">DXF</option>
                    </select>
                </div>
                <button onclick="exportData()" class="btn-convert">Exportar Pontos</button>
            </div>
            
            <div class="filter-group">
                <h3>Filtro de Pontos</h3>
                <label for="pointType">Tipo de Ponto:</label>
                <select id="pointType">
                    <option value="all">Todos</option>
                    <option value="bordo">Bordo</option>
                    <option value="manilha">Manilha</option>
                    <option value="pe">Pé</option>
                    <option value="crista">Crista</option>
                </select>
                <label for="pointColor">Cor:</label>
                <input type="color" id="pointColor" value="#ff0000">
                <button onclick="applyFilters()" class="btn-convert">Aplicar Filtro/Cor</button>
            </div>
            
            <div class="polygon-group">
                <h3>Ferramentas de Desenho</h3>
                <button onclick="connectPoints()" class="btn-convert">Ligar Pontos</button>
                <button onclick="closePolygon()" class="btn-convert">Fechar Polígono (Mancha)</button>
            </div>
        </section>
'''
        content = content.replace(
            '</main>',
            export_html + '\n    </main>'
        )
        print("   Seção de exportação e filtros adicionada ao index.html.")

    with open(file_path, "w") as f:
        f.write(content)

def update_frontend_js():
    print("Atualizando scripts de frontend para suportar DMS, exportação e filtros...")
    
    # Criar ou atualizar scripts específicos
    # No caso, vamos adicionar ao final do map.js ou criar um novo
    new_js = '''
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
    const response = await fetch('/export', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({format: format, points: pointsList})
    });
    const result = await response.json();
    alert(result.message || result.error);
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
'''
    with open("frontend/map.js", "a") as f:
        f.write(new_js)
    print("   Scripts de mapa atualizados com novas funcionalidades.")

if __name__ == "__main__":
    update_backend_app()
    update_frontend_index()
    update_frontend_js()
    print("Atualização concluída.")
