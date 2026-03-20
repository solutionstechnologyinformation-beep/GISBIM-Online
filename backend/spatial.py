"""
Módulo de conversão de coordenadas geográficas.
Suporta conversão entre DD (Graus Decimais), DMS (Graus Minutos Segundos) e UTM.
Sistemas: SIRGAS2000, SAD69, WGS84
Fusos UTM: 19-25 (Norte e Sul)
"""

from pyproj import Transformer, CRS
import math
try:
    from .epsg_codes import get_epsg_code, GEOGRAPHIC_SYSTEMS, validate_epsg_code
except ImportError:
    from epsg_codes import get_epsg_code, GEOGRAPHIC_SYSTEMS, validate_epsg_code

# Constantes UTM
WGS84_SEMI_MAJOR_AXIS = 6378137.0  # metros
WGS84_ECCENTRICITY = 0.0818191908426
UTM_SCALE_FACTOR = 0.9996
FALSE_EASTING = 500000.0
FALSE_NORTHING = 10000000.0


def dms_to_dd(degrees, minutes, seconds, direction):
    """
    Converte Graus, Minutos, Segundos (DMS) para Graus Decimais (DD).
    
    Args:
        degrees (float): Graus
        minutes (float): Minutos
        seconds (float): Segundos
        direction (str): Direção (N, S, E, W)
    
    Returns:
        float: Coordenada em Graus Decimais
    """
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction in ("S", "W", "s", "w"):
        dd *= -1
    return dd


def dd_to_dms(dd):
    """
    Converte Graus Decimais (DD) para Graus, Minutos, Segundos (DMS).
    
    Args:
        dd (float): Coordenada em Graus Decimais
    
    Returns:
        tuple: (degrees, minutes, seconds, is_negative)
    """
    is_negative = dd < 0
    dd = abs(dd)
    degrees = int(dd)
    minutes = int((dd - degrees) * 60)
    seconds = (dd - degrees - minutes/60) * 3600
    return degrees, minutes, seconds, is_negative


def dd_to_utm(latitude, longitude):
    """
    Converte coordenadas em Graus Decimais (DD) para UTM.
    
    Args:
        latitude (float): Latitude em Graus Decimais
        longitude (float): Longitude em Graus Decimais
    
    Returns:
        tuple: (zone, easting, northing, hemisphere)
    """
    # Calcular zona UTM
    zone = int((longitude + 180) / 6) + 1
    
    # Determinar hemisfério
    hemisphere = "N" if latitude >= 0 else "S"
    
    # Converter para radianos
    lat_rad = math.radians(latitude)
    lon_rad = math.radians(longitude)
    
    # Longitude central da zona
    lon_origin = (zone - 1) * 6 - 180 + 3
    lon_origin_rad = math.radians(lon_origin)
    
    # Cálculos UTM
    e2 = WGS84_ECCENTRICITY ** 2
    e_prime2 = e2 / (1 - e2)
    
    N = WGS84_SEMI_MAJOR_AXIS / math.sqrt(1 - e2 * math.sin(lat_rad) ** 2)
    T = math.tan(lat_rad) ** 2
    C = e_prime2 * math.cos(lat_rad) ** 2
    A = math.cos(lat_rad) * (lon_rad - lon_origin_rad)
    
    # Série de Fourier para latitude
    M = WGS84_SEMI_MAJOR_AXIS * (
        (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256) * lat_rad -
        (3*e2/8 + 3*e2**2/32 - 45*e2**3/1024) * math.sin(2*lat_rad) +
        (15*e2**2/256 - 45*e2**3/1024) * math.sin(4*lat_rad) -
        (35*e2**3/3072) * math.sin(6*lat_rad)
    )
    
    # Easting e Northing
    easting = UTM_SCALE_FACTOR * N * (A + A**3/6 * (1 - T + C) + A**5/120 * (5 - 18*T + T**2 + 72*C - 58*e_prime2)) + FALSE_EASTING
    
    northing = UTM_SCALE_FACTOR * (M + N * math.tan(lat_rad) * (A**2/2 + A**4/24 * (5 - T + 9*C + 4*C**2) + A**6/720 * (61 - 58*T + T**2 + 600*C - 330*e_prime2)))
    
    if latitude < 0:
        northing += FALSE_NORTHING
    
    return zone, easting, northing, hemisphere


