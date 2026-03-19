
import os
import shutil
import re

def remove_frontend_app_py():
    print("1. Removendo frontend/app.py...")
    file_path = "frontend/app.py"
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"   Arquivo {file_path} removido com sucesso.")
    else:
        print(f"   Arquivo {file_path} não encontrado, pulando remoção.")

def adjust_verify_system_py():
    print("2. Ajustando verify_system.py...")
    file_path = "verify_system.py"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.readlines()
        
        new_content = []
        removed = False
        for line in content:
            if '"frontend.app"' in line:
                print("   Removendo referência a frontend.app em verify_system.py.")
                removed = True
                continue
            new_content.append(line)
        
        if removed:
            with open(file_path, "w") as f:
                f.writelines(new_content)
            print(f"   Arquivo {file_path} atualizado com sucesso.")
        else:
            print(f"   Nenhuma referência a frontend.app encontrada em {file_path}.")
    else:
        print(f"   Arquivo {file_path} não encontrado, pulando ajuste.")

def integrate_frontend_features():
    print("3. Integrando funcionalidades de upload e desenho no frontend...")
    index_html_path = "frontend/index.html"
    backend_app_path = "backend/app.py"

    # Adicionar bibliotecas e UI no index.html
    if os.path.exists(index_html_path):
        with open(index_html_path, "r") as f:
            content = f.read()
        
        # Adicionar CSS do Leaflet.Draw
        if 'leaflet.draw.css' not in content:
            content = content.replace(
                '<!-- Custom CSS -->',
                '<!-- Leaflet Draw CSS -->\n    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css" />\n    <!-- Custom CSS -->'
            )
            print("   Adicionado Leaflet.Draw CSS ao index.html.")

        # Adicionar JS do Leaflet.Draw e Turf.js
        if 'leaflet.draw.js' not in content:
            content = content.replace(
                '<!-- Custom Scripts -->',
                '<!-- Leaflet Draw JS -->\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>\n    <!-- Turf.js -->\n    <script src="https://cdnjs.cloudflare.com/ajax/libs/Turf.js/6.5.0/turf.min.js"></script>\n    <!-- Custom Scripts -->'
            )
            print("   Adicionado Leaflet.Draw e Turf.js ao index.html.")

        # Adicionar input de upload e botões de desenho (simplificado para o exemplo)
        if 'id="fileUploadSection"' not in content:
            content = content.replace(
                '<section class="converter-section">',
                '''<section id="fileUploadSection" class="upload-section">
            <h2>Upload de Dados Espaciais</h2>
            <input type="file" id="fileInput" accept=".shp,.geojson,.json,.gpkg,.kml">
            <button onclick="uploadFile()" class="btn-upload">Upload</button>
            <div id="uploadResult" class="result-box"></div>
        </section>\n        <section class="converter-section">'''
            )
            print("   Adicionado seção de upload ao index.html.")

        with open(index_html_path, "w") as f:
            f.write(content)
        print(f"   Arquivo {index_html_path} atualizado com sucesso.")
    else:
        print(f"   Arquivo {index_html_path} não encontrado, pulando ajuste de frontend.")

    # Desenvolver o backend para upload
    if os.path.exists(backend_app_path):
        with open(backend_app_path, "r") as f:
            content = f.read()
        
        if '@app.route(\'/upload\', methods=[\'POST\'])' not in content:
            # Adicionar importação para upload.py
            content = content.replace(
                'from dotenv import load_dotenv',
                'from dotenv import load_dotenv\nfrom .upload import process_upload'
            )
            # Adicionar rota de upload
            upload_route = '''
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    result = process_upload(file)
    if 'error' in result:
        return jsonify(result), 400
    return jsonify({'message': 'Arquivo processado com sucesso', 'data': result})
'''
            content = content.replace(
                '@app.route(\'/health\', methods=[\'GET\'])',
                upload_route + '\n\n@app.route(\'/health\', methods=[\'GET\'])'
            )
            with open(backend_app_path, "w") as f:
                f.write(content)
            print(f"   Rota de upload adicionada ao {backend_app_path}.")
        else:
            print(f"   Rota de upload já existe em {backend_app_path}.")
    else:
        print(f"   Arquivo {backend_app_path} não encontrado, pulando ajuste de backend para upload.")

