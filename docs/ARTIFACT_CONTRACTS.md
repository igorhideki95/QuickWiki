# Artifact Contracts

## Objetivo

Documentar os artefatos publicos gerados pelo QuickWiki para que a v1 tenha contratos estaveis, publicos e aditivos.

## Politica de versao

- todo artefato publico recebe `schema_version`
- todo artefato publico recebe `quickwiki_version`
- quando aplicavel, o payload tambem registra `generated_at`
- mudancas futuras devem preservar chaves existentes e adicionar apenas campos novos

## Artefatos principais

### `summary.json`

- resumo consolidado da execucao
- deve conter a contagem final de paginas, assets, falhas e grupos de duplicacao
- deve incluir metadados de versao e geracao

### `run_report.json`

- relatorio estruturado da execucao para GUI, docs e automacao
- deve incluir `health`, `summary`, `stats` e `artifacts`
- deve apontar os caminhos dos artefatos relevantes do output

### `profile_diagnostics.json`

- diagnostico do perfil ativo e dos seletores carregados
- deve ajudar a investigar problemas de configuracao sem ler o log bruto

### `pages_manifest.json`

- manifesto indexado das paginas salvas
- deve manter a lista de paginas sob `pages`
- deve incluir metadados de schema e versao do produto

### `failed_pages.json`

- resumo das paginas que falharam
- deve manter a lista detalhada de URLs e razoes, alem do agregado de falhas

### `runtime_status.json`

- status vivo da execucao em andamento
- deve ser seguro para leitura pela GUI e por automacoes locais

## Regras de compatibilidade

- o contrato v1 e additive-only
- chaves antigas nao devem ser removidas sem uma nova versao de schema
- a documentacao deve tratar qualquer mudanca quebradora como mudanca de familia de schema, nao como ajuste menor

## Consumo recomendado

- GUI local `QuickWiki Studio`
- espelho offline em `output/index.html`
- painel administrativo em `output/admin/index.html`
- automacoes externas e verificacoes de release
