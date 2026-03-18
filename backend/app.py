import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pyproj import Transformer
from werkzeug.utils import secure_filename
from backend.file_processor import process_coordinate_file, format_results_for_export
from backend.upload import process_upload, allowed_file as allowed_spatial_file
import pandas as pd # Para lidar com CSV/TXT de forma robusta
from dotenv import load_dotenv
from backend.epsg_codes import EPSG_CODES

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Configurações
PORT = int(os.getenv('PORT', 5000))
HOST = os.getenv('HOST', '0.0.0.0')
FLASK_ENV = os.getenv('FLASK_ENV', 'development')


@app.route('/')
def index():
    """Serve o arquivo index.html do frontend."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/convert', methods=['POST'])
def convert():
    """Converte coordenadas entre diferentes sistemas de referência EPSG."""
    try:
        # Validar se o JSON foi recebido
        if not request.json:
            return jsonify({'error': 'Nenhum dado JSON fornecido'}), 400

        # Extrair dados
        data = request.json
        required_fields = ['x', 'y', 'src', 'dst']
        
        # Validar campos obrigatórios
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Campo obrigatório faltando: {field}'}), 400

        # Converter para tipos apropriados
        try:
            x = float(data['x'])
            y = float(data['y'])
        except (ValueError, TypeError):
            return jsonify({'error': 'Coordenadas x e y devem ser números válidos'}), 400

        src = str(data['src']).strip()
        dst = str(data['dst']).strip()

        # Validar se src e dst não estão vazios
        if not src or not dst:
            return jsonify({'error': 'Sistemas de referência (src e dst) não podem estar vazios'}), 400

        # Validar se src e dst são iguais
        if src == dst:
            return jsonify({
                'x': x,
                'y': y,
                'message': 'Sistemas de referência são iguais, nenhuma conversão necessária'
            })

        # Criar transformador
        try:
            transformer = Transformer.from_crs(
                f"EPSG:{src}",
                f"EPSG:{dst}",
                always_xy=True
            )
        except Exception as e:
            return jsonify({'error': f'Sistema de referência inválido: {str(e)}'}), 400

        # Realizar transformação
        try:
            new_x, new_y = transformer.transform(x, y)
        except Exception as e:
            return jsonify({'error': f'Erro ao transformar coordenadas: {str(e)}'}), 400

        return jsonify({
            'x': new_x,
            'y': new_y,
            'src': src,
            'dst': dst
        })

    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500


@app.route('/convert_file', methods=['POST'])
def convert_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']
        src = request.form.get('src')
        dst = request.form.get('dst')

        if not file or not src or not dst:
            return jsonify({'error': 'Arquivo, sistema de origem ou destino não fornecidos'}), 400

        if not (src.isdigit() and dst.isdigit()):
            return jsonify({'error': 'Códigos EPSG de origem e destino devem ser numéricos'}), 400

        file_content = file.read().decode('utf-8')
        
        # Usar pandas para ler o arquivo de forma mais flexível
        # Tentar inferir o separador
        try:
            df = pd.read_csv(io.StringIO(file_content), sep=None, engine='python', header=None)
        except Exception as e:
            return jsonify({'error': f'Erro ao ler o arquivo: {str(e)}. Verifique o formato (CSV/TXT).'}), 400

        # Assumir que as coordenadas X e Y estão nas duas primeiras colunas
        if df.shape[1] < 2:
            return jsonify({'error': 'O arquivo deve ter pelo menos duas colunas para as coordenadas X e Y'}), 400

        results = []
        for index, row in df.iterrows():
            try:
                x = float(row[0])
                y = float(row[1])
                converted_x, converted_y = convert(x, y, src, dst)
                results.append({"original_x": x, "original_y": y, "converted_x": converted_x, "converted_y": converted_y})
            except (ValueError, IndexError):
                continue # Ignorar linhas mal formatadas

        if not results:
            return jsonify({'error': 'Nenhuma coordenada válida encontrada ou convertida no arquivo'}), 400

        # Retornar os resultados em um formato que o frontend possa processar ou baixar
        # Por enquanto, retornaremos como JSON. O frontend pode então gerar o download.
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor ao processar arquivo: {str(e)}'}), 500

@app.route('/upload_spatial_file', methods=['POST'])
def upload_spatial_file():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        file = request.files['file']
        if not allowed_spatial_file(file.filename):
            return jsonify({'error': 'Tipo de arquivo não permitido. Apenas KMZ, KML, SHP, GeoJSON, GPKG.'}), 400

        result = process_upload(file)

        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor ao processar arquivo espacial: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de verificação de saúde da API."""
    return jsonify({'status': 'ok', 'environment': FLASK_ENV})


@app.errorhandler(404)
def not_found(error):
    """Tratador para erros 404."""
    return jsonify({'error': 'Endpoint não encontrado'}), 404


@app.route("/epsg_codes", methods=["GET"])
def get_epsg_codes():
    """Retorna os códigos EPSG disponíveis."""
    return jsonify(EPSG_CODES)

@app.errorhandler(500)
def internal_error(error):
    """Tratador para erros 500."""
    return jsonify({'error': 'Erro interno do servidor'}), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=(FLASK_ENV == 'development'))
