# Decisions

## D-001 - O projeto sera multi-wiki por configuracao, nao por fork de codigo

- Data: 2026-03-25
- Decisao: concentrar diferencas em perfis declarativos carregados pelo projeto.
- Motivo: isso reduz acoplamento, aumenta reaproveitamento e deixa a base mais escalavel para novas wikis.

## D-002 - A operacao precisa existir tanto por CLI quanto por GUI

- Data: 2026-03-25
- Decisao: manter `run_scraper.py` como ponto de entrada tecnico e `QuickWiki Studio` como camada de onboarding e operacao.
- Motivo: a CLI atende profundidade tecnica; a GUI reduz friccao para uso recorrente.

## D-003 - A documentacao tecnica detalhada continua fora de `docs/`

- Data: 2026-03-25
- Decisao: preservar `DOCUMENTACAO_TECNICA.md` e `Plan.md` na raiz, usando `docs/README.md` como hub de navegacao.
- Motivo: evita mover referencias existentes e melhora organizacao sem quebrar o historico do projeto.

## D-004 - Governanca padronizada passa a fazer parte do projeto

- Data: 2026-03-25
- Decisao: adotar `STATUS`, `ROADMAP`, `NEXT_SESSION` e `DECISIONS` como camada de continuidade.
- Motivo: o projeto ja tem profundidade tecnica suficiente para precisar de um sistema de operacao mais previsivel.
