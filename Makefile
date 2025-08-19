IMAGE_NAME=nitro-system
TAG=latest
REGISTRY=ghcr.io/pashitox

.PHONY: build push deploy login fix-requirements

fix-requirements:
	@echo "🔧 Corrigiendo requirements.txt..."
	sed -i 's/sycopg2-binary/psycopg2-binary/g' api-dashboard/dashboards/requirements.txt
	@echo "✅ requirements.txt corregido"

build: fix-requirements
	docker build -t $(REGISTRY)/$(IMAGE_NAME):$(TAG) ./api-dashboard/dashboards

push:
	@echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin
	docker push $(REGISTRY)/$(IMAGE_NAME):$(TAG)

deploy: build push
	docker compose -f docker-compose.prod.yml down
	docker compose -f docker-compose.prod.yml up -d

login:
	@echo "$$GITHUB_TOKEN" | docker login ghcr.io -u pashitox --password-stdin

clean:
	docker compose -f docker-compose.prod.yml down
	docker system prune -f

logs:
	docker compose -f docker-compose.prod.yml logs -f

status:
	docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"