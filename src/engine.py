"""
Motor da sincronizacao.

Esta e a parte que junta tudo. Para cada tabela definida no mapeamento, o
motor le os registros da origem, valida, transforma para o formato do
destino, verifica se o registro ja existe (sincronizacao incremental) e,
se for o caso, grava. Todo o caminho de cada registro fica anotado na
auditoria.

A sincronizacao e incremental: se um registro com a mesma chave natural ja
estiver no destino, ele e ignorado em vez de gravado de novo. E isso que
deixa a operacao idempotente, ou seja, rodar a sincronizacao duas vezes
nao gera dado duplicado.
"""

import json
import logging

import config
from src import adapters, validator, transformer
from src.audit import Auditoria

logger = logging.getLogger("sincrodados")


class MotorSincronizacao:
    def __init__(self, caminho_mapeamento=None):
        self.mapeamento = self._carregar_mapeamento(
            caminho_mapeamento or config.ARQUIVO_MAPEAMENTO
        )
        self.origem = adapters.AdaptadorSqliteOrigem(config.BANCO_ORIGEM)
        self.destino = adapters.AdaptadorSqliteDestino(config.BANCO_DESTINO)
        self.auditoria = Auditoria(config.BANCO_LOG)

    def _carregar_mapeamento(self, caminho):
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)

    def sincronizar(self, reset=False):
        self.destino.preparar_esquema(reset=reset)
        id_execucao = self.auditoria.abrir_execucao()

        total = {"lidos": 0, "migrados": 0, "ignorados": 0, "rejeitados": 0}

        # A ordem importa: os departamentos vao primeiro porque os
        # funcionarios dependem do mapa de departamentos ja existir.
        ordem = ["departamentos", "funcionarios"]

        for nome_tabela in ordem:
            definicao = self.mapeamento[nome_tabela]
            self._sincronizar_tabela(id_execucao, definicao, total)

        self._exportar_outros_formatos()

        self.auditoria.fechar_execucao(
            id_execucao,
            total["lidos"],
            total["migrados"],
            total["ignorados"],
            total["rejeitados"],
        )

        return total

    def _sincronizar_tabela(self, id_execucao, definicao, total):
        origem_tabela = definicao["origem_tabela"]
        destino_tabela = definicao["destino_tabela"]
        chave_natural = definicao["chave_natural"]
        campos = definicao["campos"]

        contexto = {"mapa_departamentos": self.destino.mapa_departamentos()}

        registros = self.origem.ler(origem_tabela)

        for registro in registros:
            total["lidos"] += 1

            # 1. Valida antes de qualquer coisa
            problemas = validator.validar_registro(registro, campos)
            if problemas:
                total["rejeitados"] += 1
                chave = str(registro.get(campos[0]["origem"], "?"))
                motivo = "; ".join(problemas)
                self.auditoria.registrar(
                    id_execucao, destino_tabela, chave, "rejeitado", motivo
                )
                logger.warning("Rejeitado [%s]: %s", chave, motivo)
                continue

            # 2. Transforma para o formato do destino
            transformado = transformer.transformar_registro(
                registro, campos, contexto
            )
            chave = str(transformado.get(chave_natural, "?"))

            # 3. Sincronizacao incremental: ja existe? entao ignora
            existente = self.destino.buscar_por_chave(
                destino_tabela, chave_natural, transformado[chave_natural]
            )
            if existente:
                total["ignorados"] += 1
                self.auditoria.registrar(
                    id_execucao,
                    destino_tabela,
                    chave,
                    "ignorado",
                    "registro ja existe no destino",
                )
                logger.info("Ignorado [%s]: ja sincronizado", chave)
                continue

            # 4. Grava no destino
            self.destino.inserir(destino_tabela, transformado)
            total["migrados"] += 1
            self.auditoria.registrar(
                id_execucao, destino_tabela, chave, "migrado", "ok"
            )
            logger.info("Migrado [%s]", chave)

            # Atualiza o mapa de departamentos logo apos inserir um deles,
            # para que os funcionarios consigam resolver o id em seguida.
            if destino_tabela == "departamentos":
                contexto["mapa_departamentos"] = self.destino.mapa_departamentos()

    def _exportar_outros_formatos(self):
        """Gera as saidas em JSON e CSV a partir do que foi gravado no destino."""
        funcionarios = self.destino.listar("funcionarios")
        adapters.exportar_json(funcionarios, config.SAIDA_JSON)
        adapters.exportar_csv(funcionarios, config.SAIDA_CSV)
