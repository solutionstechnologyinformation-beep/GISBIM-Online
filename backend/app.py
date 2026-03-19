import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pyproj import Transformer
from dotenv import load_dotenv
from .upload import process_upload

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configurações
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')


@app.route('/')
def index():
    """Serve o arquivo index.html do frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """Converte coordenadas entre diferentes sistemas de referência EPSG."""
    try:
        # Validar se o JSON foi recebido
        if not request.json:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400

        # Extrair dados
        data = request.json
        required_fields = ['x', 'y', 'src', 'dst']
        
        # Validar campos obrigatórios
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400

        # Converter para tipos apropriados
        try:
            x = float(data['x'])
            y = float(data['y'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Coordenadas x e y devem ser números válidos'}), 400

        src = str(data['src']).strip()
        dst = str(data['dst']).strip()

        # Validar se src e dst não estão vazios
        if not src or not dst:
            return jsonify({'error': 'Sistemas de referência (src e dst) não podem estar vazios'}), 400

        # Validar se src e dst são iguais
        if src == dst:
            return jsonify({
                'x': x,
                'y': y,
                'message': 'Sistemas de referência são iguais, nenhuma conversão necessária'
            })

        # Criar transformador
        try:
            transformer = Transformer.from_crs(
                f"EPSG:{src}",
                f"EPSG:{dst}",
                always_xy=True
            )
        except Exception as e:
            return jsonify({'error': f'Sistema de referência inválido: {str(e)}'}), 400

        # Realizar transformação
        try:
            new_x, new_y = transformer.transform(x, y)
        except Exception as e:
            return jsonify({'error': f'Erro ao transformar coordenadas: {str(e)}'}), 400

        return jsonify({
            'x': new_x,
            'y': new_y,
            'src': src,
            'dst': dst
        })

    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500



@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    result = process_upload(file)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify({'message': 'Arquivo processado com sucesso', 'data': result})



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
            content = "id,x,y,type\n"
            for i, p in enumerate(points):
                content += f"{i},{p['x']},{p['y']},{p.get('type', 'ponto')}\n"
        elif fmt == 'txt':
            content = "Exportação Mini-QGIS\n"
            for p in points:
                content += f"X: {p['x']}, Y: {p['y']}\n"
        else:
            content = f"Formato {fmt} ainda não implementado no backend, mas simulado."
            
        with open(filepath, "w") as f:
            f.write(content)
            
        return jsonify({'message': f'Arquivo {filename} gerado com sucesso', 'url': f'/download/{filename}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400



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
            content = "id,x,y,type,color\n"
            for i, p in enumerate(points):
                content += f"{i},{p['x']},{p['y']},{p.get('type', 'ponto')},{p.get('color', '#000000')}\n"
        elif fmt == 'txt':
            content = "ID\tX\tY\tTIPO\tCOR\n"
            for i, p in enumerate(points):
                content += f"{i}\t{p['x']}\t{p['y']}\t{p.get('type', 'ponto')}\t{p.get('color', '#000000')}\n"
        elif fmt == 'kml':
            content = '<?xml version="1.0" encoding="UTF-8"?>\n'
            content += '<kml xmlns="http://www.opengis.net/kml/2.2">\n<Document>\n'
            for i, p in enumerate(points):
                content += f'<Placemark>\n<name>{p.get("type", "ponto")} {i}</name>\n'
                content += f'<Point><coordinates>{p["x"]},{p["y"]},0</coordinates></Point>\n'
                content += '</Placemark>\n'
            content += '</Document>\n</kml>'
        elif fmt == 'dxf':
            # Formato DXF básico para pontos
            content = "0\nSECTION\n2\nENTITIES\n"
            for p in points:
                content += f"0\nPOINT\n8\n{p.get('type', '0')}\n10\n{p['x']}\n20\n{p['y']}\n30\n0.0\n"
            content += "0\nENDSEC\n0\nEOF"
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


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde da API."""
    return jsonify({'status': 'ok', 'environment': FLASK_ENV})


@app.errorhandler(404)
def not_found(error):
    """Tratador para erros 404."""
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Tratador para erros 500."""
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=(FLASK_ENV == 'development'))
