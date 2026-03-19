# Setup GISBIM Online v2.0 no Codespaces

## Instruções para Atualizar no Visual Studio Code Codespaces

### Passo 1: Abrir no Codespaces

1. Acesse o repositório: https://github.com/solutionstechnologyinformation-beep/GISBIM-Online
2. Clique em **Code** → **Codespaces** → **Create codespace on main**
3. Aguarde o ambiente carregar (5-10 minutos)

### Passo 2: Abrir Terminal

No Codespaces:
1. Pressione **Ctrl + `** (backtick) para abrir o terminal
2. Ou clique em **Terminal** → **New Terminal**

### Passo 3: Atualizar Arquivos

#### 3.1 Atualizar backend/spatial.py

```bash
# Copiar o arquivo atualizado
cat > backend/spatial.py << 'EOF'
"""
Módulo de conversão de coordenadas geográficas.
Suporta conversão entre DD (Graus Decimais), DMS (Graus Minutos Segundos) e UTM.
"""

from pyproj import Transformer
import math

# Constantes UTM
WGS84_SEMI_MAJOR_AXIS = 6378137.0  # metros
WGS84_ECCENTRICITY = 0.0818191908426
UTM_SCALE_FACTOR = 0.9996
FALSE_EASTING = 500000.0
FALSE_NORTHING = 10000000.0


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


def dd_to_utm(latitude, longitude):
    """
    Converte coordenadas em Graus Decimais (DD) para UTM.
    Retorna: (zone, easting, northing, hemisphere)
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
    Retorna: (latitude, longitude)
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
    """Converte uma coordenada de um sistema EPSG para outro."""
    transformer = Transformer.from_crs(f"EPSG:{src_epsg}", f"EPSG:{dst_epsg}", always_xy=True)
    new_x, new_y = transformer.transform(x, y)
    return new_x, new_y


def format_dms(latitude, longitude):
    """Formata coordenadas DD para string DMS legível."""
    lat_deg, lat_min, lat_sec, lat_neg = dd_to_dms(latitude)
    lon_deg, lon_min, lon_sec, lon_neg = dd_to_dms(longitude)
    
    lat_dir = "S" if lat_neg else "N"
    lon_dir = "W" if lon_neg else "E"
    
    lat_str = f"{lat_deg}° {lat_min}' {lat_sec:.2f}\" {lat_dir}"
    lon_str = f"{lon_deg}° {lon_min}' {lon_sec:.2f}\" {lon_dir}"
    
    return lat_str, lon_str


def format_utm(zone, easting, northing, hemisphere):
    """Formata coordenadas UTM para string legível."""
    return f"{zone}{hemisphere} {easting:.2f}m E {northing:.2f}m N"


def validate_dd(latitude, longitude):
    """Valida coordenadas em Graus Decimais."""
    if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
        return False, "Latitude e Longitude devem ser números"
    
    if latitude < -90 or latitude > 90:
        return False, "Latitude deve estar entre -90 e 90"
    
    if longitude < -180 or longitude > 180:
        return False, "Longitude deve estar entre -180 e 180"
    
    return True, "Coordenadas válidas"


def validate_utm(zone, easting, northing):
    """Valida coordenadas UTM."""
    if not isinstance(zone, int) or zone < 1 or zone > 60:
        return False, "Zona UTM deve estar entre 1 e 60"
    
    if easting < 160000 or easting > 840000:
        return False, "Easting deve estar entre 160000 e 840000"
    
    if northing < 0 or northing > 10000000:
        return False, "Northing deve estar entre 0 e 10000000"
    
    return True, "Coordenadas UTM válidas"
EOF
```

#### 3.2 Atualizar backend/requirements.txt

```bash
cat > backend/requirements.txt << 'EOF'
Flask>=2.3.0,<3.0.0
flask-cors>=4.0.0,<5.0.0
pyproj>=3.4.0,<4.0.0
python-dotenv>=1.0.0,<2.0.0
geopandas>=0.13.0
werkzeug>=2.3.0
rasterio>=1.3.0
gunicorn>=21.2.0
pandas>=2.0.0
fiona>=1.9.0
simplekml>=1.3.0
ezdxf>=1.0.0
shapefile>=2.3.0
EOF
```

#### 3.3 Atualizar backend/app.py

Copie o conteúdo do arquivo `backend/app.py` fornecido e substitua o arquivo atual no Codespaces.

### Passo 4: Instalar Dependências

```bash
# Ativar ambiente virtual (se necessário)
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r backend/requirements.txt
```

### Passo 5: Testar Localmente

```bash
# Verificar sintaxe
python3 -m py_compile backend/spatial.py backend/app.py

# Executar aplicação
cd backend
python app.py
```

A aplicação estará em: http://localhost:5000

### Passo 6: Fazer Commit e Push

```bash
# Verificar mudanças
git status

# Adicionar arquivos
git add backend/spatial.py backend/app.py backend/requirements.txt

# Commit
git commit -m "feat: Atualizar GISBIM Online v2.0 com suporte DD/DMS/UTM

- Adicionar conversão completa DD/DMS/UTM
- Novos endpoints de conversão
- Processamento em lote
- Validação de coordenadas
- Documentação de API"

# Push para GitHub
git push origin main
```

### Passo 7: Deploy no Render

1. Acesse https://render.com
2. Clique em "New +" → "Web Service"
3. Conecte seu GitHub
4. Selecione o repositório GISBIM-Online
5. Configure:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
   - **Environment**: Python 3.11
6. Clique em "Create Web Service"

## Verificação de Funcionalidades

### Testar Endpoints

```bash
# Health check
curl http://localhost:5000/health

# Converter DD para DMS
curl -X POST http://localhost:5000/convert/dd-to-dms \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'

# Converter DD para UTM
curl -X POST http://localhost:5000/convert/dd-to-utm \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'

# Processar lote
curl -X POST http://localhost:5000/batch-convert \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dd-to-dms",
    "points": [
      {"name": "SP", "latitude": -23.5505, "longitude": -46.6333},
      {"name": "RJ", "latitude": -22.9068, "longitude": -43.1729}
    ]
  }'
```

## Troubleshooting no Codespaces

### Erro: "Module not found"

```bash
# Reinstalar dependências
pip install --upgrade -r backend/requirements.txt
```

### Erro: "Port already in use"

```bash
# Usar porta diferente
cd backend
python app.py --port 5001
```

### Erro: "Permission denied"

```bash
# Dar permissão de execução
chmod +x backend/app.py
```

## Estrutura de Arquivos Atualizada

```
GISBIM-Online/
├── backend/
│   ├── app.py                  # ✓ ATUALIZADO
│   ├── spatial.py              # ✓ ATUALIZADO
│   ├── requirements.txt         # ✓ ATUALIZADO
│   ├── upload.py
│   ├── exporters.py
│   └── ...
├── frontend/
│   └── ...
├── API_ENDPOINTS.md            # ✓ NOVO
├── README_NOVO.md              # ✓ NOVO
└── ...
```

## Próximos Passos

1. ✓ Atualizar arquivos no Codespaces
2. ✓ Testar localmente
3. ✓ Fazer commit e push
4. ✓ Deploy no Render
5. Monitorar logs no Render
6. Testar endpoints em produção

---

**Data**: 19 de Março de 2026  
**Versão**: 2.0.0
