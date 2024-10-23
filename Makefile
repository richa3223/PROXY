SHELL=/bin/bash -euo pipefail
OS := $(shell uname -s)
build_dir_base_path := build
# Will default to using the shared common stack.
use_shared_common_stack := true

###################
##  installation ##
###################

install-python:
	sudo apt update
	sudo apt install software-properties-common
	sudo add-apt-repository ppa:deadsnakes/ppa
	sudo apt update
	sudo apt install python3.9 python3.9-dev python3.9-venv python3-venv


install-poetry-in-venv:
	python3.9 -m venv .venv && \
	. .venv/bin/activate && \
	python3.9 -m pip install --upgrade pip setuptools && \
	python3.9 -m pip install poetry && \
	python3.9 -m pip install awsume && \
	cd lambdas && poetry install

install-python-dependencies:
	python3.9 -m venv .venv && \
	. .venv/bin/activate && \
	python3.9 -m pip install --upgrade pip setuptools && \
	python3.9 -m pip install poetry

install-tflint:
	curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

install-tfsec:
	curl -s https://raw.githubusercontent.com/aquasecurity/tfsec/master/scripts/install_linux.sh | bash

# For more detials and troubleshooting please refer to /nhsd-git-secrets/Readme.md
install-secret-scanner:
	cd nhsd-git-secrets && cp .gitallowed-base ../.gitallowed && \
	./install-linux.sh

######################
# Formatting/Linting #
######################
black-check:
	poetry -C lambdas run black . --check

black-format:
	poetry -C lambdas run black .

## TODO: Link isort into a single lint-check & link-format make commands ##
isort-check:
	poetry -C lambdas run isort --check --color lambdas

isort-format:
	poetry -C lambdas run isort lambdas

lint-lambdas:
	poetry -C lambdas run pylint lambdas --fail-under=8.0 --rcfile=lambdas/pyproject.toml

run-vulture:
	poetry -C lambdas run vulture lambdas vulture_allowlist.txt

#####################
###### Testing ######
#####################

unit-test-coverage:
	pytest --cov

unit-test-coverage-html:
	pytest --cov=. --cov-report html; \
	cd htmlcov; \
	python3 -m http.server

###################
###### build ######
###################

build-lambda-%:
# delete last build if it exist
	if [ -d build/$* ]; then rm -Rf build/$*; fi

# Create the dependencies and function folder
	mkdir -p ${build_dir_base_path}/$*/dependencies/python
	mkdir -p ${build_dir_base_path}/$*/function/lambdas/$*
	mkdir -p ${build_dir_base_path}/$*/function/lambdas/utils

# Install the requirements in the layer dependencies/python folder through pip
	cd lambdas && \
	poetry export --only $* --without-hashes --output ../${build_dir_base_path}/$*/dependencies/python/requirements.txt && \
	python3.9 -m pip install -r ../${build_dir_base_path}/$*/dependencies/python/requirements.txt --target ../${build_dir_base_path}/$*/dependencies/python --platform manylinux2014_x86_64 --only-binary=:all:

# Copy the lambda code into the build function directory
	cp -r lambdas/$*/* ${build_dir_base_path}/$*/function/lambdas/$*
	cp -r lambdas/utils/* ${build_dir_base_path}/$*/function/lambdas/utils

build-all-lambdas: \
	build-lambda-verify_parameters \
	build-lambda-relationship_lookup \
	build-lambda-pds_get_patient_details \
	build-lambda-pds_access_token \
	build-lambda-process_validation_result \
	build-lambda-validate_eligibility \
	build-lambda-validate_relationship \
	build-lambda-redact_sensitive_data \
	build-lambda-start_standard_audit_data_crawler \
	build-lambda-start_sensitive_audit_data_crawler \
	build-lambda-splunk_log_and_metric_formatter \
	build-lambda-create_access_request \
	build-lambda-send_gp_email \
	build-lambda-ods_lookup \
	build-lambda-get_email_template \
	build-lambda-create_merged_email \
	build-lambda-redact_eventbridge_events_and_log_to_cloudwatch \
	build-lambda-get_candidate_relationships \
	build-lambda-raise_certificate_alert \
	build-lambda-slack_alerts

# This command returns an exit of one, the echo forces a return of 0
# Use this command when you have fixed all real vulture errors and the rest are false positives
update-vulture-allowlist:
	. .venv/bin/activate && \
	vulture lambdas --make-whitelist > vulture_allowlist.txt \
	|| echo "Successfully updated"

###################
##   Utilities   ##
###################
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Variable $* not set"; \
		exit 1; \
	fi

#####################
###   Terraform   ###
#####################
terraform-init: guard-env guard-stack
	rm -rf ./terraform/stacks/$(stack)/.terraform
	terraform -chdir=./terraform/stacks/$(stack) init -var-file=../../env_vars/$(env)/$(stack).tfvars -backend-config=../../backend_config/$(env)/$(stack).conf -upgrade
	terraform -chdir=./terraform/stacks/$(stack) get -update

terraform-workspace: guard-env guard-stack guard-workspace
	terraform -chdir=./terraform/stacks/$(stack) workspace select -or-create $(workspace)
	terraform -chdir=./terraform/stacks/$(stack) workspace show

terraform-workspace-list: guard-env guard-stack terraform-init
	terraform -chdir=./terraform/stacks/$(stack) workspace list

terraform-workspace-delete: guard-env guard-stack guard-workspace
	terraform -chdir=./terraform/stacks/$(stack) workspace select default
	terraform -chdir=./terraform/stacks/$(stack) workspace delete $(workspace)

terraform: guard-env guard-stack guard-tf-command terraform-init terraform-workspace
	terraform -chdir=./terraform/stacks/$(stack) $(tf-command) -var-file=../../env_vars/$(env)/$(stack).tfvars $(args) $(if $(filter $(stack),common baseconfig bootstrap),,-var use_shared_common_stack=$(use_shared_common_stack))
	rm -f ./terraform_outputs_$(stack).json || true
	mkdir -p build
	terraform -chdir=./terraform/stacks/$(stack) output -json > ./build/terraform_outputs_$(stack).json

build-and-terraform: guard-env guard-stack guard-tf-command
	make build-all-lambdas
	make terraform
