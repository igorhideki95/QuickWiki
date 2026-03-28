# 05 - Problemas Comuns

## O comando nao roda

Verifique:

- se voce esta na pasta correta do projeto;
- se o Python esta disponivel no terminal;
- se as dependencias foram instaladas com `python -m pip install .`.

Se o Windows nao reconhecer `quickwiki`, tente:

- abrir um novo terminal;
- confirmar o diretorio Scripts do Python do usuario no `PATH`;
- usar `python -m quickwiki --help` como fallback sem depender do `PATH`;
- usar `python run_scraper.py --help` como compatibilidade imediata.

## A validacao de perfis falha

Rode:

```bash
quickwiki --validate-site-profiles
```

Se houver erro, revise:

- `key`
- `default_seed_url`
- `allowed_domains`
- seletores e campos do `theme`

Se a mensagem mencionar falta de perfis na pasta atual, revise qualquer `--profiles-dir` customizado ou defina `QUICKWIKI_ROOT` para a clone correta do projeto.

## O crawl nao encontrou conteudo suficiente

Tente:

- confirmar se o perfil esta correto;
- usar `--site-profile` explicitamente;
- testar primeiro com `--max-pages 25`;
- verificar `output/logs/scraper.log`.

## O resultado foi criado, mas nao abre bem no navegador

Use o modo servidor em vez de abrir arquivos soltos:

```bash
quickwiki --serve-only --output-dir output
```

## Quero reiniciar tudo do zero

Use:

```bash
quickwiki --fresh
```

## Quero apenas inspecionar os perfis e parar

Use:

```bash
quickwiki --list-site-profiles
quickwiki --validate-site-profiles
```

## Quando procurar os logs

Confira `output/logs/scraper.log` quando:

- a execucao para no meio;
- o numero de paginas salvas parece muito baixo;
- o servidor local funciona, mas o conteudo ficou incompleto.

## Fechamento

Se o uso basico ja estiver funcionando, o proximo passo natural e repetir o fluxo com:

- outro perfil;
- outra seed;
- um `max-pages` maior;
- ou um crawl completo.