def complete_geoserver_config():
    print("4. Completando configuração do Geoserver no Docker Compose...")
    geoserver_docker_dir = "docker/geoserver"
    geoserver_dockerfile_path = os.path.join(geoserver_docker_dir, "Dockerfile")
    docker_compose_path = "docker/docker-compose.yml"

    # Criar pasta docker/geoserver e Dockerfile
    if not os.path.exists(geoserver_docker_dir):
        os.makedirs(geoserver_docker_dir)
        print(f"   Diretório {geoserver_docker_dir} criado.")
    
    if not os.path.exists(geoserver_dockerfile_path):
        with open(geoserver_dockerfile_path, "w") as f:
            f.write("FROM geoserver/geoserver:2.24.1\n") # Usando uma imagem oficial do GeoServer
            print(f"   Dockerfile básico criado em {geoserver_dockerfile_path}.")
    else:
        print(f"   Dockerfile já existe em {geoserver_dockerfile_path}.")

    # Ajustar docker-compose.yml para usar a imagem correta ou build context
    if os.path.exists(docker_compose_path):
        with open(docker_compose_path, "r") as f:
            content = f.read()
        
        # Ajustar a seção do geoserver para usar a imagem oficial ou o build correto
        # Assumindo que queremos usar a imagem oficial para simplificar
        if 'image: geoserver/geoserver:2.24.1' not in content:
            content = re.sub(
                r'geoserver:\n\s+build: \./geoserver',
                r'geoserver:\n    image: geoserver/geoserver:2.24.1',
                content
            )
            print("   docker-compose.yml ajustado para usar imagem oficial do GeoServer.")
        else:
            print("   docker-compose.yml já configurado para imagem oficial do GeoServer.")

        with open(docker_compose_path, "w") as f:
            f.write(content)
        print(f"   Arquivo {docker_compose_path} atualizado com sucesso.")
    else:
        print(f"   Arquivo {docker_compose_path} não encontrado, pulando ajuste.")

def create_data_uploads_folder():
    print("5. Criando a pasta data/uploads...")
    folder_path = "data/uploads"
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        # Criar um arquivo .gitkeep para garantir que a pasta seja versionada (opcional)
        with open(os.path.join(folder_path, ".gitkeep"), "w") as f:
            f.write("")
        print(f"   Pasta {folder_path} criada com .gitkeep.")
    else:
        print(f"   Pasta {folder_path} já existe.")

def define_database_schema():
    print("6. Definindo esquema do banco de dados em database/init.sql...")
    file_path = "database/init.sql"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        
        # Adicionar um esquema básico se o arquivo estiver vazio ou contiver apenas comentários
        if "CREATE TABLE" not in content:
            new_schema = '''
-- Initialize database schema for Mini QGIS Online
-- This file contains the SQL commands to set up the database structure

CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS spatial_data (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geom GEOMETRY(Geometry, 4326) -- Exemplo: Armazena geometria em WGS84
);

-- Adicione outras tabelas e índices conforme necessário para o seu projeto
'''
            with open(file_path, "w") as f:
                f.write(new_schema)
            print(f"   Esquema básico adicionado a {file_path}.")
        else:
            print(f"   Esquema de banco de dados já parece estar definido em {file_path}.")
    else:
        print(f"   Arquivo {file_path} não encontrado, pulando definição de esquema.")

def update_readme_md():
    print("7. Atualizando README.md...")
    file_path = "README.md"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        
        # Corrigir a referência a backend/converter.py
        if 'converter.py        # Módulo de conversão (utilitário)' in content:
            content = content.replace(
                'converter.py        # Módulo de conversão (utilitário)',
                'spatial.py          # Módulo de conversão (utilitário)'
            )
            with open(file_path, "w") as f:
                f.write(content)
            print(f"   Arquivo {file_path} atualizado com sucesso.")
        else:
            print(f"   Nenhuma referência incorreta a backend/converter.py encontrada em {file_path}.")
    else:
        print(f"   Arquivo {file_path} não encontrado, pulando atualização do README.md.")

def main():
    print("Iniciando script de correção do projeto Mini-QGIS-Online...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    remove_frontend_app_py()
    adjust_verify_system_py()
    integrate_frontend_features()
    complete_geoserver_config()
    create_data_uploads_folder()
    define_database_schema()
    update_readme_md()
    
    print("Script de correção concluído.")

if __name__ == "__main__":
    main()
