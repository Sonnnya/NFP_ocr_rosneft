# Expense Report Processor

Automated extraction and validation of business-trip expense report packages.
Accepts a ZIP of scanned documents, runs OCR + LLM extraction, returns structured JSON.

## Setup

Copy the example env file and fill in your values:
```bash
cp .env.example .env
```

## Running

### Dev
Mounts `./app` into the container — code changes reload instantly, no rebuild needed.

```bash
docker compose up
```

### Prod
No volume mounts. Rebuild the image after code changes.

```bash
docker compose -f docker-compose.prod.yml up -d
```

Rebuild after code changes:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

---

API docs available at **http://localhost:8000/docs** once the container is running.

> **Note:** on first start Surya will download model weights (~1–2 GB).
> They are stored in a named Docker volume and reused on subsequent starts.

## Useful commands

```bash
# view live logs
docker compose logs -f

# stop
docker compose down

# wipe model cache (forces re-download)
docker volume rm $(docker volume ls -q | grep surya_models)
```