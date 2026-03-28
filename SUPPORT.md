# Suporte do QuickWiki

## Onde pedir ajuda

O melhor lugar para pedir ajuda e o proprio GitHub do projeto, abrindo uma issue com contexto suficiente para reproducao.

Use:

- `Bug report` para falhas, erros de execucao e comportamento inesperado;
- `Feature request` para melhorias, ideias e novas integracoes;
- `Support` apenas quando a duvida for de uso, configuracao ou entendimento do fluxo.

## O que ajuda muito

Inclua sempre que possivel:

- sistema operacional;
- versao do Python;
- comando executado;
- perfil usado;
- se a execucao foi via `quickwiki`, `python -m quickwiki` ou `python run_scraper.py`;
- trecho do log ou mensagem de erro;
- o que voce esperava ver.

## O que nao e suporte

Este repositorio nao promete atendimento em tempo real, SLA ou consultoria personalizada. O foco e manter um projeto publico bem documentado e util para a comunidade sob licenca MIT.

## Primeiro passo recomendado

Antes de abrir uma issue, confira:

- `README.md`
- `docs/README.md`
- `docs/RELEASE_CHECKLIST.md`
- `Manual do Usuario/README.md`

Muitas duvidas de uso ja aparecem nesses documentos.

## Se a duvida for sobre a sua execucao local

Verifique primeiro:

- se a instalacao foi feita com `python -m pip install .`;
- se `quickwiki --help` responde ou se `python -m quickwiki --help` funciona;
- se os perfis embutidos foram listados com `quickwiki --list-site-profiles`;
- se existe algum `QUICKWIKI_ROOT` ou `--profiles-dir` customizado afetando a execucao.
