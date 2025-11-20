-- Migration: Adiciona coluna 'ativo' na tabela empresas_historico
-- Data: 2025-11-20
-- Descrição: A coluna 'ativo' está faltando na tabela de histórico

-- Adiciona a coluna ativo
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS ativo CHAR(1);

-- Atualiza registros existentes com valor padrão
UPDATE empresas_historico
SET ativo = 'S'
WHERE ativo IS NULL;

-- Comentário explicativo
COMMENT ON COLUMN empresas_historico.ativo IS 'Status ativo da empresa no momento do histórico (S/N)';
