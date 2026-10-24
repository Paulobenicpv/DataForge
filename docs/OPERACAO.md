# Operação

## Ambiente

Use ambiente virtual e instale o pacote a partir da raiz. Nunca copie somente um arquivo da pasta `src`: os módulos precisam estar instalados juntos. O caminho de entrada/saída é relativo ao diretório atual do terminal.

## Processamento

1. Coloque uma cópia estável da base na pasta desejada.
2. Defina as regras em um JSON específico para essa tabela.
3. Execute com um destino novo.
4. Confira `_SUCCESS`, o status no JSON, linhas/colunas antes e depois e conversões recusadas.
5. Conecte o CSV tratado ao Power BI, preservando tipos de identificadores.

Uma nova execução usa pasta nova; não aponta automaticamente o Power BI para a execução mais recente. Não há scheduler implementado. A CLI permite integração posterior com um agendador externo.

## Diagnóstico

| Situação | Ação |
| --- | --- |
| Erro de codificação | Selecione a codificação na tela ou use --encoding cp1252 na CLI |
| Separador não detectado | Selecione o separador na tela ou informe --separator na CLI |
| Quantidade de campos diferente | Corrija a estrutura do CSV e as aspas da origem |
| Conversão recusada | Revise os valores e a regra; a coluna foi mantida |
| Coluna não encontrada | Confira os nomes após normalização no relatório |
| Pasta de saída existe | Escolha outro nome |
| Lock já existe | Verifique se outra execução usa o destino. Remova manualmente o lock somente após confirmar que não há processo ativo |
| Execução interrompida à força | Confira se há `.dataforge-*` incompleto e lock no diretório pai; remova apenas os resíduos identificados, sem processo ativo |
| Memória insuficiente | Reduza a base ou implemente leitura/processamento em blocos antes de ampliar o volume |

## Segurança operacional

Processamento local, sem envio automático de dados a serviços. O resultado contém os dados originais transformados: escolha diretório com permissões adequadas. Dados reais em `data/raw/` e saídas são ignorados pelo Git; o exemplo fictício é versionável. Não há controle de acesso próprio, criptografia de arquivos nem cofre de segredos nesta ferramenta.

## CI e Docker

A configuração de CI instala dependências, roda Ruff e os testes no GitHub. Não foi publicada ou executada remotamente nesta entrega. O Dockerfile descreve o ambiente da CLI e requer teste local de build, execução e permissões de volumes antes do uso.

## Abrir no VS Code

Abra a pasta raiz que contém `pyproject.toml`, instale o pacote no ambiente virtual e selecione esse interpretador no VS Code. A pasta `.vscode/` inclui configurações de depuração para desktop e pipeline de exemplo. O exemplo de depuração usa `data/processed/debug_001`: troque o destino a cada execução ou remova conscientemente o resultado anterior. A extensão Python/Debugger precisa estar instalada.

## Instalação em outro computador

Não copie o ambiente `.venv`: ele pode conter caminhos absolutos e executáveis específicos de outra máquina. Extraia em uma pasta nova e abra `INICIAR.bat`. Se já houver ambiente inválido, renomeie a pasta `.venv` antiga e execute o inicializador novamente. Não é necessário reinstalar as dependências a cada abertura quando a instalação está íntegra.
