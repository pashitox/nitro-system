IMAGE_NAME=nitro-system
TAG=latest
REGISTRY=ghcr.io/pashitox

.PHONY: build push deploy login

build:
	docker compose -f docker-compose.prod.yml build

push:
	@echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin
	docker tag nitro-system-streamlit $(REGISTRY)/$(IMAGE_NAME):$(TAG)
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

deploy:
	docker compose -f docker-compose.prod.yml up -d --build

login:
	@echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin

clean:
	docker compose -f docker-compose.prod.yml down
	docker system prune -f

logs:
	docker compose -f docker-compose.prod.yml logs -f