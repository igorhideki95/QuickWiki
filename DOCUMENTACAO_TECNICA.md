# QuickWiki — Documentação Técnica e Análise do Projeto

## Situação da documentação atual

O projeto **já possui documentação**, mas ela estava fragmentada e parcialmente operacional:

- `README.md`: descreve a proposta da v3, a instalação, alguns comandos e a estrutura de saída.
- `Plan.md`: registra um checklist de implementação comparando o estado do código com a especificação.
- `isso que queremos.md`: funciona como especificação de produto e escopo desejado, não como documentação do código.

### Conclusão

Há documentação existente, porém ela **não cobre de forma minuciosa**:

- a arquitetura interna;
- o papel de cada módulo;
- o fluxo completo de execução;
- o que os testes realmente validam;
- os riscos, limites e dívidas técnicas;
- um conjunto organizado de sugestões de melhoria.

Este arquivo foi criado para preencher essa lacuna.

## Resumo executivo

`QuickWiki` é um espelhador offline de wikis baseadas em MediaWiki/Fandom, com foco inicial no ecossistema Tibia. O projeto combina:

- descoberta de páginas por BFS;
- fallback de captura via MediaWiki API;
- extração estruturada de conteúdo;
- download e deduplicação de assets;
- persistência em múltiplos formatos;
- geração de um front-end offline navegável;
- perfis declarativos para adaptar o scraper a mais de uma wiki.

No estado atual, a base está funcional e bem encaminhada para uso real, com bons sinais de modularidade. O principal valor da v3 está em **não acoplar o scraper a uma única wiki**, concentrando diferenças em perfis JSON e em seletores configuráveis.

## Escopo funcional encontrado no código

O código implementa as seguintes capacidades principais:

1. Resolver o perfil do site por chave explícita ou por detecção automática do domínio.
2. Iniciar o crawl a partir de uma URL seed e opcionalmente retomar de checkpoint.
3. Respeitar `robots.txt` por padrão.
4. Descobrir páginas por links internos e, em crawl completo, ampliar a cobertura usando a MediaWiki API.
5. Buscar páginas por HTTP direto e cair para a API quando a resposta HTML falha ou é inadequada.
6. Extrair título, headings, parágrafos, listas, citações, blocos de código, tabelas, infoboxes, categorias, links e imagens.
7. Capturar o wikitext da página pela API e registrar URLs de source.
8. Baixar imagens, deduplicar por hash SHA-256 e reescrever o HTML para usar arquivos locais.
9. Salvar cada página em HTML limpo, Markdown, JSON e, quando disponível, `.wiki`.
10. Gerar índices auxiliares para navegação offline, busca, backlinks, categorias, duplicados e falhas.
11. Gerar páginas estáticas de índice e painel administrativo.
12. Validar perfis declarativos pela CLI antes de rodar o crawl.

## Inventário do projeto

### Raiz

- `run_scraper.py`: ponto de entrada CLI.
- `README.md`: visão geral de uso.
- `Plan.md`: checklist de implementação.
- `isso que queremos.md`: especificação original.
- `requirements.txt`: dependências principais.
- `.gitignore`: ignora `output/`, `output-*`, `__pycache__/` e `*.pyc`.

### Diretórios principais

- `scraper/`: núcleo da aplicação.
- `profiles/`: perfis declarativos por wiki.
- `tests/`: suíte de testes unitários.
- `output/` e `output-*`: artefatos de crawls e verificações locais.
- `.test-artifacts/`: diretório temporário usado por testes.

## Dependências

Dependências diretas registradas em `requirements.txt`:

- `beautifulsoup4`
- `httpx`
- `lxml`
- `markdownify`

### Papel das dependências

- `httpx`: cliente HTTP assíncrono.
- `beautifulsoup4` + `lxml`: parsing e limpeza de HTML.
- `markdownify`: conversão de HTML limpo para Markdown.

## Arquitetura geral

O pipeline atual segue esta ordem:

1. `run_scraper.py` interpreta a CLI e monta `ScraperConfig`.
2. O perfil do site é resolvido por `scraper.site_profiles`.
3. `QuickWikiCrawler` inicializa storage, extractor, rate limiter e estado do crawl.
4. O crawler carrega `robots.txt` e, se aplicável, faz bootstrap via MediaWiki API.
5. Workers consomem URLs de uma fila assíncrona.
6. Cada página é obtida por HTTP direto, com fallback via API quando necessário.
7. `PageExtractor` transforma o HTML em `PageDocument`.
8. O crawler tenta capturar o source wiki da página.
9. Assets são baixados, deduplicados e reescritos para uso offline.
10. `StorageManager` persiste os arquivos e índices.
11. No final, são geradas páginas auxiliares, índices derivados e painel admin.

