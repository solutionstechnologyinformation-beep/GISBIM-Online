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


@app.route('/convert/dd-to-dms', methods=['POST'])
def convert_dd_to_dms():
    """Converte Graus Decimais (DD) para Graus Minutos Segundos (DMS)."""
    try:
        data = request.json
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Validar coordenadas
        valid, msg = validate_dd(latitude, longitude)
        if not valid:
            return jsonify({'error': msg}), 400
        
        lat_str, lon_str = format_dms(latitude, longitude)
        
        return jsonify({
            'latitude': latitude,
            'longitude': longitude,
            'latitude_dms': lat_str,
            'longitude_dms': lon_str,
            'format': 'DMS'
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao converter: {str(e)}'}), 400


@app.route('/convert/dd-to-utm', methods=['POST'])
def convert_dd_to_utm():
    """Converte Graus Decimais (DD) para UTM."""
    try:
        data = request.json
        latitude = float(data.get('latitude'))
        longitude = float(data.get('longitude'))
        
        # Validar coordenadas
        valid, msg = validate_dd(latitude, longitude)
        if not valid:
            return jsonify({'error': msg}), 400
        
        zone, easting, northing, hemisphere = dd_to_utm(latitude, longitude)
        utm_str = format_utm(zone, easting, northing, hemisphere)
        
        return jsonify({
            'latitude': latitude,
            'longitude': longitude,
            'utm_zone': zone,
            'utm_hemisphere': hemisphere,
            'utm_easting': round(easting, 2),
            'utm_northing': round(northing, 2),
            'utm_formatted': utm_str,
            'format': 'UTM'
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao converter: {str(e)}'}), 400


@app.route('/convert/utm-to-dd', methods=['POST'])
def convert_utm_to_dd():
    """Converte UTM para Graus Decimais (DD)."""
    try:
        data = request.json
        zone = int(data.get('zone'))
        easting = float(data.get('easting'))
        northing = float(data.get('northing'))
        hemisphere = data.get('hemisphere', 'N')
        
        # Validar coordenadas UTM
        valid, msg = validate_utm(zone, easting, northing)
        if not valid:
            return jsonify({'error': msg}), 400
        
        latitude, longitude = utm_to_dd(zone, easting, northing, hemisphere)
        
        return jsonify({
            'utm_zone': zone,
            'utm_easting': easting,
            'utm_northing': northing,
            'utm_hemisphere': hemisphere,
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'format': 'DD'
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao converter: {str(e)}'}), 400


@app.route('/convert/dms-to-dd', methods=['POST'])
def convert_dms_to_dd():
    """Converte Graus Minutos Segundos (DMS) para Graus Decimais (DD)."""
    try:
        data = request.json
        lat_deg = float(data.get('lat_degrees'))
        lat_min = float(data.get('lat_minutes'))
        lat_sec = float(data.get('lat_seconds'))
        lat_dir = data.get('lat_direction', 'N')
        
        lon_deg = float(data.get('lon_degrees'))
        lon_min = float(data.get('lon_minutes'))
        lon_sec = float(data.get('lon_seconds'))
        lon_dir = data.get('lon_direction', 'E')
        
        latitude = dms_to_dd(lat_deg, lat_min, lat_sec, lat_dir)
        longitude = dms_to_dd(lon_deg, lon_min, lon_sec, lon_dir)
        
        # Validar resultado
        valid, msg = validate_dd(latitude, longitude)
        if not valid:
            return jsonify({'error': msg}), 400
        
        return jsonify({
            'latitude_dms': f"{lat_deg}° {lat_min}' {lat_sec}\" {lat_dir}",
            'longitude_dms': f"{lon_deg}° {lon_min}' {lon_sec}\" {lon_dir}",
            'latitude': round(latitude, 6),
            'longitude': round(longitude, 6),
            'format': 'DD'
        })
    except Exception as e:
        return jsonify({'error': f'Erro ao converter: {str(e)}'}), 400


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


@app.route('/convert_dms', methods=['POST'])
def convert_dms():
    try:
        data = request.json
        x = float(data['x'])
        y = float(data['y'])
        
        deg_x, min_x, sec_x, _ = dd_to_dms(x)
        deg_y, min_y, sec_y, _ = dd_to_dms(y)
        
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
            content = "Exportação GISBIM Online\n"
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
        
        if not points:
            return jsonify({'error': 'Nenhum ponto para exportar'}), 400
        
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
            
            # Agrupar pontos por tipo
            types_dict = {}
            for p in points:
                ptype = p.get('type', 'ponto')
                if ptype not in types_dict:
                    types_dict[ptype] = []
                types_dict[ptype].append(p)
            
            # Adicionar pontos individuais
            for i, p in enumerate(points):
                content += f'<Placemark>\n<name>{p.get("type", "ponto")} {i}</name>\n'
                content += f'<Point><coordinates>{p["x"]},{p["y"]},0</coordinates></Point>\n'
                content += '</Placemark>\n'
            
            # Adicionar poligonos por tipo
            for ptype, type_points in types_dict.items():
                if len(type_points) >= 3:
                    content += f'<Placemark>\n<name>Poligono {ptype}</name>\n'
                    content += '<Polygon>\n<outerBoundaryIs>\n<LinearRing>\n<coordinates>\n'
                    for p in type_points:
                        content += f"{p['x']},{p['y']},0 \n"
                    if type_points:
                        content += f"{type_points[0]['x']},{type_points[0]['y']},0\n"
                    content += '</coordinates>\n</LinearRing>\n</outerBoundaryIs>\n</Polygon>\n</Placemark>\n'
            
            content += '</Document>\n</kml>'
        elif fmt == 'dxf':
            # Formato DXF com pontos e poligonos
            content = "0\nSECTION\n2\nHEADER\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n"
            
            # Adicionar pontos
            for i, p in enumerate(points):
                content += f"0\nPOINT\n8\n{p.get('type', 'default')}\n10\n{p['x']}\n20\n{p['y']}\n30\n0.0\n"
            
            # Agrupar pontos por tipo para poligonos
            types_dict = {}
            for p in points:
                ptype = p.get('type', 'ponto')
                if ptype not in types_dict:
                    types_dict[ptype] = []
                types_dict[ptype].append(p)
            
            # Adicionar poligonos (LWPOLYLINE em DXF)
            for ptype, type_points in types_dict.items():
                if len(type_points) >= 3:
                    content += f"0\nLWPOLYLINE\n8\n{ptype}\n70\n1\n"
                    for p in type_points:
                        content += f"10\n{p['x']}\n20\n{p['y']}\n"
                    if type_points:
                        content += f"10\n{type_points[0]['x']}\n20\n{type_points[0]['y']}\n"
            
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
    try:
        return send_from_directory('../data/uploads', filename, as_attachment=True)
    except Exception as e:
        return jsonify({'error': f'Erro ao baixar arquivo: {str(e)}'}), 400


@app.route('/batch-convert', methods=['POST'])
def batch_convert():
    """Processa lote de coordenadas para conversão."""
    try:
        data = request.json
        points = data.get('points', [])
        conversion_type = data.get('type', 'dd-to-dms')  # dd-to-dms, dd-to-utm, utm-to-dd
        
        if not points:
            return jsonify({'error': 'Nenhum ponto fornecido'}), 400
        
        results = []
        errors = []
        
        for i, point in enumerate(points):
            try:
                if conversion_type == 'dd-to-dms':
                    lat = float(point.get('latitude'))
                    lon = float(point.get('longitude'))
                    lat_str, lon_str = format_dms(lat, lon)
                    results.append({
                        'id': i,
                        'name': point.get('name', f'Ponto {i+1}'),
                        'latitude': lat,
                        'longitude': lon,
                        'latitude_dms': lat_str,
                        'longitude_dms': lon_str,
                        'status': 'success'
                    })
                
                elif conversion_type == 'dd-to-utm':
                    lat = float(point.get('latitude'))
                    lon = float(point.get('longitude'))
                    zone, easting, northing, hemisphere = dd_to_utm(lat, lon)
                    results.append({
                        'id': i,
                        'name': point.get('name', f'Ponto {i+1}'),
                        'latitude': lat,
                        'longitude': lon,
                        'utm_zone': zone,
                        'utm_hemisphere': hemisphere,
                        'utm_easting': round(easting, 2),
                        'utm_northing': round(northing, 2),
                        'status': 'success'
                    })
                
                elif conversion_type == 'utm-to-dd':
                    zone = int(point.get('zone'))
                    easting = float(point.get('easting'))
                    northing = float(point.get('northing'))
                    hemisphere = point.get('hemisphere', 'N')
                    lat, lon = utm_to_dd(zone, easting, northing, hemisphere)
                    results.append({
                        'id': i,
                        'name': point.get('name', f'Ponto {i+1}'),
                        'utm_zone': zone,
                        'utm_easting': easting,
                        'utm_northing': northing,
                        'latitude': round(lat, 6),
                        'longitude': round(lon, 6),
                        'status': 'success'
                    })
            except Exception as e:
                errors.append({'id': i, 'error': str(e)})
                results.append({'id': i, 'status': 'error', 'error': str(e)})
        
        return jsonify({
            'total': len(points),
            'processed': len([r for r in results if r.get('status') == 'success']),
            'errors': len(errors),
            'results': results
        })
    
    except Exception as e:
        return jsonify({'error': f'Erro ao processar lote: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Verifica a saúde da aplicação."""
    return jsonify({
        'status': 'healthy',
        'message': 'GISBIM Online está funcionando',
        'version': '2.0.0'
    })


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=(FLASK_ENV == 'development'))
