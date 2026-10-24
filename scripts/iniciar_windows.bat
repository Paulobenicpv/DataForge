@echo off
setlocal
cd /d "%~dp0.."
if not exist "scripts\verificar_projeto.py" goto projeto_incompleto
if exist ".venv\Scripts\python.exe" goto verificar
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 goto tentar_python
py -3 -m venv .venv
if errorlevel 1 goto erro
goto verificar
:tentar_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 goto sem_python
python -m venv .venv
if errorlevel 1 goto erro
:verificar
".venv\Scripts\python.exe" -c "import sys,tkinter; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if errorlevel 1 goto ambiente_invalido
".venv\Scripts\python.exe" scripts\verificar_projeto.py
if errorlevel 1 goto fim_erro
".venv\Scripts\python.exe" scripts\verificar_instalacao.py >nul 2>&1
if not errorlevel 1 goto executar
".venv\Scripts\python.exe" -m pip install -e .
if errorlevel 1 goto erro
".venv\Scripts\python.exe" scripts\verificar_instalacao.py
if errorlevel 1 goto erro
:executar
".venv\Scripts\python.exe" -m dataforge.interfaces.desktop
if errorlevel 1 goto erro
exit /b 0
:projeto_incompleto
echo Projeto incompleto. Extraia o ZIP inteiro em uma pasta nova.
goto fim_erro
:sem_python
echo Python 3.10 ou superior nao encontrado. Instale Python com Tkinter e tente novamente.
goto fim_erro
:ambiente_invalido
echo Ambiente .venv invalido ou Tkinter ausente.
echo Renomeie a pasta .venv antiga e execute este arquivo novamente.
goto fim_erro
:erro
echo Falha. Consulte o erro acima. A primeira instalacao precisa de internet.
:fim_erro
pause
exit /b 1
