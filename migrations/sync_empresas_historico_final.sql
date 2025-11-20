-- Migration: Sincroniza COMPLETAMENTE empresas_historico com empresas
-- Data: 2025-11-20
-- Descrição: Adiciona TODAS as colunas faltantes de uma vez

-- Adiciona usuario_cadastro_id (chave estrangeira para a tabela de usuários)
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS usuario_cadastro_id INTEGER;

COMMENT ON COLUMN empresas_historico.usuario_cadastro_id IS 'ID do usuário que cadastrou a empresa originalmente';

-- Verifica se todas as colunas foram adicionadas
SELECT 'empresas_historico tem ' || COUNT(*) || ' colunas' as status
FROM information_schema.columns
WHERE table_name = 'empresas_historico';

-- Lista todas as colunas
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'empresas_historico'
ORDER BY ordinal_position;
