"""
Cria e popula o banco do Sistema X (RH legado).

O Sistema X representa um sistema antigo de recursos humanos. O esquema
usa nomes de coluna em ingles, guarda salario como texto, data no padrao
ISO e o status do funcionario como 0 ou 1. Esses detalhes foram colocados
de proposito para que a etapa de transformacao tenha trabalho real a fazer.

Alguns registros tem problema de proposito (nome vazio, CPF invalido,
salario nao numerico, email mal formado e um CPF repetido). Isso serve
para demonstrar a validacao e a deduplicacao na hora da sincronizacao.
"""

import sqlite3
import os

import config


def criar_banco_origem():
    config.garantir_pasta_dados()

    # Recria o banco do zero a cada execucao para a demonstracao ficar previsivel
    if os.path.exists(config.BANCO_ORIGEM):
        os.remove(config.BANCO_ORIGEM)

    conexao = sqlite3.connect(config.BANCO_ORIGEM)
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE tb_department (
            dept_code TEXT PRIMARY KEY,
            dept_name TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE tb_employee (
            emp_id    INTEGER PRIMARY KEY,
            full_name TEXT,
            cpf       TEXT,
            dept_code TEXT,
            salary    TEXT,
            hire_date TEXT,
            email     TEXT,
            active    INTEGER
        )
    """)

    departamentos = [
        ("D01", "tecnologia da informacao"),
        ("D02", "recursos humanos"),
        ("D03", "financeiro"),
        ("D04", "comercial"),
    ]
    cursor.executemany(
        "INSERT INTO tb_department (dept_code, dept_name) VALUES (?, ?)",
        departamentos,
    )

    # Os campos seguem o padrao do sistema antigo de proposito
    funcionarios = [
        # registros validos
        (1,  "joao da silva",        "104.332.181-00", "D01", "4500.00", "2019-03-12", "JOAO.SILVA@EMPRESA.COM",     1),
        (2,  "MARIA OLIVEIRA SOUZA", "960.013.389-14", "D02", "6200.50", "2017-08-01", "maria.souza@empresa.com",    1),
        (3,  "  carlos pereira  ",   "083.863.794-99", "D03", "8300.75", "2015-01-20", "carlos.pereira@empresa.com", 1),
        (4,  "ANA PAULA RAMOS",      "026.542.351-14", "D01", "5100.00", "2021-11-05", "ana.ramos@empresa.com",      1),
        (5,  "Pedro Henrique Costa", "161.559.407-89", "D04", "3900.90", "2020-06-18", "pedro.costa@empresa.com",    0),
        (6,  "luciana martins",      "816.184.959-50", "D02", "7200.00", "2016-09-30", "luciana.martins@empresa.com",1),
        (7,  "ROBERTO ALMEIDA",      "310.341.316-56", "D03", "9800.00", "2014-02-14", "roberto.almeida@empresa.com",1),
        (8,  "fernanda lima",        "475.255.341-44", "D04", "4100.25", "2022-04-22", "fernanda.lima@empresa.com",  1),
        (9,  "Marcos Vinicius Dias", "928.327.648-51", "D01", "6800.00", "2018-07-09", "marcos.dias@empresa.com",    0),
        (10, "patricia gomes",       "350.305.641-60", "D02", "5500.00", "2019-12-01", "patricia.gomes@empresa.com", 1),

        # registros com problema, usados para demonstrar a validacao
        (11, "",                     "395.376.724-09", "D01", "5000.00", "2020-01-10", "sem.nome@empresa.com",       1),  # nome vazio
        (12, "JORGE TEIXEIRA",       "123.456.789-00", "D03", "4700.00", "2019-05-05", "jorge.teixeira@empresa.com", 1),  # cpf invalido
        (13, "BEATRIZ NOVAES",       "475.255.341-44", "D04", "4300.00", "2023-02-28", "beatriz.novaes@empresa.com", 1),  # cpf repetido (igual ao 8)
        (14, "RAFAEL MENDES",        "238.849.696-92", "D02", "salario", "2018-10-10", "rafael.mendes@empresa.com",  1),  # salario nao numerico
        (15, "TATIANE ROCHA",        "532.871.012-69", "D01", "5900.00", "2021-03-15", "tatiane#empresa",            1),  # email mal formado
    ]
    cursor.executemany(
        """INSERT INTO tb_employee
           (emp_id, full_name, cpf, dept_code, salary, hire_date, email, active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        funcionarios,
    )

    conexao.commit()
    conexao.close()

    print("Banco do Sistema X criado em:", config.BANCO_ORIGEM)
    print("Departamentos inseridos:", len(departamentos))
    print("Funcionarios inseridos:", len(funcionarios))


if __name__ == "__main__":
    criar_banco_origem()
