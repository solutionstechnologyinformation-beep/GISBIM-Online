# Documentação de Endpoints - GISBIM Online v2.0

## Base URL
```
http://localhost:5000
```

## Endpoints de Conversão de Coordenadas

### 1. Converter DD para DMS
**Endpoint**: `POST /convert/dd-to-dms`

**Descrição**: Converte Graus Decimais (DD) para Graus Minutos Segundos (DMS)

**Request**:
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Response**:
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "latitude_dms": "23° 33' 1.80\" S",
  "longitude_dms": "46° 37' 59.88\" W",
  "format": "DMS"
}
```

---

### 2. Converter DD para UTM
**Endpoint**: `POST /convert/dd-to-utm`

**Descrição**: Converte Graus Decimais (DD) para UTM (Universal Transverse Mercator)

**Request**:
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333
}
```

**Response**:
```json
{
  "latitude": -23.5505,
  "longitude": -46.6333,
  "utm_zone": 23,
  "utm_hemisphere": "S",
  "utm_easting": 324123.45,
  "utm_northing": 7397456.78,
  "utm_formatted": "23S 324123.45m E 7397456.78m N",
  "format": "UTM"
}
```

---

### 3. Converter UTM para DD
**Endpoint**: `POST /convert/utm-to-dd`

**Descrição**: Converte UTM para Graus Decimais (DD)

**Request**:
```json
{
  "zone": 23,
  "easting": 324123.45,
  "northing": 7397456.78,
  "hemisphere": "S"
}
```

**Response**:
```json
{
  "utm_zone": 23,
  "utm_easting": 324123.45,
  "utm_northing": 7397456.78,
  "utm_hemisphere": "S",
  "latitude": -23.550500,
  "longitude": -46.633300,
  "format": "DD"
}
```

---

### 4. Converter DMS para DD
**Endpoint**: `POST /convert/dms-to-dd`

**Descrição**: Converte Graus Minutos Segundos (DMS) para Graus Decimais (DD)

**Request**:
```json
{
  "lat_degrees": 23,
  "lat_minutes": 33,
  "lat_seconds": 1.8,
  "lat_direction": "S",
  "lon_degrees": 46,
  "lon_minutes": 37,
  "lon_seconds": 59.88,
  "lon_direction": "W"
}
```

**Response**:
```json
{
  "latitude_dms": "23° 33' 1.8\" S",
  "longitude_dms": "46° 37' 59.88\" W",
  "latitude": -23.550500,
  "longitude": -46.633300,
  "format": "DD"
}
```

---

### 5. Converter EPSG para EPSG
**Endpoint**: `POST /convert`

**Descrição**: Converte coordenadas entre diferentes sistemas EPSG

**Request**:
```json
{
  "x": -46.6333,
  "y": -23.5505,
  "src": "4326",
  "dst": "3857"
}
```

**Response**:
```json
{
  "x": -5195426.45,
  "y": -2711245.67,
  "src": "4326",
  "dst": "3857"
}
```

---

## Endpoints de Processamento em Lote

### 6. Processar Lote de Coordenadas
**Endpoint**: `POST /batch-convert`

**Descrição**: Processa múltiplas coordenadas para conversão

**Request**:
```json
{
  "type": "dd-to-dms",
  "points": [
    {
      "name": "São Paulo",
      "latitude": -23.5505,
      "longitude": -46.6333
    },
    {
      "name": "Rio de Janeiro",
      "latitude": -22.9068,
      "longitude": -43.1729
    }
  ]
}
```

**Response**:
```json
{
  "total": 2,
  "processed": 2,
  "errors": 0,
  "results": [
    {
      "id": 0,
      "name": "São Paulo",
      "latitude": -23.5505,
      "longitude": -46.6333,
      "latitude_dms": "23° 33' 1.80\" S",
      "longitude_dms": "46° 37' 59.88\" W",
      "status": "success"
    },
    {
      "id": 1,
      "name": "Rio de Janeiro",
      "latitude": -22.9068,
      "longitude": -43.1729,
      "latitude_dms": "22° 54' 24.48\" S",
      "longitude_dms": "43° 10' 22.44\" W",
      "status": "success"
    }
  ]
}
```

---

## Endpoints de Upload e Exportação

### 7. Upload de Arquivo
**Endpoint**: `POST /upload`

**Descrição**: Faz upload de arquivo geoespacial (SHP, GeoJSON, KML, KMZ, etc.)

**Request**: Form-data com arquivo

**Response**:
```json
{
  "message": "Arquivo processado com sucesso",
  "data": {
    "filename": "pontos.shp",
    "features": 150,
    "bounds": {
      "minx": -46.7,
      "miny": -23.6,
      "maxx": -46.5,
      "maxy": -23.4
    }
  }
}
```

---

### 8. Exportar Dados
**Endpoint**: `POST /export_full`

**Descrição**: Exporta coordenadas em múltiplos formatos

**Request**:
```json
{
  "format": "kml",
  "points": [
    {
      "x": -46.6333,
      "y": -23.5505,
      "type": "capital",
      "color": "#FF0000"
    }
  ]
}
```

**Response**:
```json
{
  "message": "Arquivo export_points.kml gerado com sucesso",
  "url": "/download/export_points.kml",
  "filename": "export_points.kml"
}
```

**Formatos Suportados**: txt, csv, kml, dxf

---

## Endpoints de Utilidade

### 9. Health Check
**Endpoint**: `GET /health`

**Descrição**: Verifica a saúde da aplicação

**Response**:
```json
{
  "status": "healthy",
  "message": "GISBIM Online está funcionando",
  "version": "2.0.0"
}
```

---

## Códigos de Erro

| Código | Descrição |
|--------|-----------|
| 400 | Requisição inválida ou dados ausentes |
| 404 | Recurso não encontrado |
| 500 | Erro interno do servidor |

---

## Exemplos com cURL

### Converter DD para DMS
```bash
curl -X POST http://localhost:5000/convert/dd-to-dms \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'
```

### Converter DD para UTM
```bash
curl -X POST http://localhost:5000/convert/dd-to-utm \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'
```

### Processar Lote
```bash
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

---

## Notas Importantes

1. **Validação de Coordenadas**: Latitude deve estar entre -90 e 90, Longitude entre -180 e 180
2. **Precisão**: Coordenadas são retornadas com até 6 casas decimais
3. **Zona UTM**: Válida de 1 a 60
4. **CORS**: Habilitado para requisições de qualquer origem
5. **Rate Limiting**: Não implementado (considerar para produção)

---

**Última atualização**: 19 de Março de 2026  
**Versão**: 2.0.0
