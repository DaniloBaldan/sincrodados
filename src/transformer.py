"""
Transformacao dos dados.

Cada campo do mapeamento aponta para uma transformacao pelo nome. Aqui
ficam essas transformacoes, reunidas em um dicionario que liga o nome
usado no mapeamento a funcao que faz o trabalho. Assim, para criar um
tipo novo de conversao, basta escrever a funcao e registra-la, sem mexer
no resto da aplicacao.

O resultado de transformar uma linha e o registro ja no formato padrao do
destino, ou seja, o modelo canonico que o Sistema Y espera receber.
"""

import re
from datetime import datetime


def para_titulo(valor, contexto=None):
    """Tira espacos sobrando e deixa cada palavra com a inicial maiuscula."""
    return " ".join(str(valor).split()).title()


def para_texto(valor, contexto=None):
    return str(valor).strip()


def para_cpf(valor, contexto=None):
    """Devolve o CPF sempre no formato 000.000.000-00."""
    numeros = re.sub(r"\D", "", str(valor))
    return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"


def para_decimal(valor, contexto=None):
    """Converte o salario que veio como texto em numero."""
    return float(str(valor).replace(",", "."))


def para_data_br(valor, contexto=None):
    """Troca a data do padrao ISO (AAAA/MM/DD) para o padrao brasileiro."""
    data = datetime.strptime(str(valor).strip(), "%Y-%m-%d")
    return data.strftime("%d/%m/%Y")


def para_situacao(valor, contexto=None):
    """Troca o 1 ou 0 do sistema antigo por um texto legivel."""
    return "Ativo" if str(valor).strip() in ("1", "True", "true") else "Inativo"


def para_email(valor, contexto=None):
    return str(valor).strip().lower()


def para_departamento(valor, contexto=None):
    """
    Resolve o codigo de departamento do sistema antigo para o id novo,
    usando o mapa de departamentos que foi montado na migracao anterior.
    """
    mapa = (contexto or {}).get("mapa_departamentos", {})
    return mapa.get(str(valor).strip())


# Registro que liga o nome usado no mapeamento a funcao correspondente
TRANSFORMACOES = {
    "titulo": para_titulo,
    "texto": para_texto,
    "cpf": para_cpf,
    "decimal": para_decimal,
    "data_br": para_data_br,
    "situacao": para_situacao,
    "email": para_email,
    "departamento": para_departamento,
}


def transformar_registro(registro_origem, campos, contexto=None):
    """
    Aplica, campo a campo, a transformacao indicada no mapeamento e monta
    o registro de destino. Campo opcional que veio vazio simplesmente nao
    entra no resultado.
    """
    destino = {}

    for campo in campos:
        valor = registro_origem.get(campo["origem"])
        texto = "" if valor is None else str(valor).strip()

        if texto == "" and not campo.get("obrigatorio"):
            continue

        funcao = TRANSFORMACOES[campo["transformacao"]]
        destino[campo["destino"]] = funcao(valor, contexto)

    return destino
