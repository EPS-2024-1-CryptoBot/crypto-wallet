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
	@printf "%-30b %b\n" "$(CYAN)dev$(END):" "Runs run-dev starting $(UNDERLINE)main.py$(END)."
	@printf "%-30b %b\n" "$(CYAN)dev-ports$(END):" "Shows localhost port bindings."
	@printf "%-30b %b\n" "$(CYAN)build-dev$(END):" "Builds the project using Docker."
	@printf "%-30b %b\n" "$(CYAN)run-dev$(END):" "Runs dev environment."
	@printf "%-30b %b\n" "$(CYAN)tf-apply-dev$(END):" "Applies terraform infrastructure changes with $(UNDERLINE)terraform.tfvars$(END) file."
	@echo ""
	@echo "$(RED)@ PROD$(END)"
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
	act --container-architecture linux/amd64
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