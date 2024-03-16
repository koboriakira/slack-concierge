dev:
	docker compose up -d
	open http://localhost:10314/docs

cdk-test:
	cd cdk && npm run test

ngrok:
	ngrok http 10121

run:
	python -m slack.lazy_main
