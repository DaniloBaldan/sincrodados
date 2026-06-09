"""
Configuracoes centrais do SincroDados.

Aqui ficam os caminhos dos bancos de origem e destino, do log de
sincronizacao e dos arquivos de saida. Centralizar isso em um unico
lugar evita ter caminho espalhado pelo codigo.
"""

import os

# Pasta raiz do projeto (onde este arquivo esta)
RAIZ = os.path.dirname(os.path.abspath(__file__))

# Pasta onde ficam os bancos e os arquivos gerados
PASTA_DADOS = os.path.join(RAIZ, "dados")

# Banco do Sistema X (origem): RH legado, esquema em ingles
BANCO_ORIGEM = os.path.join(PASTA_DADOS, "sistema_x.db")

# Banco do Sistema Y (destino): RH novo, esquema em portugues e normalizado
BANCO_DESTINO = os.path.join(PASTA_DADOS, "sistema_y.db")

# Banco que guarda o registro de auditoria de cada sincronizacao
BANCO_LOG = os.path.join(PASTA_DADOS, "sincronizacao.db")

# Saidas em outros formatos de armazenamento, exigidas pelo enunciado
SAIDA_JSON = os.path.join(PASTA_DADOS, "funcionarios.json")
SAIDA_CSV = os.path.join(PASTA_DADOS, "funcionarios.csv")

# Arquivo de mapeamento declarativo entre os esquemas
ARQUIVO_MAPEAMENTO = os.path.join(RAIZ, "mapeamento.json")


def garantir_pasta_dados():
    """Cria a pasta de dados caso ela ainda nao exista."""
    os.makedirs(PASTA_DADOS, exist_ok=True)
