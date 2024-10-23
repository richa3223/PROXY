.PHONY: test-api test-lambdas test-infra test-step-functions

ENVIRONMENT ?= dev
APIGEE_ENVIRONMENT ?= internal-dev
APIGEE_INPUT_VALUES := --api-name=validated-relationships-service-api --proxy-name=validated-relationships-service-api-$(APIGEE_ENVIRONMENT)
LOAD_TEST_HOST = https://$(APIGEE_ENVIRONMENT).api.service.nhs.uk/validated-relationships/FHIR/R4

test-api:
	poetry run pytest test_api -s -o log_cli=true -o log_cli_level=INFO --tb=short --gherkin-terminal-reporter -vvv $(APIGEE_INPUT_VALUES) --html-report=test_api/report.html $(PYTEST_ARGS) -k "not skip" --color=yes --reruns 2 --reruns-delay 10 --only-rerun AssertionError

test-lambdas:
	poetry run pytest test_lambdas -s -o log_cli=true -o log_cli_level=INFO --html-report=test_lambdas/report.html -vv $(PYTEST_ARGS) --color=yes

test-infra:
	poetry run pytest test_infrastructure -s -o log_cli=true -o log_cli_level=INFO --gherkin-terminal-reporter -vvv $(APIGEE_INPUT_VALUES) --html-report=test_infrastructure/report.html $(PYTEST_ARGS) --color=yes

test-step-functions:
	poetry run pytest test_step_functions -s -o log_cli=true -o log_cli_level=INFO --tb=short --gherkin-terminal-reporter -vvv --html-report=test_step_functions/report.html $(PYTEST_ARGS) --color=yes -k "not skip"

test-weekly:
	poetry run pytest test_weekly -s -o log_cli=true -o log_cli_level=INFO -vvv --html-report=test_weekly/report.html $(PYTEST_ARGS) --color=yes

test-load:
	poetry run locust --headless --users 5 --spawn-rate 1 --run-time 10s -H $(LOAD_TEST_HOST) -f=test_load/locustfiles/all_endpoints.py --csv example

test-load-relationship-validation:
	poetry run locust --headless --users 5 --spawn-rate 1 --run-time 10s -H $(LOAD_TEST_HOST) -f=test_load/locustfiles/relationship_validation.py --csv example

test-load-questionnaire-response:
	poetry run locust --headless --users 5 --spawn-rate 1 --run-time 10s -H $(LOAD_TEST_HOST) -f=test_load/locustfiles/questionnaire_response.py --csv example

test-load-master:
	poetry run locust --headless --users 5 --spawn-rate 1 --run-time 120s -H $(LOAD_TEST_HOST) -f=test_load/locustfiles/all_endpoints.py --master --html=load-testing-report.html

test-load-worker:
	poetry run locust --headless --users 5 --spawn-rate 1 --run-time 120s -H $(LOAD_TEST_HOST) -f=test_load/locustfiles/all_endpoints.py --worker --master-host=$(MASTER_HOST) --html=load-testing-report.html

load-test-results:
	@timestamp=$$(date +%d-%m-%Y-%H-%M); \
	aws s3 cp load-testing-report.html s3://main-$(ENVIRONMENT)-load-testing-bucket/$$timestamp-load-testing-report.html

%-with-get-token:
	make $* APIGEE_ACCESS_TOKEN=`get_token`
