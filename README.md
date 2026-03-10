# Mini-QGIS-Online

Um projeto básico em Rust para uma versão mini do QGIS online, usando Rocket para servir uma página web com um mapa interativo usando Leaflet.

## Como executar

Certifique-se de ter o Rust instalado. Então:

```bash
cargo build
cargo run
```

O servidor será iniciado na porta definida pela variável de ambiente `PORT` (padrão 8000). Acesse http://localhost:PORT para ver o mapa.

## Deploy

Este projeto pode ser implantado no Render.com ou outras plataformas que suportam Rust. Configure:
- Build Command: `cargo build --release`
- Start Command: `./target/release/mini-qgis-online`