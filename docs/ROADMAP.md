# Roadmap

Estado atual: V1.0.0 publicada em 2026-03-28, com distribuicao source-first sob licenca MIT e backlog de manutencao pos-lancamento aberto.

## RC1 - Release Polish

- `quickwiki` como comando canonico documentado.
- `python -m quickwiki` como fallback sem depender do `PATH`.
- `python run_scraper.py` mantido como caminho de compatibilidade.
- README, hub de docs e manual alinhados com a mensagem publica da v1.
- GUI com linguagem mais publica, focada nos perfis built-in oficiais.
- Checklist de instalacao, quickstart e troubleshooting consolidado.

## RC2 - Contract Hardening

- contratos publicos de artefatos versionados por `schema_version`.
- `quickwiki_version` e metadados de geracao nos JSONs publicos.
- CI com matriz Windows e Linux.
- smoke checks para `--help`, `--list-site-profiles` e `--validate-site-profiles`.

## V1 Done

- release source-first pronta para uso publico.
- perfis built-in como escopo oficial suportado.
- GUI, output offline e diagnostico operacional alinhados.
- distribuicao aberta sob licenca MIT.
- release `v1.0.0` publicada no GitHub com metadata e governanca basica ativas.

## Post-v1

- schema versionado para perfis declarativos, com base v1 ja entregue.
- matriz de compatibilidade por familia de wiki.
- onboarding guiado para perfis externos.
- decomposicao futura de crawler e storage em subservicos menores.
- integracoes mais amplas com ferramentas externas de busca e IA.
