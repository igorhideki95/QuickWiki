# QuickWiki Docs

## Objetivo do hub

Concentrar a documentacao executiva, tecnica, operacional e de governanca do QuickWiki em um unico ponto de entrada.

## Estado atual

- produto validado localmente em modo source-first e em modo instalado por modulo
- CI com testes, build de distribuicao, `twine check` e smoke de entrypoints
- perfis built-in bundled no pacote para reduzir dependencia da raiz do repositorio
- documentacao de contribuicao, seguranca e release pronta para repositorio publico

## Ordem de leitura recomendada

1. [`../README.md`](../README.md) para a visao geral do projeto.
2. [`STATUS.md`](./STATUS.md) para o retrato atual da release.
3. [`RELEASE_CHECKLIST.md`](./RELEASE_CHECKLIST.md) para o gate final de publicacao.
4. [`ROADMAP.md`](./ROADMAP.md) para milestones e backlog.
5. [`ARTIFACT_CONTRACTS.md`](./ARTIFACT_CONTRACTS.md) para os contratos publicos dos artefatos.
6. [`PROFILE_SCHEMA.md`](./PROFILE_SCHEMA.md) para a base versionada de perfis.
7. [`DECISIONS.md`](./DECISIONS.md) para escolhas estruturais registradas.
8. [`NEXT_SESSION.md`](./NEXT_SESSION.md) para retomada de contexto.
9. [`../DOCUMENTACAO_TECNICA.md`](../DOCUMENTACAO_TECNICA.md) para analise tecnica detalhada.
10. [`../Manual do Usuario/README.md`](../Manual%20do%20Usu%C3%A1rio/README.md) para onboarding operacional.
11. [`../CONTRIBUTING.md`](../CONTRIBUTING.md) para o fluxo de colaboracao.
12. [`../SECURITY.md`](../SECURITY.md) para a trilha de reporte responsavel.
13. [`../SUPPORT.md`](../SUPPORT.md) para orientacoes de uso e suporte.
14. [`../CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) para a etiqueta publica do repositorio.
15. [`../CHANGELOG.md`](../CHANGELOG.md) para historico de evolucao.

## Areas principais do codigo

- `../quickwiki/`: package entrypoint para `python -m quickwiki`
- `../run_scraper.py`: CLI principal e bootstrap da execucao
- `../scraper/`: crawler, storage, GUI, utilitarios e recursos bundled
- `../profiles/`: perfis declarativos do checkout source-first
- `../schemas/`: contratos auxiliares para validacao e extensibilidade
- `../tests/`: suite automatizada
- `../Manual do Usuario/`: guia navegavel de uso

## Regra de manutencao

Ao concluir uma mudanca relevante, revisar pelo menos:

- `STATUS.md`
- `RELEASE_CHECKLIST.md`
- `ROADMAP.md`
- `NEXT_SESSION.md`
- `DECISIONS.md`, quando houver decisao estrutural
- `../CHANGELOG.md`
