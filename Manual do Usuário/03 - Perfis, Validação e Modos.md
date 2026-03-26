# 03 - Perfis, Validação e Modos

## Objetivo

Entender como escolher a wiki certa e como controlar a forma de execução.

## Perfis incluídos

O projeto já traz dois perfis:

- `tibiawiki_br`
- `tibia_fandom`

## Listar perfis disponíveis

```bash
python run_scraper.py --list-site-profiles
```

## Validar perfis carregados

```bash
python run_scraper.py --validate-site-profiles
```

Use esse comando quando:

- alterar um arquivo em `profiles/`;
- adicionar um perfil extra;
- quiser confirmar rapidamente que a configuração está íntegra.

## Forçar um perfil específico

```bash
python run_scraper.py --site-profile tibia_fandom
```

## Deixar o sistema detectar automaticamente

```bash
python run_scraper.py --site-profile auto --seed-url https://www.tibiawiki.com.br/wiki/Home
```

## Carregar perfil extra por arquivo

```bash
python run_scraper.py --site-profile-file .\profiles\minha_wiki.json --site-profile minha_wiki
```

## Modos úteis no dia a dia

### Retomar execução anterior

Por padrão, o QuickWiki tenta retomar do checkpoint quando ele existe.

### Ignorar checkpoint e começar do zero

```bash
python run_scraper.py --fresh
```

### Desativar captura do source wiki

```bash
python run_scraper.py --no-source
```

### Apenas servir uma saída já existente

```bash
python run_scraper.py --serve-only --output-dir output
```

## Regra prática

Se você só quer testar:

- valide os perfis;
- rode com `--max-pages`;
- confira a saída;
- só depois faça um crawl maior.

## Próximo passo

Abra `04 - Navegação Offline.md`.
