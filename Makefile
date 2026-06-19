SHELL := /bin/bash
.DEFAULT_GOAL := help

COMPOSE_DEV  := docker-compose.yml
COMPOSE_PROD := docker-compose.prod.yml
SERVICES_DIR := services
LIBS_DIR     := libs

SERVICES := ai career crisis-engine game notifications study users

.PHONY: help
help: ## Показать это справочное сообщение
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

.PHONY: init-env
init-env: ## Инициализировать локальные .env файлы из шаблонов .env.example
	@echo "==> Инициализация локальных .env файлов..."
	@# 1. Копируем корневой файл общих настроек
	@if [ -f common.env.example ] && [ ! -f common.env ]; then \
		cp common.env.example common.env && echo "Создан: common.env"; \
	fi
	@# 2. Копируем переменные для инфраструктуры (postgres, kafka, redis, s3)
	@find infrastructure/env -name "*.env.example" | while read -r file; do \
		target_file="$${file%.example}"; \
		if [ ! -f "$$target_file" ]; then \
			cp "$$file" "$$target_file"; \
			echo "Создан: $$target_file"; \
		fi; \
	done
	@# 3. Копируем переменные для каждого микросервиса
	@find services -name ".env.example" | while read -r file; do \
		target_file="$${file%.example}"; \
		if [ ! -f "$$target_file" ]; then \
			cp "$$file" "$$target_file"; \
			echo "Создан: $$target_file"; \
		fi; \
	done
	@echo "==> Инициализация конфигураций завершена."


.PHONY: up
up: ## Запустить локальное окружение в фоновом режиме
	docker compose -f $(COMPOSE_DEV) up -d

.PHONY: down
down: ## Остановить локальное окружение и удалить связанные volumes
	docker compose -f $(COMPOSE_DEV) down -v

.PHONY: build
build: ## Собрать или пересобрать локальные контейнеры
	docker compose -f $(COMPOSE_DEV) build

.PHONY: restart
restart: ## Перезапустить контейнеры локального окружения
	docker compose -f $(COMPOSE_DEV) restart

.PHONY: logs
logs: ## Просмотр логов всех контейнеров в реальном времени
	docker compose -f $(COMPOSE_DEV) logs -f --tail=100


.PHONY: prod-up
prod-up: ## Запустить продакшен конфигурацию
	docker compose -f $(COMPOSE_PROD) up -d

.PHONY: prod-down
prod-down: ## Остановить продакшен контейнеры
	docker compose -f $(COMPOSE_PROD) down

.PHONY: prod-build
prod-build: ## Собрать продакшен образы
	docker compose -f $(COMPOSE_PROD) build


.PHONY: format
format: ## Форматировать Python-код (ruff или black) во всем монорепозитории
	@if command -v ruff >/dev/null 2>&1; then \
		ruff format $(SERVICES_DIR) $(LIBS_DIR); \
	elif command -v black >/dev/null 2>&1; then \
		black $(SERVICES_DIR) $(LIBS_DIR); \
	else \
		echo "Ошибка: Ни ruff, ни black не установлены в вашей локальной системе."; \
		exit 1; \
	fi

.PHONY: lint
lint: ## Проверить код линтером (ruff или flake8)
	@if command -v ruff >/dev/null 2>&1; then \
		ruff check $(SERVICES_DIR) $(LIBS_DIR); \
	elif command -v flake8 >/dev/null 2>&1; then \
		flake8 $(SERVICES_DIR) $(LIBS_DIR); \
	else \
		echo "Ошибка: Ни ruff, ни flake8 не установлены локально."; \
		exit 1; \
	fi

.PHONY: test
test: ## Запустить тесты внутри Docker-контейнеров для всех сервисов (где они настроены)
	@echo "==> Запуск тестов в микросервисах..."
	@for service in $(SERVICES); do \
		if [ -d "$(SERVICES_DIR)/$$service/app/tests" ] || [ -d "$(SERVICES_DIR)/$$service/tests" ]; then \
			echo "Тестирование сервиса: $$service..."; \
			docker compose -f $(COMPOSE_DEV) run --rm $$service pytest || exit 1; \
		else \
			echo "Пропуск $$service (папка с тестами не найдена)"; \
		fi \
	done


.PHONY: clean
clean: ## Удалить файлы кэша Python, кэш тестов и системный мусор (.DS_Store и т.д.)
	@echo "==> Очистка временных файлов..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".DS_Store" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	@echo "==> Очистка завершена."