# 05 - Problemas Comuns

## O comando não roda

Verifique:

- se você está na pasta correta do projeto;
- se o Python está disponível no terminal;
- se as dependências foram instaladas com `pip install -r requirements.txt`.

## A validação de perfis falha

Rode:

```bash
python run_scraper.py --validate-site-profiles
```

Se houver erro, revise:

- `key`
- `default_seed_url`
- `allowed_domains`
- seletores e campos do `theme`

## O crawl não encontrou conteúdo suficiente

Tente:

- confirmar se o perfil está correto;
- usar `--site-profile` explicitamente;
- testar primeiro com `--max-pages 25`;
- verificar `output/logs/scraper.log`.

## O resultado foi criado, mas não abre bem no navegador

Use o modo servidor em vez de abrir arquivos soltos:

```bash
python run_scraper.py --serve-only --output-dir output
```

## Quero reiniciar tudo do zero

Use:

```bash
python run_scraper.py --fresh
```

## Quero apenas inspecionar os perfis e parar

Use:

```bash
python run_scraper.py --list-site-profiles
python run_scraper.py --validate-site-profiles
```

## Quando procurar os logs

Confira `output/logs/scraper.log` quando:

- a execução para no meio;
- o número de páginas salvas parece muito baixo;
- o servidor local funciona, mas o conteúdo ficou incompleto.

## Fechamento

Se o uso básico já estiver funcionando, o próximo passo natural é repetir o fluxo com:

- outro perfil;
- outra seed;
- um `max-pages` maior;
- ou um crawl completo.
