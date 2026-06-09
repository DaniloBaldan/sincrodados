"""
Teste de integracao do motor de sincronizacao.

Roda o fluxo completo de ponta a ponta: cria o banco de origem, executa a
sincronizacao e confere os numeros do resultado. Tambem testa a
idempotencia, rodando a sincronizacao duas vezes e verificando que a
segunda rodada nao grava nada de novo.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import seed_data
from src.engine import MotorSincronizacao


def _ambiente_limpo():
    """Garante origem populada e destino e auditoria zerados."""
    seed_data.criar_banco_origem()
    for caminho in (config.BANCO_DESTINO, config.BANCO_LOG):
        if os.path.exists(caminho):
            os.remove(caminho)


def test_fluxo_completo_de_sincronizacao():
    _ambiente_limpo()

    motor = MotorSincronizacao()
    total = motor.sincronizar(reset=True)

    # Foram lidos 4 departamentos e 15 funcionarios
    assert total["lidos"] == 19

    # 4 departamentos + 10 funcionarios validos e unicos
    assert total["migrados"] == 14

    # 4 registros com problema de dado: nome vazio, cpf invalido,
    # salario nao numerico e email mal formado
    assert total["rejeitados"] == 4

    # 1 registro com CPF repetido, barrado pela sincronizacao incremental
    assert total["ignorados"] == 1


def test_sincronizacao_e_idempotente():
    _ambiente_limpo()

    motor = MotorSincronizacao()
    motor.sincronizar(reset=True)

    # Rodar de novo, sem reset, nao deve gravar nada: tudo ja existe
    segunda = motor.sincronizar(reset=False)
    assert segunda["migrados"] == 0
    assert segunda["ignorados"] == 15