## Mapa de módulos

### `run_scraper.py`

Responsabilidades:

- expor a CLI;
- configurar logging;
- carregar perfis;
- validar perfis declarativos;
- construir `ScraperConfig`;
- executar o crawler;
- opcionalmente servir o diretório offline por HTTP local.

Principais funções:

- `parse_args()`
- `configure_logging()`
- `serve_output()`
- `main()`

Observações:

- A CLI está relativamente madura e cobre execução, retomada, bootstrap, perfis, source capture e modo servidor.
- `--validate-site-profiles` antecipa erros de configuração antes do crawl.
- `--serve-only` evita novo crawl e reaproveita a saída existente.
- O script separa bem a fase de configuração da fase assíncrona de scraping.

### `scraper/config.py`

Responsabilidades:

- encapsular a configuração de execução;
- oferecer defaults sensatos;
- normalizar o diretório de saída;
- decidir quando o bootstrap via API deve ocorrer.

Pontos importantes:

- `should_bootstrap_from_api()` só ativa o bootstrap automático quando `max_pages` não foi definido.
- O dataclass é simples e direto, o que facilita testes e extensão.

### `scraper/site_profiles.py`

Responsabilidades:

- modelar um perfil de wiki;
- carregar perfis JSON;
- validar payloads de perfis antes da materialização;
- resolver automaticamente o perfil pelo domínio da URL;
- expor a lista de perfis disponíveis.

Campos relevantes do perfil:

- `key`
- `label`
- `description`
- `default_seed_url`
- `allowed_domains`
- `allowed_path_prefix`
- `api_path`
- `title_selectors`
- `content_root_selectors`
- `category_selectors`
- `extra_noise_selectors`
- `theme`

Pontos fortes:

- boa separação entre código e configuração;
- validação explícita de payloads durante o carregamento;
- suporte a perfis adicionais via arquivo ou diretório externo;
- construção centralizada das URLs de source.

Pontos de atenção:

- a validação atual é útil, mas ainda não substitui um schema formal versionado;
- erros de perfil agora falham cedo, mas ainda podem evoluir em granularidade e tooling.

### `scraper/url_utils.py`

Responsabilidades:

- canonicalizar URLs internas;
- rejeitar variantes problemáticas;
- transformar URL em slug estável;
- inferir bucket de asset;
- derivar URL de imagem original a partir de thumbnails MediaWiki;
- identificar extensão de arquivo.

Decisões relevantes:

- queries irrelevantes são descartadas para evitar duplicidade;
- URLs fora do domínio permitido são rejeitadas cedo;
- slugs recebem hash curto para reduzir colisão;
- assets são separados por buckets semânticos (`images`, `items`, `monsters`, `maps`).

Trade-off:

- a estratégia de descartar qualquer query remanescente em páginas wiki reduz duplicatas, mas também pode eliminar casos legítimos dependendo da wiki alvo.

### `scraper/models.py`

Responsabilidades:

- modelar os objetos centrais persistidos pelo pipeline.

Estruturas:

- `ImageRecord`: metadados de imagens e vínculo com asset local.
- `PageDocument`: representação canônica de uma página já extraída.

Pontos positivos:

- o `PageDocument` é abrangente e já carrega tudo que o storage e a UI precisam;
- `to_dict()` simplifica a serialização em JSON.

### `scraper/extractor.py`

Responsabilidades:

- localizar a raiz de conteúdo;
- remover ruído;
- extrair estrutura textual e semiestruturada;
- separar links internos e externos;
- mapear imagens;
- produzir HTML limpo, Markdown, hash de conteúdo e metadados.

O que ele extrai hoje:

- título;
- categorias;
- headings `h2` a `h6`;
- parágrafos;
- listas;
- citações;
- blocos de código;
- tabelas;
- infoboxes;
- templates por classes;
- links internos;
- links externos;
- imagens com contexto local;
- `excerpt`, `word_count`, `reading_time_minutes`, `content_hash`.

Pontos fortes:

- limpeza de ruído baseada em seletores padrão mais overrides por perfil;
- reescrita de links internos já na fase de extração;
- saída suficientemente rica para alimentar JSON, Markdown e HTML offline.

Limitações:

