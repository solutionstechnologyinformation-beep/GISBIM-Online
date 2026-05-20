"""
Módulo de conversão entre datums geodésicos com precisão
Implementa transformações entre WGS84, SIRGAS2000 e SAD69
"""

from pyproj import Transformer, CRS
import math

# Definição de sistemas de referência
DATUMS = {
    'WGS84': {
        'epsg': 4326,
        'nome': 'WGS84 (World Geodetic System 1984)',
        'descricao': 'Sistema de referência global mais utilizado'
    },
    'SIRGAS2000': {
        'epsg': 4674,
        'nome': 'SIRGAS2000 (Sistema de Referência Geocêntrico para as Américas)',
        'descricao': 'Sistema oficial do Brasil desde 2005'
    },
    'SAD69': {
        'epsg': 4618,
        'nome': 'SAD69 (South American Datum 1969)',
        'descricao': 'Sistema anterior ao SIRGAS2000'
    }
}

# Parâmetros de transformação entre datums (Molodensky)
TRANSFORMATION_PARAMS = {
    ('WGS84', 'SIRGAS2000'): {
        'dx': 0.0,
        'dy': 0.0,
        'dz': 0.0,
        'rx': 0.0,
        'ry': 0.0,
        'rz': 0.0,
        'scale': 0.0,
        'descricao': 'WGS84 e SIRGAS2000 são praticamente idênticos'
    },
    ('WGS84', 'SAD69'): {
        'dx': -66.87,
        'dy': -4.37,
        'dz': -38.52,
        'rx': -0.554,
        'ry': 0.207,
        'rz': -0.106,
        'scale': -0.26,
        'descricao': 'Transformação de WGS84 para SAD69'
    },
    ('SIRGAS2000', 'SAD69'): {
        'dx': -66.87,
        'dy': -4.37,
        'dz': -38.52,
        'rx': -0.554,
        'ry': 0.207,
        'rz': -0.106,
        'scale': -0.26,
        'descricao': 'Transformação de SIRGAS2000 para SAD69'
    }
}

