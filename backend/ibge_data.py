"""
Módulo de integração com dados do IBGE
Fornece acesso a camadas geoespaciais oficiais do IBGE
"""

import json
import requests
from typing import Dict, List, Optional

# URLs dos serviços do IBGE
IBGE_GEOJSON_MUNICIPIOS = "https://servicodados.ibge.gov.br/api/v1/geo/municipios"
IBGE_GEOJSON_ESTADOS = "https://servicodados.ibge.gov.br/api/v1/geo/estados"

# Cache de dados
_cache = {}

def get_municipios_geojson() -> Optional[Dict]:
    """
    Obtém dados de municípios do IBGE em formato GeoJSON.
    
    Returns:
        Dict com GeoJSON dos municípios ou None se falhar
    """
    if 'municipios' in _cache:
        return _cache['municipios']
    
    try:
        response = requests.get(IBGE_GEOJSON_MUNICIPIOS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Converter para GeoJSON
        features = []
        for municipio in data:
            if 'geometry' in municipio:
                features.append({
                    'type': 'Feature',
                    'geometry': municipio['geometry'],
                    'properties': {
                        'id': municipio.get('id'),
                        'nome': municipio.get('nome'),
                        'tipo': 'municipio'
                    }
                })
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        _cache['municipios'] = geojson
        return geojson
    
    except Exception as e:
        print(f"Erro ao obter dados de municípios: {str(e)}")
        return None

def get_estados_geojson() -> Optional[Dict]:
    """
    Obtém dados de estados do IBGE em formato GeoJSON.
    
    Returns:
        Dict com GeoJSON dos estados ou None se falhar
    """
    if 'estados' in _cache:
        return _cache['estados']
    
    try:
        response = requests.get(IBGE_GEOJSON_ESTADOS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Converter para GeoJSON
        features = []
        for estado in data:
            if 'geometry' in estado:
                features.append({
                    'type': 'Feature',
                    'geometry': estado['geometry'],
                    'properties': {
                        'id': estado.get('id'),
                        'nome': estado.get('nome'),
                        'sigla': estado.get('sigla'),
                        'tipo': 'estado'
                    }
                })
        
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        _cache['estados'] = geojson
        return geojson
    
    except Exception as e:
        print(f"Erro ao obter dados de estados: {str(e)}")
        return None

def get_municipio_by_id(municipio_id: int) -> Optional[Dict]:
    """
    Obtém dados de um município específico pelo ID.
    
    Args:
        municipio_id: ID do município (código IBGE)
    
    Returns:
        Dict com dados do município ou None se falhar
    """
    try:
        response = requests.get(f"{IBGE_GEOJSON_MUNICIPIOS}/{municipio_id}", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Erro ao obter dados do município {municipio_id}: {str(e)}")
        return None

def get_municipios_by_estado(estado_sigla: str) -> Optional[List[Dict]]:
    """
    Obtém lista de municípios de um estado específico.
    
    Args:
        estado_sigla: Sigla do estado (ex: 'SP', 'RJ')
    
    Returns:
        Lista com dados dos municípios ou None se falhar
    """
    try:
        municipios_data = get_municipios_geojson()
        if not municipios_data:
            return None
        
        municipios = []
        for feature in municipios_data.get('features', []):
            props = feature.get('properties', {})
            # Aqui seria necessário ter a informação do estado
            # Por enquanto, retorna todos os municípios
            municipios.append(props)
        
        return municipios
    except Exception as e:
        print(f"Erro ao obter municípios do estado {estado_sigla}: {str(e)}")
        return None

def get_layer_info(layer_type: str) -> Dict:
    """
    Retorna informações sobre uma camada disponível.
    
    Args:
        layer_type: Tipo de camada ('municipios', 'estados', etc)
    
    Returns:
        Dict com informações da camada
    """
    layers_info = {
        'municipios': {
            'nome': 'Municípios do Brasil',
            'descricao': 'Divisão territorial dos municípios brasileiros',
            'fonte': 'IBGE',
            'tipo': 'FeatureCollection'
        },
        'estados': {
            'nome': 'Estados do Brasil',
            'descricao': 'Divisão territorial dos estados brasileiros',
            'fonte': 'IBGE',
            'tipo': 'FeatureCollection'
        },
        'mapbiomas': {
            'nome': 'Uso e Cobertura do Solo',
            'descricao': 'Mapa de uso e cobertura do solo do MapBiomas',
            'fonte': 'MapBiomas',
            'tipo': 'WMS'
        }
    }
    
    return layers_info.get(layer_type, {})

def clear_cache():
    """Limpa o cache de dados."""
    global _cache
    _cache = {}

if __name__ == '__main__':
    # Teste
    print("Testando integração com IBGE...")
    
    municipios = get_municipios_geojson()
    if municipios:
        print(f"✓ {len(municipios.get('features', []))} municípios carregados")
    
    estados = get_estados_geojson()
    if estados:
        print(f"✓ {len(estados.get('features', []))} estados carregados")
