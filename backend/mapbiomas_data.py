"""
Módulo de integração com dados do MapBiomas
Fornece acesso a camadas de uso e cobertura do solo
"""

import json
from typing import Dict, List, Optional

# Informações sobre camadas do MapBiomas
MAPBIOMAS_LAYERS = {
    'uso_solo': {
        'nome': 'Uso e Cobertura do Solo',
        'descricao': 'Classificação de uso e cobertura do solo no Brasil',
        'wms_url': 'https://api.mapbiomas.org/wms',
        'layer': 'mapbiomas_uso_solo',
        'anos_disponiveis': list(range(1985, 2024))
    },
    'biomas': {
        'nome': 'Biomas do Brasil',
        'descricao': 'Delimitação dos biomas brasileiros',
        'wms_url': 'https://api.mapbiomas.org/wms',
        'layer': 'mapbiomas_biomas',
        'anos_disponiveis': [2020]
    }
}

# Classificações de uso do solo
MAPBIOMAS_CLASSES = {
    1: {'nome': 'Floresta', 'cor': '#004000'},
    2: {'nome': 'Savana', 'cor': '#B4CC33'},
    3: {'nome': 'Pastagem', 'cor': '#FFD37F'},
    4: {'nome': 'Agricultura', 'cor': '#E974A1'},
    5: {'nome': 'Urbano', 'cor': '#E60000'},
    6: {'nome': 'Água', 'cor': '#0000FF'},
    7: {'nome': 'Nuvem', 'cor': '#FFFFFF'},
    8: {'nome': 'Não observado', 'cor': '#CCCCCC'}
}

def get_layer_info(layer_name: str) -> Optional[Dict]:
    """
    Retorna informações sobre uma camada do MapBiomas.
    
    Args:
        layer_name: Nome da camada ('uso_solo', 'biomas')
    
    Returns:
        Dict com informações da camada ou None
    """
    return MAPBIOMAS_LAYERS.get(layer_name)

def get_all_layers() -> Dict:
    """
    Retorna informações sobre todas as camadas disponíveis.
    
    Returns:
        Dict com todas as camadas
    """
    return MAPBIOMAS_LAYERS

def get_classification_colors() -> Dict:
    """
    Retorna as classificações de uso do solo com cores.
    
    Returns:
        Dict com classificações e cores
    """
    return MAPBIOMAS_CLASSES

def get_wms_url(layer_name: str, year: int = 2023) -> Optional[str]:
    """
    Gera URL do serviço WMS para uma camada específica.
    
    Args:
        layer_name: Nome da camada
        year: Ano desejado
    
    Returns:
        String com URL do WMS ou None
    """
    layer_info = get_layer_info(layer_name)
    if not layer_info:
        return None
    
    if year not in layer_info.get('anos_disponiveis', []):
        # Usar o ano mais recente disponível
        year = max(layer_info.get('anos_disponiveis', [2023]))
    
    base_url = layer_info.get('wms_url')
    layer = layer_info.get('layer')
    
    if base_url and layer:
        return f"{base_url}?service=WMS&version=1.1.0&request=GetMap&layers={layer}_{year}&styles=&bbox=-73.99,-33.74,-34.79,-60.51&width=512&height=512&srs=EPSG:4326&format=application/openlayers"
    
    return None

def get_biomas_list() -> List[Dict]:
    """
    Retorna lista dos biomas brasileiros.
    
    Returns:
        Lista com dados dos biomas
    """
    biomas = [
        {
            'id': 1,
            'nome': 'Amazônia',
            'descricao': 'Maior floresta tropical do mundo',
            'area_km2': 5500000
        },
        {
            'id': 2,
            'nome': 'Cerrado',
            'descricao': 'Savana tropical brasileira',
            'area_km2': 2000000
        },
        {
            'id': 3,
            'nome': 'Mata Atlântica',
            'descricao': 'Floresta tropical atlântica',
            'area_km2': 1300000
        },
        {
            'id': 4,
            'nome': 'Caatinga',
            'descricao': 'Vegetação de semiárido',
            'area_km2': 900000
        },
        {
            'id': 5,
            'nome': 'Pantanal',
            'descricao': 'Maior área úmida tropical',
            'area_km2': 150000
        },
        {
            'id': 6,
            'nome': 'Pampas',
            'descricao': 'Campos do sul do Brasil',
            'area_km2': 180000
        }
    ]
    
    return biomas

def get_statistics(layer_name: str, year: int = 2023) -> Optional[Dict]:
    """
    Retorna estatísticas de uma camada para um ano específico.
    
    Args:
        layer_name: Nome da camada
        year: Ano desejado
    
    Returns:
        Dict com estatísticas ou None
    """
    layer_info = get_layer_info(layer_name)
    if not layer_info:
        return None
    
    # Aqui seria feita uma chamada real à API do MapBiomas
    # Por enquanto, retorna estrutura de exemplo
    return {
        'layer': layer_name,
        'year': year,
        'total_area_km2': 8514877,
        'classes': {
            'floresta': {'area_km2': 4900000, 'percentual': 57.5},
            'pastagem': {'area_km2': 2100000, 'percentual': 24.6},
            'agricultura': {'area_km2': 800000, 'percentual': 9.4},
            'urbano': {'area_km2': 150000, 'percentual': 1.8},
            'agua': {'area_km2': 100000, 'percentual': 1.2},
            'outro': {'area_km2': 464877, 'percentual': 5.5}
        }
    }

if __name__ == '__main__':
    # Teste
    print("Testando integração com MapBiomas...")
    
    print("\nCamadas disponíveis:")
    for layer_name, info in get_all_layers().items():
        print(f"  - {info['nome']}: {info['descricao']}")
    
    print("\nBiomas:")
    for bioma in get_biomas_list():
        print(f"  - {bioma['nome']}: {bioma['area_km2']:,} km²")
    
    print("\nClassificações:")
    for class_id, class_info in get_classification_colors().items():
        print(f"  {class_id}: {class_info['nome']} ({class_info['cor']})")
