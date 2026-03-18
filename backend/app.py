import os
import io
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from pyproj import Transformer
from backend.spatial import dms_to_dd, dd_to_dms, convert
from werkzeug.utils import secure_filename
from backend.upload import process_upload, allowed_file as allowed_spatial_file
import pandas as pd # Para lidar com CSV/TXT de forma robusta
from dotenv import load_dotenv
from backend.epsg_codes import EPSG_CODES
from backend.exporters import export_to_kml, export_to_dxf

# Carregar variáveis de ambiente
load_dotenv()

app = Flask(__name__, static_folder=\'../frontend\', static_url_path=\'\')
CORS(app)

# Configurações
PORT = int(os.getenv(\'PORT\', 5000))
HOST = os.getenv(\'HOST\', \'0.0.0.0\')
FLASK_ENV = os.getenv(\'FLASK_ENV\', \'development\')


@app.route(\'/\')
def index():
    """Serve o arquivo index.html do frontend."""
    return send_from_directory(app.static_folder, \'index.html\')


@app.route(\'/convert\', methods=[\'POST\'])
def convert_single():
    """Converte coordenadas entre diferentes sistemas de referência EPSG."""
    try:
        # Validar se o JSON foi recebido
        if not request.json:
            return jsonify({\'error\': \'Nenhum dado JSON fornecido\'}), 400

        # Extrair dados
        data = request.json
        required_fields = ["src", "dst"]
        
        # Validar campos obrigatórios
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Campo obrigatório faltando: {field}"}), 400

        input_format = data.get("input_format", "dd") # \'dd\' para Graus Decimais, \'dms\' para GMS
        output_format = data.get("output_format", "dd") # \'dd\' para Graus Decimais, \'dms\' para GMS

        x, y = None, None

        if input_format == "dd":
            try:
                x = float(data["x"])
                y = float(data["y"])
            except (ValueError, TypeError):
                return jsonify({"error": "Coordenadas x e y devem ser números válidos para Graus Decimais"}), 400
        elif input_format == "dms":
            try:
                # Espera-se que o frontend envie os componentes DMS separados
                x_deg = float(data["x_deg"])
                x_min = float(data["x_min"])
                x_sec = float(data["x_sec"])
                x_dir = data["x_dir"]

                y_deg = float(data["y_deg"])
                y_min = float(data["y_min"])
                y_sec = float(data["y_sec"])
                y_dir = data["y_dir"]

                x = dms_to_dd(x_deg, x_min, x_sec, x_dir)
                y = dms_to_dd(y_deg, y_min, y_sec, y_dir)
            except (ValueError, TypeError, KeyError):
                return jsonify({"error": "Componentes de Graus, Minutos, Segundos (DMS) inválidos ou faltando"}), 400
        else:
            return jsonify({"error": "Formato de entrada inválido. Use \'dd\' ou \'dms\'."}), 400

        src = str(data["src"]).strip()
        dst = str(data["dst"]).strip()

        # Validar se src e dst não estão vazios
        if not src or not dst:
            return jsonify({\'error\': \'Sistemas de referência (src e dst) não podem estar vazios\'}), 400

        # Validar se src e dst são iguais
        if src == dst:
            # Se os sistemas são iguais, apenas retorna a coordenada no formato de saída solicitado
            if output_format == "dms":
                new_x_dms_deg, new_x_dms_min, new_x_dms_sec, new_x_dms_is_neg = dd_to_dms(x)
                new_y_dms_deg, new_y_dms_min, new_y_dms_sec, new_y_dms_is_neg = dd_to_dms(y)
                return jsonify({
                    "x_deg": new_x_dms_deg,
                    "x_min": new_x_dms_min,
                    "x_sec": round(new_x_dms_sec, 3),
                    "x_dir": "W" if new_x_dms_is_neg else "E",
                    "y_deg": new_y_dms_deg,
                    "y_min": new_y_dms_min,
                    "y_sec": round(new_y_dms_sec, 3),
                    "y_dir": "S" if new_y_dms_is_neg else "N",
                    "src": src,
                    "dst": dst,
                    "output_format": "dms"
                })
            else:
                return jsonify({
                    "x": x,
                    "y": y,
                    "src": src,
                    "dst": dst,
                    "output_format": "dd"
                })

        # Realizar transformação
        new_x, new_y = convert(x, y, src, dst)

        if output_format == "dms":
            new_x_dms_deg, new_x_dms_min, new_x_dms_sec, new_x_dms_is_neg = dd_to_dms(new_x)
            new_y_dms_deg, new_y_dms_min, new_y_dms_sec, new_y_dms_is_neg = dd_to_dms(new_y)
            return jsonify({
                "x_deg": new_x_dms_deg,
                "x_min": new_x_dms_min,
                "x_sec": round(new_x_dms_sec, 3),
                "x_dir": "W" if new_x_dms_is_neg else "E",
                "y_deg": new_y_dms_deg,
                "y_min": new_y_dms_min,
                "y_sec": round(new_y_dms_sec, 3),
                "y_dir": "S" if new_y_dms_is_neg else "N",
                "src": src,
                "dst": dst,
                "output_format": "dms"
            })
        else:
            return jsonify({
                "x": new_x,
                "y": new_y,
                "src": src,
                "dst": dst,
                "output_format": "dd"
            })

    except Exception as e:
        return jsonify({\'error\': f\'Erro interno do servidor: {str(e)}\'}), 500


@app.route(\'/convert_file\', methods=[\'POST\'])
def convert_file():
    try:
        if \'file\' not in request.files:
            return jsonify({\'error\': \'Nenhum arquivo enviado\'}), 400

        file = request.files["file"]
        src = request.form.get("src")
        dst = request.form.get("dst")
        input_file_format = request.form.get("input_file_format", "xy") # \'xy\' ou \'pnec\'

        if not file or not src or not dst:
            return jsonify({"error": "Arquivo, sistema de origem ou destino não fornecidos"}), 400

        if not (src.isdigit() and dst.isdigit()):
            return jsonify({"error": "Códigos EPSG de origem e destino devem ser numéricos"}), 400

        file_content = file.read().decode("utf-8")
        
        try:
            # Tentar ler o arquivo com pandas, inferindo o separador e sem cabeçalho inicialmente
            df = pd.read_csv(io.StringIO(file_content), sep=None, engine=\'python\', header=None)
        except Exception as e:
            return jsonify({\'error\': f\'Erro ao ler o arquivo: {str(e)}. Verifique o formato (CSV/TXT).\'}), 400

        results = []
        try:
            transformer = Transformer.from_crs(
                f"EPSG:{src}",
                f"EPSG:{dst}",
                always_xy=True
            )
        except Exception as e:
            return jsonify({\'error\': f\'Sistema de referência inválido: {str(e)}\'}), 400

        if input_file_format == "pnec": # Ponto, N, E, Cota, Descrição
            # Heurística para detectar cabeçalho: se a primeira linha não for numérica nas colunas de coord
            start_row = 0
            # Verifica se as colunas N (índice 1) e E (índice 2) da primeira linha não são numéricas
            if df.shape[1] > 2 and (pd.to_numeric(df.iloc[0, 1], errors=\'coerce\').isna().all() or pd.to_numeric(df.iloc[0, 2], errors=\'coerce\').isna().all()):
                 start_row = 1

            for index in range(start_row, len(df)):
                row = df.iloc[index]
                try:
                    # N (Latitude) é a segunda coluna (índice 1), E (Longitude) é a terceira (índice 2)
                    y = float(row[1]) 
                    x = float(row[2]) 
                    ponto = row[0]
                    cota = row[3] if len(row) > 3 else None
                    descricao = row[4] if len(row) > 4 else None
                except (ValueError, IndexError, TypeError):
                    continue # Ignorar linhas mal formatadas ou com valores não numéricos
                
                try:
                    converted_x, converted_y = transformer.transform(x, y)
                    results.append({
                        "ponto": ponto,
                        "original_y": y, 
                        "original_x": x, 
                        "cota": cota,
                        "descricao": descricao,
                        "converted_y": converted_y, 
                        "converted_x": converted_x
                    })
                except Exception:
                    continue # Ignorar linhas com erro de transformação
        else: # Formato padrão (X, Y nas duas primeiras colunas)
            # Heurística para detectar cabeçalho
            start_row = 0
            # Verifica se as colunas X (índice 0) e Y (índice 1) da primeira linha não são numéricas
            if df.shape[1] > 1 and (pd.to_numeric(df.iloc[0, 0], errors=\'coerce\').isna().all() or pd.to_numeric(df.iloc[0, 1], errors=\'coerce\').isna().all()):
                 start_row = 1

            for index in range(start_row, len(df)):
                row = df.iloc[index]
                try:
                    x = float(row[0])
                    y = float(row[1])
                except (ValueError, IndexError, TypeError):
                    continue # Ignorar linhas mal formatadas ou com valores não numéricos
                
                try:
                    converted_x, converted_y = transformer.transform(x, y)
                    results.append({"original_x": x, "original_y": y, "converted_x": converted_x, "converted_y": converted_y})
                except Exception:
                    continue # Ignorar linhas com erro de transformação

        if not results:
            return jsonify({\'error\': \'Nenhuma coordenada válida encontrada ou convertida no arquivo\'}), 400

        return jsonify(results)

    except Exception as e:
        return jsonify({\'error\': f\'Erro interno do servidor ao processar arquivo: {str(e)}\'}), 500

@app.route(\'/upload_spatial_file\', methods=[\'POST\'])
def upload_spatial_file():
    try:
        if \'file\' not in request.files:
            return jsonify({\'error\': \'Nenhum arquivo enviado\'}), 400

        file = request.files[\'file\']
        if not allowed_spatial_file(file.filename):
            return jsonify({\'error\': \'Tipo de arquivo não permitido. Apenas KMZ, KML, SHP, GeoJSON, GPKG.\'}), 400

        result = process_upload(file)

        if \'error\' in result:
            return jsonify(result), 400
        
        return jsonify(result)

    except Exception as e:
        return jsonify({\'error\': f\'Erro interno do servidor ao processar arquivo espacial: {str(e)}\'}), 500

@app.route(\'/health\', methods=[\'GET\'])
def health():
    """Endpoint de verificação de saúde da API."""
    return jsonify({\'status\': \'ok\', \'environment\': FLASK_ENV})


@app.errorhandler(404)
def not_found(error):
    """Tratador para erros 404."""
    return jsonify({\'error\': \'Endpoint não encontrado\'}), 404

@app.route(\"/epsg_codes\", methods=[\"GET\"])
def get_epsg_codes():
    """Retorna os códigos EPSG disponíveis."""
    return jsonify(EPSG_CODES)

@app.route(\"/export_kml\", methods=[\"POST\"])
def export_kml_route():
    try:
        data = request.json.get("data")
        input_file_format = request.json.get("input_file_format")
        if not data:
            return jsonify({"error": "Nenhum dado para exportar"}), 400
        kml_data = export_to_kml(data, input_file_format)
        return Response(kml_data, mimetype="application/vnd.google-earth.kml+xml", headers={"Content-disposition": "attachment; filename=coordenadas_convertidas.kml"})
    except Exception as e:
        return jsonify({"error": f"Erro ao exportar KML: {str(e)}"}), 500

@app.route(\"/export_dxf\", methods=[\"POST\"])
def export_dxf_route():
    try:
        data = request.json.get("data")
        input_file_format = request.json.get("input_file_format")
        if not data:
            return jsonify({"error": "Nenhum dado para exportar"}), 400
        dxf_data = export_to_dxf(data, input_file_format)
        return Response(dxf_data, mimetype="application/dxf", headers={"Content-disposition": "attachment; filename=coordenadas_convertidas.dxf"})
    except Exception as e:
        return jsonify({"error": f"Erro ao exportar DXF: {str(e)}"}), 500app.errorhandler(500)
def internal_error(error):
    """Tratador para erros 500."""
    return jsonify({\'error\': \'Erro interno do servidor\'}), 500


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=(FLASK_ENV == \'development\'))
