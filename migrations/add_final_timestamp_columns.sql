-- Migration: Adiciona colunas de timestamp em empresas_historico
-- Data: 2025-11-20
-- Descrição: Adiciona data_criacao e data_atualizacao

-- Adiciona data_criacao
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS data_criacao TIMESTAMP WITHOUT TIME ZONE;

-- Adiciona data_atualizacao
ALTER TABLE empresas_historico
ADD COLUMN IF NOT EXISTS data_atualizacao TIMESTAMP WITHOUT TIME ZONE;

-- Comentários
COMMENT ON COLUMN empresas_historico.data_criacao IS 'Data/hora de criação do registro da empresa original';
COMMENT ON COLUMN empresas_historico.data_atualizacao IS 'Data/hora de última atualização do registro da empresa original';

-- Verifica se agora todas as colunas estão presentes
SELECT 'Colunas em empresas mas NÃO em empresas_historico:' as status;

SELECT column_name
FROM information_schema.columns
WHERE table_name = 'empresas'
  AND column_name NOT IN (
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = 'empresas_historico'
  )
ORDER BY column_name;

-- Se não retornar nada, significa que está sincronizado!
