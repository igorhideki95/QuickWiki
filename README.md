# QuickWiki

QuickWiki é um espelhador offline multi-wiki com foco em MediaWiki/Fandom, preparado para crescer sem acoplar a lógica a um único site.

## Ownership

Igor Hideki (`@IgorDev`) e o criador e responsavel principal pelo QuickWiki,
atuando como idealizador, owner de produto, direcao tecnica e gestao da
evolucao do projeto.

## Caminho recomendado

O projeto agora possui uma GUI local chamada `QuickWiki Studio`, pensada para facilitar onboarding, operação básica e acompanhamento visual de crawls.

Para abrir a interface:

```bash
python run_scraper.py --gui
```

A GUI sobe localmente por padrão em `http://127.0.0.1:8877`.

## Documentação complementar

- `DOCUMENTACAO_TECNICA.md`: análise técnica consolidada e arquitetura.
- `CHANGELOG.md`: histórico organizado das mudanças.
- `Manual do Usuário/README.md`: índice do manual em Markdown.
- `Manual do Usuário/index.html`: versão visual e navegável do manual.

## O que o projeto entrega hoje

- perfis declarativos em JSON para diferentes wikis;
- auto-detecção por domínio ou escolha explícita de perfil;
- crawl BFS com bootstrap opcional via MediaWiki API;
- captura de HTML, Markdown, JSON e wikitext bruto;
- índices auxiliares para busca offline, backlinks, categorias, duplicados e falhas;
- frontend offline com assets estáticos, tema por perfil e painel admin;
- GUI local `QuickWiki Studio` para configurar, validar e acompanhar execuções.

## Perfis de wiki

Os perfis ficam em `profiles/*.json` e controlam:

- domínios permitidos;
- seed padrão;
- caminho da API;
- seletores de título, conteúdo e categorias;
- ruído extra a remover;
- tema visual do espelho.

Perfis incluídos hoje:

- `tibiawiki_br`
- `tibia_fandom`

Também é possível carregar perfis externos com `--site-profile-file` ou apontar outro diretório com `--profiles-dir`.

## Instalação

```bash
cd <diretorio-do-projeto>
python -m pip install -r requirements.txt
```

## Primeiros passos

### Opção A — GUI local

```bash
python run_scraper.py --validate-site-profiles
python run_scraper.py --gui
```

Depois disso:

1. valide os perfis pela própria GUI;
2. rode um crawl pequeno com `--max-pages` configurado na tela;
3. abra o espelho offline pelos atalhos da interface.

### Opção B — CLI direta

```bash
python run_scraper.py --max-pages 25 --workers 6 --rate-limit 2
python run_scraper.py --serve-only --output-dir output
```

## Comandos úteis

### Abrir a GUI local

```bash
python run_scraper.py --gui
```

### Usar outra porta para a GUI

```bash
python run_scraper.py --gui --gui-port 8899
```

### Crawl padrão

```bash
python run_scraper.py --workers 8 --rate-limit 2
```

### Usar perfil específico

```bash
python run_scraper.py --site-profile tibia_fandom
```

### Listar perfis carregados

```bash
python run_scraper.py --list-site-profiles
```

### Validar perfis carregados

```bash
python run_scraper.py --validate-site-profiles
```

### Carregar perfil extra por arquivo

```bash
python run_scraper.py --site-profile-file .\\profiles\\minha_wiki.json --site-profile minha_wiki
```

### Usar outro diretório de perfis

```bash
python run_scraper.py --profiles-dir .\\profiles_custom --site-profile auto
```

### Servir o espelho por HTTP local

```bash
python run_scraper.py --serve-only --output-dir output
```

## Estrutura de saída

```text
output/
  index.html
  admin/
    index.html
  static/
    mirror.css
    mirror-index.js
  checkpoints/
    state.json
  logs/
    scraper.log
  data/
    pages/
      html/<shard>/<slug>.html
      markdown/<shard>/<slug>.md
      json/<shard>/<slug>.json
      source/<shard>/<slug>.wiki
    assets/
      <bucket>/<shard>/<sha256>.<ext>
    indexes/
      assets_by_hash.json
      assets_by_url.json
      backlinks.json
      categories.json
      duplicate_content.json
      failed_pages.json
      link_graph.json
      pages_manifest.json
      profile_diagnostics.json
      search_index.js
      summary.json
      url_to_slug.json
```

## Observações de operação

- `--site-profile auto` tenta detectar a wiki pela `--seed-url`.
- `--api-bootstrap-mode auto` só ativa bootstrap completo quando `--max-pages` não é usado.
- `--retry-failed-passes` é mais útil em crawls completos.
- O QuickWiki salva links para `action=edit`, `action=raw` e o `.wiki` local quando a wiki permite capturar o source.
- Abra `output/index.html` para navegar no espelho.
- Abra `output/admin/index.html` para inspecionar perfil, seletores, tema e atalhos de diagnóstico.
- Os arquivos em `data/indexes/` foram pensados para consumo por ferramentas externas, IA e futuras telas administrativas.
