# QuickWiki Studio

## Objetivo

Ensinar o uso da GUI local do QuickWiki para quem prefere uma experiência visual ao invés de configurar tudo pela linha de comando.

## Quando usar

Use a GUI quando quiser:

- validar perfis com um clique;
- configurar um crawl sem decorar parâmetros;
- acompanhar logs em tempo real;
- abrir rapidamente o espelho, o admin e o resumo do crawl.

## Como abrir

```bash
python run_scraper.py --gui
```

Se quiser mudar a porta:

```bash
python run_scraper.py --gui --gui-port 8899
```

## O que existe na tela

### 1. Cabeçalho

Mostra o estado atual do sistema e o último resumo conhecido do output ativo.

### 2. Bloco de execução

Permite ajustar:

- perfil;
- seed URL;
- pasta de saída;
- limite de páginas;
- workers;
- rate limit;
- timeout.

### 3. Perfil selecionado

Ao trocar o perfil, a interface mostra a descrição do site e a seed padrão quando existir.

### 4. Configurações avançadas

Você pode alterar:

- retries;
- passes extras de retry;
- checkpoint;
- bootstrap da API;
- nível de log;
- `--fresh`;
- `--ignore-robots`;
- `--no-source`.

### 5. Atalhos rápidos

Depois do crawl, use os links da própria tela para abrir:

- o espelho offline;
- o painel admin;
- o `summary.json`;
- o manual visual.

## Fluxo recomendado

1. Clique em validar perfis.
2. Escolha o perfil correto.
3. Rode um teste pequeno com `Max. paginas`.
4. Revise logs e exit code.
5. Abra o espelho pelos atalhos da direita.
6. Só depois aumente a escala.

## Observações

- A GUI impede iniciar uma segunda execução enquanto houver uma ativa.
- O processo continua sendo o mesmo `run_scraper.py`; a interface é uma camada visual por cima da CLI.
- O output ativo muda conforme a execução mais recente iniciada pela GUI.