- templates são inferidos por classes HTML, o que é útil, mas impreciso;
- não há renderização de JavaScript;
- a lógica de tabelas não tenta preservar `rowspan`, `colspan` ou estruturas mais complexas;
- a extração semântica de infoboxes é funcional, porém rasa.

### `scraper/crawler.py`

Este é o centro operacional do projeto.

Responsabilidades:

- manter o estado do crawl;
- gerenciar fila, visitados e falhas;
- aplicar rate limit;
- baixar páginas e assets;
- fazer fallback via API;
- capturar source wiki;
- acionar checkpoint;
- contabilizar métricas;
- finalizar o espelho.

Principais blocos de lógica:

- `AsyncRateLimiter`: serializa a cadência global de requisições.
- `_bootstrap_state()`: decide seed, retomada e checkpoint.
- `_load_robots()`: carrega e aplica `robots.txt`.
- `_bootstrap_from_mediawiki_api()`: amplia cobertura usando `allpages`.
- `_worker_loop()`: consome a fila concorrente.
- `_process_url()`: fluxo completo de uma URL.
- `_fetch_page_content()`: HTTP direto com fallback pela API.
- `_fetch_page_source()`: captura wikitext por `revisions`.
- `_download_and_rewrite_assets()`: baixa imagens e reescreve referências locais.
- `_requeue_failed_pages_for_retry()`: reprocessa páginas que falharam.

Detalhes importantes do comportamento:

- O crawler tenta HTML direto primeiro, o que preserva a estrutura real da página quando possível.
- Se a resposta falha, não é HTML ou parece bloqueada, tenta montar a página pela MediaWiki API.
- O source wiki é obtido em uma segunda etapa, separada da captura do HTML.
- URLs descobertas pela API podem complementar as extraídas do HTML.
- Downloads de assets possuem cache de tarefas para evitar baixar o mesmo arquivo simultaneamente.

Pontos fortes:

- fallback híbrido HTTP/API;
- retry com backoff;
- checkpoint para retomada;
- métricas úteis de execução;
- reuso de assets por hash e por URL;
- separação consistente entre fetch, extração e persistência.

Limitações e observações:

- não há suporte a renderização real de páginas dependentes de JavaScript;
- a cobertura por API depende de compatibilidade com endpoints MediaWiki;
- a estratégia de template extraction em wikitext é heurística;
- existe uma variável local não utilizada em `_fetch_page_source()` (`normalized_title`), o que é um detalhe pequeno, mas indica limpeza pendente;
- o arquivo está grande e concentra muitas responsabilidades, mesmo com boa organização interna.

### `scraper/storage.py`

Responsabilidades:

- criar a árvore de diretórios;
- persistir páginas e assets;
- manter índices primários;
- gerar índices derivados;
- gerar a home offline e o painel admin;
- reescrever páginas com navegação complementar.

Principais entregas do storage:

- `markdown`, `json`, `html`, `source` por página;
- `url_to_slug.json`;
- `assets_by_hash.json`;
- `assets_by_url.json`;
- `pages_manifest.json`;
- `link_graph.json`;
- `backlinks.json`;
- `categories.json`;
- `duplicate_content.json`;
- `failed_pages.json`;
- `search_index.js`;
- `profile_diagnostics.json`;
- `summary.json`;
- `index.html`;
- `admin/index.html`;
- `static/mirror.css`;
- `static/mirror-index.js`.

Pontos fortes:

- escrita atômica de arquivos;
- deduplicação real de assets;
- manifesto de páginas rico o bastante para UI e integrações futuras;
- geração de navegação offline com backlinks e links internos.

Limitações:

- o módulo também está muito grande;
- mistura persistência, derivação de índices e renderização HTML estática;
- não há versionamento explícito do schema dos índices;
- `search_index.js` cresce linearmente com o número de páginas e pode ficar pesado em espelhos maiores.

### `scraper/ui_assets.py`

Responsabilidades:

- definir CSS base do espelho offline;
- definir o JavaScript de busca e filtragem da landing page.

Pontos positivos:

- UI pronta para uso offline sem dependências externas;
- tema visual configurável por perfil;
- busca simples e suficiente para uso local.

Limitações:

- a busca é totalmente carregada no cliente;
- não existe paginação real;
- o ranking de resultados é heurístico e simples.

## Perfis disponíveis

Perfis encontrados em `profiles/`:

- `tibiawiki_br.json`
- `tibia_fandom.json`

### Diferença conceitual entre os perfis

