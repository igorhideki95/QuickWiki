# QuickWiki Docs

## Objetivo do hub

Concentrar a documentacao publica, tecnica e de manutencao do QuickWiki em um unico ponto de entrada.

## Estado atual

- repositorio publico em `https://github.com/igorhideki95/QuickWiki`
- licenca MIT aplicada ao codigo e ao pacote
- release `v1.0.0` como baseline publica do projeto
- CI com testes, build de distribuicao, `twine check` e smoke dos entrypoints
- perfis built-in bundled no pacote para reduzir dependencia da raiz do repositorio

## Leitura publica recomendada

1. [`../README.md`](../README.md) para a visao geral do projeto.
2. [`../Manual do Usuario/README.md`](../Manual%20do%20Usu%C3%A1rio/README.md) para uso operacional.
3. [`ARTIFACT_CONTRACTS.md`](./ARTIFACT_CONTRACTS.md) para os contratos publicos dos artefatos.
4. [`PROFILE_SCHEMA.md`](./PROFILE_SCHEMA.md) para a base versionada de perfis.
5. [`ROADMAP.md`](./ROADMAP.md) para milestones e backlog visivel.
6. [`../DOCUMENTACAO_TECNICA.md`](../DOCUMENTACAO_TECNICA.md) para analise tecnica detalhada.

## Docs de mantenedor

- [`STATUS.md`](./STATUS.md) para o retrato atual da release
- [`RELEASE_CHECKLIST.md`](./RELEASE_CHECKLIST.md) para o gate final de publicacao
- [`DECISIONS.md`](./DECISIONS.md) para escolhas estruturais registradas
- [`NEXT_SESSION.md`](./NEXT_SESSION.md) para retomada de contexto do mantenedor
- [`../CHANGELOG.md`](../CHANGELOG.md) para historico de evolucao
- [`../CONTRIBUTING.md`](../CONTRIBUTING.md) para o fluxo de colaboracao
- [`../SECURITY.md`](../SECURITY.md) para a trilha de reporte responsavel
- [`../SUPPORT.md`](../SUPPORT.md) para orientacoes de uso e suporte
- [`../CODE_OF_CONDUCT.md`](../CODE_OF_CONDUCT.md) para a etiqueta publica do repositorio

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
