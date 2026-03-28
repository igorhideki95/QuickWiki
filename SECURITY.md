# Security Policy

## Escopo

QuickWiki e uma ferramenta local de crawling e espelhamento offline. O foco atual de seguranca e:

- evitar exposicao acidental de paths e arquivos fora do workspace esperado
- manter o comportamento local previsivel na GUI e na CLI
- reduzir riscos de packaging quebrado ou distribuicao inconsistente

O repositorio e publico sob licenca MIT, mas vulnerabilidades devem ser reportadas com responsabilidade antes de qualquer divulgacao ampla.

## Como reportar

Canal preferencial:

- GitHub Private Vulnerability Reporting, quando a interface estiver disponivel: `https://github.com/igorhideki95/QuickWiki/security/advisories/new`

Fallback se o link acima nao estiver disponivel na sua conta:

1. nao abra issue publica com detalhes exploraveis
2. abra uma issue publica minima pedindo um canal privado, sem publicar exploit, payload ou passos completos
3. inclua versao, sistema operacional e impacto observado

## O que incluir no relato

- fluxo afetado: `quickwiki`, `python -m quickwiki` ou `python run_scraper.py`
- sistema operacional e versao do Python
- passos minimos de reproducao
- impacto observado e superficie afetada
- se o problema depende de `QUICKWIKI_ROOT`, `--profiles-dir` ou outro caminho customizado

## Expectativa de resposta

- confirmacao inicial em ate 7 dias corridos
- triagem e atualizacoes conforme a severidade e a reproducao
- divulgacao coordenada apos a mitigacao, quando fizer sentido

## Fora de escopo

- problemas em conteudo de terceiros espelhado pelo usuario
- indisponibilidade temporaria de wikis de origem
- comportamento de ambientes alterados manualmente pelo usuario fora do fluxo documentado
