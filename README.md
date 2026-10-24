# DataForge — Engenharia de Dados

Projeto Python modular para preparar bases tabulares de diferentes áreas. Versão 2.1.1.

Recebe CSV ou XLSX, calcula métricas de qualidade, aplica regras explícitas e publica CSV tratado com relatório auditável. Interface desktop para uso local e CLI para automação. Não depende de IA/API.

## Início rápido no Windows

1. Extraia todo o ZIP para uma pasta.
2. Instale Python 3.10 ou superior com Tkinter e o inicializador `py`.
3. Abra `INICIAR.bat`.
4. Selecione uma base e a pasta onde os resultados serão criados.
5. Escolha as regras e execute. A instalação inicial precisa de internet. Extraia em uma pasta nova; não reutilize o ambiente `.venv` de outro computador.

Experimente `data/raw/exemplo.csv`. Ao selecionar `configs/conversoes.exemplo.json`, o valor monetário será convertido e a coluna de datas será preservada porque há uma data inválida. Quando um JSON é selecionado, ele substitui as opções da tela.

## Instalação para desenvolvimento

Na raiz do projeto:

```bash
python -m venv .venv
```

Ative no Windows com `.venv\Scripts\activate`; no Linux/macOS, `source .venv/bin/activate`.

```bash
python -m pip install -e ".[dev]"
python -m dataforge.interfaces.desktop
```

No Linux, Tkinter pode exigir o pacote de sistema `python3-tk`. O terminal não precisa de Tkinter.

## Executar o pipeline

```bash
python -m dataforge data/raw/exemplo.csv --output data/processed/execucao_001 --config configs/conversoes.exemplo.json
```

Após instalar o pacote, o mesmo comando também está disponível como `dataforge`.

```bash
dataforge base.csv --output data/processed/execucao_002 --separator ";" --encoding cp1252
dataforge base.xlsx --output data/processed/execucao_003 --sheet "Vendas"
```

Na interface, escolha separador e codificação do CSV e, se necessário, o nome da aba Excel. Use “Limpar configuração JSON” para voltar às opções manuais. A primeira linha é o cabeçalho; primeira aba XLSX por padrão. Uma tabela por execução. CSV sem separador detectável exige `--separator`. Para arquivos Windows antigos, use a CLI com `--encoding cp1252`.

## Organização do repositório

| Caminho | Responsabilidade |
| --- | --- |
| `src/dataforge/core/` | Contrato e validação da configuração |
| `src/dataforge/ingestion/` | Leitura tabular e resolução de cabeçalhos |
| `src/dataforge/quality/` | Métricas de qualidade antes e depois |
| `src/dataforge/transformation/` | Regras de limpeza e conversão |
| `src/dataforge/export/` | Publicação do lote e bloqueio exclusivo |
| `src/dataforge/orchestration/` | Coordenação e rastreabilidade da execução |
| `src/dataforge/interfaces/` | Interface desktop e CLI |
| `configs/` | Configurações gerais e exemplo por coluna |
| `tests/unit/` | Regressões de leitura e transformação |
| `tests/integration/` | CLI, publicação, falhas e concorrência |
| `data/raw/` | Exemplo de entrada; adicione suas bases localmente |
| `data/processed/` | Destino sugerido dos lotes tratados |
| `reports/` | Pasta disponível para relatórios consolidados futuros |
| `scripts/` | Inicialização e testes no Windows |
| `docs/` | Arquitetura, configuração e operação |
| `.github/workflows/ci.yml` | Definição de CI para testes e análise estática |
| `pyproject.toml` | Metadados, dependências e comandos instaláveis |
| `Dockerfile` | Ambiente de execução da CLI |

## Saída por execução

- `dados_tratados.csv`: UTF-8 com BOM, delimitador `;`, números com ponto decimal.
- `relatorio.json`: UUID, fingerprint SHA-256, configuração, nomes das colunas, métricas, mudanças e conversões recusadas.
- `execution.log`: eventos até a preparação da publicação. A conclusão da publicação aparece no log do terminal.
- `LEIA_RESULTADO.txt`: resumo do resultado.
- `_SUCCESS`: marca que o lote foi gravado por completo. Pode conter avisos; consulte `status` no relatório.

