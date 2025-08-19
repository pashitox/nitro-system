# 🚀 Guía de Despliegue en Producción

## Prerrequisitos
- Docker y Docker Compose instalados
- Acceso a GitHub Actions
- Secrets configurados en el repositorio

## Pasos
1. Ejecutar `git push origin main` → dispara el workflow.
2. El workflow construye imágenes y las sube a GHCR.
3. En el servidor de producción:
   ```bash
   docker login ghcr.io -u <tu_usuario> -p <TOKEN>
   git pull origin main
   make deploy
