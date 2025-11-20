"""
Service para Ordens de Serviço (regras de negócio)
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from app.models.ordem_servico import OrdemServico
from app.models.equipamento import EquipamentoEmpresa, Equipamento
from app.models.logs import LogOrdemServico
from app.utils.security import generate_chave_acesso


class OSService:
    """Service com regras de negócio de Ordens de Serviço"""

    @staticmethod
    def create_ordem_servico(db: Session, os_data: dict, usuario_id: int) -> OrdemServico:
        """
        Cria nova OS com regras de negócio

        - Gera chave de acesso única
        - Define fase inicial como "Solicitado" (id=1)
        - Define situação como "E" (Espera)
        - Registra log de criação
        """
        # Gerar chave de acesso única
        while True:
            chave_acesso = generate_chave_acesso()
            if not db.query(OrdemServico).filter(OrdemServico.chave_acesso == chave_acesso).first():
                break

        # Criar OS
        os = OrdemServico(
            **os_data,
            chave_acesso=chave_acesso,
            fase_id=1,  # Fase "Solicitado"
            situacao_servico="E"  # Espera
        )
        db.add(os)
        db.flush()  # Para obter o ID

        # Registrar log
        log = LogOrdemServico(
            ordem_servico_id=os.id,
            usuario_id=usuario_id,
            tipo_autor="S",
            acao="CRIACAO",
            descricao=f"Ordem de serviço criada com chave {chave_acesso}"
        )
        db.add(log)

        return os

    @staticmethod
    def mudar_fase(db: Session, os: OrdemServico, nova_fase_id: int, usuario_id: int):
        """
        Muda fase da OS e atualiza timestamps correspondentes

        Mapeamento fase -> campo de data:
        1. Solicitado → data_solicitacao (já definida na criação)
        2. Enviado → data_envio
        3. Recebido → data_chegada
        4. Em Calibração → (sem campo específico)
        5. Calibrado → data_calibracao
        6. Retornando → data_retorno
        7. Entregue → data_entrega
        8. Cancelado → situacao_servico = 'C'
        """
        fase_antiga = os.fase_id
        os.fase_id = nova_fase_id

        # Atualizar timestamp correspondente
        now = datetime.utcnow()
        if nova_fase_id == 2:  # Enviado
            os.data_envio = now
            os.situacao_servico = "A"  # Andamento
        elif nova_fase_id == 3:  # Recebido
            os.data_chegada = now
        elif nova_fase_id == 4:  # Em Calibração
            os.situacao_servico = "A"  # Andamento
        elif nova_fase_id == 5:  # Calibrado
            if not os.data_calibracao:  # Só atualiza se não foi definida manualmente
                os.data_calibracao = now
        elif nova_fase_id == 6:  # Retornando
            os.data_retorno = now
        elif nova_fase_id == 7:  # Entregue
            os.data_entrega = now
            os.situacao_servico = "F"  # Finalizado
        elif nova_fase_id == 8:  # Cancelado
            os.situacao_servico = "C"  # Cancelado

        # Registrar log
        log = LogOrdemServico(
            ordem_servico_id=os.id,
            usuario_id=usuario_id,
            tipo_autor="S",
            acao="MUDANCA_FASE",
            descricao=f"Fase alterada de {fase_antiga} para {nova_fase_id}"
        )
        db.add(log)

    @staticmethod
    def finalizar_ordem_servico(
        db: Session,
        os: OrdemServico,
        dados_calibracao: dict,
        usuario_id: int
    ):
        """
        Finaliza OS com dados de calibração

        Regras:
        1. Atualiza dados de calibração na OS
        2. Atualiza equipamento_empresa com:
           - data_ultima_calibracao
           - data_proxima_calibracao (calculada)
           - Copia dados de certificação
        3. Define situacao_servico = 'F'
        4. Registra log
        """
        # Atualizar OS
        for field, value in dados_calibracao.items():
            setattr(os, field, value)

        os.situacao_servico = "F"  # Finalizado
        os.fase_id = 5  # Calibrado

        # Atualizar equipamento empresa
        equipamento_empresa = db.query(EquipamentoEmpresa).filter(
            EquipamentoEmpresa.id == os.equipamento_empresa_id
        ).first()

        if equipamento_empresa:
            equipamento_empresa.data_ultima_calibracao = dados_calibracao["data_calibracao"].date()

            # Calcular próxima calibração
            equipamento = db.query(Equipamento).filter(
                Equipamento.id == equipamento_empresa.equipamento_id
            ).first()

            if equipamento:
                dias = equipamento.periodo_calibracao_dias or 365
                equipamento_empresa.data_proxima_calibracao = (
                    dados_calibracao["data_calibracao"].date() + timedelta(days=dias)
                )

            # Copiar dados de certificação
            equipamento_empresa.certificado_numero = dados_calibracao.get("certificado_numero")
            equipamento_empresa.certificado_temperatura = dados_calibracao.get("certificado_temperatura")
            equipamento_empresa.certificado_pressao = dados_calibracao.get("certificado_pressao")
            equipamento_empresa.teste_1 = dados_calibracao.get("teste_1")
            equipamento_empresa.teste_2 = dados_calibracao.get("teste_2")
            equipamento_empresa.teste_3 = dados_calibracao.get("teste_3")
            equipamento_empresa.teste_media = dados_calibracao.get("teste_media")
            equipamento_empresa.situacao_calibracao = dados_calibracao.get("situacao_calibracao")
            equipamento_empresa.os_atual_id = os.id

        # Registrar log
        log = LogOrdemServico(
            ordem_servico_id=os.id,
            usuario_id=usuario_id,
            tipo_autor="S",
            acao="FINALIZACAO",
            descricao="Ordem de serviço finalizada com dados de calibração"
        )
        db.add(log)