def utm_to_dd(zone, easting, northing, hemisphere="N"):
    """
    Converte coordenadas UTM para Graus Decimais (DD).
    
    Args:
        zone (int): Zona UTM
        easting (float): Coordenada Easting (X)
        northing (float): Coordenada Northing (Y)
        hemisphere (str): Hemisfério (N ou S)
    
    Returns:
        tuple: (latitude, longitude)
    """
    # Ajustar northing para hemisfério sul
    if hemisphere in ("S", "s"):
        northing = northing - FALSE_NORTHING
    
    # Longitude central da zona
    lon_origin = (zone - 1) * 6 - 180 + 3
    
    # Cálculos inversos
    e2 = WGS84_ECCENTRICITY ** 2
    e_prime2 = e2 / (1 - e2)
    
    # Footpoint latitude
    M = northing / UTM_SCALE_FACTOR
    mu = M / (WGS84_SEMI_MAJOR_AXIS * (1 - e2/4 - 3*e2**2/64 - 5*e2**3/256))
    
    footpoint_lat = (
        mu + (3*e2/8 + 3*e2**2/32 - 45*e2**3/1024) * math.sin(2*mu) +
        (15*e2**2/256 - 45*e2**3/1024) * math.sin(4*mu) +
        (35*e2**3/3072) * math.sin(6*mu)
    )
    
    # Latitude e Longitude
    C1 = e_prime2 * math.cos(footpoint_lat) ** 2
    T1 = math.tan(footpoint_lat) ** 2
    N1 = WGS84_SEMI_MAJOR_AXIS / math.sqrt(1 - e2 * math.sin(footpoint_lat) ** 2)
    R1 = WGS84_SEMI_MAJOR_AXIS * (1 - e2) / math.sqrt((1 - e2 * math.sin(footpoint_lat) ** 2) ** 3)
    D = (easting - FALSE_EASTING) / (N1 * UTM_SCALE_FACTOR)
    
    latitude = (
        footpoint_lat - (N1 * math.tan(footpoint_lat) / R1) * (
            D**2/2 - D**4/24 * (5 + 3*T1 + 10*C1 - 4*C1**2 - 9*e_prime2) +
            D**6/720 * (61 + 90*T1 + 28*T1**2 + 45*e_prime2 - 252*e_prime2 - 3*e_prime2**2)
        )
    )
    
    longitude = (
        math.radians(lon_origin) + (D - D**3/6 * (1 + 2*T1 + C1) + D**5/120 * (5 - 2*C1 + 28*T1 - 3*C1**2 + 8*e_prime2 + 24*T1**2)) / math.cos(footpoint_lat)
    )
    
    latitude = math.degrees(latitude)
    longitude = math.degrees(longitude)
    
    # Ajustar para hemisfério sul
    if hemisphere in ("S", "s"):
        latitude = -latitude
    
    return latitude, longitude


def convert(x, y, src_epsg, dst_epsg):
    """
    Converte uma coordenada de um sistema EPSG para outro.
    
    Args:
        x (float): Coordenada X
        y (float): Coordenada Y
        src_epsg (str): Código EPSG de origem
        dst_epsg (str): Código EPSG de destino
    
    Returns:
        tuple: (new_x, new_y)
    
    Raises:
        ValueError: Se os códigos EPSG forem inválidos
    """
    if not validate_epsg_code(src_epsg) or not validate_epsg_code(dst_epsg):
        raise ValueError("Código EPSG inválido")
    
    try:
        transformer = Transformer.from_crs(
            f"EPSG:{src_epsg}",
            f"EPSG:{dst_epsg}",
            always_xy=True
        )
        new_x, new_y = transformer.transform(x, y)
        return new_x, new_y
    except Exception as e:
        raise ValueError(f"Erro ao transformar coordenadas: {str(e)}")


