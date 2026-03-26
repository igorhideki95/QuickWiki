# Changelog

Todas as mudanças relevantes do QuickWiki devem ser registradas aqui de forma objetiva e rastreável.

O formato segue uma estrutura simples por data, com agrupamento por tipo de mudança.

## 2026-03-25 — QuickWiki Studio e trilha visual oficial

### Adicionado

- GUI local `QuickWiki Studio`, acessível por `python run_scraper.py --gui`.
- Novo parâmetro `--gui-port` para controlar a porta da interface visual.
- Backend HTTP local para iniciar execuções, validar perfis, encerrar processos ativos e servir manual, projeto e espelho atual.
- Tela visual com formulário de execução, leitura de estado, resumo do último crawl, logs em tempo real e atalhos rápidos.
- Testes dedicados para helpers da GUI em `tests/test_gui_server.py`.
- Capítulo novo do manual em `Manual do Usuário/06 - QuickWiki Studio.md` e `Manual do Usuário/06-gui-studio.html`.

### Alterado

- O `run_scraper.py` agora prepara logging também ao abrir a GUI, para manter rastreabilidade consistente.
- A GUI passou a exibir descrição e seed padrão dos perfis carregados.
- O preview de comando da interface ficou mais fiel ao ambiente local, inclusive em caminhos com espaços no Windows.
- O servidor da GUI foi endurecido com validação de payload, cache simples de perfis e proteção de navegação em arquivos servidos localmente.

### Documentação

- `README.md` reestruturado para apresentar a GUI como trilha recomendada de onboarding.
- `DOCUMENTACAO_TECNICA.md` atualizado para incluir arquitetura e responsabilidade dos módulos da GUI.
- `Manual do Usuário/index.html` e `Manual do Usuário/README.md` ajustados para destacar o QuickWiki Studio como recurso oficial.
- `Plan.md` ampliado para refletir a camada visual de operação do produto.

### Testes

- Validação estrutural com `python -m py_compile run_scraper.py scraper\\gui_server.py scraper\\gui_assets.py tests\\test_gui_server.py`.
- Suíte local executada com `16/16` testes aprovados.
- Smoke test da GUI executado com resposta `200` no endpoint `/api/state`.

## 2026-03-25 — Rebrand para QuickWiki e melhorias estruturais

### Alterado

- A identidade pública do projeto passou de `TibiaWiki Web Scrapper` para `QuickWiki`.
- O entrypoint `run_scraper.py` agora apresenta o projeto como `QuickWiki` na CLI.
- O crawler público principal passou a ser `QuickWikiCrawler`, mantendo alias compatível para `TibiaWikiCrawler`.
- O namespace de logs foi atualizado para `quickwiki.scraper`.
- O `user_agent` padrão foi atualizado para `QuickWikiBot/1.0`.
- A interface offline passou a usar títulos e textos de navegação alinhados com a marca `QuickWiki`.

### Adicionado

- Comando `--validate-site-profiles` para validar os perfis carregados e encerrar.
- Validação explícita de payloads de perfis JSON durante o carregamento.
- Export público de `validate_site_profile_payload` no pacote `scraper`.
- Compatibilidade retroativa no frontend para `window.TibiaMirrorApp` e no índice legado `window.__TIBIA_WIKI_SEARCH_INDEX__`.

### Documentação

- `README.md` atualizado para a identidade `QuickWiki`.
- `DOCUMENTACAO_TECNICA.md` ajustado para refletir o rebrand e apontar este changelog como fonte canônica.
- `Plan.md` atualizado para a nova identidade do projeto.
- `isso que queremos.md` ajustado para nomear o sistema como `QuickWiki`.

### Testes

- Adicionados testes para rejeição de perfis inválidos.
- Ajustados testes de storage para a nova identidade da interface administrativa.
- Validação final executada com 11 testes aprovados e com o comando `--validate-site-profiles` concluindo com sucesso.

## 2026-03-25 — Consolidação de documentação técnica

### Adicionado

- Documento técnico consolidado em `DOCUMENTACAO_TECNICA.md`.

### Documentação

- Registrada análise minuciosa da arquitetura, fluxo, módulos, perfis, formatos de saída, riscos e sugestões de melhoria.
- README ligado à documentação técnica complementar.

### Verificação

- Suíte local executada com sucesso durante a rodada de documentação inicial.

## 2026-03-25 — Manual do Usuário estruturado

### Adicionado

- Pasta `Manual do Usuário` com guias separados por etapa de uso.
- Índice principal do manual com trilha recomendada de leitura.
- Instruções passo a passo para instalação, primeiro espelho, perfis, validação, navegação offline e problemas comuns.

### Documentação

- `README.md` atualizado para apontar o manual de usuário como trilha de onboarding prático.

### Verificação

- O estado atual da CLI e da validação de perfis foi revisado antes da escrita do manual, sem bloqueios críticos para uso básico.

## 2026-03-25 — Manual visual refinado

### Alterado

- O diretório físico do projeto foi renomeado de `wiki-web-scrapper` para `QuickWiki`.
- O `README.md` principal passou a apontar também para a entrada visual do manual.

### Adicionado

- `Manual do Usuário/index.html` como home visual do manual.
- `Manual do Usuário/manual.css` com uma apresentação mais editorial, responsiva e navegável.
- Páginas HTML individuais para cada capítulo do manual, com navegação entre etapas.

### Documentação

- O índice markdown do manual foi ajustado para orientar o usuário a abrir primeiro a versão HTML.
