# Security Policy

## Escopo

QuickWiki e uma ferramenta local de crawling e espelhamento offline. O foco atual de seguranca e:

- evitar exposicao acidental de paths e arquivos fora do workspace esperado
- manter o comportamento local previsivel na GUI e na CLI
- reduzir riscos de packaging quebrado ou distribuicao inconsistente

O repositorio e publico sob licenca MIT, mas vulnerabilidades devem continuar sendo reportadas com responsabilidade antes de qualquer divulgacao ampla.

## Como reportar

Se voce identificar uma vulnerabilidade ou um comportamento com risco real:

1. nao abra issue publica com detalhes exploraveis
2. envie um relato privado ao mantenedor com passos de reproducao claros
3. inclua versao, sistema operacional e impacto observado

## Boas praticas de reporte

- informe se o problema depende de `QUICKWIKI_ROOT`
- diga se o fluxo afetado ocorre em `quickwiki`, `python -m quickwiki` ou `python run_scraper.py`
- indique se o risco afeta GUI, packaging, docs locais ou artefatos do crawler

## Fora de escopo

- problemas em conteudo de terceiros espelhado pelo usuario
- indisponibilidade temporaria de wikis de origem
- comportamento de ambientes alterados manualmente pelo usuario fora do fluxo documentado
