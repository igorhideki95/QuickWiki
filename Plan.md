# Plan.md - Execucao do QuickWiki

Este plano registra a implementacao operacional do QuickWiki e a camada visual de operacao do produto.

## 1. Crawling completo (BFS)

- [x] Descoberta automatica de paginas `/wiki/`
- [x] Fila FIFO + conjunto de visitadas
- [x] Canonicalizacao de URLs
- [x] Ignorar ancoras e parametros irrelevantes

## 2. Extracao de conteudo

- [x] Titulo `h1`
- [x] Hierarquia `h2-h6`
- [x] Paragrafos, listas, citacoes e blocos de codigo
- [x] Tabelas para JSON
- [x] Infoboxes como objetos estruturados
- [x] Templates detectados por classes
- [x] Links internos e externos separados

## 3. Download de assets

- [x] Download de imagens com fallback (original/thumbnail)
- [x] Resolucao de URL relativa para absoluta
- [x] Deduplicacao por hash SHA-256
- [x] Bucketizacao (`images`, `items`, `monsters`, `maps`)

## 4. Normalizacao e transformacao

- [x] Limpeza de ruido (script/style/UI)
- [x] Export para HTML limpo e Markdown
- [x] JSON estruturado por pagina
- [x] Reescrita de links para navegacao offline

## 5. Armazenamento organizado e fast opening

- [x] Estrutura por shards para reduzir custo de diretorios gigantes
- [x] Indices (`manifest`, `graph`, `assets`, `summary`)
- [x] `index.html` local para abertura rapida

## 6. Controle e execucao resiliente

- [x] Rate limit configuravel
- [x] Retry com backoff exponencial
- [x] Logs de progresso/erro
- [x] Checkpoint para retomar apos interrupcao

## 7. Experiencia visual e operacao guiada

- [x] GUI local `QuickWiki Studio`
- [x] Inicio de execucao por formulario visual
- [x] Validacao de perfis pela interface
- [x] Leitura de estado e logs em tempo real
- [x] Atalhos para espelho, admin, resumo e manual
- [x] Manual do usuario alinhado com a GUI

## 8. Estado atual

- [x] Implementacao completa do pipeline em `run_scraper.py` + `scraper/*`
- [x] Interface visual local integrada ao fluxo principal
- [x] Documentacao principal, manual e changelog alinhados com a operacao atual
