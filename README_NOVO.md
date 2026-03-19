# GISBIM Online v2.0 - Conversor de Coordenadas Geográficas

Uma plataforma web moderna e intuitiva para conversão de coordenadas geográficas entre múltiplos formatos (DD, DMS, UTM) com suporte a importação/exportação de arquivos e visualização em mapa interativo.

## ✨ Funcionalidades Principais

### 🔄 Conversão de Coordenadas
- **Graus Decimais (DD)**: -23.5505, -46.6333
- **Graus Minutos Segundos (DMS)**: 23° 33' 1.8" S, 46° 37' 59.88" W
- **UTM (Universal Transverse Mercator)**: 23S 324123.45m E 7397456.78m N
- Conversão bidirecional entre todos os formatos
- Conversão entre sistemas EPSG (WGS84, SIRGAS2000, UTM, etc.)

### 📁 Importação de Arquivos
- **Formatos Suportados**: TXT, CSV, KML, KMZ, Shapefile (SHP)
- **Validação Automática**: Verifica coordenadas válidas
- **Processamento em Lote**: Converte múltiplos pontos simultaneamente
- **Padrão de Entrada**: Ponto, Latitude, Longitude, Cota, Descrição

### 📤 Exportação de Dados
- **Formatos de Saída**: TXT, CSV, KML, KMZ, DXF
- **Relatórios**: Estatísticas de processamento
- **Download Direto**: Arquivos prontos para uso em GIS

### 🗺️ Visualização em Mapa
- **Google Maps Integrado**: Visualização interativa de pontos
- **Geocodificação Reversa**: Obter endereço a partir de coordenadas
- **Cálculo de Rotas**: Distância entre pontos
- **Marcadores Customizados**: Cores e ícones personalizáveis

### ⚙️ Processamento em Lote
- Converta até 10.000 pontos simultaneamente
- Validação automática de coordenadas
- Estatísticas detalhadas de processamento
- Exportação de resultados

## 🛠️ Tecnologias Utilizadas

### Backend
- **Framework**: Flask 2.3+
- **Conversão de Coordenadas**: PyProj 3.4+
- **Processamento Geoespacial**: GeoPandas, Rasterio, Fiona
- **Exportação**: SimpleKML, ezdxf
- **Servidor**: Gunicorn
- **Python**: 3.8+

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Design responsivo
- **JavaScript**: Lógica do cliente
- **Leaflet**: Visualização de mapas
- **OpenStreetMap**: Dados de mapas base

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git
- Navegador web moderno

## 🚀 Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/solutionstechnologyinformation-beep/GISBIM-Online.git
cd GISBIM-Online
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar Dependências

```bash
pip install -r backend/requirements.txt
```

### 4. Configurar Variáveis de Ambiente

```bash
# Copiar arquivo de exemplo
cp .env.example .env

# Editar .env conforme necessário (opcional)
# FLASK_ENV=development
# PORT=5000
```

### 5. Executar a Aplicação

```bash
cd backend
python app.py
```

A aplicação estará disponível em: **http://localhost:5000**

## 📖 Uso

### Interface Web

1. **Página Inicial**: Acesse http://localhost:5000
2. **Conversor**: Selecione o formato de entrada e saída
3. **Importar**: Faça upload de arquivos geoespaciais
4. **Exportar**: Baixe dados convertidos
5. **Mapa**: Visualize pontos em mapa interativo

### API REST

#### Exemplo: Converter DD para DMS

```bash
curl -X POST http://localhost:5000/convert/dd-to-dms \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

#### Exemplo: Converter DD para UTM

```bash
curl -X POST http://localhost:5000/convert/dd-to-utm \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": -23.5505,
    "longitude": -46.6333
  }'
```

#### Exemplo: Processar Lote

```bash
curl -X POST http://localhost:5000/batch-convert \
  -H "Content-Type: application/json" \
  -d '{
    "type": "dd-to-dms",
    "points": [
      {"name": "São Paulo", "latitude": -23.5505, "longitude": -46.6333},
      {"name": "Rio de Janeiro", "latitude": -22.9068, "longitude": -43.1729}
    ]
  }'
