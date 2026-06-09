"""
Adaptadores de leitura e escrita.

A ideia aqui e isolar o resto da aplicacao de saber como cada formato de
armazenamento funciona. O extrator pede os registros e o adaptador de
origem cuida de ler do banco. O carregador entrega os registros prontos e
o adaptador de destino cuida de gravar, seja em banco, em JSON ou em CSV.

Trocar a origem ou o destino por outro formato vira so uma questao de
escrever um novo adaptador, sem mexer na logica de transformacao.
"""

import sqlite3
import json
import csv


class AdaptadorSqliteOrigem:
    """Le tabelas do banco de origem e devolve cada linha como dicionario."""

    def __init__(self, caminho_banco):
        self.caminho_banco = caminho_banco

    def ler(self, tabela):
        conexao = sqlite3.connect(self.caminho_banco)
        # row_factory faz cada linha vir como dicionario com o nome das colunas
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute(f"SELECT * FROM {tabela}")
        linhas = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        return linhas


class AdaptadorSqliteDestino:
    """Cria o esquema do destino e grava os registros ja transformados."""

    def __init__(self, caminho_banco):
        self.caminho_banco = caminho_banco

    def preparar_esquema(self, reset=False):
        """
        Garante que o esquema do destino exista.

        Com reset igual a True, apaga as tabelas antes de criar de novo,
        comecando do zero. Com reset igual a False, so cria o que ainda nao
        existe, preservando o que ja foi gravado. E esse modo que permite a
        sincronizacao incremental entre execucoes.
        """
        conexao = sqlite3.connect(self.caminho_banco)
        cursor = conexao.cursor()

        if reset:
            cursor.execute("DROP TABLE IF EXISTS funcionarios")
            cursor.execute("DROP TABLE IF EXISTS departamentos")

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS departamentos (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_origem TEXT UNIQUE,
                nome          TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS funcionarios (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                nome_completo   TEXT NOT NULL,
                cpf             TEXT NOT NULL UNIQUE,
                salario         REAL NOT NULL,
                data_admissao   TEXT NOT NULL,
                email           TEXT NOT NULL,
                situacao        TEXT NOT NULL,
                id_departamento INTEGER,
                FOREIGN KEY (id_departamento) REFERENCES departamentos (id)
            )
        """)

        conexao.commit()
        conexao.close()

    def buscar_por_chave(self, tabela, campo_chave, valor):
        """Usado na sincronizacao incremental para ver se o registro ja existe."""
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute(
            f"SELECT * FROM {tabela} WHERE {campo_chave} = ?", (valor,)
        )
        linha = cursor.fetchone()
        conexao.close()
        return dict(linha) if linha else None

    def inserir(self, tabela, registro):
        conexao = sqlite3.connect(self.caminho_banco)
        cursor = conexao.cursor()
        colunas = ", ".join(registro.keys())
        marcadores = ", ".join(["?"] * len(registro))
        cursor.execute(
            f"INSERT INTO {tabela} ({colunas}) VALUES ({marcadores})",
            list(registro.values()),
        )
        id_gerado = cursor.lastrowid
        conexao.commit()
        conexao.close()
        return id_gerado

    def mapa_departamentos(self):
        """Devolve um dicionario que liga o codigo de origem ao id novo."""
        conexao = sqlite3.connect(self.caminho_banco)
        cursor = conexao.cursor()
        cursor.execute("SELECT codigo_origem, id FROM departamentos")
        mapa = {codigo: id_novo for codigo, id_novo in cursor.fetchall()}
        conexao.close()
        return mapa

    def listar(self, tabela):
        conexao = sqlite3.connect(self.caminho_banco)
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute(f"SELECT * FROM {tabela}")
        linhas = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        return linhas


def exportar_json(registros, caminho):
    """Grava a lista de registros em um arquivo JSON."""
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(registros, arquivo, ensure_ascii=False, indent=2)


def exportar_csv(registros, caminho):
    """Grava a lista de registros em um arquivo CSV."""
    if not registros:
        return
    colunas = list(registros[0].keys())
    with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(registros)
