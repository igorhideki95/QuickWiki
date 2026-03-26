# Plan.md — Execução do QuickWiki

Este plano operacionaliza a especificação de `isso que queremos.md` e agora também reflete a camada visual de operação do produto.

## 1. Crawling completo (BFS)

- [x] Descoberta automática de páginas `/wiki/`
- [x] Fila FIFO + conjunto de visitadas
- [x] Canonicalização de URLs
- [x] Ignorar âncoras e parâmetros irrelevantes

## 2. Extração de conteúdo

- [x] Título `h1`
- [x] Hierarquia `h2-h6`
- [x] Parágrafos, listas, citações e blocos de código
- [x] Tabelas para JSON
- [x] Infoboxes como objetos estruturados
- [x] Templates detectados por classes
- [x] Links internos e externos separados

## 3. Download de assets

- [x] Download de imagens com fallback (original/thumbnail)
- [x] Resolução de URL relativa para absoluta
- [x] Deduplicação por hash SHA-256
- [x] Bucketização (`images`, `items`, `monsters`, `maps`)

## 4. Normalização e transformação

- [x] Limpeza de ruído (script/style/UI)
- [x] Export para HTML limpo e Markdown
- [x] JSON estruturado por página
- [x] Reescrita de links para navegação offline

## 5. Armazenamento organizado e fast opening

- [x] Estrutura por shards para reduzir custo de diretórios gigantes
- [x] Índices (`manifest`, `graph`, `assets`, `summary`)
- [x] `index.html` local para abertura rápida

## 6. Controle e execução resiliente

- [x] Rate limit configurável
- [x] Retry com backoff exponencial
- [x] Logs de progresso/erro
- [x] Checkpoint para retomar após interrupção

## 7. Experiência visual e operação guiada

- [x] GUI local `QuickWiki Studio`
- [x] Início de execução por formulário visual
- [x] Validação de perfis pela interface
- [x] Leitura de estado e logs em tempo real
- [x] Atalhos para espelho, admin, resumo e manual
- [x] Manual do usuário alinhado com a GUI

## 8. Estado atual

- [x] Implementação completa do pipeline em `run_scraper.py` + `scraper/*`
- [x] Interface visual local integrada ao fluxo principal
- [x] Documentação principal, manual e changelog alinhados com a operação atual
