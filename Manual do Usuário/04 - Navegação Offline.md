# 04 - Navegacao Offline

## Objetivo

Aprender onde o QuickWiki grava o espelho e como navegar pelo resultado.

## Arquivos principais

Depois de uma execucao bem-sucedida, os pontos mais importantes sao:

- `output/index.html`
- `output/admin/index.html`
- `output/data/indexes/summary.json`
- `output/data/indexes/run_report.json`
- `output/checkpoints/runtime_status.json`
- `output/data/indexes/pages_manifest.json`
- `output/logs/scraper.log`

## Jeito mais simples de abrir

Use:

```bash
quickwiki --serve-only --output-dir output
```

Depois abra:

- `http://127.0.0.1:8765/index.html`

## O que existe na home offline

Na home voce encontra:

- busca local;
- filtros por categoria;
- links para manifesto, backlinks, categorias, duplicados e falhas;
- acesso ao painel administrativo;
- referencia para o resumo da execucao.

## O que existe no painel admin

Em `output/admin/index.html` voce encontra:

- dados do perfil ativo;
- seletores configurados;
- atalhos para arquivos de diagnostico;
- resumo do estado do espelho;
- informacoes sobre `run_report.json` e `runtime_status.json`.

## Onde estao as paginas e assets

- paginas HTML: `output/data/pages/html/`
- paginas Markdown: `output/data/pages/markdown/`
- paginas JSON: `output/data/pages/json/`
- source wiki: `output/data/pages/source/`
- assets: `output/data/assets/`

## Dica pratica

Se voce quer revisar rapidamente se o crawl ficou bom, normalmente basta abrir:

1. `output/index.html`
2. `output/admin/index.html`
3. `output/data/indexes/summary.json`
4. `output/data/indexes/run_report.json`

## Proximo passo

Abra `05 - Problemas Comuns.md`.
