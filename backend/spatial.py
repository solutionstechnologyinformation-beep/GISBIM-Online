from pyproj import Transformer

def dms_to_dd(degrees, minutes, seconds, direction):
    """Converte Graus, Minutos, Segundos (DMS) para Graus Decimais (DD)."""
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    if direction in ("S", "W", "s", "w"):
        dd *= -1
    return dd

def dd_to_dms(dd):
    """Converte Graus Decimais (DD) para Graus, Minutos, Segundos (DMS)."""
    is_negative = dd < 0
    dd = abs(dd)
    degrees = int(dd)
    minutes = int((dd - degrees) * 60)
    seconds = (dd - degrees - minutes/60) * 3600
    return degrees, minutes, seconds, is_negative

def convert(x, y, src_epsg, dst_epsg):
    """Converte uma coordenada de um sistema EPSG para outro."""
    transformer = Transformer.from_crs(f"EPSG:{src_epsg}", f"EPSG:{dst_epsg}", always_xy=True)
    new_x, new_y = transformer.transform(x, y)
    return new_x, new_y
