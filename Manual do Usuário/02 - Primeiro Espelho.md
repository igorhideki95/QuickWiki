# 02 - Primeiro Espelho

## Objetivo

Rodar o primeiro crawl controlado usando um perfil built-in oficial.

## Fluxo recomendado

```bash
quickwiki --validate-site-profiles
quickwiki --site-profile tibiawiki_br --max-pages 25
```

## O que observar

- se o perfil escolhido e reconhecido corretamente;
- se o espelho gerou `index.html` e `admin/index.html`;
- se `summary.json`, `run_report.json` e `runtime_status.json` foram criados;
- se o log mostra um crawl saudavel.

## Dica pratica

Comece pequeno. A v1 foi pensada para ser previsivel com perfis built-in e ciente de que perfis externos ficam como preview via CLI.

## Proximo passo

Abra `03 - Perfis, Validacao e Modos.md`.
