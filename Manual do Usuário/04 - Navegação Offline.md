# 04 - Navegação Offline

## Objetivo

Aprender onde o QuickWiki grava o espelho e como navegar pelo resultado.

## Arquivos principais

Depois de uma execução bem-sucedida, os pontos mais importantes são:

- `output/index.html`
- `output/admin/index.html`
- `output/data/indexes/summary.json`
- `output/data/indexes/pages_manifest.json`
- `output/logs/scraper.log`

## Jeito mais simples de abrir

Use:

```bash
python run_scraper.py --serve-only --output-dir output
```

Depois abra:

- `http://127.0.0.1:8765/index.html`

## O que existe na home offline

Na home você encontra:

- busca local;
- filtros por categoria;
- links para manifesto, backlinks, categorias, duplicados e falhas;
- acesso ao painel administrativo.

## O que existe no painel admin

Em `output/admin/index.html` você encontra:

- dados do perfil ativo;
- seletores configurados;
- atalhos para arquivos de diagnóstico;
- resumo do estado do espelho.

## Onde estão as páginas e assets

- páginas HTML: `output/data/pages/html/`
- páginas Markdown: `output/data/pages/markdown/`
- páginas JSON: `output/data/pages/json/`
- source wiki: `output/data/pages/source/`
- assets: `output/data/assets/`

## Dica prática

Se você quer revisar rapidamente se o crawl ficou bom, normalmente basta abrir:

1. `output/index.html`
2. `output/admin/index.html`
3. `output/data/indexes/summary.json`

## Próximo passo

Abra `05 - Problemas Comuns.md`.