`tibiawiki_br` representa uma wiki MediaWiki clássica com estrutura mais direta. `tibia_fandom` adiciona seletores e ruídos extras associados ao ecossistema Fandom, como elementos de navegação global, comentários e componentes laterais.

### Avaliação

A estratégia de perfis declarativos é uma das melhores decisões deste projeto. Ela reduz acoplamento e cria um caminho claro para suportar novas wikis sem bifurcar o código principal.

## Fluxo completo de execução

### 1. Inicialização

O usuário executa `run_scraper.py`, define seed, perfil, limites e diretório de saída. O script monta `ScraperConfig`, resolve o perfil e inicializa o crawler.

### 2. Recuperação de estado

Se `resume=True`, o crawler tenta carregar `checkpoints/state.json`. Se existir, recupera:

- URLs visitadas;
- URLs pendentes;
- estatísticas;
- páginas que falharam.

### 3. Pré-crawl

Antes dos workers começarem:

- `robots.txt` é carregado, se habilitado;
- o bootstrap via API pode adicionar muitas páginas ao frontier antes do BFS tradicional.

### 4. Processamento de página

Cada URL:

1. entra na contagem de tentativa;
2. passa por verificação de robots;
3. tenta fetch direto em HTML;
4. se necessário, tenta fallback via MediaWiki API;
5. passa pelo extractor;
6. tenta capturar wikitext;
7. baixa e reescreve imagens;
8. salva os formatos locais;
9. descobre novos links internos;
10. dispara checkpoint periódico.

### 5. Finalização

Ao encerrar, o storage:

- grava índices derivados;
- reescreve páginas com navegação complementar;
- gera a home offline;
- gera a página admin;
- persiste o resumo final do crawl.

## Estrutura de saída gerada

### Páginas

Cada página pode gerar:

- `data/pages/html/<shard>/<slug>.html`
- `data/pages/markdown/<shard>/<slug>.md`
- `data/pages/json/<shard>/<slug>.json`
- `data/pages/source/<shard>/<slug>.wiki`

### Assets

Assets são gravados em:

- `data/assets/images/...`
- `data/assets/items/...`
- `data/assets/monsters/...`
- `data/assets/maps/...`

### Índices

Índices centrais:

- `url_to_slug.json`: mapeia URL canônica para slug local.
- `pages_manifest.json`: catálogo principal de páginas.
- `link_graph.json`: grafo de links internos.
- `assets_by_hash.json`: deduplicação física.
- `assets_by_url.json`: alias lógico de URLs para hashes.

Índices derivados:

- `backlinks.json`
- `categories.json`
- `duplicate_content.json`
- `failed_pages.json`
- `profile_diagnostics.json`
- `summary.json`
- `search_index.js`

### Interface offline

- `index.html`: landing page com busca local.
- `admin/index.html`: painel de diagnóstico do perfil ativo.
- `static/mirror.css`: tema visual.
- `static/mirror-index.js`: filtro e renderização de resultados.

## Qualidade do código

### Pontos fortes observados

- arquitetura modular melhor do que a média para um scraper desse porte;
- bom isolamento entre configuração, crawling, extração, storage e perfis;
- validação antecipada de perfis antes da execução efetiva do crawl;
- suporte real a retomada por checkpoint;
- preocupação com deduplicação de assets;
- front-end offline utilitário e consistente;
- cobertura básica de testes já presente;
- fallback de captura via API, que aumenta robustez contra falhas de HTML direto.

### Pontos fracos observados

- `crawler.py` e `storage.py` estão grandes e acumulam responsabilidades;
- a validação de perfis JSON ainda é fraca;
- a suíte de testes cobre apenas a base, não os cenários mais arriscados;
- não há rastreabilidade formal de versão de schema dos artefatos gerados;
- a busca client-side pode escalar mal em espelhos grandes;
- a presença de múltiplos diretórios `output-*` na raiz indica acúmulo operacional e falta de política clara de artefatos.

## Testes existentes

Testes encontrados:

- `test_crawler_source.py`
- `test_extractor.py`
- `test_site_profiles.py`
- `test_storage.py`
- `test_url_utils.py`

### O que eles validam

- extração de nomes de templates a partir do wikitext;
- extração básica de conteúdo e reescrita de links;
- detecção automática de perfis;
- construção de URLs de source;
- finalização do storage com navegação e admin page;
- canonicalização de URLs;
- regra de bootstrap automático.

### Verificação executada nesta análise

Em `2026-03-25`, a suíte foi executada com:

```bash
python -m unittest discover -s tests -v
```

