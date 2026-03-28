# Contributing

Obrigado por considerar melhorias para o QuickWiki.

## Antes de abrir PR

- alinhe o escopo com o objetivo atual da v1: estabilidade dos perfis built-in, crawler confiavel e docs claras
- verifique se a mudanca afeta CLI, GUI, artefatos JSON, docs ou contratos
- atualize a documentacao relevante quando houver impacto no uso ou no release gate

## Ambiente recomendado

```bash
python -m pip install .
python -m unittest discover -s tests -v
python -m build
python -m twine check dist/*
```

## Padrao de contribuicao

- mantenha o repositorio source-first e simples de operar localmente
- preserve compatibilidade com `python -m quickwiki`
- trate perfis built-in como o fluxo oficialmente suportado
- adicione testes quando alterar paths, packaging, GUI, CLI ou contratos publicos
- registre mudancas relevantes em `CHANGELOG.md`
- contribuicoes enviadas para o repositorio passam a seguir a licenca MIT do projeto

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
