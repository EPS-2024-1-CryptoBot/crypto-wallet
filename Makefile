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
	@printf "%-30b %b\n" "$(CYAN)help$(END):" "Shows this message."
	@printf "%-30b %b\n" "$(CYAN)act$(END):" "Runs GitHub actions locally."
	@printf "%-30b %b\n" "$(CYAN)clean-build$(END):" "Removes the 'deps' directory and the 'lambda_function.zip' file."
	@printf "%-30b %b\n" "$(CYAN)prune$(END):" "Stops all containers and prunes docker."
	@echo ""
	@echo "$(GREEN)@ DEV$(END)"
	@printf "%-30b %b\n" "$(CYAN)sonar-dev$(END):" "Uploads coverage and analyses code to SonarQube locally using '.secrets' file for envs."
	@printf "%-30b %b\n" "$(CYAN)test-dev$(END):" "Runs all test suites using docker ready for production coverage."
	@printf "%-30b %b\n" "$(CYAN)coverage-dev$(END):" "Generates coverage report without docker at ./coverage-reports directory."
	@echo ""
	@printf "%-30b %b\n" "$(CYAN)dev$(END):" "Runs run-dev starting $(UNDERLINE)main.py$(END)."
	@printf "%-30b %b\n" "$(CYAN)dev-ports$(END):" "Shows localhost port bindings."
	@printf "%-30b %b\n" "$(CYAN)build-dev$(END):" "Builds the project using Docker."
	@printf "%-30b %b\n" "$(CYAN)run-dev$(END):" "Runs dev environment."
	@printf "%-30b %b\n" "$(CYAN)tf-apply-dev$(END):" "Applies terraform infrastructure changes with $(UNDERLINE)terraform.tfvars$(END) file."
	@echo ""
	@echo "$(RED)@ PROD$(END)"
	@printf "%-30b %b\n" "$(CYAN)sonar$(END):" "Uploads coverage and analyses code in production using SonarQube."
	@printf "%-30b %b\n" "$(CYAN)coverage$(END):" "Generates coverage report using docker at ./coverage-reports directory."
	@echo ""
	@printf "%-30b %b\n" "$(CYAN)prod-build-deps$(END):" "Installs depencendies into ./deps directory."
	@printf "%-30b %b\n" "$(CYAN)build-local$(END):" "Installs depencendies into ./deps directory using Docker."
	@printf "%-30b %b\n" "$(CYAN)zip$(END):" "Zips dependencies for lambda function."
	@printf "%-30b %b\n" "$(CYAN)lint$(END):" "Formats code inside ./wallet directory by PEP8."
	@echo ""
	@printf "%-30b %b\n" "$(CYAN)aws-config$(END):" "Configures AWS credentials using AWS CLI."
	@echo ""
	@printf "%-30b %b\n" "$(CYAN)tf-init$(END):" "Initializes terraform backend."
	@printf "%-30b %b\n" "$(CYAN)tf-plan$(END):" "Shows terraform modifications."
	@printf "%-30b %b\n" "$(CYAN)tf-apply$(END):" "Applies terraform infrastructure changes."

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