Resultado observado:

- 16 testes executados;
- 16 testes aprovados;
- nenhuma falha.

### Gaps de cobertura

Faltam testes relevantes para:

- retomada a partir de checkpoint;
- comportamento com `robots.txt`;
- retry e backoff em páginas e assets;
- fallback completo via MediaWiki API;
- reescrita de imagens em HTML com múltiplas variações de URL;
- tabelas complexas e infoboxes reais;
- concorrência do cache de downloads de assets;
- crescimento de índices em crawls maiores.

## Riscos, limites e dívida técnica

### Riscos funcionais

- Wikis com HTML muito customizado podem exigir seletores novos ou limpeza adicional.
- Wikis que dependem de JavaScript para renderizar conteúdo relevante não serão espelhadas integralmente.
- Algumas páginas podem ser consideradas inválidas pela canonicalização se a wiki usar parâmetros não previstos.

### Riscos operacionais

- Espelhos grandes podem gerar `search_index.js` e `pages_manifest.json` muito pesados.
- A multiplicação de diretórios `output-*` dificulta manutenção e revisão manual.
- Sem uma política de versionamento dos índices, consumidores externos podem quebrar quando o formato mudar.

### Dívida técnica identificada

- falta de divisão mais fina em `crawler.py` e `storage.py`;
- ausência de schema formal para perfis;
- pouca instrumentação além de logs e counters básicos;
- heurísticas simples para templates e buckets semânticos;
- limpeza pequena pendente em variáveis internas não usadas.

## Sugestões de melhoria

### Prioridade alta

- Evoluir a validação explícita dos perfis JSON para um schema formal versionado, como `jsonschema` ou `pydantic`.
- Cobrir com testes os cenários de retry, checkpoint, bootstrap API e robots.
- Refatorar `crawler.py` em subcomponentes menores, por exemplo `fetcher`, `asset_pipeline`, `bootstrap` e `source_capture`.
- Refatorar `storage.py` separando persistência, índices derivados e renderização estática.
- Criar um versionamento explícito para `summary.json`, `pages_manifest.json` e demais índices públicos.

### Prioridade média

- Permitir validar um perfil isolado por caminho ou chave, além do `--validate-site-profiles`.
- Criar um modo `--dry-run` para validar seed, perfil, seletores e API sem executar crawl completo.
- Melhorar a extração de templates do wikitext com parser mais robusto ou estratégia híbrida.
- Criar limpeza automatizada para artefatos antigos de verificação (`output-*`).
- Registrar métricas adicionais, como tempo médio por página, taxa de falha por estágio e origem dos assets.

### Prioridade baixa

- Adicionar paginação ou lazy rendering no índice offline.
- Permitir exportar um resumo consolidado em CSV ou NDJSON.
- Criar documentação de schema dos arquivos em `data/indexes/`.
- Adicionar benchmarks simples de crawl parcial e crawl completo.

## Sugestão de organização futura da documentação

Se o projeto continuar crescendo, vale separar a documentação em:

- `README.md`: onboarding rápido;
- `DOCUMENTACAO_TECNICA.md`: visão técnica consolidada;
- `docs/ARQUITETURA.md`: fluxo interno e responsabilidades;
- `docs/SCHEMAS.md`: formatos de saída;
- `docs/PERFIS.md`: criação e validação de novos perfis;
- `docs/OPERACAO.md`: execução, retomada e troubleshooting.

## Comandos úteis

Instalação:

```bash
python -m pip install -r requirements.txt
```

Listar perfis:

```bash
python run_scraper.py --list-site-profiles
```

Crawl parcial:

```bash
python run_scraper.py --max-pages 25 --workers 6 --rate-limit 2
```

Crawl com perfil explícito:

```bash
python run_scraper.py --site-profile tibia_fandom
```

Servir saída existente:

```bash
python run_scraper.py --serve-only --output-dir output
```

Executar testes:

```bash
python -m unittest discover -s tests -v
```

## GUI local (`QuickWiki Studio`)

### Objetivo da GUI

A GUI local foi introduzida para reduzir fricÃ§Ã£o operacional e tornar o projeto mais acessÃ­vel para usuÃ¡rios que nÃ£o querem depender da CLI para cada interaÃ§Ã£o. Em vez de competir com a linha de comando, ela atua como uma camada de orquestraÃ§Ã£o visual sobre o mesmo `run_scraper.py`.

### Arquitetura da GUI

O fluxo da GUI segue esta estrutura:

