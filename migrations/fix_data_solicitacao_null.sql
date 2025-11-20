-- Corrigir data_solicitacao NULL em ordens de serviço antigas
-- Define data_solicitacao = data_criacao para registros antigos onde está NULL

UPDATE ordens_servico
SET data_solicitacao = COALESCE(data_criacao, NOW())
WHERE data_solicitacao IS NULL;

-- Comentário
COMMENT ON COLUMN ordens_servico.data_solicitacao IS 'Data e hora da solicitação da ordem de serviço (obrigatório)';
