# SincroDados

Ferramenta de migracao e sincronizacao de dados entre dois sistemas de RH
com esquemas e formatos diferentes. Projeto Integrador do curso de Analise
e Desenvolvimento de Sistemas.

O Sistema X representa um RH legado, com banco SQLite, nomes de coluna em
ingles, salario guardado como texto, data no padrao ISO e status como 0 ou
1. A ferramenta le esses dados, valida, converte para o formato padrao do
Sistema Y (nomes em portugues, tipos corretos, datas no padrao brasileiro)
e grava no destino, alem de exportar tambem em JSON e CSV.

## O que a ferramenta faz

- Extrai os dados do Sistema X (SQLite).
- Valida cada registro, com checagem dos digitos do CPF, do email e do salario.
- Converte os campos seguindo um mapeamento declarativo (mapeamento.json).
- Grava no Sistema Y (SQLite) e exporta em JSON e CSV.
- Faz sincronizacao incremental: registro que ja existe nao e gravado de novo.
- Registra a auditoria de cada execucao e o destino de cada registro.
- Mostra tudo em um painel web.

## Como rodar

Requer Python 3.10 ou mais novo.

```bash
pip install -r requirements.txt

python main.py init      # cria e popula o Sistema X, zera o destino
python main.py sync      # executa a sincronizacao
python main.py status    # mostra o resumo da ultima execucao
python main.py rejeitados   # lista os registros recusados, com o motivo
python main.py painel    # sobe o painel web em http://127.0.0.1:5000
```

Rodar `python main.py sync` uma segunda vez demonstra a idempotencia:
nenhum registro novo e gravado, porque todos ja existem no destino.

## Testes

```bash
pytest -v
```

## Estrutura

```
sincrodados/
  main.py               linha de comando
  config.py             caminhos e configuracoes
  mapeamento.json       mapeamento declarativo entre os esquemas
  seed_data.py          cria e popula o Sistema X
  src/
    adapters.py         leitura e escrita (SQLite, JSON, CSV)
    validator.py        regras de validacao e checagem de CPF
    transformer.py      conversao dos campos
    audit.py            registro de auditoria
    engine.py           orquestracao da sincronizacao
  dashboard/
    app.py              painel web em Flask
    templates/index.html
  tests/                testes com pytest
  dados/                bancos e arquivos gerados
```
