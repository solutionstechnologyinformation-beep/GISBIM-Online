# Use uma imagem base Python oficial mais recente e robusta
FROM python:3.11-slim-bookworm

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

# Define variáveis de ambiente essenciais para o GDAL e PROJ
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV PROJ_LIB=/usr/share/proj

# Copia o arquivo de requisitos e instala as dependências
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copia o restante do código da aplicação
COPY . .

# Garante que o diretório atual esteja no PYTHONPATH
ENV PYTHONPATH=/app

# Define variáveis de ambiente para o Flask
ENV FLASK_APP=backend/app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PORT=5000

# Expõe a porta que o Flask vai usar
EXPOSE 5000

# Comando para iniciar a aplicação Flask usando Gunicorn
# Usamos 'backend.app:app' porque o diretório 'backend' é um pacote (tem __init__.py)
# e estamos no diretório /app (WORKDIR)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "backend.app:app"]
