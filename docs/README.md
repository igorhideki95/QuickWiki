# QuickWiki Docs

## Objetivo do hub

Reunir em um unico lugar a documentacao executiva, tecnica e operacional do QuickWiki, apontando quais arquivos sao canonicos para uso diario, manutencao e retomada de contexto.

## Estado atual

- Produto: espelhador offline multi-wiki com GUI local.
- Fase: base funcional consolidada, com foco atual em robustez operacional.
- Stack: Python, crawler assinc, perfis declarativos e frontend estatico gerado.

## Leitura recomendada

1. [`../README.md`](../README.md) para uso rapido.
2. [`STATUS.md`](./STATUS.md) para estado atual.
3. [`ROADMAP.md`](./ROADMAP.md) para fases e backlog.
4. [`NEXT_SESSION.md`](./NEXT_SESSION.md) para retomada.
5. [`DECISIONS.md`](./DECISIONS.md) para decisoes registradas.
6. [`../DOCUMENTACAO_TECNICA.md`](../DOCUMENTACAO_TECNICA.md) para analise tecnica detalhada.
7. [`../Plan.md`](../Plan.md) para checklist historico de implementacao.
8. [`../Manual do Usuario/README.md`](../Manual%20do%20Usu%C3%A1rio/README.md) para onboarding operacional.
9. [`../CHANGELOG.md`](../CHANGELOG.md) para historico de entregas.

## Areas principais do codigo

- `../run_scraper.py`: CLI e bootstrap da execucao.
- `../scraper/`: crawler, extractor, storage, GUI e utilitarios.
- `../profiles/`: perfis declarativos por wiki.
- `../tests/`: suite de testes automatizados.
- `../Manual do Usuario/`: guia navegavel de uso.

## Regra de manutencao

Ao terminar uma evolucao relevante, atualizar:

- `STATUS.md`
- `ROADMAP.md`, se a prioridade mudar
- `NEXT_SESSION.md`
- `DECISIONS.md`, se houve escolha estrutural
- `../CHANGELOG.md`