1. `run_scraper.py --gui` prepara logging e sobe um servidor HTTP local.
2. `scraper/gui_server.py` expÃµe endpoints para ler estado, validar perfis, iniciar execuÃ§Ãµes e interromper o processo ativo.
3. `scraper/gui_assets.py` fornece HTML, CSS e JavaScript estÃ¡ticos da interface `QuickWiki Studio`.
4. O backend dispara o mesmo entrypoint do projeto via subprocesso, preservando compatibilidade com o fluxo CLI jÃ¡ existente.
5. A GUI consome `summary.json`, `scraper.log`, o manual visual e o espelho atual pelos atalhos locais.

### Responsabilidades dos mÃ³dulos novos

#### `scraper/gui_server.py`

Responsabilidades:

- normalizar payloads vindos da GUI;
- validar modos, nÃ­veis de log e toggles;
- montar o comando de subprocesso para o scraper;
- manter estado em memÃ³ria da execuÃ§Ã£o ativa;
- servir manual, projeto e espelho por rotas locais seguras;
- impedir novas execuÃ§Ãµes enquanto houver um processo em andamento.

Pontos positivos:

- integra a GUI sem duplicar a lÃ³gica de scraping;
- usa `subprocess` para preservar o comportamento real do pipeline;
- melhora a experiÃªncia de suporte com logs e resumo acessÃ­veis em tempo real;
- endurece a navegaÃ§Ã£o local com `safe_path_join`.

#### `scraper/gui_assets.py`

Responsabilidades:

- definir a interface visual do `QuickWiki Studio`;
- oferecer um formulÃ¡rio visual para parÃ¢metros comuns e avanÃ§ados;
- exibir estado, mÃ©tricas, logs e atalhos;
- apresentar descriÃ§Ã£o e seed padrÃ£o do perfil selecionado;
- fazer polling periÃ³dico de `/api/state`.

Pontos positivos:

- onboarding mais amigÃ¡vel para usuÃ¡rios nÃ£o tÃ©cnicos;
- visual coerente com o manual e com a identidade `QuickWiki`;
- boa separaÃ§Ã£o entre backend de orquestraÃ§Ã£o e frontend local leve.

### Trade-offs assumidos

- A GUI nÃ£o persiste histÃ³rico de execuÃ§Ãµes entre reinÃ­cios do servidor.
- O estado visual continua dependente dos artefatos em disco e do processo filho.
- O modelo atual cobre bem uso local, mas ainda nÃ£o Ã© uma camada multiusuÃ¡rio ou remota.

### Cobertura de testes adicionada

Com a introduÃ§Ã£o da GUI, foi criada `tests/test_gui_server.py` cobrindo:

- normalizaÃ§Ã£o de payloads da interface;
- validaÃ§Ã£o de modos invÃ¡lidos;
- montagem do comando do subprocesso;
- bloqueio de path traversal em arquivos servidos;
- exposiÃ§Ã£o de perfis com seed padrÃ£o no estado inicial.

### Melhorias futuras especÃ­ficas da GUI

- adicionar histÃ³rico local das Ãºltimas execuÃ§Ãµes;
- criar presets visuais como "amostra segura" e "crawl completo";
- permitir validaÃ§Ã£o visual de perfis externos sem editar a CLI;
- destacar estatÃ­sticas mais detalhadas do `summary.json` no painel;
- adicionar um modo `dry-run` integrado Ã  GUI.

## Fechamento

O projeto está em um ponto bom de maturidade para um scraper especializado: ele já não é apenas um coletor de HTML, mas um pipeline de espelhamento offline com extração estruturada, UI local e flexibilidade para múltiplas wikis. O maior ganho imediato, daqui para frente, não parece ser adicionar mais funcionalidades isoladas, e sim fortalecer validação, testes de cenários críticos e organização operacional.

## Changelog

O registro canônico de mudanças agora vive em `CHANGELOG.md`. Esta seção mantém apenas um resumo contextual da rodada de análise e documentação.

### 2026-03-25

- Verificada a existência de documentação prévia em `README.md`, `Plan.md` e `isso que queremos.md`.
- Consolidada uma análise técnica completa do projeto neste arquivo.
- Documentados arquitetura, fluxo de execução, módulos, perfis, formatos de saída, testes, riscos e sugestões de melhoria.
- Registrada a validação local da suíte de testes com 16 testes aprovados.
- Registrado o rebrand do projeto para `QuickWiki`, a validação explícita de perfis e a introdução da GUI local `QuickWiki Studio` no changelog principal.
