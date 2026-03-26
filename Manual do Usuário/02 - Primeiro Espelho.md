# 02 - Primeiro Espelho

## Objetivo

Fazer a primeira execução de forma segura, rápida e fácil de verificar.

## Recomendação

Na primeira vez, use um crawl pequeno. Isso ajuda a confirmar:

- se a rede está funcionando;
- se o perfil escolhido está correto;
- se a saída está sendo criada no lugar esperado.

## Passo 1 — Rodar uma execução de amostra

```bash
python run_scraper.py --max-pages 25 --workers 6 --rate-limit 2
```

## O que esse comando faz

- limita a captura a 25 páginas;
- usa 6 workers;
- mantém um ritmo moderado de requisições;
- grava a saída em `output/`.

## Passo 2 — Verificar a pasta de saída

Depois da execução, confira se foram criados:

- `output/index.html`
- `output/admin/index.html`
- `output/data/indexes/summary.json`
- `output/logs/scraper.log`

## Passo 3 — Servir a saída localmente

```bash
python run_scraper.py --serve-only --output-dir output
```

Depois abra:

- `http://127.0.0.1:8765/index.html`

## Quando partir para um crawl maior

Depois que a execução de amostra funcionar bem, você pode usar:

```bash
python run_scraper.py --workers 8 --rate-limit 2
```

## Checklist rápido

- amostra executada sem erro;
- pasta `output/` criada;
- home offline acessível no navegador.

## Próximo passo

Abra `03 - Perfis, Validação e Modos.md`.
