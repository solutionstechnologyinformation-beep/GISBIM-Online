# Troubleshooting - GISBIM Online v2.0

## Erros Comuns e Soluções

### 1. ModuleNotFoundError: No module named 'flask_cors'

**Erro Completo:**
```
ModuleNotFoundError: No module named 'flask_cors'
```

**Solução:**
```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Ou instalar individualmente
pip install Flask flask-cors pyproj python-dotenv werkzeug gunicorn
```

---

### 2. ImportError: attempted relative import with no known parent package

**Erro Completo:**
```
ImportError: attempted relative import with no known parent package
```

**Causa:** Executando `python app.py` diretamente do diretório backend

**Solução:**
```bash
# Executar do diretório backend
cd backend
python app.py

# Ou do diretório raiz
python -m backend.app
```

---

### 3. ModuleNotFoundError: No module named 'geopandas'

**Erro Completo:**
```
ModuleNotFoundError: No module named 'geopandas'
```

**Causa:** Versão antiga do `upload.py` que requer geopandas

**Solução:**
```bash
# O projeto agora usa upload_simple.py que não requer geopandas
# Verificar que está usando a versão corrigida
git pull origin main

# Reinstalar dependências
pip install -r backend/requirements.txt
```

---

### 4. Port already in use

**Erro Completo:**
```
Address already in use
```

**Solução:**
```bash
# Usar porta diferente
cd backend
python app.py --port 5001

# Ou matar processo na porta 5000
lsof -i :5000
kill -9 <PID>
```

---

### 5. Permission denied ao criar diretório

**Erro Completo:**
```
PermissionError: [Errno 13] Permission denied: '../data/uploads'
```

**Solução:**
```bash
# Criar diretório manualmente
mkdir -p data/uploads

# Ou executar com permissões apropriadas
chmod 755 data/
```

---

### 6. No module named 'upload'

**Erro Completo:**
```
ModuleNotFoundError: No module named 'upload'
```

**Causa:** Arquivo `upload_simple.py` não encontrado

**Solução:**
```bash
# Verificar que o arquivo existe
ls -la backend/upload_simple.py

# Se não existir, fazer pull do GitHub
git pull origin main
```

---

## Verificação de Setup

### Verificar Instalação

```bash
# Verificar Python
python3 --version

# Verificar pip
pip --version

# Verificar dependências instaladas
pip list | grep -E "Flask|pyproj|werkzeug"
```

### Testar Imports

```bash
# No diretório backend
cd backend
python3 << EOF
try:
    from app import app
    print("✓ App importado com sucesso")
except Exception as e:
    print(f"✗ Erro: {e}")
EOF
```

### Testar Endpoints

```bash
# Em um terminal, iniciar a aplicação
cd backend
python app.py

# Em outro terminal, testar
curl http://localhost:5000/health
```

---

## Problemas no Codespaces

### Erro: "bash: python3: command not found"

**Solução:**
```bash
# Usar python em vez de python3
python --version
python -m pip install -r backend/requirements.txt
```

### Erro: "Permission denied" ao executar script

**Solução:**
```bash
# Dar permissão de execução
chmod +x QUICK_START_CODESPACES.sh

# Executar
bash QUICK_START_CODESPACES.sh
```

### Erro: "venv not found"

**Solução:**
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar (Linux/macOS)
source venv/bin/activate

# Ativar (Windows)
venv\Scripts\activate

# Instalar dependências
pip install -r backend/requirements.txt
```

---

## Problemas de Conversão de Coordenadas

### Erro: "Latitude deve estar entre -90 e 90"

**Causa:** Coordenada fora do intervalo válido

**Solução:**
```bash
# Verificar coordenadas
# Latitude: -90 a 90
# Longitude: -180 a 180

# Exemplo correto
curl -X POST http://localhost:5000/convert/dd-to-dms \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'
```

### Erro: "Zona UTM deve estar entre 1 e 60"

**Causa:** Zona UTM inválida

**Solução:**
```bash
# Zona UTM válida: 1-60
# Exemplo correto
curl -X POST http://localhost:5000/convert/utm-to-dd \
  -H "Content-Type: application/json" \
  -d '{"zone": 23, "easting": 324123.45, "northing": 7397456.78, "hemisphere": "S"}'
```

---

## Problemas de Arquivo

### Erro: "Tipo de arquivo inválido"

**Causa:** Extensão de arquivo não suportada

**Solução:**
```bash
# Formatos suportados: txt, csv, kml, kmz, json, geojson
# Verificar extensão do arquivo
# Usar um dos formatos suportados
```

### Erro: "Nenhum arquivo KML encontrado no KMZ"

**Causa:** Arquivo KMZ não contém KML

**Solução:**
```bash
# Verificar conteúdo do KMZ
unzip -l arquivo.kmz

# KMZ deve conter pelo menos um arquivo .kml
```

---

## Debug e Logs

### Ativar Debug Mode

```bash
# No arquivo backend/app.py, alterar
if __name__ == '__main__':
    app.run(debug=True)  # Ativar debug

# Executar
python app.py
```

### Ver Logs Detalhados

```bash
# Com verbose
python app.py -v

# Ou redirecionar para arquivo
python app.py > app.log 2>&1
tail -f app.log
```

---

## Verificação Final

Antes de fazer deploy, execute:

```bash
# 1. Verificar sintaxe
python3 -m py_compile backend/app.py backend/spatial.py backend/upload_simple.py

# 2. Verificar imports
cd backend && python3 -c "from app import app; print('✓ OK')"

# 3. Testar health check
curl http://localhost:5000/health

# 4. Testar conversão
curl -X POST http://localhost:5000/convert/dd-to-dms \
  -H "Content-Type: application/json" \
  -d '{"latitude": -23.5505, "longitude": -46.6333}'
```

---

## Suporte

Se o problema persistir:

1. Verificar logs: `tail -f app.log`
2. Abrir issue no GitHub: https://github.com/solutionstechnologyinformation-beep/GISBIM-Online/issues
3. Incluir:
   - Versão do Python
   - Versão do Flask
   - Mensagem de erro completa
   - Passos para reproduzir

---

**Última atualização**: 19 de Março de 2026  
**Versão**: 2.0.0
