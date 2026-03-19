# Mini QGIS Online

Uma ferramenta GIS web simples e intuitiva para conversão de coordenadas e visualização de mapas interativos.

## ✨ Funcionalidades

- **Mapa Interativo**: Visualize mapas com Leaflet e OpenStreetMap
- **Conversão de Coordenadas**: Converta entre diferentes sistemas de referência EPSG
- **Suporte a Múltiplos EPSG**: WGS84, SIRGAS2000, UTM 23S e mais
- **Precisão Geodésica**: Utiliza PyProj para transformações precisas
- **Interface Responsiva**: Funciona em desktop, tablet e mobile
- **API RESTful**: Backend Flask com endpoints bem documentados

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **Flask-CORS**: Suporte a CORS
- **PyProj**: Transformações de coordenadas geodésicas
- **Python 3.8+**

### Frontend
- **HTML5**: Estrutura semântica
- **CSS3**: Design responsivo
- **JavaScript**: Lógica do cliente
- **Leaflet**: Biblioteca de mapas
- **OpenStreetMap**: Dados de mapas

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Git

## 🚀 Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/solutionstechnologyinformation-beep/Mini-QGIS-Online.git
cd Mini-QGIS-Online
```

### 2. Criar Ambiente Virtual (Recomendado)

```bash
# Linux/macOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scriptsctivate
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

1. **Visualizar Mapa**: O mapa é carregado automaticamente mostrando o Brasil
2. **Obter Coordenadas**: Clique no mapa para obter as coordenadas do ponto
3. **Converter Coordenadas**:
   - Preencha os campos X (Longitude) e Y (Latitude)
   - Selecione o sistema de origem (Origem)
   - Selecione o sistema de destino (Destino)
   - Clique em "Converter"

### API REST

#### Endpoint: POST `/convert`

**Request:**
```json
{
  "x": -55.5,
  "y": -15.5,
  "src": "4326",
  "dst": "31983"
}
```

**Response (Sucesso):**
```json
{
  "x": 500000.0,
  "y": 8280000.0,
  "src": "4326",
  "dst": "31983"
}
```

**Response (Erro):**
```json
{
  "error": "Descrição do erro"
}
```

#### Endpoint: GET `/health`

Verifica o status da API.

**Response:**
```json
{
  "status": "ok",
  "environment": "development"
}
```

## 🔧 Sistemas de Referência Suportados

| Código EPSG | Nome | Descrição |
|-------------|------|-----------|
| 4326 | WGS84 | Sistema de referência global padrão |
| 4674 | SIRGAS2000 | Sistema de referência para América do Sul |
| 31983 | UTM 23S | Projeção UTM Zona 23 Sul |

Para adicionar mais sistemas, edite o arquivo `frontend/index.html` e adicione novas opções aos selects.

## 📁 Estrutura do Projeto

```
Mini-QGIS-Online/
├── backend/
│   ├── app.py              # Aplicação Flask principal
│   ├── spatial.py          # Módulo de conversão (utilitário)
│   └── requirements.txt    # Dependências Python
├── frontend/
│   ├── index.html          # Página principal
│   ├── style.css           # Estilos CSS
│   ├── map.js              # Lógica do mapa
│   └── converter.js        # Lógica de conversão
├── .env.example            # Exemplo de variáveis de ambiente
├── .gitignore              # Arquivos ignorados pelo Git
├── Procfile                # Configuração para Heroku/Render
├── render.yaml             # Configuração para Render
├── README.md               # Este arquivo
└── LICENSE                 # Licença do projeto
```

## 🐛 Tratamento de Erros

A API fornece mensagens de erro descritivas:

- **400 Bad Request**: Dados inválidos ou incompletos
- **404 Not Found**: Endpoint não encontrado
- **500 Internal Server Error**: Erro no servidor

## 🚢 Implantação

### Render

1. Conecte o repositório ao Render
2. Configure as variáveis de ambiente
3. O `render.yaml` será usado automaticamente

### Heroku

1. Instale o Heroku CLI
2. Execute: `heroku create seu-app-name`
3. Execute: `git push heroku main`

### Outras Plataformas

Use o `Procfile` como referência para configurar a implantação.

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Faça um Fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Autor

**Solutions Technology Information**

## 📧 Suporte

Para reportar problemas ou sugerir melhorias, abra uma issue no repositório GitHub.

## 🔗 Links Úteis

- [PyProj Documentation](https://pyproj4.github.io/pyproj/stable/)
- [Leaflet Documentation](https://leafletjs.com/)
- [EPSG Codes](https://epsg.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Última atualização**: Março de 2026
