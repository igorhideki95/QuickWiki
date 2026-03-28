# QuickWiki

[![CI](https://github.com/igorhideki95/QuickWiki/actions/workflows/ci.yml/badge.svg)](https://github.com/igorhideki95/QuickWiki/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)

Offline wiki mirror for MediaWiki/Fandom with declarative profiles, local GUI, and navigable HTML/JSON outputs.

README principal em pt-BR, com um resumo curto em ingles para visitantes internacionais.

## English Summary

QuickWiki is a local-first wiki mirroring project designed for auditable offline preservation and portfolio-quality output. It ships with declarative site profiles, a local monitoring GUI, source-first workflows, and documented HTML/JSON artifact contracts.

![QuickWiki Studio Desktop](docs/assets/quickwiki-studio-desktop.png)

## Por que o projeto existe

- preservar conteudo util de wikis em artefatos offline navegaveis
- transformar crawls em saidas HTML e JSON que ajudem auditoria, troubleshooting e showcase tecnico
- reduzir atrito entre CLI, GUI local, packaging e documentacao
- manter um fluxo source-first simples, mas bom o suficiente para distribuicao publica no GitHub

## Inicio em 60 segundos

Requisito minimo: Python 3.11 ou superior.

```bash
git clone https://github.com/igorhideki95/QuickWiki.git
cd QuickWiki
python -m pip install .
python -m quickwiki --validate-site-profiles
python -m quickwiki --list-site-profiles
python -m quickwiki --site-profile tibiawiki_br --max-pages 25
python -m quickwiki --serve-only --output-dir output
```

Para abrir a GUI local:

```bash
python -m quickwiki --gui
```

Entrypoints suportados:

- `quickwiki`
- `python -m quickwiki`
- `python run_scraper.py` para compatibilidade em checkout local

Se `quickwiki` nao for reconhecido no Windows apos a instalacao, use `python -m quickwiki` ou ajuste o `PATH` da pasta `Scripts` do Python do usuario.

Os perfis built-in oficiais tambem funcionam a partir do pacote instalado fora da raiz do repositorio. Use `QUICKWIKI_ROOT`, `--profiles-dir` ou `--site-profile-file` quando quiser apontar para um checkout especifico, perfis externos ou caminhos customizados.

## O que o QuickWiki entrega

- crawl offline com foco em MediaWiki e Fandom
- perfis declarativos versionados por wiki
- GUI local `QuickWiki Studio` para iniciar, acompanhar e validar execucoes
- artefatos HTML e JSON prontos para navegacao, auditoria e troubleshooting
- contratos de artefatos e schema de perfis documentados no proprio repositorio
- instalacao source-first com packaging validado fora da raiz do projeto

## Artefatos gerados

Uma execucao tipica produz:

- `output/index.html`
- `output/admin/index.html`
- `output/data/indexes/summary.json`
- `output/data/indexes/run_report.json`
- `output/checkpoints/runtime_status.json`
- `output/data/indexes/pages_manifest.json`
- `output/data/indexes/failed_pages.json`
- `output/logs/scraper.log`

## Destaques de portfolio

- arquitetura separada entre CLI, crawler, storage, GUI e contratos publicos
- release gate automatizado em Windows e Ubuntu com build, `twine check`, testes e smoke dos entrypoints
- smoke do pacote instalado fora da raiz do repositorio para provar distribuicao real
- perfis built-in bundled na distribuicao para reduzir dependencia do checkout source-first
- documentacao de produto, operacao, contribuicao, seguranca e suporte no proprio repo
- interface local com foco em observabilidade de runtime e navegacao do output

## Capturas da interface

![QuickWiki Studio Mobile](docs/assets/quickwiki-studio-mobile.png)

## Validacao publica

Validado em 2026-03-28:

- `python -m unittest discover -s tests -v`
- `python -m compileall run_scraper.py quickwiki scraper tests`
- `python -m build`
- `python -m twine check dist/*`
- `python -m pip install .`
- `python -m quickwiki --version`
- `python -m quickwiki --list-site-profiles`
- `python -m quickwiki --validate-site-profiles`
- smoke crawl curto com perfil built-in
- smoke de GUI instalada respondendo em `/api/state`
- smoke do modulo instalado fora da raiz do repositorio

## Documentacao

Para entrar rapido:

- [docs/README.md](docs/README.md) para o hub principal
- [Manual do Usuario/README.md](Manual%20do%20Usu%C3%A1rio/README.md) para uso operacional
- [docs/ROADMAP.md](docs/ROADMAP.md) para o backlog visivel

Para referencia tecnica:

- [docs/PROFILE_SCHEMA.md](docs/PROFILE_SCHEMA.md)
- [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md)
- [DOCUMENTACAO_TECNICA.md](DOCUMENTACAO_TECNICA.md)

Para manutencao do projeto:

- [docs/STATUS.md](docs/STATUS.md)
- [docs/NEXT_SESSION.md](docs/NEXT_SESSION.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [SUPPORT.md](SUPPORT.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## Comunidade e manutencao

- os perfis built-in do projeto sao o escopo oficialmente suportado na v1
- perfis externos continuam disponiveis via CLI como modo avancado e preview
- contribuicoes passam a seguir a licenca MIT do projeto
- issues de bug, feature e suporte ficam abertas para a comunidade no GitHub

## O que ainda vale fazer

- publicar uma homepage ou case study externo para reforcar o showcase
- adicionar mais perfis oficiais e uma matriz de compatibilidade por familia de wiki
- melhorar ainda mais a descoberta do `quickwiki` no PATH do Windows para novos usuarios
- ampliar assets de release, social preview e demos visuais do output final

## Licenca

QuickWiki e distribuido sob a licenca [MIT](LICENSE). O projeto pode ser estudado, reutilizado e evoluido pela comunidade, mantendo os creditos e o aviso de licenca.
