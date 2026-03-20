"""
Códigos EPSG para sistemas de referência geodésicos brasileiros.
Suporta SIRGAS2000, SAD69, WGS84 e fusos UTM 19-25 (Norte e Sul).
"""

EPSG_CODES = {
    "WGS84": {
        "Geográficas": {
            "WGS84 (Graus Decimais)": "4326"
        },
        "UTM_Sul": {
            "Zona 19S": "32719",
            "Zona 20S": "32720",
            "Zona 21S": "32721",
            "Zona 22S": "32722",
            "Zona 23S": "32723",
            "Zona 24S": "32724",
            "Zona 25S": "32725"
        },
        "UTM_Norte": {
            "Zona 19N": "32619",
            "Zona 20N": "32620",
            "Zona 21N": "32621",
            "Zona 22N": "32622",
            "Zona 23N": "32623",
            "Zona 24N": "32624",
            "Zona 25N": "32625"
        }
    },
    "SIRGAS2000": {
        "Geográficas": {
            "SIRGAS2000 (Graus Decimais)": "4674"
        },
        "UTM_Sul": {
            "Zona 19S": "31979",
            "Zona 20S": "31980",
            "Zona 21S": "31981",
            "Zona 22S": "31982",
            "Zona 23S": "31983",
            "Zona 24S": "31984",
            "Zona 25S": "31985"
        },
        "UTM_Norte": {
            "Zona 19N": "31879",
            "Zona 20N": "31880",
            "Zona 21N": "31881",
            "Zona 22N": "31882",
            "Zona 23N": "31883",
            "Zona 24N": "31884",
            "Zona 25N": "31885"
        }
    },
    "SAD69": {
        "Geográficas": {
            "SAD69 (Graus Decimais)": "4618"
        },
        "UTM_Sul": {
            "Zona 19S": "29189",
            "Zona 20S": "29190",
            "Zona 21S": "29191",
            "Zona 22S": "29192",
            "Zona 23S": "29193",
            "Zona 24S": "29194",
            "Zona 25S": "29195"
        },
        "UTM_Norte": {
            "Zona 19N": "29089",
            "Zona 20N": "29090",
            "Zona 21N": "29091",
            "Zona 22N": "29092",
            "Zona 23N": "29093",
            "Zona 24N": "29094",
            "Zona 25N": "29095"
        }
    }
}

# Mapeamento de fusos UTM para códigos EPSG
UTM_ZONE_MAPPING = {
    # SIRGAS2000
    "SIRGAS2000_19S": "31979",
    "SIRGAS2000_20S": "31980",
    "SIRGAS2000_21S": "31981",
    "SIRGAS2000_22S": "31982",
    "SIRGAS2000_23S": "31983",
    "SIRGAS2000_24S": "31984",
    "SIRGAS2000_25S": "31985",
    "SIRGAS2000_19N": "31879",
    "SIRGAS2000_20N": "31880",
    "SIRGAS2000_21N": "31881",
    "SIRGAS2000_22N": "31882",
    "SIRGAS2000_23N": "31883",
    "SIRGAS2000_24N": "31884",
    "SIRGAS2000_25N": "31885",
    
    # SAD69
    "SAD69_19S": "29189",
    "SAD69_20S": "29190",
    "SAD69_21S": "29191",
    "SAD69_22S": "29192",
    "SAD69_23S": "29193",
    "SAD69_24S": "29194",
    "SAD69_25S": "29195",
    "SAD69_19N": "29089",
    "SAD69_20N": "29090",
    "SAD69_21N": "29091",
    "SAD69_22N": "29092",
    "SAD69_23N": "29093",
    "SAD69_24N": "29094",
    "SAD69_25N": "29095",
    
    # WGS84
    "WGS84_19S": "32719",
    "WGS84_20S": "32720",
    "WGS84_21S": "32721",
    "WGS84_22S": "32722",
    "WGS84_23S": "32723",
    "WGS84_24S": "32724",
    "WGS84_25S": "32725",
    "WGS84_19N": "32619",
    "WGS84_20N": "32620",
    "WGS84_21N": "32621",
    "WGS84_22N": "32622",
    "WGS84_23N": "32623",
    "WGS84_24N": "32624",
    "WGS84_25N": "32625",
}

# Sistemas de referência geográficos
GEOGRAPHIC_SYSTEMS = {
    "SIRGAS2000": "4674",
    "SAD69": "4618",
    "WGS84": "4326"
}

# Fusos UTM disponíveis
AVAILABLE_UTM_ZONES = {
    "Sul": ["19S", "20S", "21S", "22S", "23S", "24S", "25S"],
    "Norte": ["19N", "20N", "21N", "22N", "23N", "24N", "25N"]
}


def get_epsg_code(system, zone=None):
    """
    Retorna o código EPSG para um sistema de referência e zona UTM.
    
    Args:
        system (str): Sistema de referência (SIRGAS2000, SAD69, WGS84)
        zone (str): Zona UTM (ex: "19S", "20N") ou None para geográficas
    
    Returns:
        str: Código EPSG ou None se não encontrado
    """
    if zone is None:
        return GEOGRAPHIC_SYSTEMS.get(system)
    
    key = f"{system}_{zone}"
    return UTM_ZONE_MAPPING.get(key)


def get_all_systems():
    """Retorna lista de todos os sistemas disponíveis."""
    return list(EPSG_CODES.keys())


def get_all_zones(hemisphere="Sul"):
    """Retorna lista de zonas UTM disponíveis para um hemisfério."""
    return AVAILABLE_UTM_ZONES.get(hemisphere, [])


def validate_epsg_code(epsg_code):
    """Valida se um código EPSG está na lista de códigos suportados."""
    all_codes = []
    for system_data in EPSG_CODES.values():
        for category_data in system_data.values():
            if isinstance(category_data, dict):
                all_codes.extend(category_data.values())
    
    return str(epsg_code) in all_codes
