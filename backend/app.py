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
        format_dms, format_utm, validate_dd, validate_utm,
        convert, convert_between_systems, validate_system, validate_utm_zone
    )
    from .epsg_codes import get_epsg_code, get_all_systems, get_all_zones, GEOGRAPHIC_SYSTEMS
except ImportError:
    from upload_simple import process_upload
    from spatial import (
        dms_to_dd, dd_to_dms, dd_to_utm, utm_to_dd,
        format_dms, format_utm, validate_dd, validate_utm,
        convert, convert_between_systems, validate_system, validate_utm_zone
    )
    from epsg_codes import get_epsg_code, get_all_systems, get_all_zones, GEOGRAPHIC_SYSTEMS

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
        'message': 'Conversor de Coordenadas Online está funcionando',
        'status': 'healthy',
        'version': '3.0.0'
    }), 200


@app.route('/api/systems', methods=['GET'])
def get_systems():
    """Retorna lista de sistemas de referência disponíveis."""
    try:
        systems = get_all_systems()
        return jsonify({
            'systems': systems,
            'count': len(systems)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Retorna lista de zonas UTM disponíveis."""
    try:
        hemisphere = request.args.get('hemisphere', 'Sul')
        zones = get_all_zones(hemisphere)
        return jsonify({
            'hemisphere': hemisphere,
            'zones': zones,
            'count': len(zones)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/epsg-code', methods=['GET'])
def get_epsg():
    """Retorna o código EPSG para um sistema e zona."""
    try:
        system = request.args.get('system')
        zone = request.args.get('zone')
        
        if not system:
            return jsonify({'error': 'Sistema de referência obrigatório'}), 400
        
        epsg = get_epsg_code(system, zone)
        
        if not epsg:
            return jsonify({'error': 'Sistema ou zona inválido'}), 400
        
        return jsonify({
            'system': system,
            'zone': zone,
            'epsg': epsg
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/convert', methods=['POST'])
def convert_coordinates():
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
            'x': round(new_x, 6),
            'y': round(new_y, 6),
            'src': src,
            'dst': dst
        }), 200

    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500


@app.route('/convert/system', methods=['POST'])
def convert_between_systems_endpoint():
    """Converte coordenadas entre sistemas de referência e fusos UTM."""
    try:
        if not request.json:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400
        
        data = request.json
        required_fields = ['x', 'y', 'src_system', 'dst_system']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400
        
        x = float(data['x'])
        y = float(data['y'])
        src_system = str(data['src_system']).strip()
        dst_system = str(data['dst_system']).strip()
        src_zone = data.get('src_zone')
        dst_zone = data.get('dst_zone')
        
        # Validar sistemas
        if not validate_system(src_system) or not validate_system(dst_system):
            return jsonify({'error': 'Sistema de referência inválido'}), 400
        
        # Validar zonas se fornecidas
        if src_zone:
            valid, _, _ = validate_utm_zone(src_zone)
            if not valid:
                return jsonify({'error': f'Zona UTM de origem inválida: {src_zone}'}), 400
        
        if dst_zone:
            valid, _, _ = validate_utm_zone(dst_zone)
            if not valid:
                return jsonify({'error': f'Zona UTM de destino inválida: {dst_zone}'}), 400
        
        # Realizar conversão
        result = convert_between_systems(x, y, src_system, src_zone, dst_system, dst_zone)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
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


@app.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Converte múltiplas coordenadas em lote."""
    try:
        if not request.json:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400
        
        data = request.json
        
        if 'coordinates' not in data or not isinstance(data['coordinates'], list):
            return jsonify({'error': 'Campo "coordinates" deve ser uma lista'}), 400
        
        src_system = data.get('src_system')
        dst_system = data.get('dst_system')
        src_zone = data.get('src_zone')
        dst_zone = data.get('dst_zone')
        
        if not src_system or not dst_system:
            return jsonify({'error': 'Sistemas de origem e destino obrigatórios'}), 400
        
        results = []
        errors = []
        
        for i, coord in enumerate(data['coordinates']):
            try:
                if not isinstance(coord, dict) or 'x' not in coord or 'y' not in coord:
                    errors.append(f"Coordenada {i}: formato inválido")
                    continue
                
                x = float(coord['x'])
                y = float(coord['y'])
                
                result = convert_between_systems(x, y, src_system, src_zone, dst_system, dst_zone)
                
                if result['success']:
                    result['index'] = i
                    result['name'] = coord.get('name', f'Ponto {i}')
                    results.append(result)
                else:
                    errors.append(f"Coordenada {i}: {result['error']}")
            except Exception as e:
                errors.append(f"Coordenada {i}: {str(e)}")
        
        return jsonify({
            'total': len(data['coordinates']),
            'successful': len(results),
            'failed': len(errors),
            'results': results,
            'errors': errors
        }), 200
    
    except Exception as e:
        return jsonify({'error': f'Erro ao processar requisição: {str(e)}'}), 500


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
