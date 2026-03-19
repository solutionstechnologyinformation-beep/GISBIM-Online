import geopandas as gpd
import os
from werkzeug.utils import secure_filename
import fiona
import zipfile
import shutil

UPLOAD_FOLDER = '../data/uploads'
ALLOWED_EXTENSIONS = {'shp', 'geojson', 'json', 'gpkg', 'kml', 'kmz'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def read_spatial_file(filepath, driver=None):
    """Read spatial file and return as GeoJSON."""
    try:
        # Fiona pode ter problemas com drivers KML/KMZ sem especificar explicitamente
        if driver:
            gdf = gpd.read_file(filepath, driver=driver)
        else:
            gdf = gpd.read_file(filepath)
        
        # Converter para WGS84 (EPSG:4326) para exibição no mapa Leaflet
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs(epsg=4326)
            
        # Extrair apenas as geometrias e suas coordenadas
        features = []
        for _, row in gdf.iterrows():
            if row.geometry:
                if row.geometry.geom_type == 'Point':
                    features.append({
                        'type': 'Point',
                        'coordinates': [row.geometry.x, row.geometry.y]
                    })
                elif row.geometry.geom_type in ['LineString', 'MultiLineString']:
                    # Simplificar para o primeiro ponto da linha para visualização inicial
                    if row.geometry.geom_type == 'LineString':
                        coords = list(row.geometry.coords)
                    else: # MultiLineString
                        coords = list(row.geometry.geoms[0].coords) if row.geometry.geoms else []
                    if coords:
                        features.append({
                            'type': 'Point',
                            'coordinates': [coords[0][0], coords[0][1]] # Apenas o primeiro ponto
                        })
                elif row.geometry.geom_type in ['Polygon', 'MultiPolygon']:
                    # Simplificar para o centróide do polígono para visualização inicial
                    if row.geometry.centroid:
                        features.append({
                            'type': 'Point',
                            'coordinates': [row.geometry.centroid.x, row.geometry.centroid.y]
                        })
        return {'features': features}
    except Exception as e:
        return {'error': str(e)}

def process_upload(file):
    """Process uploaded file and return GeoJSON or coordinates."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Lidar com KMZ: descompactar e encontrar o KML
        if filename.lower().endswith('.kmz'):
            temp_dir = os.path.join(UPLOAD_FOLDER, 'temp_kmz_extract')
            os.makedirs(temp_dir, exist_ok=True)
            zip_path = os.path.join(temp_dir, filename)
            file.save(zip_path)
            
            kml_filepath = None
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
                for root, _, files in os.walk(temp_dir):
                    for f in files:
                        if f.lower().endswith('.kml'):
                            kml_filepath = os.path.join(root, f)
                            break
                    if kml_filepath: break
            
            if kml_filepath:
                result = read_spatial_file(kml_filepath, driver='KML')
            else:
                result = {'error': 'Nenhum arquivo KML encontrado dentro do KMZ.'}
            
            shutil.rmtree(temp_dir) # Limpar arquivos temporários
            return result
        
        # Lidar com outros formatos espaciais (KML, GeoJSON, Shapefile, etc.)
        file.save(filepath)
        if filename.lower().endswith('.kml'):
            return read_spatial_file(filepath, driver='KML')
        else:
            return read_spatial_file(filepath)
    
    return {'error': 'Tipo de arquivo inválido ou arquivo não fornecido.'}
