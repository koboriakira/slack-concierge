dev:
	docker compose up -d
	open http://localhost:10120/docs

cdk-test:
	cd cdk && npm run test
