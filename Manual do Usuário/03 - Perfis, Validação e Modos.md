# 03 - Perfis, Validacao e Modos

## Objetivo

Entender como escolher a wiki certa e como controlar a execucao.

## Perfis incluidos

O projeto traz dois perfis oficiais para a v1:

- `tibiawiki_br`
- `tibia_fandom`

Perfis externos continuam carregaveis pela CLI, mas sao tratados como preview avancado.

Os perfis declarativos agora usam `schema_version: 1` e `wiki_family`, preparando futuras validacoes e a matriz de compatibilidade do projeto.

## Listar perfis disponiveis

```bash
quickwiki --list-site-profiles
```

## Validar perfis carregados

```bash
quickwiki --validate-site-profiles
```

Use esse comando quando:

- alterar um arquivo em `profiles/`;
- adicionar um perfil extra;
- quiser confirmar rapidamente que a configuracao esta integra.

## Forcar um perfil especifico

```bash
quickwiki --site-profile tibia_fandom
```

## Deixar o sistema detectar automaticamente

```bash
quickwiki --site-profile auto --seed-url https://www.tibiawiki.com.br/wiki/Home
```

## Carregar perfil extra por arquivo

```bash
quickwiki --site-profile-file .\profiles\minha_wiki.json --site-profile minha_wiki
```

## Modos uteis no dia a dia

### Retomar execucao anterior

Por padrao, o QuickWiki tenta retomar do checkpoint quando ele existe.

### Ignorar checkpoint e comecar do zero

```bash
quickwiki --fresh
```

### Desativar captura do source wiki

```bash
quickwiki --no-source
```

### Apenas servir uma saida ja existente

```bash
quickwiki --serve-only --output-dir output
```

## Regra pratica

Se voce so quer testar:

- valide os perfis;
- rode com `--max-pages`;
- confira a saida;
- so depois faca um crawl maior.

## Proximo passo

Abra `04 - Navegacao Offline.md`.
