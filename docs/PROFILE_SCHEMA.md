# Profile Schema

## Objetivo

Definir a base versionada dos perfis declarativos do QuickWiki para que novas
features possam evoluir com compatibilidade previsivel.

## Estado atual

- versao de schema suportada: `1`
- arquivo de referencia: `schemas/site_profile.schema.v1.json`
- politica de compatibilidade: perfis sem `schema_version` continuam aceitos
  como legado v1; novas evolucoes quebradoras exigem nova versao de schema

## Campos estruturais

### `schema_version`

- inteiro
- identifica a versao do contrato do perfil
- na v1 atual, `1` e a unica versao suportada

### `wiki_family`

- string curta em minusculas
- classifica a familia da wiki para futuras matrizes de compatibilidade
- exemplos atuais:
  - `mediawiki`
  - `fandom`

## Campos funcionais do perfil

- `key`
- `label`
- `description`
- `default_seed_url`
- `allowed_domains`
- `allowed_path_prefix`
- `api_path`
- `title_selectors`
- `content_root_selectors`
- `category_selectors`
- `extra_noise_selectors`
- `theme`

## Regras de evolucao

- adicionar campos novos e preferivel a reinterpretar campos existentes
- mudancas quebradoras exigem nova versao de schema
- a GUI e os diagnosticos podem expor `schema_version` e `wiki_family`
- perfis built-in devem sempre ser a referencia de migracao para novos campos

## Proximo uso natural

- matriz de compatibilidade por familia de wiki
- onboarding mais guiado para perfis externos
- lint e verificacao automatica de perfis em CI
