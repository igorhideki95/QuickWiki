# 01 - Instalacao e Preparacao

## Objetivo

Deixar o QuickWiki pronto para o primeiro uso sem atrito.

## Pre-requisitos

Voce precisa ter:

- Python instalado;
- acesso ao terminal na pasta do projeto;
- conexao com a internet para instalar dependencias e acessar a wiki alvo.

## Passo 1 - Entrar na pasta do projeto

```bash
cd <diretorio-do-projeto>
```

## Passo 2 - Instalar a partir do source

```bash
python -m pip install .
```

Isso instala o comando canonico `quickwiki`.

## Passo 3 - Confirmar que a CLI esta disponivel

```bash
quickwiki --help
```

Se o Windows ainda nao reconhecer `quickwiki`, abra um novo terminal. Se mesmo assim nao resolver, use `python -m quickwiki --help` enquanto ajusta o `PATH` do Scripts do Python do usuario.

Se quiser os fallbacks oficiais:

```bash
python -m quickwiki --help
python run_scraper.py --help
```

## Passo 4 - Validar os perfis antes do uso

```bash
quickwiki --validate-site-profiles
```

Esse comando confirma se os perfis JSON carregados pelo sistema estao validos antes de iniciar um crawl.

## Checklist rapido

- dependencias instaladas;
- `quickwiki --help` funcionando;
- `python -m quickwiki --help` funcionando;
- perfis validados com sucesso;
- comando `python run_scraper.py --help` ainda disponivel como compatibilidade.

## Proximo passo

Abra `06 - QuickWiki Studio.md` para conhecer a interface visual oficial do projeto. Se preferir seguir direto pela trilha CLI, avance para `02 - Primeiro Espelho.md`.