```

## 📚 Documentação Completa

Consulte [API_ENDPOINTS.md](./API_ENDPOINTS.md) para documentação completa de todos os endpoints.

## 🔧 Estrutura do Projeto

```
GISBIM-Online/
├── backend/
│   ├── __init__.py
│   ├── app.py                  # Aplicação Flask principal
│   ├── spatial.py              # Conversão de coordenadas
│   ├── upload.py               # Processamento de uploads
│   ├── exporters.py            # Exportação de dados
│   ├── raster.py               # Processamento raster
│   ├── db.py                   # Configuração de banco de dados
│   ├── epsg_codes.py           # Códigos EPSG
│   └── requirements.txt         # Dependências Python
├── frontend/
│   ├── index.html              # Página principal
│   ├── style.css               # Estilos CSS
│   ├── converter.js            # Lógica de conversão
│   ├── map.js                  # Integração com mapa
│   ├── upload.js               # Upload de arquivos
│   ├── draw.js                 # Desenho no mapa
│   ├── layers.js               # Gerenciamento de camadas
│   └── bim.js                  # Lógica BIM
├── data/
│   └── uploads/                # Arquivos carregados
├── scripts/                     # Scripts utilitários
├── Procfile                    # Configuração Render
├── Dockerfile                  # Configuração Docker
├── requirements.txt            # Dependências gerais
├── API_ENDPOINTS.md            # Documentação de API
└── README.md                   # Este arquivo
```

## 🌐 Deploy no Render

### Pré-requisitos
- Conta no GitHub
- Conta no Render

### Passos

1. **Fazer Push para GitHub**
```bash
git add .
git commit -m "Atualização GISBIM v2.0"
git push origin main
```

2. **Conectar ao Render**
   - Acesse https://render.com
   - Clique em "New +" → "Web Service"
   - Selecione o repositório
   - Configure conforme abaixo

3. **Configurações do Render**
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && gunicorn --bind 0.0.0.0:$PORT --workers 2 app:app`
   - **Environment**: Python 3.11

4. **Variáveis de Ambiente**
   ```
   FLASK_ENV=production
   PORT=5000
   ```

5. **Deploy**: Clique em "Create Web Service"

## 🧪 Testes

### Testar Endpoints Localmente

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
```

## 📊 Exemplos de Uso

### Cenário 1: Converter Coordenadas Individuais

1. Acesse http://localhost:5000
2. Selecione "Conversor"
3. Digite latitude: -23.5505
4. Digite longitude: -46.6333
5. Selecione formato de saída: DMS ou UTM
6. Clique em "Converter"

### Cenário 2: Importar e Converter Lote

1. Prepare um arquivo CSV com coordenadas
2. Acesse "Importar Arquivo"
3. Selecione o arquivo
4. Clique em "Processar"
5. Exporte os resultados

### Cenário 3: Visualizar em Mapa

1. Importe um arquivo KML/KMZ
2. Acesse "Mapa"
3. Visualize os pontos
4. Clique para obter informações
5. Calcule rotas entre pontos

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError: No module named 'pyproj'"

```bash
# Reinstalar dependências
pip install -r backend/requirements.txt
```

### Erro: "Connection refused"

Verifique se a aplicação está rodando:
```bash
curl http://localhost:5000/health
```

### Erro: "Invalid coordinate"

Valide suas coordenadas:
- Latitude: -90 a 90
- Longitude: -180 a 180

## 📝 Changelog

### v2.0.0 (19 de Março de 2026)
- ✨ Adicionado suporte completo a DD/DMS/UTM
- ✨ Novo endpoint de processamento em lote
- ✨ Melhorias na validação de coordenadas
- ✨ Documentação completa de API
- 🐛 Correções de bugs menores

### v1.0.0 (Data anterior)
- Versão inicial com conversão EPSG

## 🤝 Contribuindo

1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

## 📧 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato através do email: support@gisbim.com

## 🙏 Agradecimentos

- PyProj por transformações de coordenadas precisas
- Leaflet por visualização de mapas
- Flask por framework web robusto
- Comunidade open-source geoespacial

---

**Versão**: 2.0.0  
**Última atualização**: 19 de Março de 2026  
**Status**: Ativo e em desenvolvimento
