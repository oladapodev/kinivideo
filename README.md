# KiniVideo

KiniVideo is an open-source, replay-first clipping workflow for TikTok LIVE creators who want better AI-assisted highlights without downloading large source videos to their own device.

The product source of truth lives in [docs/prd.md](/home/oladapo/Desktop/kinivideo/docs/prd.md). Supporting design and research documents live in:

- [docs/research.md](/home/oladapo/Desktop/kinivideo/docs/research.md)
- [docs/technical-design.md](/home/oladapo/Desktop/kinivideo/docs/technical-design.md)

## Repo Layout

- root Python files: FastAPI backend, domain models, pipeline stubs, and services
- `web`: React frontend scaffold
- `docs`: PRD, research, and technical design docs

## Local Development

Use `make` for day-to-day commands:

```bash
make install
make dev
make test
make build
```

Main targets:

- `make dev`: run backend and frontend together with colored `[api]` and `[web]` log prefixes
- `make dev-backend`: run only FastAPI with reload
- `make dev-frontend`: run only Vite
- `make test`: run backend tests
- `make build`: compile backend modules and build the frontend
- `make clean`: remove generated runtime and build artifacts

## Current Status

This first implementation establishes:

- the PRD and technical source documents
- a runnable backend with the planned API surface
- a lightweight frontend covering ingest, processing status, transcript review, and clip review/export

The heavy media pipeline is scaffolded with adapter and service interfaces so real `yt-dlp`, `ffmpeg`, `faster-whisper`, diarization, and export workers can replace the demo implementations incrementally.
