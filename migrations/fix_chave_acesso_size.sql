-- Aumentar tamanho do campo chave_acesso em ordens_servico
-- De VARCHAR(12) para VARCHAR(20) para acomodar chaves geradas no formato '16DM-BYV7-XGUJ' (15 caracteres)

ALTER TABLE ordens_servico
ALTER COLUMN chave_acesso TYPE VARCHAR(20);

-- Comentário explicativo
COMMENT ON COLUMN ordens_servico.chave_acesso IS 'Chave de acesso única para rastreamento da OS (até 20 caracteres)';
