# Alterações

## 2.1.1

- Inicializador INICIAR.bat restaurado na raiz.
- Arquivo verificar_instalacao.py incluído, validando imports e versão instalada.
- Checagem de integridade antes da instalação, com nomes dos módulos ausentes.
- Conversor presente no pacote, com arquivo UTF-8 normalizado.
- ZIP sem ambiente virtual, caches e metadados de instalação da máquina de origem.
- .gitignore ampliado para ambientes, segredos locais, caches e resultados.
- Regressões da inicialização, precisão decimal e distribuição.


## 2.1.0

- ZIP sem ambiente virtual e arquivos compilados da máquina de origem.
- Inicializador na raiz, suporte a `py` ou `python` e instalação somente quando necessária.
- Interface com separador, codificação, nome da aba, limpeza de JSON, rolagem e acesso ao resultado.
- Avisos de conversão destacam as colunas que foram preservadas.
- Decimais exatos e validação dos grupos de milhar.
- Datas exportadas com horário e frações preservados.
- JSON UTF-8 com BOM aceito na CLI e no desktop.
- Validação de configuração com cópia independente e erros de tipo explícitos.
- CSV com conteúdo multilinha preservado e TSV com cabeçalho sem dados suportado.
- Regressões para os problemas corrigidos.

## 2.0.0

- Código dividido em pacote src com módulos por responsabilidade.
- CLI e desktop compartilham a mesma orquestração.
- Instalação e comandos definidos em pyproject.toml.
- Publicação isolada com lock e pasta temporária.
- UUID, status de avisos, logs e fingerprint em blocos.
- Testes de integração da CLI e de falhas na exportação.
- Documentação, scripts Windows, definição de CI e Dockerfile.

## 1.0.0

- Primeira implementação local com CSV/XLSX, regras de limpeza e relatório.
