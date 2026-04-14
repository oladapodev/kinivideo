# KiniVideo Technical Design

## Goal

Define the initial architecture for a replay-first clipping system that is runnable locally, deployable to a single remote GPU box, and extensible enough to replace the scaffolded demo pipeline with production media workers over time.

## Architecture Summary

- root Python modules: FastAPI application, domain models, orchestration services, source and storage adapters
- `web`: React UI for ingest, processing state, transcript review, and clip approval/export
- `docs`: product and system source documents

The first code implementation uses an in-memory metadata store plus local filesystem assets for development. Production-oriented interfaces are already separated so PostgreSQL, Redis workers, S3 object storage, and real AI/media executors can be swapped in without changing API contracts.

## Key Interfaces

### SourceAdapter

`ingest(source_ref) -> AssetRef`

Responsibilities:

- validate and normalize the incoming source reference
- fetch or register source media
- return a durable asset reference for downstream stages

Initial adapters:

- `TikTokReplayAdapter`
- `LocalUploadAdapter`

### ClipRecipe

Configuration object defining:

- recipe id and display name
- description
- target clip durations
- ranking weights
- content cues
- caption preset
- output aspect ratio
- model prompt framing

### Pipeline Records

- `TranscriptSegment`
- `WordTimestamp`
- `SpeakerTurn`
- `ClipCandidate`
- `ExportPackage`

These records form the public data model between pipeline stages and the UI.

## API Surface

- `POST /jobs`
- `GET /jobs/{id}`
- `GET /jobs/{id}/transcript`
- `POST /jobs/{id}/recipes/run`
- `GET /jobs/{id}/clips`
- `POST /clips/{id}/approve`
- `POST /clips/{id}/export`
- `GET /recipes`
- `GET /health`

## Pipeline Stages

1. Ingest source
2. Persist source asset reference
3. Preprocess media
4. Create transcript
5. Generate candidate clips by recipe
6. Review and approval
7. Export approved clips with captions and metadata

## Local Development Strategy

- Python backend via `uv`
- React frontend via `bun`
- Local filesystem for assets
- In-memory repository for metadata

This keeps the repo runnable while preserving production interfaces.

## Production Evolution Path

- replace in-memory metadata with PostgreSQL
- introduce Redis-backed worker queue
- switch storage backend to S3-compatible object storage
- wire source adapter to actual `yt-dlp` fetch execution
- replace transcript and clip generation stubs with `faster-whisper`, precision alignment, diarization, and LLM analysis

## Design Constraints

- keep API payloads stable while internals evolve
- treat recipe configuration as product data, not hard-coded branching
- avoid coupling the frontend to specific model providers
- preserve explainability for each clip suggestion