class DatumConverter:
    """Classe para conversão entre datums geodésicos."""
    
    def __init__(self):
        self.transformers = {}
        self._initialize_transformers()
    
    def _initialize_transformers(self):
        """Inicializa transformadores pyproj para todos os datums."""
        for src_name, src_info in DATUMS.items():
            for dst_name, dst_info in DATUMS.items():
                if src_name != dst_name:
                    try:
                        key = (src_name, dst_name)
                        transformer = Transformer.from_crs(
                            CRS.from_epsg(src_info['epsg']),
                            CRS.from_epsg(dst_info['epsg']),
                            always_xy=True
                        )
                        self.transformers[key] = transformer
                    except Exception as e:
                        print(f"Erro ao inicializar transformador {key}: {str(e)}")
    
    def convert(self, lat: float, lon: float, src_datum: str, dst_datum: str) -> dict:
        """
        Converte coordenadas entre datums.
        
        Args:
            lat: Latitude em Graus Decimais
            lon: Longitude em Graus Decimais
            src_datum: Datum de origem (WGS84, SIRGAS2000, SAD69)
            dst_datum: Datum de destino
        
        Returns:
            Dict com coordenadas convertidas e metadados
        """
        if src_datum == dst_datum:
            return {
                'latitude': lat,
                'longitude': lon,
                'src_datum': src_datum,
                'dst_datum': dst_datum,
                'diferenca_lat': 0.0,
                'diferenca_lon': 0.0,
                'precisao_m': 0.0,
                'mensagem': 'Datums são idênticos'
            }
        
        # Validar datums
        if src_datum not in DATUMS:
            raise ValueError(f"Datum de origem inválido: {src_datum}")
        if dst_datum not in DATUMS:
            raise ValueError(f"Datum de destino inválido: {dst_datum}")
        
        # Validar coordenadas
        if lat < -90 or lat > 90:
            raise ValueError(f"Latitude inválida: {lat}")
        if lon < -180 or lon > 180:
            raise ValueError(f"Longitude inválida: {lon}")
        
        try:
            # Obter transformador
            key = (src_datum, dst_datum)
            if key not in self.transformers:
                raise ValueError(f"Transformação não disponível: {src_datum} -> {dst_datum}")
            
            transformer = self.transformers[key]
            
            # Realizar transformação
            new_lon, new_lat = transformer.transform(lon, lat)
            
            # Calcular diferenças
            diff_lat = abs(new_lat - lat)
            diff_lon = abs(new_lon - lon)
            
            # Estimar precisão em metros (aproximado)
            # 1 grau ≈ 111 km
            precisao_m = math.sqrt((diff_lat * 111000)**2 + (diff_lon * 111000 * math.cos(math.radians(lat)))**2)
            
            return {
                'latitude': round(new_lat, 8),
                'longitude': round(new_lon, 8),
                'src_datum': src_datum,
                'dst_datum': dst_datum,
                'diferenca_lat': round(diff_lat, 8),
                'diferenca_lon': round(diff_lon, 8),
                'precisao_m': round(precisao_m, 2),
                'src_info': DATUMS[src_datum],
                'dst_info': DATUMS[dst_datum]
            }
        
        except Exception as e:
            raise Exception(f"Erro ao converter coordenadas: {str(e)}")
    
    def get_available_datums(self) -> dict:
        """Retorna lista de datums disponíveis."""
        return DATUMS
    
    def get_transformation_info(self, src_datum: str, dst_datum: str) -> dict:
        """Retorna informações sobre a transformação entre dois datums."""
        key = (src_datum, dst_datum)
        reverse_key = (dst_datum, src_datum)
        
        if key in TRANSFORMATION_PARAMS:
            return TRANSFORMATION_PARAMS[key]
        elif reverse_key in TRANSFORMATION_PARAMS:
            params = TRANSFORMATION_PARAMS[reverse_key]
            # Inverter parâmetros
            return {
                'dx': -params['dx'],
                'dy': -params['dy'],
                'dz': -params['dz'],
                'rx': -params['rx'],
                'ry': -params['ry'],
                'rz': -params['rz'],
                'scale': -params['scale'],
                'descricao': f"Transformação inversa: {dst_datum} para {src_datum}"
            }
        else:
            return {'descricao': 'Transformação não parametrizada'}

# Instância global
_converter = DatumConverter()

def convert_datum(lat: float, lon: float, src_datum: str, dst_datum: str) -> dict:
    """Função de conveniência para conversão de datums."""
    return _converter.convert(lat, lon, src_datum, dst_datum)

def get_available_datums() -> dict:
    """Função de conveniência para obter datums disponíveis."""
    return _converter.get_available_datums()

def get_transformation_info(src_datum: str, dst_datum: str) -> dict:
    """Função de conveniência para obter informações de transformação."""
    return _converter.get_transformation_info(src_datum, dst_datum)

if __name__ == '__main__':
    # Teste
    print("Testando conversão entre datums...")
    
    # Exemplo: Ponto em São Paulo
    lat, lon = -23.550520, -46.633309
    
    print(f"\nPonto original (WGS84): {lat}, {lon}")
    
    try:
        # Converter para SIRGAS2000
        result = convert_datum(lat, lon, 'WGS84', 'SIRGAS2000')
        print(f"SIRGAS2000: {result['latitude']}, {result['longitude']}")
        print(f"Diferença: {result['diferenca_lat']}° lat, {result['diferenca_lon']}° lon")
        print(f"Precisão: {result['precisao_m']} metros")
        
        # Converter para SAD69
        result = convert_datum(lat, lon, 'WGS84', 'SAD69')
        print(f"\nSAD69: {result['latitude']}, {result['longitude']}")
        print(f"Diferença: {result['diferenca_lat']}° lat, {result['diferenca_lon']}° lon")
        print(f"Precisão: {result['precisao_m']} metros")
    
    except Exception as e:
        print(f"Erro: {str(e)}")
