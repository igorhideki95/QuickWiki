# NEXT SESSION

Data: 2026-03-28
Fase: repositorio publico no ar, release `v1.0.0` publicada e backlog pos-lancamento aberto

## Nota

Este arquivo e para retomada do mantenedor. Ele nao faz parte do onboarding principal do usuario final.

## Contexto rapido

O QuickWiki ja esta publico no GitHub, sob MIT, com packaging source-first, GUI local, output offline, contratos publicos versionados, smoke de instalacao com `quickwiki`, fallback por `python -m quickwiki`, crawl curto validado localmente e release `v1.0.0` publicada.

## Fazer primeiro

Escolher o proximo ganho externo entre homepage ou case study, social preview de release e ampliacao dos perfis oficiais.

## Tarefas sugeridas

- [ ] publicar uma homepage ou case study externo para o projeto
- [ ] montar uma matriz de compatibilidade por familia de wiki
- [ ] ampliar a suite de smoke com mais cenarios de crawl curto
- [ ] avaliar melhoria futura para descoberta do `quickwiki` no PATH do Windows
- [ ] produzir assets visuais extras para a proxima release publica

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
