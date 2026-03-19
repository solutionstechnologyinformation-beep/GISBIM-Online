import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pyproj import Transformer
from dotenv import load_dotenv

# Tentar imports relativos (para módulo) ou absolutos (para script)
try:
    from .upload_simple import process_upload
    from .spatial import (
        dms_to_dd, dd_to_dms, dd_to_utm, utm_to_dd,
        format_dms, format_utm, validate_dd, validate_utm
    )
except ImportError:
    from upload_simple import process_upload
    from spatial import (
        dms_to_dd, dd_to_dms, dd_to_utm, utm_to_dd,
        format_dms, format_utm, validate_dd, validate_utm
    )

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


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'message': 'GISBIM Online está funcionando',
        'status': 'healthy',
        'version': '2.0.0'
    }), 200


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
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500


@app.route('/convert/dd-to-dms', methods=['POST'])
def convert_dd_to_dms():
    """Converte Graus Decimais para Graus Minutos Segundos."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400
        
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Validar
        valid, msg = validate_dd(latitude, longitude)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Converter
        lat_deg, lat_min, lat_sec, lat_neg = dd_to_dms(latitude)
        lon_deg, lon_min, lon_sec, lon_neg = dd_to_dms(longitude)
        
        lat_dir = "S" if lat_neg else "N"
        lon_dir = "W" if lon_neg else "E"
        
        return jsonify({
            'latitude': latitude,
            'longitude': longitude,
            'latitude_dms': format_dms(lat_deg, lat_min, lat_sec, lat_dir),
            'longitude_dms': format_dms(lon_deg, lon_min, lon_sec, lon_dir),
            'components': {
                'latitude': {'degrees': lat_deg, 'minutes': lat_min, 'seconds': lat_sec, 'direction': lat_dir},
                'longitude': {'degrees': lon_deg, 'minutes': lon_min, 'seconds': lon_sec, 'direction': lon_dir}
            }
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/convert/dd-to-utm', methods=['POST'])
def convert_dd_to_utm():
    """Converte Graus Decimais para UTM."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400
        
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Validar
        valid, msg = validate_dd(latitude, longitude)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Converter
        zone, easting, northing, hemisphere = dd_to_utm(latitude, longitude)
        
        return jsonify({
            'latitude': latitude,
            'longitude': longitude,
            'utm_zone': zone,
            'utm_hemisphere': hemisphere,
            'utm_easting': round(easting, 2),
            'utm_northing': round(northing, 2),
            'utm_formatted': format_utm(zone, easting, northing, hemisphere)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/convert/utm-to-dd', methods=['POST'])
def convert_utm_to_dd():
    """Converte UTM para Graus Decimais."""
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400
        
        zone = int(data.get('zone'))
        easting = float(data.get('easting'))
        northing = float(data.get('northing'))
        hemisphere = data.get('hemisphere', 'S')
        
        # Validar
        valid, msg = validate_utm(zone, easting, northing)
        if not valid:
            return jsonify({'error': msg}), 400
        
        # Converter
        latitude, longitude = utm_to_dd(zone, easting, northing, hemisphere)
        
        return jsonify({
            'utm_zone': zone,
            'utm_hemisphere': hemisphere,
            'utm_easting': easting,
            'utm_northing': northing,
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload e parse de arquivo de coordenadas."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo fornecido'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        result = process_upload(file)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.errorhandler(404)
def not_found(error):
    """Tratamento de erro 404."""
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Tratamento de erro 500."""
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=(FLASK_ENV == 'development'))
