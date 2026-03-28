# Changelog

Todas as mudancas relevantes do QuickWiki devem ser registradas aqui de forma objetiva e rastreavel.

## v1.0.0 - 2026-03-28

Primeira release publica do QuickWiki no GitHub, sob licenca MIT, com packaging validado, docs alinhadas para publico externo e governanca basica do repositorio fechada.

### Alterado

- `LICENSE` substituida por MIT para abertura publica coerente com o objetivo de portfolio e reuso comunitario
- `pyproject.toml` atualizado para declarar licenca MIT no pacote
- `README.md` reestruturado com resumo em ingles, onboarding de 60 segundos, requisito de Python 3.11+ e trilha publica de documentacao
- `docs/README.md`, `docs/STATUS.md` e `docs/NEXT_SESSION.md` reorganizados para separar onboarding publico de continuidade de mantenedor
- `CONTRIBUTING.md` alinhado ao fluxo reproduzivel com `python -m pip install -e ".[dev]"`
- `SECURITY.md` e `SUPPORT.md` atualizados com canais, expectativas e orientacao publica mais clara
- templates de issue ampliados com suporte dedicado e links publicos de contato
- `CODEOWNERS` adicionado para explicitar ownership inicial do repositorio

### Publicado

- repositorio publico em `https://github.com/igorhideki95/QuickWiki`
- descricao e topicos do GitHub refinados para descoberta publica
- tag e GitHub Release `v1.0.0`

### Validado

- `python -m unittest discover -s tests -v`
- `python -m compileall run_scraper.py quickwiki scraper tests`
- `python -m build`
- `python -m twine check dist/*`
- `python -m pip install .`
- `python -m quickwiki --list-site-profiles`
- `python -m quickwiki --validate-site-profiles`

## 2026-03-27 - Packaging hardening e repositorio public-ready

### Adicionado

- package `quickwiki/` para `python -m quickwiki`
- perfis built-in bundled em `scraper/bundled/profiles/`
- testes para paths, modo instalado e fallback de perfis
- `CONTRIBUTING.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CODE_OF_CONDUCT.md`
- template de PR em `.github/PULL_REQUEST_TEMPLATE.md`
- templates de issue em `.github/ISSUE_TEMPLATE/`

### Alterado

- `README.md` reestruturado para portfolio publico com screenshots, quickstart e estado de validacao
- `run_scraper.py` desacoplado do bootstrap pesado em comandos simples e alinhado ao fallback de perfis bundled
- `QuickWiki Studio` agora dispara o crawler por modulo com `python -m quickwiki`
- `scraper/paths.py` agora diferencia raiz source-first de workspace padrao
- `scraper/site_profiles.py` agora suporta melhor perfis bundled, JSON malformado e chaves duplicadas
- `pyproject.toml` agora inclui package-data de perfis e metadata de licenca coerente com `LICENSE`
- `docs/README.md`, `docs/STATUS.md` e `docs/RELEASE_CHECKLIST.md` reescritos para a trilha publica atual
- CI ampliada com build, `twine check` e smoke do modulo instalado fora da raiz do repositorio

### Validado

- `python -m unittest discover -s tests -v`
- `python -m build`
- `python -m twine check dist/*`
- `python -m pip install .`
- `python -m quickwiki --version`
- `python -m quickwiki --list-site-profiles`
- `python -m quickwiki --validate-site-profiles`
- smoke crawl curto com perfil built-in

## Historico anterior

- 2026-03-25 - QuickWiki Studio e trilha visual oficial.
- 2026-03-25 - Rebrand para QuickWiki e melhorias estruturais.
- 2026-03-25 - Consolidacao de documentacao tecnica.
- 2026-03-25 - Manual do usuario estruturado.
- 2026-03-25 - Manual visual refinado.
