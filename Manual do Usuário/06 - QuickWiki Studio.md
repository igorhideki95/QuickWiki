# QuickWiki Studio

## Objetivo

Ensinar o uso da GUI local do QuickWiki para quem prefere uma experiencia visual ao inves de configurar tudo pela linha de comando.

## Quando usar

Use a GUI quando quiser:

- validar perfis com um clique;
- configurar um crawl sem decorar parametros;
- acompanhar logs em tempo real;
- abrir rapidamente o espelho, o admin e o resumo do crawl;
- ver claramente que a v1 oficial foca os perfis built-in, com externos em preview via CLI.

## Como abrir

```bash
quickwiki --gui
```

Se quiser mudar a porta:

```bash
quickwiki --gui --gui-port 8899
```

## O que existe na tela

### 1. Cabecalho

Mostra o estado atual do sistema, a versao do produto e o ultimo resumo conhecido do output ativo.

### 2. Bloco de execucao

Permite ajustar:

- perfil;
- seed URL;
- pasta de saida;
- limite de paginas;
- workers;
- rate limit;
- timeout.

### 3. Perfil selecionado

Ao trocar o perfil, a interface mostra a descricao do site e a seed padrao quando existir.

### 4. Configuracoes avancadas

Voce pode alterar:

- retries;
- passes extras de retry;
- checkpoint;
- bootstrap da API;
- nivel de log;
- `--fresh`;
- `--ignore-robots`;
- `--no-source`.

### 5. Atalhos rapidos

Depois do crawl, use os links da propria tela para abrir:

- o espelho offline;
- o painel admin;
- o `summary.json`;
- o `run_report.json`;
- o `runtime_status.json`;
- o manual visual.

## Fluxo recomendado

1. Clique em validar perfis.
2. Escolha o perfil correto.
3. Rode um teste pequeno com `Max. paginas`.
4. Revise logs e exit code.
5. Abra o espelho pelos atalhos da direita.
6. So depois aumente a escala.

## Observacoes

- A GUI impede iniciar uma segunda execucao enquanto houver uma ativa.
- O processo continua sendo o mesmo `run_scraper.py`; a interface e uma camada visual por cima da CLI.
- O output ativo muda conforme a execucao mais recente iniciada pela GUI.
- Perfis externos continuam disponiveis apenas como preview via CLI, nao como fluxo guiado da interface.
