# Release Checklist

## Objetivo

Usar esta lista como gate final para publicar o QuickWiki com qualidade de portfolio e previsibilidade para novos colaboradores.

## Produto e UX

- `README.md` apresenta proposta, screenshots, quickstart e links de docs.
- `Manual do Usuario/` esta consistente com a CLI e com a GUI atual.
- `CHANGELOG.md`, `STATUS.md` e `ROADMAP.md` refletem o estado real do projeto.

## Instalacao e entrypoints

- `python -m pip install .` funciona em ambiente limpo.
- `quickwiki --help` responde corretamente quando o `PATH` estiver configurado.
- `python -m quickwiki --help` funciona fora da raiz do repositorio.
- `python run_scraper.py --help` continua valido como compatibilidade em checkout local.
- `python -m quickwiki --list-site-profiles` lista os perfis built-in bundled.
- `python -m quickwiki --validate-site-profiles` valida os perfis built-in bundled.

## Smoke de uso

- um crawl curto com perfil built-in conclui com sucesso.
- `python -m quickwiki --gui` abre a GUI local.
- `python -m quickwiki --serve-only --output-dir output` expoe o espelho offline.
- `output/index.html` abre sem depender do servidor Python.
- `output/admin/index.html` abre com o resumo operacional.

## Qualidade tecnica

- `python -m unittest discover -s tests -v`
- `python -m compileall run_scraper.py quickwiki scraper tests`
- `python -m build`
- `python -m twine check dist/*`
- smoke do modulo instalado fora da raiz do repositorio

## Governanca de repositorio publico

- `CONTRIBUTING.md` presente e alinhado com o fluxo real do projeto
- `SECURITY.md` presente com canal de reporte
- template de PR presente em `.github/`
- licenca MIT aplicada e reconhecivel pelo GitHub

## Escopo de release

- perfis built-in sao oficialmente suportados na v1
- perfis externos seguem como preview via CLI
- a GUI nao promete fluxo guiado para perfis externos nesta v1
- nao ha executavel standalone de Windows nesta v1
