# Use uma imagem base Python oficial
FROM python:3.9-slim-buster

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Instala as dependências do sistema necessárias para geopandas, rasterio e pyproj
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    libproj-dev \
    gdal-bin \
    libgeos-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Define variáveis de ambiente para o GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copia o arquivo de requisitos e instala as dependências
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Define a variável de ambiente para o Flask
ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

# Expõe a porta que o Flask vai usar
EXPOSE 5000

# Comando para iniciar a aplicação Flask
CMD ["python", "backend/app.py"]
