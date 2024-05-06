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
	@echo "$(CYAN)help$(END):				Shows this message."
	@echo "$(CYAN)clean-build$(END):			Removes the 'deps' directory and the 'lambda_function.zip' file."
	@echo "$(CYAN)prune$(END):				Stops all containers and prunes docker."
	@echo ""
	@echo "$(GREEN)@ DEV$(END)"
	@echo "$(CYAN)dev$(END):				Runs run-dev starting $(UNDERLINE)main.py$(END)."
	@echo "$(CYAN)dev-ports$(END):			Shows localhost port bindings."
	@echo "$(CYAN)build-dev$(END):			Builds the project using Docker."
	@echo "$(CYAN)run-dev$(END):			Runs dev environment."
	@echo "$(CYAN)tf-apply-dev$(END):			Applies terraform infrastructure changes with $(UNDERLINE)terraform.tfvars$(END) file."
	@echo ""
	@echo "$(RED)@ PROD$(END)"
	@echo "$(CYAN)prod-build-deps$(END):		Installs depencendies into ./deps directory."
	@echo "$(CYAN)build-local$(END):			Installs depencendies into ./deps directory using Docker."
	@echo "$(CYAN)zip$(END):				Zips dependencies for lambda function."
	@echo "$(CYAN)lint$(END):				Lints code inside ./wallet directory by PEP8."
	@echo "$(CYAN)aws-config$(END):			Configures AWS credentials using AWS CLI."
	@echo "$(CYAN)tf-init$(END):			Initializes terraform backend."
	@echo "$(CYAN)tf-plan$(END):			Shows terraform modifications."
	@echo "$(CYAN)tf-apply$(END):			Applies terraform infrastructure changes."

###########################################################
# PRODUCTION
act:
	act --container-architecture linux/amd64
prod-build-deps:
	pip install -t ./deps -r requirements.txt
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


###########################################################
# DEV
dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env up -d --force-recreate
	$(MAKE) dev-ports
	docker exec -it wallet_api python main.py
clean-build:
	rm -rf ./deps
	rm -rf ./lambda_function.zip
build-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env build
run-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env up -d
	$(MAKE) dev-ports
	docker exec -it wallet_api bash
dev-ports:
	@echo "$(GREEN)Mongo-Express at $(UNDERLINE)http://localhost:8081$(END)"
	@echo "$(GREEN)WalletAPI at $(UNDERLINE)http://localhost:8000$(END)"
prune:
	docker stop $$(docker ps -a -q)
	docker system prune -a -f


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