# Contributing

Obrigado por considerar melhorias para o QuickWiki.

## Escopo atual

O foco da v1 publica e manter:

- perfis built-in estaveis
- crawler confiavel
- packaging reproduzivel
- GUI local previsivel
- docs claras para usuarios e mantenedores

## Ambiente recomendado

Requisito minimo: Python 3.11 ou superior.

```bash
git clone https://github.com/igorhideki95/QuickWiki.git
cd QuickWiki
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```

Se quiser validar tambem a experiencia instalada:

```bash
python -m quickwiki --validate-site-profiles
python -m quickwiki --list-site-profiles
```

## Antes de abrir PR

- alinhe a mudanca com o objetivo atual do projeto
- verifique se o impacto atinge CLI, GUI, artefatos JSON, docs ou contratos publicos
- atualize a documentacao relevante quando houver impacto em onboarding, release gate ou comportamento visivel
- adicione ou ajuste testes quando mexer em paths, packaging, GUI, CLI ou contratos publicos

## Padrao de contribuicao

- preserve compatibilidade com `quickwiki` e `python -m quickwiki`
- trate perfis built-in como o fluxo oficialmente suportado
- mantenha o repositorio source-first e simples de operar localmente
- registre mudancas relevantes em `CHANGELOG.md`
- contribuicoes enviadas ao repositorio passam a seguir a licenca MIT do projeto

## Arquivos para revisar quando houver impacto real

- `README.md`
- `docs/STATUS.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/README.md`
- `CHANGELOG.md`

## Checklist rapido de PR

- testes locais executados
- docs atualizadas
- sem artefatos gerados acidentalmente no commit
- comportamento de novos usuarios validado