def convert_between_systems(x, y, src_system, src_zone, dst_system, dst_zone):
    """
    Converte coordenadas entre diferentes sistemas de referência e fusos UTM.
    
    Args:
        x (float): Coordenada X
        y (float): Coordenada Y
        src_system (str): Sistema de origem (SIRGAS2000, SAD69, WGS84)
        src_zone (str): Zona UTM de origem (ex: "19S", "20N") ou None para geográficas
        dst_system (str): Sistema de destino
        dst_zone (str): Zona UTM de destino ou None para geográficas
    
    Returns:
        dict: Resultado da conversão com coordenadas e metadados
    """
    try:
        # Obter códigos EPSG
        src_epsg = get_epsg_code(src_system, src_zone)
        dst_epsg = get_epsg_code(dst_system, dst_zone)
        
        if not src_epsg or not dst_epsg:
            raise ValueError("Sistema ou zona UTM inválido")
        
        # Realizar conversão
        new_x, new_y = convert(x, y, src_epsg, dst_epsg)
        
        return {
            'x': round(new_x, 6),
            'y': round(new_y, 6),
            'src_system': src_system,
            'src_zone': src_zone,
            'src_epsg': src_epsg,
            'dst_system': dst_system,
            'dst_zone': dst_zone,
            'dst_epsg': dst_epsg,
            'success': True
        }
    except Exception as e:
        return {
            'error': str(e),
            'success': False
        }


def format_dms(degrees, minutes, seconds, direction):
    """
    Formata coordenadas DMS para string legível.
    
    Args:
        degrees (int): Graus
        minutes (int): Minutos
        seconds (float): Segundos
        direction (str): Direção (N, S, E, W)
    
    Returns:
        str: String formatada
    """
    return f"{degrees}° {minutes}' {seconds:.2f}\" {direction}"


def format_utm(zone, easting, northing, hemisphere):
    """
    Formata coordenadas UTM para string legível.
    
    Args:
        zone (int): Zona UTM
        easting (float): Easting
        northing (float): Northing
        hemisphere (str): Hemisfério (N ou S)
    
    Returns:
        str: String formatada
    """
    return f"{zone}{hemisphere} {easting:.2f}m E {northing:.2f}m N"


def validate_dd(latitude, longitude):
    """
    Valida coordenadas em Graus Decimais.
    
    Args:
        latitude (float): Latitude
        longitude (float): Longitude
    
    Returns:
        tuple: (is_valid, message)
    """
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False, "Latitude e Longitude devem ser números"
    
    if latitude < -90 or latitude > 90:
        return False, "Latitude deve estar entre -90 e 90"
    
    if longitude < -180 or longitude > 180:
        return False, "Longitude deve estar entre -180 e 180"
    
    return True, "Coordenadas válidas"


def validate_utm(zone, easting, northing):
    """
    Valida coordenadas UTM.
    
    Args:
        zone (int): Zona UTM
        easting (float): Easting
        northing (float): Northing
    
    Returns:
        tuple: (is_valid, message)
    """
    if not isinstance(zone, int) or zone < 1 or zone > 60:
        return False, "Zona UTM deve estar entre 1 e 60"
    
    if easting < 160000 or easting > 840000:
        return False, "Easting deve estar entre 160000 e 840000"
    
    if northing < 0 or northing > 10000000:
        return False, "Northing deve estar entre 0 e 10000000"
    
    return True, "Coordenadas UTM válidas"


def validate_system(system):
    """
    Valida se um sistema de referência é suportado.
    
    Args:
        system (str): Sistema de referência
    
    Returns:
        bool: True se válido, False caso contrário
    """
    return system in GEOGRAPHIC_SYSTEMS


def validate_utm_zone(zone_str):
    """
    Valida se uma zona UTM é válida.
    
    Args:
        zone_str (str): Zona UTM (ex: "19S", "20N")
    
    Returns:
        tuple: (is_valid, zone_number, hemisphere)
    """
    if not isinstance(zone_str, str) or len(zone_str) < 2:
        return False, None, None
    
    try:
        zone_num = int(zone_str[:-1])
        hemisphere = zone_str[-1].upper()
        
        if zone_num < 19 or zone_num > 25:
            return False, None, None
        
        if hemisphere not in ("N", "S"):
            return False, None, None
        
        return True, zone_num, hemisphere
    except (ValueError, IndexError):
        return False, None, None
