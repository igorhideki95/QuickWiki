# NEXT SESSION

Data: 2026-03-28
Fase: publicacao externa concluida localmente e backlog post-v1

## Contexto rapido

O QuickWiki ja tem packaging source-first, GUI local, output offline, contratos publicos versionados, smoke de instalacao com `quickwiki`, fallback por `python -m quickwiki`, crawl curto validado localmente e licenca MIT aplicada para publicacao aberta.

## Fazer primeiro

Registrar a publicacao externa da v1 e seguir para backlog post-v1 sem reabrir contratos publicos.

## Tarefas sugeridas

- [ ] registrar a publicacao externa da v1 em `STATUS`, `CHANGELOG` e `DECISIONS`, se surgir alguma decisao estrutural nova
- [ ] aproveitar a base de `schema_version` e `wiki_family` para abrir a matriz de compatibilidade por familia de wiki
- [ ] planejar a decomposicao futura de crawler e storage sem quebrar os contratos v1
- [ ] avaliar melhoria futura para descoberta do `quickwiki` no PATH do Windows sem depender de ajuste manual

## Arquivos centrais

- `README.md`
- `docs/README.md`
- `docs/ROADMAP.md`
- `docs/ARTIFACT_CONTRACTS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/STATUS.md`
- `docs/DECISIONS.md`
- `Manual do Usuario/README.md`

## Riscos conhecidos

- artefatos publicos precisam manter compatibilidade aditiva
- perfis externos devem permanecer claramente marcados como preview para nao virar promessa de suporte oficial
- a decomposicao de crawler e storage precisa preservar os contratos publicos da v1
