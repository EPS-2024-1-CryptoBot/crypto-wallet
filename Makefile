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
	@echo "$(CYAN)dev$(END):		Runs run-dev starting $(UNDERLINE)main.py$(END)."
	@echo "$(CYAN)clean-build$(END):	Removes the 'deps' directory and the 'lambda_function.zip' file."
	@echo "$(CYAN)build-dev$(END):	Builds the project using Docker."
	@echo "$(CYAN)run-dev$(END):	Runs dev environment."
	@echo "$(CYAN)prune$(END):		Stops all containers and prunes docker."

###########################################################
# PRODUCTION
prod-build-deps:
	pip install -t ./deps -r requirements.txt
zip:
	cd deps && zip ../lambda_function.zip -r .
	cd wallet && zip ../lambda_function.zip -u ./*


###########################################################
# DEV
dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env up -d --force-recreate
	docker exec -it wallet_api python main.py
clean-build:
	rm -rf ./deps
	rm -rf ./lambda_function.zip
build-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env build
run-dev:
	docker-compose -f docker-compose.dev.yaml --env-file ./dev.env up -d
	docker exec -it wallet_api bash
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