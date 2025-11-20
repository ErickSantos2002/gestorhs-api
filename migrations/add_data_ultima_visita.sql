-- Migration: Adiciona coluna data_ultima_visita em empresas_historico
-- Data: 2025-11-20

-- Adiciona coluna data_ultima_visita
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS data_ultima_visita DATE;

COMMENT ON COLUMN empresas_historico.data_ultima_visita IS 'Data da última visita à empresa no momento do histórico';
