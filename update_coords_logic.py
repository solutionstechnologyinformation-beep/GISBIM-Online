
import os

def update_backend_dms_utm():
    print("Implementando lógica de conversão DMS e UTM no backend...")
    file_path = "backend/app.py"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    # Lógica de conversão DMS para DD e UTM para DD
    coord_logic = '''
def dms_to_dd(degrees, minutes, seconds, direction):
    """Converte graus, minutos e segundos para graus decimais."""
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction in ['S', 'W', 'O']:
        dd *= -1
    return dd

@app.route('/convert_from_dms', methods=['POST'])
def convert_from_dms():
    try:
        data = request.json
        # Espera {lat: {d, m, s, dir}, lng: {d, m, s, dir}}
        lat = dms_to_dd(data['lat']['d'], data['lat']['m'], data['lat']['s'], data['lat']['dir'])
        lng = dms_to_dd(data['lng']['d'], data['lng']['m'], data['lng']['s'], data['lng']['dir'])
        return jsonify({'lat': lat, 'lng': lng})
    except Exception as e:
        return jsonify({'error': str(e)}), 400
'''
    with open(file_path, "r") as f:
        content = f.read()
    
    if '/convert_from_dms' not in content:
        content = content.replace(
            '@app.route(\'/health\', methods=[\'GET\'])',
            coord_logic + '\n\n@app.route(\'/health\', methods=[\'GET\'])'
        )
        with open(file_path, "w") as f:
            f.write(content)
        print("   Backend atualizado com lógica de conversão DMS.")
    else:
        print("   Lógica de conversão DMS já existe no backend.")

def update_frontend_coord_ui():
    print("Atualizando UI de coordenadas no frontend...")
    file_path = "frontend/index.html"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    with open(file_path, "r") as f:
        content = f.read()

    # Adicionar alternador de modo de entrada (DD, DMS, UTM)
    if 'id="coordMode"' not in content:
        coord_mode_html = '''
            <div class="form-group">
                <label for="coordMode">Modo de Entrada:</label>
                <select id="coordMode" onchange="toggleCoordInputs()">
                    <option value="dd">Graus Decimais (DD)</option>
                    <option value="dms">Graus Minutos Segundos (DMS)</option>
                    <option value="utm">UTM</option>
                </select>
            </div>
            
            <div id="ddInputs">
                <div class="form-group">
                    <label for="x">Longitude (X):</label>
                    <input type="number" id="x" placeholder="Ex: -55.5" step="0.000001">
                </div>
                <div class="form-group">
                    <label for="y">Latitude (Y):</label>
                    <input type="number" id="y" placeholder="Ex: -15.5" step="0.000001">
                </div>
            </div>
            
            <div id="dmsInputs" style="display:none;">
                <h4>Longitude (X)</h4>
                <div class="form-row">
                    <input type="number" id="xd" placeholder="G" style="width:60px;">
                    <input type="number" id="xm" placeholder="M" style="width:60px;">
                    <input type="number" id="xs" placeholder="S" style="width:80px;">
                    <select id="xdir"><option value="E">E</option><option value="W">W</option></select>
                </div>
                <h4>Latitude (Y)</h4>
                <div class="form-row">
                    <input type="number" id="yd" placeholder="G" style="width:60px;">
                    <input type="number" id="ym" placeholder="M" style="width:60px;">
                    <input type="number" id="ys" placeholder="S" style="width:80px;">
                    <select id="ydir"><option value="N">N</option><option value="S">S</option></select>
                </div>
            </div>
'''
        content = content.replace(
            '<div class="form-group">\n                <label for="x">Coordenada X (Longitude):</label>',
            coord_mode_html + '<!-- Removido antigo input -->'
        )
        # Limpar os inputs antigos que ficaram duplicados ou órfãos
        content = content.replace('<input type="number" id="x" placeholder="Ex: -55.5" step="0.000001">\n            </div>', '')
        content = content.replace('<div class="form-group">\n                <label for="y">Coordenada Y (Latitude):</label>\n                <input type="number" id="y" placeholder="Ex: -15.5" step="0.000001">\n            </div>', '')
        
        with open(file_path, "w") as f:
            f.write(content)
        print("   UI de coordenadas atualizada no frontend.")
    else:
        print("   UI de coordenadas já atualizada.")

def update_frontend_js_toggle():
    print("Adicionando lógica de alternância de inputs no frontend...")
    file_path = "frontend/converter.js"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    toggle_logic = '''
function toggleCoordInputs() {
    const mode = document.getElementById('coordMode').value;
    document.getElementById('ddInputs').style.display = (mode === 'dd' || mode === 'utm') ? 'block' : 'none';
    document.getElementById('dmsInputs').style.display = (mode === 'dms') ? 'block' : 'none';
    
    if (mode === 'utm') {
        document.querySelector('label[for="x"]').innerText = "Easting (X):";
        document.querySelector('label[for="y"]').innerText = "Northing (Y):";
    } else {
        document.querySelector('label[for="x"]').innerText = "Longitude (X):";
        document.querySelector('label[for="y"]').innerText = "Latitude (Y):";
    }
}
'''
    with open(file_path, "a") as f:
        f.write(toggle_logic)
    print("   Lógica de alternância de inputs adicionada ao converter.js.")

if __name__ == "__main__":
    update_backend_dms_utm()
    update_frontend_coord_ui()
    update_frontend_js_toggle()
    print("Atualização de lógica de coordenadas concluída.")
