dev:
	docker compose up -d
	open http://localhost:10120/docs

cdk-test:
	cd cdk && npm run test

ngrok:
	ngrok http 10121

run:
	python slack/lazy_main.py
