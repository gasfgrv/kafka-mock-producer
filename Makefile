.PHONY: help docker-up docker-down docker-restart venv-create venv-destroy pip-install pip-uninstall run-tests clean-test-artifacts run-app build-and-run vscode-setup

WORKDIR=$(shell pwd)
PYTHON-VERSION=python3.14
VENV-NAME=.venv
VENV-PYTHON=$(WORKDIR)/$(VENV-NAME)/bin/python
PIP=$(VENV-PYTHON) -m pip

help:
	@echo "Makefile para o projeto"
	@echo ""
	@echo "Comandos disponíveis:"
	@echo "  make docker-up       - Subir o docker compose"
	@echo "  make docker-down     - Parar o docker compose"
	@echo "  make docker-restart  - Reiniciar o docker compose"
	@echo "  make venv-create     - Criar o ambiente virtual"
	@echo "  make venv-destroy    - Destruir o ambiente virtual"
	@echo "  make pip-install     - Instalar as dependências do projeto"
	@echo "  make pip-uninstall   - Desinstalar as dependências do projeto"
	@echo "  make run-tests       - Rodar os testes do projeto"
	@echo "  make clean-test-artifacts - Limpar arquivos temporários e cache"
	@echo "  make run-app         - Rodar a aplicação"
	@echo "  make build-and-run   - Construir a imagem Docker e rodar a aplicação"
	@echo "  make vscode-setup    - Configurar o Visual Studio Code para o projeto"

docker-up:
	@echo "Subindo o docker compose..."
	docker compose up -d
	
docker-down:
	@echo "Parando o docker compose..."
	docker compose down

docker-restart:
	@echo "Reiniciando o docker compose..."
	docker compose down
	docker compose up -d

venv-create:
	@echo "Criando o ambiente virtual..."
	$(PYTHON-VERSION) -m venv $(VENV-NAME)
	@echo "Ambiente virtual criado em $(VENV-NAME)"
	@echo "Você pode ativar o ambiente virtual usando: source $(VENV-NAME)/bin/activate"

venv-destroy:
	@echo "Destruindo o ambiente virtual..."
	rm -rf $(VENV-NAME)

pip-install:
	@echo "Instalando as dependências do projeto..."
	$(PIP) install -r requirements.txt
	@echo "Dependências instaladas com sucesso!"

pip-uninstall:
	@echo "Desinstalando as dependências do projeto..."
	$(PIP) uninstall -r requirements.txt -y
	@echo "Dependências desinstaladas com sucesso!"

run-tests:
	@echo "Rodando os testes do projeto..."
	$(VENV-PYTHON) -m pytest -v
	@echo "Testes executados com sucesso!"

clean-test-artifacts:
	@echo "Limpando arquivos temporários e cache..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Limpeza concluída!"

run-app:
	@echo "Rodando a aplicação..."
	$(VENV-PYTHON) main.py run --debug --host=0.0.0.0 --port=5000

build-and-run:
	@echo "Subindo o docker compose..."
	docker compose up -d
	@echo "Rodando a aplicação..."
	$(VENV-PYTHON) main.py run --debug --host=0.0.0.0 --port=5000
	@echo "Aplicação rodando em http://localhost:5000"

vscode-setup:
	@echo "Configurando o Visual Studio Code para o projeto..."
	@echo "Criando diretório de configuração do VS Code..."
	mkdir -p $(WORKDIR)/.vscode
	@echo "Diretório de configuração do VS Code criado!"
	@echo "Criando arquivo de configuração de execução no VS Code..."
	echo '{"version":"0.2.0","configurations":[{"name":"Python: Flask (app)","type":"debugpy","request":"launch","program":"${workspaceFolder}/main.py","console":"integratedTerminal","cwd":"${workspaceFolder}","env":{"FLASK_APP":"main.py","FLASK_ENV":"development"},"args":["run","--debug","--host=0.0.0.0","--port=5000"],"justMyCode":true,"python":"${workspaceFolder}/.venv/bin/python"}]}' > $(WORKDIR)/.vscode/launch.json
	@echo "Arquivo de configuração de execução criado!"
	@echo "Criando arquivo de configuração para os testes no VS Code..."
	echo '{"python.testing.pytestArgs":["tests","-v"],"python.testing.unittestEnabled":false,"python.testing.pytestEnabled":true}' > $(WORKDIR)/.vscode/settings.json
	@echo "Arquivo de configuração de testes criado!"
	@echo "Configuração do Visual Studio Code concluída! Você pode agora depurar a aplicação e rodar os testes diretamente do VS Code."