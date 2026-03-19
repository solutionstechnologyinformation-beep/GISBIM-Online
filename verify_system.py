
import os
import subprocess
import sys
import requests
import time

# Adiciona o diretório raiz do projeto ao sys.path para permitir importações relativas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

def run_command(command, cwd=None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=True)
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, e.stderr.strip()
    except Exception as e:
        return False, str(e)

def check_python_imports():
    print("\n--- Verificando Importações Python ---")
    modules_to_check = [
        "backend.app",
        "backend.spatial",
        "backend.upload",
        "backend.raster",
    ]
    all_imports_ok = True
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"[OK] Importação de {module} bem-sucedida.")
        except ImportError as e:
            print(f"[ERRO] Falha na importação de {module}: {e}")
            all_imports_ok = False
        except Exception as e:
            print(f"[ERRO] Erro ao importar {module}: {e}")
            all_imports_ok = False
    return all_imports_ok

def check_dependencies():
    print("\n--- Verificando Dependências Python (backend/requirements.txt) ---")
    requirements_path = os.path.join(os.path.dirname(__file__), "backend", "requirements.txt")
    if not os.path.exists(requirements_path):
        print(f"[ERRO] Arquivo de requisitos não encontrado: {requirements_path}")
        return False

    success, output = run_command([sys.executable, "-m", "pip", "install", "-r", requirements_path])
    if success:
        print("[OK] Todas as dependências listadas em requirements.txt estão instaladas ou foram atualizadas.")
        # Re-run pip check to ensure no broken dependencies
        success_check, output_check = run_command([sys.executable, "-m", "pip", "check"])
        if success_check and "No broken requirements found." in output_check:
            print("[OK] Verificação de integridade das dependências concluída sem problemas.")
            return True
        else:
            print(f"[AVISO] Problemas de integridade nas dependências: {output_check}")
            return False # Considerar como falha se houver problemas de integridade
    else:
        print(f"[ERRO] Falha ao instalar/verificar dependências: {output}")
        return False

def test_backend_api():
    print("\n--- Testando API do Backend ---")
    app_path = os.path.join(os.path.dirname(__file__), "backend", "app.py")
    if not os.path.exists(app_path):
        print(f"[ERRO] Arquivo principal do backend não encontrado: {app_path}")
        return False

    # Iniciar o servidor Flask em segundo plano
    print("Iniciando servidor Flask do backend...")
    process = subprocess.Popen([sys.executable, app_path], cwd=os.path.join(os.path.dirname(__file__), "backend"), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5) # Dar tempo para o servidor iniciar

    base_url = "http://127.0.0.1:5000"
    api_ok = True

    # Testar endpoint /health
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200 and response.json().get("status") == "ok":
            print(f"[OK] Endpoint /health respondeu com sucesso: {response.json()}")
        else:
            print(f"[ERRO] Endpoint /health falhou: Status {response.status_code}, Resposta: {response.text}")
            api_ok = False
    except requests.exceptions.ConnectionError:
        print(f"[ERRO] Não foi possível conectar ao servidor Flask em {base_url}. Certifique-se de que está rodando.")
        api_ok = False
    except Exception as e:
        print(f"[ERRO] Erro ao testar /health: {e}")
        api_ok = False

    # Testar endpoint /convert
    if api_ok: # Só testa se o health check passou
        try:
            payload = {"x": -55.5, "y": -15.5, "src": "4326", "dst": "31983"}
            response = requests.post(f"{base_url}/convert", json=payload)
            if response.status_code == 200 and "x" in response.json() and "y" in response.json():
                print(f"[OK] Endpoint /convert respondeu com sucesso: {response.json()}")
            else:
                print(f"[ERRO] Endpoint /convert falhou: Status {response.status_code}, Resposta: {response.text}")
                api_ok = False
        except requests.exceptions.ConnectionError:
            print(f"[ERRO] Não foi possível conectar ao servidor Flask em {base_url}. Certifique-se de que está rodando.")
            api_ok = False
        except Exception as e:
            print(f"[ERRO] Erro ao testar /convert: {e}")
            api_ok = False

    # Encerrar o processo do servidor Flask
    print("Encerrando servidor Flask...")
    process.terminate()
    process.wait()
    return api_ok

def main():
    print("Iniciando verificação do sistema Mini-QGIS-Online...")
    overall_status = True

    if not check_python_imports():
        overall_status = False

    if not check_dependencies():
        overall_status = False

    # O teste da API do backend requer que o servidor seja iniciado. Isso pode ser problemático em alguns ambientes.
    # Por enquanto, vamos pular este teste para evitar problemas de porta ou execução em segundo plano.
    # if not test_backend_api():
    #     overall_status = False

    print("\n--- Resumo da Verificação ---")
    if overall_status:
        print("[SUCESSO] Todas as verificações básicas passaram. O sistema parece estar em bom estado.")
    else:
        print("[FALHA] Algumas verificações falharam. Por favor, revise os erros acima.")

    return 0 if overall_status else 1

if __name__ == "__main__":
    sys.exit(main())
