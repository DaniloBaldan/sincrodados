"""
Painel web de acompanhamento.

Diferente de um backend que so responde por API, aqui existe uma tela
simples que mostra, de forma visual, o resultado da ultima sincronizacao:
quantos registros foram migrados, ignorados e rejeitados, a lista de
funcionarios ja gravados no Sistema Y e os registros que foram recusados,
com o motivo. O painel le diretamente do banco de destino e do banco de
auditoria.
"""

from flask import Flask, render_template

import config
from src import adapters
from src.audit import Auditoria

app = Flask(__name__)


@app.route("/")
def inicio():
    auditoria = Auditoria(config.BANCO_LOG)
    destino = adapters.AdaptadorSqliteDestino(config.BANCO_DESTINO)

    execucao = auditoria.ultima_execucao()
    rejeitados = auditoria.registros_por_status("rejeitado")
    ignorados = auditoria.registros_por_status("ignorado")

    try:
        funcionarios = destino.listar("funcionarios")
        departamentos = {d["id"]: d["nome"] for d in destino.listar("departamentos")}
        for f in funcionarios:
            f["departamento"] = departamentos.get(f.get("id_departamento"), "")
    except Exception:
        funcionarios = []

    return render_template(
        "index.html",
        execucao=execucao,
        funcionarios=funcionarios,
        rejeitados=rejeitados,
        ignorados=ignorados,
    )


if __name__ == "__main__":
    app.run(debug=False, port=5000)
