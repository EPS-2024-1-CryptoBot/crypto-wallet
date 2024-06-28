PURPLE = \033[95m
CYAN = \033[96m
DARKCYAN = \033[36m
BLUE = \033[94m
GREEN = \033[92m
YELLOW = \033[93m
RED = \033[91m
BOLD = \033[1m
UNDERLINE = \033[4m
END = \033[0m

help:
	@echo "$(YELLOW)# ------------------- Makefile commands ------------------- #$(END)"
	@echo ""
	@echo "$(RED)## PRODUCTION$(END)"
	@printf "$(CYAN)%-20s$(END) %b \n" "act:" "Runs GitHub actions workflows using 'act'"
	@printf "$(CYAN)%-20s$(END) %b \n" "prod-build-deps:" "Installs production dependencies"
	@printf "$(CYAN)%-20s$(END) %b \n" "build-local:" "Builds the production Docker image and prepares zip"
	@printf "$(CYAN)%-20s$(END) %b \n" "zip:" "Creates a zip archive for deployment"
	@printf "$(CYAN)%-20s$(END) %b \n" "lint:" "Runs linting using black"
	@printf "$(CYAN)%-20s$(END) %b \n" "coverage:" "Runs tests with coverage and uploads to SonarQube"
	@printf "$(CYAN)%-20s$(END) %b \n" "sonar:" "Runs SonarQube analysis for Python code"
	@echo ""

	@echo "$(GREEN)## DEV$(END)"
	@printf "$(CYAN)%-20s$(END) %b \n" "dev:" "Builds and runs the development environment"
	@printf "$(CYAN)%-20s$(END) %b \n" "clean-build:" "Cleans previous build artifacts"
	@printf "$(CYAN)%-20s$(END) %b \n" "build-dev:" "Builds the development Docker image"
	@printf "$(CYAN)%-20s$(END) %b \n" "run-dev:" "Runs the development Docker containers"
	@printf "$(CYAN)%-20s$(END) %b \n" "dev-ports:" "Displays ports for services in development"
	@printf "$(CYAN)%-20s$(END) %b \n" "prune:" "Stops and removes all Docker containers"
	@printf "$(CYAN)%-20s$(END) %b \n" "test-dev:" "Runs tests in the development environment"
	@printf "$(CYAN)%-20s$(END) %b \n" "coverage-dev:" "Runs coverage tests in the development environment"
	@printf "$(CYAN)%-20s$(END) %b \n" "sonar-dev:" "Runs SonarQube analysis for development"
	@echo ""

	@echo "$(BLUE)## AWS$(END)"
	@printf "$(CYAN)%-20s$(END) %b \n" "aws-config:" "Configures AWS CLI"
	@echo ""

	@echo "$(PURPLE)## TERRAFORM$(END)"
	@printf "$(CYAN)%-20s$(END) %b \n" "tf-init:" "Initializes Terraform in the 'terraform' directory"
	@printf "$(CYAN)%-20s$(END) %b \n" "tf-plan:" "Runs Terraform plan in the 'terraform' directory"
	@printf "$(CYAN)%-20s$(END) %b \n" "tf-apply:" "Applies Terraform changes in the 'terraform' directory"
	@printf "$(CYAN)%-20s$(END) %b \n" "tf-apply-dev:" "Applies Terraform changes with dev environment specifics"
	@echo ""

###########################################################
# PRODUCTION
act:
	act --container-architecture linux/amd64 --rm --secret-file .secrets --var-file .vars
prod-build-deps:
	python -m pip install -t ./deps -r requirements.txt
build-local:
	docker build -t wallet_api -f Dockerfile.prod .
	docker create --name api_zip wallet_api
	docker cp api_zip:/app/deps ./deps
	docker rm api_zip
zip:
	cd deps && zip ../lambda_function.zip -r .
	cd wallet && zip ../lambda_function.zip -u ./*
lint:
	find ./wallet/* -name "*.py" | xargs black
	find ./tests/* -name "*.py" | xargs black
.PHONY: coverage
coverage:
	docker compose -f docker-compose.dev.yaml --profile tests up tests --build -d
	docker exec -t wallet_tests bash -c "pytest --cov=wallet"
	docker exec -t wallet_tests bash -c "pytest --cov-report xml:/app/coverage.xml --cov=wallet && coverage xml -i"
	docker cp wallet_tests:/app/coverage.xml ./coverage-reports/coverage.xml
	docker stop wallet_tests
	docker rm wallet_tests
sonar:
	sonar-scanner \
	-Dsonar.projectKey=$$SONAR_PROJECT_KEY \
	-Dsonar.organization=$$SONAR_ORGANIZATION \
	-Dsonar.host.url=https://sonarcloud.io \
	-Dsonar.token=$$SONAR_TOKEN \
	-Dsonar.sonar.sources=wallet \
	-Dsonar.python.coverage.reportPaths=$$(pwd)/coverage-reports/coverage.xml \
	-Dsonar.sonar.language=py \
	-Dsonar.sonar.sourceEncoding=UTF-8 \
	-Dsonar.sonar.exclusions=/venv/** \
	-Dsonar.cpd.exclusions=tests/**,terraform/** \
	-Dsonar.coverage.exclusions=tests/**,terraform/** \
	# -Dsonar.qualitygate.wait=true \


###########################################################
# DEV
dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env --profile dev up -d --force-recreate
	$(MAKE) dev-ports
	docker exec -it wallet_api python main.py
bigbang:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env --profile dev up -d --force-recreate
	$(MAKE) dev-ports
	docker exec -d wallet_api python main.py
clean-build:
	rm -rf ./deps
	rm -rf ./lambda_function.zip
build-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env --profile dev build
run-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env --profile dev up -d
	$(MAKE) dev-ports
	docker exec -it wallet_api bash
dev-ports:
	@echo "$(GREEN)Mongo-Express at $(UNDERLINE)http://localhost:8081$(END)"
	@echo "$(GREEN)WalletAPI at $(UNDERLINE)http://localhost:8000$(END)"
prune:
	docker stop $$(docker ps -a -q)
	docker system prune -a -f
test-dev:
	clear
	export $$(grep -v '^#' dev.env | xargs) && \
	docker compose -f docker-compose.dev.yaml --profile tests run --name wallet_tests --rm tests bash -c "pytest -v -s"
coverage-dev:
	clear
	export $$(grep -v '^#' dev.env | xargs) && \
	PYTHONPATH=${PYTHONPATH}:$$(pwd)/wallet pytest --cov-report xml:./coverage-reports/coverage.xml --cov-report html:./coverage-reports/html --cov=wallet && coverage xml -i
sonar-dev:
	clear
	export $$(grep -v '^#' .secrets | xargs) && \
	$(MAKE) sonar


###########################################################
# AWS
aws-config:
	rm -rf ~/.aws
	aws configure


###########################################################
# TERRAFORM
tf-init:
	cd terraform && $(MAKE) init
tf-plan:
	cd terraform && $(MAKE) plan
tf-apply:
	cd terraform && $(MAKE) apply
tf-apply-dev:
	cd terraform && $(MAKE) apply-dev