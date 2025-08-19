IMAGE_NAME=nitro-system
TAG=latest
REGISTRY=ghcr.io/pashitox

build:
	docker compose -f docker-compose.prod.yml build

push:
	echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin
	docker compose -f docker-compose.prod.yml push

deploy:
	docker compose -f docker-compose.prod.yml up -d

login:
	echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin