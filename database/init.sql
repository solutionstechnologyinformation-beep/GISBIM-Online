
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
