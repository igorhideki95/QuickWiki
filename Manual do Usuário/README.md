# Manual do Usuário — QuickWiki

> Guia simples, direto e organizado para usar o QuickWiki do zero.

## Melhor forma de abrir

Se quiser a versão mais bonita e navegável do manual, abra:

- `index.html`

## Trilha recomendada hoje

Se você quer o fluxo mais prático para começar sem atrito, siga esta ordem:

1. Abra `01 - Instalação e Preparação.md`
2. Depois leia `06 - QuickWiki Studio.md`
3. Use `02 - Primeiro Espelho.md` para o primeiro teste controlado
4. Consulte `03 - Perfis, Validação e Modos.md` quando quiser personalizar a execução
5. Use `04 - Navegação Offline.md` para revisar a saída
6. Se algo falhar, vá para `05 - Problemas Comuns.md`

## Fluxo rápido

```bash
python -m pip install -r requirements.txt
python run_scraper.py --validate-site-profiles
python run_scraper.py --gui
```

## O que você vai aprender

- como preparar o ambiente;
- como validar os perfis do projeto;
- como usar a GUI local QuickWiki Studio;
- como rodar um espelho de teste;
- como abrir e navegar no resultado offline;
- como resolver os problemas mais comuns.

## Estrutura desta pasta

- `index.html`
- `manual.css`
- `01-instalacao.html`
- `02-primeiro-espelho.html`
- `03-perfis-validacao-modos.html`
- `04-navegacao-offline.html`
- `05-problemas-comuns.html`
- `06-gui-studio.html`
- `01 - Instalação e Preparação.md`
- `02 - Primeiro Espelho.md`
- `03 - Perfis, Validação e Modos.md`
- `04 - Navegação Offline.md`
- `05 - Problemas Comuns.md`
- `06 - QuickWiki Studio.md`

## Observação importante

Este manual já considera:

- a identidade `QuickWiki`;
- o comando `--validate-site-profiles`;
- a GUI local `QuickWiki Studio`;
- o fluxo de espelho offline já presente no sistema.