Os arquivos de uma execução ficam juntos na pasta selecionada; `reports/` não recebe uma cópia automática. Entrada e resultados anteriores não são sobrescritos.

## Qualidade e regras

Por padrão, somente espaços no início/fim dos textos são removidos. Exclusão de linhas/colunas vazias, duplicados e padronização de cabeçalhos são opcionais. Não há preenchimento automático de ausentes ou regras de negócio implícitas.

IDs são carregados como texto. Conversões de datas/números dependem de configuração por coluna. Um único valor preenchido inválido faz a conversão dessa coluna ser recusada, preservando os valores (outras transformações configuradas continuam válidas). Isso aparece em `conversion_errors` e em `status=completed_with_warnings`.

CSV não guarda tipos: no Power BI, revise a etapa de alteração automática de tipo, mantenha IDs/CPFs/CEPs como Texto e escolha localidade compatível com ponto decimal. Excel com célula numérica 123 formatada visualmente como 00123 não armazena o texto com zeros: essa máscara não é recuperada.

## Verificação

```bash
python -m unittest discover -s tests -v
python -m ruff check src tests
```

Testes usam biblioteca padrão unittest; Ruff faz parte das dependências opcionais de desenvolvimento. Consulte `docs/VALIDACAO.md` para o que foi efetivamente executado nesta entrega.

## Docker (CLI)

```bash
docker build -t dataforge:2.1 .
docker run --rm -v "${PWD}/data:/data" dataforge:2.1 /data/raw/exemplo.csv --output /data/processed/docker_001
```

Exemplo de terminal POSIX; adapte a sintaxe de volume no Windows. A pasta de saída montada precisa permitir escrita pelo usuário `worker`. A imagem não executa a interface gráfica.

## Escopo

Preparação local em memória, sem processamento distribuído. CSV é materializado em texto e em registros antes da tabela: comece com bases pequenas em notebooks de 8 GB. Volume máximo depende da RAM e da largura dos dados. Os dados continuam em memória. Não lê PDF/imagens/XLS antigo, não conecta a SAP/SQL/SharePoint, não agenda atualizações e não integra IA. Essas integrações não estão implementadas.

As faixas de dependência não constituem lockfile. Antes de usar em produção, homologue e fixe versões no ambiente de destino. Interface Windows, CI hospedada e imagem Docker precisam ser validadas nesses ambientes.

## Distribuir o projeto

Compartilhe o ZIP limpo ou o código-fonte. Não inclua `.venv`, `__pycache__`, arquivos `.pyc` ou metadados de instalação. Cada computador deve criar seu próprio ambiente virtual. A versão corrigida inclui `INICIAR.bat` na raiz e cria esse ambiente localmente.

## Revisão 2.1.1 — execução e publicação

Extraia este ZIP completo em uma pasta nova. Abra `INICIAR.bat` na raiz com dois cliques; no terminal PowerShell, execute `./INICIAR.bat`. O inicializador também continua disponível em `scripts/iniciar_windows.bat`.

A distribuição inclui `src/dataforge/transformation/converters.py`, `scripts/verificar_instalacao.py` e `scripts/verificar_projeto.py`. A checagem de integridade informa módulos ausentes antes de instalar o projeto. O ambiente `.venv` é criado em cada computador e não acompanha o ZIP.

O `.gitignore` exclui ambiente virtual, caches, configurações locais e resultados. Publique no GitHub os arquivos extraídos da distribuição; não envie a pasta `.venv` criada depois da execução. Os dados fictícios de demonstração estão em `data/raw/exemplo.csv`.

Consulte `docs/VALIDACAO.md` para os testes desta revisão. A presença do inicializador e dos módulos foi verificada; a janela e os scripts .bat ainda devem ser confirmados no Windows.
