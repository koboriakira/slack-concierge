.PHONY: dev
dev:
	docker compose up -d
	open http://localhost:10314/docs

.PHONY: cdk-test
cdk-test:
	cd cdk && npm run test

.PHONY: ngrok
ngrok:
	ngrok http 10121

.PHONY: run
run:
	python -m slack.lazy_main

.PHONY: test
test:
	pytest -m "not learning and not slow"
