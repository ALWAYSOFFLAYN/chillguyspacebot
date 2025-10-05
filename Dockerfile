FROM python:3.11-slim
WORKDIR /app
# Avoid hash-enforcement + speed up installs
ENV PIP_REQUIRE_HASHES=0
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel \
 && pip install -r requirements.txt

COPY app/ app/
COPY .env.example .env

# Prebuild placeholder index (safe no-op for now)
RUN python app/rag/build_index.py || true

CMD ["python", "-m", "app.main"]
