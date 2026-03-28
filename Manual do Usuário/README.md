# Manual do Usuario - QuickWiki

> Guia pratico para instalar, validar e usar o QuickWiki pelo fluxo mais simples e confiavel da versao publica.

## Melhor forma de abrir

Se quiser a versao visual do manual, abra:

- `index.html`

## Trilha recomendada

1. Abra `01 - Instalacao e Preparacao.md`
2. Depois leia `06 - QuickWiki Studio.md`
3. Use `02 - Primeiro Espelho.md` para o primeiro teste controlado
4. Consulte `03 - Perfis, Validacao e Modos.md` para entender os perfis oficiais e os modos avancados
5. Use `04 - Navegacao Offline.md` para revisar a saida
6. Se algo falhar, va para `05 - Problemas Comuns.md`

## Fluxo rapido

```bash
python -m pip install .
python -m quickwiki --validate-site-profiles
python -m quickwiki --gui
```

Quando `quickwiki` ja estiver disponivel no `PATH`, voce tambem pode usar:

```bash
quickwiki --validate-site-profiles
quickwiki --gui
```

## O que voce vai aprender

- como preparar o ambiente;
- como comecar pelo fluxo mais confiavel com `python -m quickwiki`;
- como usar o comando canonico `quickwiki` quando ele ja estiver disponivel no `PATH`;
- como validar os perfis built-in oficiais;
- como usar perfis externos pela CLI quando precisar de um caso mais avancado;
- como rodar um espelho de teste;
- como abrir e navegar no resultado offline;
- como ler os artefatos `summary.json`, `run_report.json` e `runtime_status.json`.

## Estrutura desta pasta

- `index.html`
- `manual.css`
- `01-instalacao.html`
- `02-primeiro-espelho.html`
- `03-perfis-validacao-modos.html`
- `04-navegacao-offline.html`
- `05-problemas-comuns.html`
- `06-gui-studio.html`
- `01 - Instalacao e Preparacao.md`
- `02 - Primeiro Espelho.md`
- `03 - Perfis, Validacao e Modos.md`
- `04 - Navegacao Offline.md`
- `05 - Problemas Comuns.md`
- `06 - QuickWiki Studio.md`

## Observacao importante

Este manual considera:

- o primeiro uso com `python -m quickwiki`;
- o comando canonico `quickwiki` quando ele ja estiver disponivel no `PATH`;
- a compatibilidade com `python run_scraper.py`;
- o modelo source-first, com `QUICKWIKI_ROOT` quando voce quiser apontar para um checkout especifico ou caminhos customizados;
- os perfis built-in como suporte oficial da v1;
- os perfis externos como modo avancado via CLI;
- a GUI local `QuickWiki Studio`;
- os artefatos operacionais `runtime_status.json` e `run_report.json`.
