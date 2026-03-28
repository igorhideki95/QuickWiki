# QuickWiki - Documentacao Tecnica

## Visao geral

QuickWiki e um espelhador offline source-first para wikis baseadas em MediaWiki e Fandom. O projeto foi desenhado para transformar conteudo publico em artefatos locais navegaveis, com trilha de operacao clara por CLI, GUI local e contratos JSON versionados.

Os objetivos tecnicos da v1 sao:

- espelhar conteudo com navegacao offline consistente;
- manter perfis declarativos para reduzir acoplamento por wiki;
- gerar artefatos publicos estaveis para GUI, automacao e debugging;
- oferecer uma experiencia source-first simples para uso real e para portfolio tecnico.

## Modelo de distribuicao

QuickWiki segue um modelo source-first.

Entrypoints suportados:

- `quickwiki`
- `python -m quickwiki`
- `python run_scraper.py`

Resolucao de recursos:

- quando existe um checkout valido, o projeto usa a raiz do repositorio;
- quando o comando roda fora do checkout, os perfis built-in podem ser carregados da distribuicao empacotada;
- `QUICKWIKI_ROOT` permite apontar explicitamente para uma clone valida;
- atalhos da GUI para docs e manual dependem do checkout completo; quando ele nao existe, a GUI devolve uma pagina explicativa em vez de falhar silenciosamente.

## Fluxo de execucao

1. A CLI interpreta argumentos e resolve o modelo de execucao.
2. O QuickWiki localiza os perfis declarativos disponiveis.
3. O crawler inicializa fila, checkpoint, rate limiting e estado de runtime.
4. O fetch tenta HTML direto e usa fallback via MediaWiki API quando necessario.
5. O extractor limpa o DOM e transforma a pagina em uma estrutura canonica.
6. O pipeline de assets baixa, deduplica e reescreve referencias para uso offline.
7. O storage persiste paginas, indices derivados, painel admin e landing page.
8. A GUI consome os artefatos gerados e acompanha a execucao em tempo real.

## Modulos principais

### `run_scraper.py`

Responsavel pela CLI, logging, validacao de perfis, boot da GUI e fluxo principal de execucao.

### `quickwiki/`

Camada de entrada por modulo para suportar `python -m quickwiki`.

### `scraper/paths.py`

Resolve raiz source-first, fallback de perfis empacotados e comportamento orientado por `QUICKWIKI_ROOT`.

### `scraper/site_profiles.py`

Carrega, valida e resolve perfis de wiki. A v1 trabalha com `schema_version` e `wiki_family`, preservando compatibilidade de perfis legados da linha v1.

### `scraper/crawler.py`

Centro operacional do espelhamento:

- BFS concorrente;
- checkpoint;
- retry com backoff;
- respeito a `robots.txt` por padrao;
- bootstrap via MediaWiki API;
- captura opcional de source wiki.

### `scraper/extractor.py`

Extrai titulo, headings, paragrafos, listas, tabelas, links, imagens, categorias e metadados derivados como `excerpt`, `word_count` e `content_hash`.

### `scraper/storage.py`

Persiste paginas, assets e indices e gera a experiencia offline:

- `index.html`
- `admin/index.html`
- `summary.json`
- `run_report.json`
- `runtime_status.json`
- `pages_manifest.json`
- `failed_pages.json`
- `profile_diagnostics.json`

### `scraper/gui_server.py` e `scraper/gui_assets.py`

Implementam a GUI local `QuickWiki Studio`, incluindo validacao de perfis, disparo de execucao, leitura de telemetria, logs e atalhos para espelho e documentacao.

## Perfis declarativos

Os perfis oficiais da v1 sao:

- `tibiawiki_br`
- `tibia_fandom`

Cada perfil declara:

- chave e rotulo publico;
- seed padrao;
- dominios permitidos;
- seletores de titulo e raiz de conteudo;
- regras de limpeza;
- tema visual;
- contrato de schema.

Perfis externos continuam suportados por CLI, mas permanecem como preview avancado na v1.

## Contratos publicos

O QuickWiki expande e documenta contratos publicos versionados em `docs/ARTIFACT_CONTRACTS.md`.

Principios da v1:

- todo artefato publico relevante recebe `schema_version`;
- os payloads publicos expostos para integracao recebem `quickwiki_version`;
- a evolucao prevista para a mesma familia de schema e aditiva;
- GUI, navegacao offline e automacoes devem consumir esses contratos em vez de depender de heuristicas sobre logs.

## Layout de saida

Estrutura principal do mirror:

- `output/index.html`
- `output/admin/index.html`
- `output/data/pages/`
- `output/data/assets/`
- `output/data/indexes/`
- `output/checkpoints/`
- `output/logs/`

Os dados por pagina podem incluir HTML, Markdown, JSON estruturado e, quando habilitado, source wiki.

## Qualidade e validacao

Quality gates atuais:

- `python -m unittest discover -s tests -v`
- `python -m compileall run_scraper.py scraper tests`
- `python -m build`
- `python -m twine check dist/*`
- smoke de `--help`, `--list-site-profiles` e `--validate-site-profiles`
- CI em Windows e Linux

Cobertura automatizada existente:

- runtime do crawler;
- source capture;
- extractor;
- storage;
- GUI server;
- resolucao e validacao de perfis;
- URL utils;
- CLI principal.

## Decisoes de arquitetura que moldam a v1

- multi-wiki por configuracao, nao por forks de codigo;
- CLI e GUI convivem como camadas complementares;
- docs operacionais fazem parte do produto, nao apenas do repositiorio;
- artefatos JSON importantes sao tratados como contrato;
- a distribuicao publica da v1 e source-first, com foco nos perfis built-in.

## Limites conhecidos

- nao ha renderizacao real de JavaScript;
- `crawler.py` e `storage.py` ainda concentram muitas responsabilidades;
- perfis externos nao fazem parte do fluxo guiado da GUI;
- a experiencia mais rica de docs/manual depende do checkout completo do projeto;
- a distribuicao continua source-first; a abertura sob MIT nao muda esse posicionamento tecnico.

## Proximos passos tecnicos

- decompor crawler e storage em componentes menores;
- ampliar a matriz de compatibilidade por familia de wiki;
- endurecer ainda mais a validacao de perfis e o tooling de extensao;
- evoluir a GUI com mais presets e historico local;
- manter os contratos v1 estaveis enquanto o backlog post-v1 cresce.

## Referencias

- `README.md`
- `docs/README.md`
- `docs/STATUS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/ARTIFACT_CONTRACTS.md`
- `docs/PROFILE_SCHEMA.md`
- `Manual do Usuario/README.md`
- `CHANGELOG.md`
