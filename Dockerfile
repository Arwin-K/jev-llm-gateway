FROM python:3.12.7-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 JEV_BIND_HOST=0.0.0.0
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN python -m pip install --no-cache-dir . && \
    useradd --system --uid 10001 --create-home gateway
USER gateway
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c 'from urllib.request import urlopen; urlopen("http://127.0.0.1:8080/healthz", timeout=2).close()'
CMD ["jev", "serve"]
