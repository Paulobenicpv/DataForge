# Validação da revisão 2.1.1

Ambiente de testes: Linux com Python 3.12 e dependências disponíveis no runtime.

17 testes aprovados com `PYTHONPATH=src python -m unittest discover -s tests -v`.

Os testes verificam: leitura CSV/XLSX, preservação de identificadores, cabeçalhos repetidos, rejeição de CSV malformado, conversões inválidas, precisão decimal, agrupamento de milhar, horários e frações, JSON com BOM do Windows, original intacto, publicação completa, bloqueio de destino, falha na exportação, CLI, presença dos inicializadores e mensagem para converter ausente.

A distribuição é inspecionada para confirmar presença de INICIAR.bat, converters.py e verificar_instalacao.py, e ausência de .venv, __pycache__, .pyc e metadados .egg-info. Os testes também são executados a partir de uma extração limpa do ZIP final para conferir os arquivos efetivamente entregues.

O funcionamento da janela e dos scripts .bat precisa ser confirmado no Windows. Não foram executados Docker, GitHub Actions remoto nem testes de carga. A ferramenta executa tratamentos locais determinísticos; não contém IA integrada.
