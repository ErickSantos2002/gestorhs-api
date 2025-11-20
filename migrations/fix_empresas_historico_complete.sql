-- Migration: Sincroniza tabela empresas_historico com o modelo atual
-- Data: 2025-11-20
-- Descrição: Adiciona todas as colunas faltantes na tabela de histórico

-- Adiciona coluna status_contato
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS status_contato VARCHAR(20);

-- Adiciona coluna data_cadastro
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS data_cadastro DATE;

-- Atualiza registros existentes com valores padrão
UPDATE empresas_historico
SET status_contato = 'ativo'
WHERE status_contato IS NULL;

-- Comentários explicativos
COMMENT ON COLUMN empresas_historico.status_contato IS 'Status de contato da empresa no momento do histórico (ativo, sem_contato, inativo, perdido)';
COMMENT ON COLUMN empresas_historico.data_cadastro IS 'Data de cadastro original da empresa';

-- Verifica as colunas da tabela
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'empresas_historico'
ORDER BY ordinal_position;
