"""
Módulo simplificado de upload de arquivos geoespaciais.
Não requer geopandas para funcionalidade básica.
"""

import os
import json
import zipfile
import shutil
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '../data/uploads'
ALLOWED_EXTENSIONS = {'shp', 'geojson', 'json', 'gpkg', 'kml', 'kmz', 'txt', 'csv'}


def allowed_file(filename):
    """Verifica se a extensão do arquivo é permitida."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_csv_coordinates(content):
    """Parse CSV com coordenadas."""
    features = []
    lines = content.strip().split('\n')
    
    for i, line in enumerate(lines[1:], 1):  # Pular header
        try:
            parts = line.split(',')
            if len(parts) >= 3:
                name = parts[0].strip() if len(parts) > 0 else f"Ponto {i}"
                lat = float(parts[1].strip())
                lon = float(parts[2].strip())
                
                features.append({
                    'type': 'Point',
                    'name': name,
                    'coordinates': [lon, lat]
                })
        except (ValueError, IndexError):
            continue
    
    return {'features': features, 'count': len(features)}


def parse_txt_coordinates(content):
    """Parse TXT com coordenadas."""
    features = []
    lines = content.strip().split('\n')
    
    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        
        try:
            # Tentar diferentes formatos
            parts = line.split()
            if len(parts) >= 2:
                lat = float(parts[0])
                lon = float(parts[1])
                name = parts[2] if len(parts) > 2 else f"Ponto {i}"
                
                features.append({
                    'type': 'Point',
                    'name': name,
                    'coordinates': [lon, lat]
                })
        except (ValueError, IndexError):
            continue
    
    return {'features': features, 'count': len(features)}


def parse_kml_basic(content):
    """Parse básico de KML sem bibliotecas externas."""
    features = []
    
    try:
        # Extrair coordenadas de tags <coordinates>
        import re
        coords_pattern = r'<coordinates>(.*?)</coordinates>'
        matches = re.findall(coords_pattern, content, re.DOTALL)
        
        for match in matches:
            coords_str = match.strip()
            coords_list = coords_str.split()
            
            for coord in coords_list:
                parts = coord.split(',')
                if len(parts) >= 2:
                    try:
                        lon = float(parts[0])
                        lat = float(parts[1])
                        features.append({
                            'type': 'Point',
                            'coordinates': [lon, lat]
                        })
                    except ValueError:
                        continue
    except Exception as e:
        return {'error': f'Erro ao parsear KML: {str(e)}'}
    
    return {'features': features, 'count': len(features)}


def process_upload(file):
    """Processa arquivo carregado e retorna coordenadas."""
    if not file or not allowed_file(file.filename):
        return {'error': 'Tipo de arquivo inválido ou arquivo não fornecido.'}
    
    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[1].lower()
    
    try:
        # Criar pasta de uploads se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Ler conteúdo do arquivo
        content = file.read().decode('utf-8', errors='ignore')
        
        if ext == 'csv':
            result = parse_csv_coordinates(content)
        elif ext == 'txt':
            result = parse_txt_coordinates(content)
        elif ext == 'kml':
            result = parse_kml_basic(content)
        elif ext == 'kmz':
            # Descompactar KMZ e procurar KML
            temp_dir = os.path.join(UPLOAD_FOLDER, 'temp_kmz')
            os.makedirs(temp_dir, exist_ok=True)
            
            zip_path = os.path.join(temp_dir, filename)
            with open(zip_path, 'wb') as f:
                file.seek(0)
                f.write(file.read())
            
            kml_content = None
            try:
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    for file_info in zip_ref.filelist:
                        if file_info.filename.lower().endswith('.kml'):
                            kml_content = zip_ref.read(file_info.filename).decode('utf-8')
                            break
            except Exception as e:
                return {'error': f'Erro ao descompactar KMZ: {str(e)}'}
            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)
            
            if kml_content:
                result = parse_kml_basic(kml_content)
            else:
                result = {'error': 'Nenhum arquivo KML encontrado no KMZ'}
        
        elif ext == 'json' or ext == 'geojson':
            try:
                data = json.loads(content)
                if 'features' in data:
                    result = {'features': data['features'], 'count': len(data['features'])}
                else:
                    result = {'error': 'Formato GeoJSON inválido'}
            except json.JSONDecodeError:
                result = {'error': 'JSON inválido'}
        
        else:
            result = {'error': f'Formato {ext} não suportado'}
        
        # Salvar arquivo
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        
        result['filename'] = filename
        result['filepath'] = filepath
        return result
    
    except Exception as e:
        return {'error': f'Erro ao processar arquivo: {str(e)}'}
