"""
Interface de linha de comando do SincroDados.

Comandos disponiveis:

    python main.py init      cria e popula o banco do Sistema X (origem)
    python main.py sync      executa a sincronizacao para o Sistema Y
    python main.py status    mostra o resumo da ultima execucao
    python main.py rejeitados   lista os registros que foram recusados
    python main.py painel    sobe o painel web de acompanhamento
"""

import argparse
import logging

import config
import seed_data
from src.engine import MotorSincronizacao
from src.audit import Auditoria


def configurar_log():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  %(levelname)-7s  %(message)s",
        datefmt="%H:%M:%S",
    )


def comando_init():
    import os
    seed_data.criar_banco_origem()

    # Zera o destino e a auditoria para a demonstracao comecar do zero
    if os.path.exists(config.BANCO_DESTINO):
        os.remove(config.BANCO_DESTINO)
    if os.path.exists(config.BANCO_LOG):
        os.remove(config.BANCO_LOG)
    from src import adapters
    adapters.AdaptadorSqliteDestino(config.BANCO_DESTINO).preparar_esquema(reset=True)
    print("Destino e auditoria reiniciados. Pronto para sincronizar.")


def comando_sync():
    print("Iniciando sincronizacao do Sistema X para o Sistema Y...\n")
    motor = MotorSincronizacao()
    total = motor.sincronizar()

    print("\nResumo da sincronizacao")
    print("  Lidos      :", total["lidos"])
    print("  Migrados   :", total["migrados"])
    print("  Ignorados  :", total["ignorados"])
    print("  Rejeitados :", total["rejeitados"])
    print("\nSaidas geradas:")
    print("  Banco destino :", config.BANCO_DESTINO)
    print("  JSON          :", config.SAIDA_JSON)
    print("  CSV           :", config.SAIDA_CSV)


def comando_status():
    auditoria = Auditoria(config.BANCO_LOG)
    execucao = auditoria.ultima_execucao()
    if not execucao:
        print("Nenhuma sincronizacao foi executada ainda.")
        return
    print("Ultima execucao")
    print("  Inicio     :", execucao["inicio"])
    print("  Fim        :", execucao["fim"])
    print("  Lidos      :", execucao["lidos"])
    print("  Migrados   :", execucao["migrados"])
    print("  Ignorados  :", execucao["ignorados"])
    print("  Rejeitados :", execucao["rejeitados"])


def comando_rejeitados():
    auditoria = Auditoria(config.BANCO_LOG)
    rejeitados = auditoria.registros_por_status("rejeitado")
    if not rejeitados:
        print("Nenhum registro rejeitado na ultima execucao.")
        return
    print("Registros rejeitados\n")
    for item in rejeitados:
        print(f"  chave {item['chave']}  ->  {item['detalhe']}")


def comando_painel():
    from dashboard.app import app
    print("Painel disponivel em http://127.0.0.1:5000")
    app.run(debug=False, port=5000)


def main():
    configurar_log()
    parser = argparse.ArgumentParser(description="SincroDados")
    parser.add_argument(
        "comando",
        choices=["init", "sync", "status", "rejeitados", "painel"],
        help="acao a executar",
    )
    args = parser.parse_args()

    acoes = {
        "init": comando_init,
        "sync": comando_sync,
        "status": comando_status,
        "rejeitados": comando_rejeitados,
        "painel": comando_painel,
    }
    acoes[args.comando]()


if __name__ == "__main__":
    main()
