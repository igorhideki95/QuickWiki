# NEXT SESSION

Data: 2026-03-25
Fase: base funcional consolidada

## Contexto rapido

O QuickWiki ja consegue carregar perfis declarativos, executar crawl, extrair conteudo, baixar assets, gerar espelho offline e operar via GUI local.

## Fazer primeiro

Escolher a primeira frente de robustez operacional: validacao de perfis, observabilidade ou UX da GUI.

## Tarefas sugeridas

- [ ] revisar o fluxo de validacao de perfis e mensagens de erro
- [ ] mapear os eventos e metricas minimas da GUI e do crawler
- [ ] revisar o resumo final de execucao e artefatos de diagnostico
- [ ] consolidar criterios de aceite para novos perfis
- [ ] priorizar melhorias de UX para crawls longos

## Arquivos centrais

- `run_scraper.py`
- `scraper/crawler.py`
- `scraper/site_profiles.py`
- `scraper/gui_server.py`
- `DOCUMENTACAO_TECNICA.md`
- `Plan.md`

## Riscos conhecidos

- perfis mal definidos ainda podem gerar falhas dificeis de diagnosticar
- o backlog tecnico historico estava espalhado em documentos com objetivos diferentes
- operacao longa ainda pode exigir feedback visual e logs mais orientados a suporte

