# 01 - Instalação e Preparação

## Objetivo

Deixar o QuickWiki pronto para o primeiro uso sem complicação.

## Pré-requisitos

Você precisa ter:

- Python instalado;
- acesso ao terminal na pasta do projeto;
- conexão com a internet para instalar dependências e acessar a wiki alvo.

## Passo 1 — Entrar na pasta do projeto

```bash
cd <diretorio-do-projeto>
```

## Passo 2 — Instalar dependências

```bash
python -m pip install -r requirements.txt
```

## Passo 3 — Confirmar que a CLI está disponível

```bash
python run_scraper.py --help
```

Se tudo estiver certo, o terminal vai mostrar a lista de opções do QuickWiki.

## Passo 4 — Validar os perfis antes do uso

```bash
python run_scraper.py --validate-site-profiles
```

Esse comando é recomendado porque confirma que os perfis JSON carregados pelo sistema estão válidos antes de iniciar um crawl.

## Checklist rápido

- dependências instaladas;
- `--help` funcionando;
- perfis validados com sucesso.

## Próximo passo

Abra `06 - QuickWiki Studio.md` para começar pela interface visual oficial do projeto. Se preferir seguir direto pela trilha CLI, avance então para `02 - Primeiro Espelho.md`.
