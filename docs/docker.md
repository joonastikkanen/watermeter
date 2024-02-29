# Build dockerimage

```bash
export DOCKER_CLI_EXPERIMENTAL=enabled
sudo docker buildx create --name watermeter --use
sudo docker buildx inspect --bootstrap
sudo docker buildx build --platform linux/arm64 -t watermeter:latest .
```