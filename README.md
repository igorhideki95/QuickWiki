# QuickWiki

QuickWiki e um espelhador offline multi-wiki com foco em MediaWiki/Fandom,
preparado para crescer sem acoplar a logica a um unico site.

## Ownership

Igor Hideki (`@IgorDev`) e o criador e responsavel principal pelo QuickWiki,
atuando como idealizador, owner de produto, direcao tecnica e gestao da
evolucao do projeto.

## QuickBrain

Este repositorio se conecta ao `QuickBrain` local em `C:\IgorDev\QuickBrain`.

O `QuickBrain` serve como memoria operacional da workspace: identidade,
portfolio, publish state, decisoes transversais e aprendizado continuo. Sempre
que o papel do QuickWiki no portfolio mudar, esse contexto deve ser resumido la
de forma curta e cumulativa.

## Publication Status

- GitHub visibility: `private`
- Curadoria atual: baseline privada publicada e sincronizada com o QuickBrain
- Abertura publica futura: somente apos rodada especifica de showcase e release
  polish

## Caminho recomendado

O projeto agora possui uma GUI local chamada `QuickWiki Studio`, pensada para
facilitar onboarding, operacao basica e acompanhamento visual de crawls.

Para abrir a interface:

```bash
python run_scraper.py --gui
```

A GUI sobe localmente por padrao em `http://127.0.0.1:8877`.

## Documentacao complementar

- `DOCUMENTACAO_TECNICA.md`: analise tecnica consolidada e arquitetura
- `CHANGELOG.md`: historico organizado das mudancas
- `Manual do Usuario/README.md`: indice do manual em Markdown
- `Manual do Usuario/index.html`: versao visual e navegavel do manual

## O que o projeto entrega hoje

- perfis declarativos em JSON para diferentes wikis
- auto-deteccao por dominio ou escolha explicita de perfil
- crawl BFS com bootstrap opcional via MediaWiki API
- captura de HTML, Markdown, JSON e wikitext bruto
- indices auxiliares para busca offline, backlinks, categorias, duplicados e
  falhas
- frontend offline com assets estaticos, tema por perfil e painel admin
- GUI local `QuickWiki Studio` para configurar, validar e acompanhar execucoes

## Perfis de wiki

Os perfis ficam em `profiles/*.json` e controlam:

- dominios permitidos
- seed padrao
- caminho da API
- seletores de titulo, conteudo e categorias
- ruido extra a remover
- tema visual do espelho

Perfis incluidos hoje:

- `tibiawiki_br`
- `tibia_fandom`

Tambem e possivel carregar perfis externos com `--site-profile-file` ou
apontar outro diretorio com `--profiles-dir`.

## Instalacao

```bash
cd <diretorio-do-projeto>
python -m pip install -r requirements.txt
```

## Primeiros passos

### Opcao A - GUI local

```bash
python run_scraper.py --validate-site-profiles
python run_scraper.py --gui
```

Depois disso:

1. valide os perfis pela propria GUI
2. rode um crawl pequeno com `--max-pages` configurado na tela
3. abra o espelho offline pelos atalhos da interface

### Opcao B - CLI direta

```bash
python run_scraper.py --max-pages 25 --workers 6 --rate-limit 2
python run_scraper.py --serve-only --output-dir output
```

## Comandos uteis

### Abrir a GUI local

```bash
python run_scraper.py --gui
```

### Usar outra porta para a GUI

```bash
python run_scraper.py --gui --gui-port 8899
```

### Crawl padrao

```bash
python run_scraper.py --workers 8 --rate-limit 2
```

### Usar perfil especifico

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

### Usar outro diretorio de perfis

```bash
python run_scraper.py --profiles-dir .\\profiles_custom --site-profile auto
```

### Servir o espelho por HTTP local

```bash
python run_scraper.py --serve-only --output-dir output
```

## Estrutura de saida

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

## Observacoes de operacao

- `--site-profile auto` tenta detectar a wiki pela `--seed-url`
- `--api-bootstrap-mode auto` so ativa bootstrap completo quando `--max-pages`
  nao e usado
- `--retry-failed-passes` e mais util em crawls completos
- o QuickWiki salva links para `action=edit`, `action=raw` e o `.wiki` local
  quando a wiki permite capturar o source
- abra `output/index.html` para navegar no espelho
- abra `output/admin/index.html` para inspecionar perfil, seletores, tema e
  atalhos de diagnostico
- os arquivos em `data/indexes/` foram pensados para consumo por ferramentas
  externas, IA e futuras telas administrativas
