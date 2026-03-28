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

## D-005 - Diagnostico operacional deve sair como artefato de produto, nao so como log

- Data: 2026-03-27
- Decisao: persistir `runtime_status.json` durante a execucao e gerar `run_report.json` ao final, com saude, falhas e atalhos para artefatos.
- Motivo: logs puros nao respondem rapido o suficiente se o crawl esta saudavel, parcial ou quebrado; o operador precisa de um resumo estruturado reaproveitavel pela GUI e pelo output offline.

## D-006 - A v1 publica sera source-first e centrada nos perfis built-in

- Data: 2026-03-27
- Decisao: documentar `quickwiki` como comando canonico, manter `python run_scraper.py` como compatibilidade e tratar perfis externos como preview via CLI.
- Motivo: reduz atrito de onboarding sem ampliar a promessa de suporte alem do escopo oficial da v1.

## D-007 - Artefatos publicos precisam de contrato versionado e evolucao aditiva

- Data: 2026-03-27
- Decisao: registrar `schema_version` e `quickwiki_version` nos artefatos publicos e documentar que mudancas futuras devem ser aditivas dentro da mesma familia de schema.
- Motivo: isso protege integracoes com GUI, automacao, navegacao offline e ferramentas externas.

## D-008 - Perfis declarativos passam a ter schema versionado e familia explicita

- Data: 2026-03-27
- Decisao: adicionar `schema_version` e `wiki_family` aos perfis declarativos, aceitar legado sem `schema_version` como v1 e registrar um schema JSON dedicado em `schemas/`.
- Motivo: isso prepara a matriz de compatibilidade, futuras automacoes de validacao e novas features de onboarding sem quebrar perfis existentes.

## D-009 - Instalacao source-first deve ter fallback por modulo e mensagem explicita de raiz

- Data: 2026-03-27
- Decisao: manter `quickwiki` como comando canonico, adicionar `python -m quickwiki` como fallback sem depender do `PATH` e orientar `QUICKWIKI_ROOT` quando a execucao acontecer fora da clone do projeto.
- Motivo: isso reduz atrito no Windows, deixa o modelo source-first mais explicito e evita erros confusos quando o repositorio nao esta sendo executado da raiz esperada.

## D-010 - A abertura publica do QuickWiki adota licenca MIT

- Data: 2026-03-28
- Decisao: publicar o repositorio e o pacote sob licenca MIT, alinhando `LICENSE`, metadata do pacote e documentacao publica.
- Motivo: isso preserva o valor de portfolio do projeto, reduz friccao para estudo e reuso e deixa a mensagem juridica coerente com a intencao de abertura comunitaria.
