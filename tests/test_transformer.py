"""
Testes da camada de transformacao.

Conferem se cada conversao entrega o dado no formato esperado pelo
Sistema Y: nome com a inicial maiuscula, CPF com mascara, salario virando
numero, data no padrao brasileiro e o indicador de situacao em texto.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import transformer


def test_titulo_remove_espacos_e_ajusta_maiusculas():
    assert transformer.para_titulo("  joao da SILVA  ") == "Joao Da Silva"


def test_cpf_recebe_mascara():
    assert transformer.para_cpf("52998224725") == "529.982.247-25"


def test_decimal_converte_texto_em_numero():
    assert transformer.para_decimal("1500.75") == 1500.75
    assert transformer.para_decimal("1500,75") == 1500.75


def test_data_passa_para_padrao_brasileiro():
    assert transformer.para_data_br("2026-06-08") == "08/06/2026"


def test_situacao_traduz_indicador():
    assert transformer.para_situacao("1") == "Ativo"
    assert transformer.para_situacao("0") == "Inativo"


def test_email_fica_em_minusculas():
    assert transformer.para_email("JOAO@EMPRESA.COM") == "joao@empresa.com"


def test_departamento_resolve_pelo_mapa():
    contexto = {"mapa_departamentos": {"D01": 7}}
    assert transformer.para_departamento("D01", contexto) == 7


def test_transformar_registro_completo():
    campos = [
        {"origem": "full_name", "destino": "nome_completo", "transformacao": "titulo", "obrigatorio": True},
        {"origem": "salary", "destino": "salario", "transformacao": "decimal", "obrigatorio": True},
    ]
    origem = {"full_name": "maria souza", "salary": "6200.50"}
    resultado = transformer.transformar_registro(origem, campos, {})
    assert resultado == {"nome_completo": "Maria Souza", "salario": 6200.50}
