"""
Auditoria da sincronizacao.

Toda execucao precisa deixar rastro. Este modulo guarda, em um banco
separado, um resumo de cada rodada de sincronizacao e tambem o destino de
cada registro: se foi migrado, se foi ignorado por ja existir ou se foi
rejeitado, com o motivo. E essa parte que da sentido a auditoria do
projeto, porque permite responder depois o que aconteceu com cada dado.
"""

import sqlite3
from datetime import datetime


class Auditoria:
    def __init__(self, caminho_banco):
        self.caminho_banco = caminho_banco
        self._preparar()

    def _conectar(self):
        return sqlite3.connect(self.caminho_banco)

    def _preparar(self):
        conexao = self._conectar()
        cursor = conexao.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execucao (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                inicio      TEXT,
                fim         TEXT,
                lidos       INTEGER,
                migrados    INTEGER,
                ignorados   INTEGER,
                rejeitados  INTEGER
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS log_registro (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                id_execucao  INTEGER,
                tabela       TEXT,
                chave        TEXT,
                status       TEXT,
                detalhe      TEXT,
                momento      TEXT,
                FOREIGN KEY (id_execucao) REFERENCES execucao (id)
            )
        """)

        conexao.commit()
        conexao.close()

    def abrir_execucao(self):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute(
            "INSERT INTO execucao (inicio) VALUES (?)",
            (datetime.now().isoformat(timespec="seconds"),),
        )
        id_execucao = cursor.lastrowid
        conexao.commit()
        conexao.close()
        return id_execucao

    def registrar(self, id_execucao, tabela, chave, status, detalhe=""):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute(
            """INSERT INTO log_registro
               (id_execucao, tabela, chave, status, detalhe, momento)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (
                id_execucao,
                tabela,
                chave,
                status,
                detalhe,
                datetime.now().isoformat(timespec="seconds"),
            ),
        )
        conexao.commit()
        conexao.close()

    def fechar_execucao(self, id_execucao, lidos, migrados, ignorados, rejeitados):
        conexao = self._conectar()
        cursor = conexao.cursor()
        cursor.execute(
            """UPDATE execucao
               SET fim = ?, lidos = ?, migrados = ?, ignorados = ?, rejeitados = ?
               WHERE id = ?""",
            (
                datetime.now().isoformat(timespec="seconds"),
                lidos,
                migrados,
                ignorados,
                rejeitados,
                id_execucao,
            ),
        )
        conexao.commit()
        conexao.close()

    def ultima_execucao(self):
        conexao = self._conectar()
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM execucao ORDER BY id DESC LIMIT 1")
        linha = cursor.fetchone()
        conexao.close()
        return dict(linha) if linha else None

    def registros_por_status(self, status):
        conexao = self._conectar()
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute(
            "SELECT * FROM log_registro WHERE status = ? ORDER BY id DESC",
            (status,),
        )
        linhas = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        return linhas

    def todos_registros(self):
        conexao = self._conectar()
        conexao.row_factory = sqlite3.Row
        cursor = conexao.cursor()
        cursor.execute("SELECT * FROM log_registro ORDER BY id DESC")
        linhas = [dict(linha) for linha in cursor.fetchall()]
        conexao.close()
        return linhas
