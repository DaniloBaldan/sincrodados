"""
Validacao dos dados.

Antes de gravar qualquer registro no destino, a aplicacao confere se ele
faz sentido. Campo obrigatorio nao pode vir vazio, o CPF precisa ter
digitos validos, o salario precisa ser um numero e o email precisa ter um
formato aceitavel. Registro que nao passa nessas regras e separado e
guardado no log com o motivo, em vez de ir para o destino.
"""

import re

EXPRESSAO_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def cpf_valido(cpf):
    """
    Verifica os digitos verificadores do CPF.

    Tira tudo que nao e numero, confere se sobraram onze digitos, descarta
    sequencias repetidas como 11111111111 e entao recalcula os dois digitos
    verificadores para comparar com os informados.
    """
    numeros = re.sub(r"\D", "", cpf or "")

    if len(numeros) != 11:
        return False
    if numeros == numeros[0] * 11:
        return False

    def calcular_digito(parcial, peso_inicial):
        soma = 0
        peso = peso_inicial
        for algarismo in parcial:
            soma += int(algarismo) * peso
            peso -= 1
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    primeiro = calcular_digito(numeros[:9], 10)
    segundo = calcular_digito(numeros[:10], 11)

    return primeiro == int(numeros[9]) and segundo == int(numeros[10])


def email_valido(email):
    return bool(EXPRESSAO_EMAIL.match(email or ""))


def validar_registro(registro_origem, campos):
    """
    Recebe a linha original e a definicao dos campos do mapeamento.
    Devolve uma lista de problemas encontrados. Lista vazia quer dizer
    que o registro esta apto a ser transformado e gravado.
    """
    problemas = []

    for campo in campos:
        nome_origem = campo["origem"]
        valor = registro_origem.get(nome_origem)
        texto = ("" if valor is None else str(valor)).strip()

        if campo.get("obrigatorio") and texto == "":
            problemas.append(f"campo obrigatorio vazio: {nome_origem}")
            continue

        if texto == "":
            continue

        tipo = campo["transformacao"]

        if tipo == "cpf" and not cpf_valido(texto):
            problemas.append(f"cpf invalido: {texto}")
        elif tipo == "email" and not email_valido(texto):
            problemas.append(f"email invalido: {texto}")
        elif tipo == "decimal":
            try:
                float(texto.replace(",", "."))
            except ValueError:
                problemas.append(f"salario nao numerico: {texto}")

    return problemas
