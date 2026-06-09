"""
Testes da camada de validacao.

Conferem a checagem dos digitos do CPF, a validacao de email e o
comportamento da funcao que junta os problemas de um registro inteiro.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import validator


def test_cpf_valido_aceita_numero_correto():
    assert validator.cpf_valido("529.982.247-25") is True
    assert validator.cpf_valido("11144477735") is True


def test_cpf_valido_recusa_digito_errado():
    assert validator.cpf_valido("123.456.789-00") is False


def test_cpf_valido_recusa_sequencia_repetida():
    assert validator.cpf_valido("111.111.111-11") is False


def test_cpf_valido_recusa_tamanho_errado():
    assert validator.cpf_valido("123") is False


def test_email_valido():
    assert validator.email_valido("nome@empresa.com") is True
    assert validator.email_valido("nome#empresa") is False


def test_validar_registro_aponta_campo_obrigatorio_vazio():
    campos = [{"origem": "full_name", "transformacao": "titulo", "obrigatorio": True}]
    problemas = validator.validar_registro({"full_name": "   "}, campos)
    assert any("obrigatorio" in p for p in problemas)


def test_validar_registro_sem_problemas_retorna_lista_vazia():
    campos = [
        {"origem": "cpf", "transformacao": "cpf", "obrigatorio": True},
        {"origem": "email", "transformacao": "email", "obrigatorio": True},
    ]
    registro = {"cpf": "529.982.247-25", "email": "joao@empresa.com"}
    assert validator.validar_registro(registro, campos) == []
