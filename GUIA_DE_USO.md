# Guia de Uso do Software Mini-QGIS-Online

## Introdução

Bem-vindo ao **Mini-QGIS-Online**, uma ferramenta GIS web projetada para simplificar a conversão de coordenadas, visualização de mapas interativos, filtragem de dados espaciais e exportação em diversos formatos. Este guia detalha como utilizar todas as funcionalidades do software, desde a configuração inicial até as operações avançadas.

## 1. Instalação e Configuração

Para começar a usar o Mini-QGIS-Online, siga os passos abaixo para configurar o ambiente e iniciar a aplicação:

### 1.1. Clonar o Repositório

Primeiro, clone o projeto do GitHub para o seu ambiente local:

```bash
git clone https://github.com/solutionstechnologyinformation-beep/Mini-QGIS-Online.git
cd Mini-QGIS-Online
```

### 1.2. Configurar Ambiente Virtual e Dependências

É altamente recomendável criar um ambiente virtual para isolar as dependências do projeto:

```bash
# Criar ambiente virtual (Linux/macOS)
python3 -m venv venv
source venv/bin/activate

# Criar ambiente virtual (Windows)
python -m venv venv
venc\Scripts\activate

# Instalar dependências do backend
pip install -r backend/requirements.txt
```

### 1.3. Iniciar a Aplicação

Com as dependências instaladas, você pode iniciar o servidor Flask do backend:

```bash
cd backend
python app.py
```

A aplicação estará acessível em seu navegador através do endereço: `http://localhost:5000`.

### 1.4. Configuração Docker (Opcional)

Para um ambiente de desenvolvimento mais completo, incluindo PostGIS e GeoServer, utilize o Docker Compose:

```bash
cd docker
docker-compose up --build
```

## 2. Visão Geral da Interface

A interface do Mini-QGIS-Online é dividida em seções principais:

-   **Mapa Interativo**: Exibe o mapa base (OpenStreetMap) e permite a interação para coleta de pontos.
-   **Conversor de Coordenadas**: Ferramenta para converter coordenadas entre diferentes sistemas de referência.
-   **Upload de Dados Espaciais**: Permite o envio de arquivos geoespaciais para visualização.
-   **Exportação e Filtros**: Seção para exportar dados e aplicar filtros visuais aos pontos no mapa.

## 3. Conversão de Coordenadas

O sistema oferece flexibilidade na entrada e conversão de coordenadas:

### 3.1. Seleção do Modo de Entrada

Utilize o seletor **"Modo de Entrada"** para escolher entre:

-   **Graus Decimais (DD)**: Entrada simples de longitude (X) e latitude (Y).
-   **Graus Minutos Segundos (DMS)**: Campos separados para graus, minutos, segundos e direção (N/S para latitude, E/W para longitude).
-   **UTM**: Entrada de Easting (X) e Northing (Y) para coordenadas projetadas.

### 3.2. Realizando a Conversão

1.  Insira os valores de X e Y (ou G, M, S e Direção para DMS) no modo de entrada desejado.
2.  Selecione o **Sistema de Origem (SRC)** e o **Sistema de Destino (DST)** (códigos EPSG, como 4326 para WGS84 ou 31983 para UTM 23S).
3.  Clique no botão **"Converter"** para visualizar o resultado.

## 4. Coleta, Filtragem e Personalização de Pontos

O mapa interativo permite coletar pontos e personalizá-los visualmente:

### 4.1. Coleta de Pontos

Clique em qualquer lugar do mapa para adicionar um ponto. Cada ponto adicionado é armazenado internamente e pode ser categorizado.

### 4.2. Filtragem e Cores

Na seção **"Exportação e Filtros"**:

1.  **Tipo de Ponto**: Selecione uma categoria para o ponto (ex: Bordo, Manilha, Pé, Crista, ou Ponto padrão).
2.  **Cor**: Escolha uma cor para o tipo de ponto selecionado usando o seletor de cores.
3.  Clique em **"Aplicar Filtro/Cor"** para atualizar a visualização dos pontos no mapa.

### 4.3. Ligação de Pontos

Para conectar pontos de uma mesma categoria:

1.  Selecione o **"Tipo de Ponto"** desejado (ou "Todos" para ligar todos os pontos).
2.  Clique em **"Ligar Pontos"**. Uma linha será desenhada conectando os pontos na ordem em que foram adicionados.

### 4.4. Fechar Polígono (Mancha)

Para criar um polígono a partir de pontos:

1.  Selecione o **"Tipo de Ponto"** desejado (ou "Todos").
2.  Certifique-se de ter pelo menos três pontos adicionados.
3.  Clique em **"Fechar Polígono (Mancha)"**. Um polígono preenchido será criado, conectando o último ponto ao primeiro.

## 5. Exportação de Dados

Após coletar e personalizar seus pontos, você pode exportá-los em diversos formatos:

1.  Na seção **"Exportação e Filtros"**, selecione o **"Formato de Exportação"** desejado (TXT, CSV, KML, DXF).
2.  Clique em **"Exportar Pontos"**. O arquivo será gerado e um download será iniciado automaticamente.

## 6. Upload de Dados Espaciais

A seção **"Upload de Dados Espaciais"** permite carregar arquivos geoespaciais para visualização no mapa:

1.  Clique em **"Escolher arquivo"** e selecione um arquivo nos formatos `.shp`, `.geojson`, `.json`, `.gpkg` ou `.kml`.
2.  Clique em **"Upload"**. O conteúdo do arquivo será processado e exibido no mapa.

## 7. Solução de Problemas

-   **Problemas de Conexão**: Verifique se o servidor Flask está em execução (`python app.py` na pasta `backend`).
-   **Erros de Conversão**: Certifique-se de que os códigos EPSG de origem e destino estão corretos e que os valores de coordenadas são válidos.
-   **Funcionalidades Inoperantes**: Verifique o console do navegador (F12) para mensagens de erro JavaScript e o terminal do servidor Flask para erros de backend.

## Conclusão

Este guia cobriu as principais funcionalidades do Mini-QGIS-Online. Explore as ferramentas e utilize-as para suas necessidades de visualização e processamento de dados geoespaciais. Para suporte adicional ou sugestões, consulte a documentação do projeto no GitHub.

**Autor:** Manus AI
**Data:** 18 de Março de 2026
