###########################################################
# PRODUCTION
prod-build-deps:
	pip install -t ./deps -r requirements.txt
zip:
	cd deps && zip ../lambda_function.zip -r .
	cd wallet && zip ../lambda_function.zip -u ./*


###########################################################
# DEV
build-dev: build-requirements zip

clean-build:
	rm -rf ./deps
	rm -rf ./lambda_function.zip
build-requirements:
	docker build -t zip-build-lambda -f Dockerfile.prod .
	docker create --name zip-build zip-build-lambda
	docker cp zip-build:/app/deps .
	docker remove zip-build
run-dev:
	docker-compose -f docker-compose.dev.yaml up -d
	docker exec -it wallet_api python main.py


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