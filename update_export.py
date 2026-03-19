
import os

def update_backend_export_logic():
    print("Implementando lógica de exportação completa no backend...")
    file_path = "backend/app.py"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    # Lógica de exportação para múltiplos formatos
    export_logic = '''
@app.route('/export_full', methods=['POST'])
def export_full():
    """Gera arquivos de exportação em múltiplos formatos (txt, csv, kml, dxf)."""
    try:
        data = request.json
        fmt = data.get('format', 'txt').lower()
        points = data.get('points', [])
        
        filename = f"export_points.{fmt}"
        # Garantir que o diretório de uploads exista
        os.makedirs('../data/uploads', exist_ok=True)
        filepath = os.path.join('../data/uploads', filename)
        
        content = ""
        if fmt == 'csv':
            content = "id,x,y,type,color\\n"
            for i, p in enumerate(points):
                content += f"{i},{p['x']},{p['y']},{p.get('type', 'ponto')},{p.get('color', '#000000')}\\n"
        elif fmt == 'txt':
            content = "ID\\tX\\tY\\tTIPO\\tCOR\\n"
            for i, p in enumerate(points):
                content += f"{i}\\t{p['x']}\\t{p['y']}\\t{p.get('type', 'ponto')}\\t{p.get('color', '#000000')}\\n"
        elif fmt == 'kml':
            content = '<?xml version="1.0" encoding="UTF-8"?>\\n'
            content += '<kml xmlns="http://www.opengis.net/kml/2.2">\\n<Document>\\n'
            for i, p in enumerate(points):
                content += f'<Placemark>\\n<name>{p.get("type", "ponto")} {i}</name>\\n'
                content += f'<Point><coordinates>{p["x"]},{p["y"]},0</coordinates></Point>\\n'
                content += '</Placemark>\\n'
            content += '</Document>\\n</kml>'
        elif fmt == 'dxf':
            # Formato DXF básico para pontos
            content = "0\\nSECTION\\n2\\nENTITIES\\n"
            for p in points:
                content += f"0\\nPOINT\\n8\\n{p.get('type', '0')}\\n10\\n{p['x']}\\n20\\n{p['y']}\\n30\\n0.0\\n"
            content += "0\\nENDSEC\\n0\\nEOF"
        else:
            return jsonify({'error': 'Formato não suportado'}), 400
            
        with open(filepath, "w") as f:
            f.write(content)
            
        return jsonify({'message': f'Arquivo {filename} gerado com sucesso', 'url': f'/download/{filename}', 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """Permite o download dos arquivos gerados."""
    return send_from_directory('../data/uploads', filename, as_attachment=True)
'''
    with open(file_path, "r") as f:
        content = f.read()
    
    if '/export_full' not in content:
        content = content.replace(
            '@app.route(\'/health\', methods=[\'GET\'])',
            export_logic + '\n\n@app.route(\'/health\', methods=[\'GET\'])'
        )
        with open(file_path, "w") as f:
            f.write(content)
        print("   Backend atualizado com lógica de exportação completa.")
    else:
        print("   Lógica de exportação completa já existe no backend.")

def update_frontend_export_call():
    print("Atualizando chamada de exportação no frontend...")
    file_path = "frontend/map.js"
    if not os.path.exists(file_path):
        print(f"Erro: {file_path} não encontrado.")
        return

    with open(file_path, "r") as f:
        content = f.read()
    
    # Atualizar a função exportData para usar o novo endpoint export_full
    old_func = '''async function exportData() {
    const format = document.getElementById('exportFormat').value;
    const response = await fetch('/export', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({format: format, points: pointsList})
    });
    const result = await response.json();
    alert(result.message || result.error);
}'''
    
    new_func = '''async function exportData() {
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
}'''
    
    if old_func in content:
        content = content.replace(old_func, new_func)
        with open(file_path, "w") as f:
            f.write(content)
        print("   Função exportData atualizada no frontend.")
    else:
        print("   Função exportData não encontrada ou já atualizada.")

if __name__ == "__main__":
    update_backend_export_logic()
    update_frontend_export_call()
    print("Atualização de exportação concluída.")
