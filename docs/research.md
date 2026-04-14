# KiniVideo Research Notes

## Objective

Identify what already exists, where it falls short for the KiniVideo use case, and which technologies are the strongest building blocks for an open-source replay-to-clips system.

## Open-Source Reference Projects

### ClipsAI

Repo: <https://github.com/ClipsAI/clipsai>

What it contributes:

- transcript-driven clipping concepts
- vertical reframing ideas
- code-first pipeline orientation

Why it is not enough alone:

- more library-centric than creator-product-centric
- does not directly solve remote TikTok replay ingestion
- does not define an approval-first creator workflow

Conclusion:

Use ClipsAI as a reference for transcript segmentation, clip boundary thinking, and reframing direction, not as the full product foundation.

### FunClip

Repo: <https://github.com/modelscope/FunClip>

What it contributes:

- strong speech/timestamp workflow ideas
- creator-friendly clipping interactions
- speech-aware editing concepts

Why it is not enough alone:

- biased toward local-file workflows
- not opinionated enough about remote ingestion and job orchestration
- not a full creator operations product

Conclusion:

Borrow timestamp UX and speech-aware editing concepts, but do not inherit its local-first assumptions.

### ai-highlight-clip

Repo: <https://github.com/toki-plus/ai-highlight-clip>

What it contributes:

- closest reference to an LLM-scored highlight pipeline
- useful pattern for scoring candidate segments and suggesting titles
- directly relevant to the "find interesting moments" problem

Why it is not enough alone:

- insufficient focus on remote replay ingestion
- limited overall system design for storage, queues, and review workflow
- not designed as the source-of-truth product architecture for a web app

Conclusion:

Use it as the clearest reference for recipe-driven highlight ranking and clip rationale generation.

## Core Tooling Choices

### Remote Ingestion

- `yt-dlp` is the pragmatic path for replay fetching on a server.
- TikTok official developer docs do not appear to expose a replay-retrieval API suitable for this workflow.

Implication:

KiniVideo should treat replay fetching as a remote ingestion concern owned by a source adapter, not a client-device concern.

### Media Processing

- `ffmpeg` remains the standard choice for audio extraction, mezzanine preparation, cutting, and caption burn-in.

Implication:

All clip export and preprocessing stages should standardize around `ffmpeg` command assembly, not custom video logic.

### Speech-to-Text

- `faster-whisper` is a strong default for full-replay transcription.
- `WhisperX` patterns are useful when higher timestamp precision is needed.
- `pyannote.audio` is the obvious reference for speaker diarization.

Implication:

KiniVideo should split the pipeline into a broad first-pass transcript and an optional precision pass for higher-value candidate sections.

### LLM Layer

- Local instruct models through Ollama or vLLM fit the open-source-first requirement.
- External model APIs should remain adapters, not assumptions.

Implication:

Recipe prompts and clip ranking logic should sit behind a model provider interface.

## Managed Alternative Comparison

### RunPod or GPU VPS

Strengths:

- good fit for persistent `ffmpeg` + Whisper-style jobs
- cheap enough for solo creator use
- aligns with self-hosted, open-source operations

Weaknesses:

- more operational setup than pure serverless

Conclusion:

Primary remote deployment target for v1.

### Modal

Strengths:

- strong managed Python and GPU ergonomics
- good future path for cleaner operations

Weaknesses:

- less self-hosted
- not the simplest first deployment for this project goal

Conclusion:

Reasonable future option, not the v1 default.

### Google Colab

Strengths:

- inexpensive experimentation
- useful for prototyping model and pipeline behavior

Weaknesses:

- weak product architecture
- poor fit for a durable always-on web workflow

Conclusion:

Treat as a backup experimentation path only.

## What KiniVideo Adds

Compared with the existing open-source references, KiniVideo combines:

- remote TikTok replay ingestion
- approval-first creator workflow
- configurable clip recipes as a product feature
- persistent asset handling
- deployment-oriented backend and UI architecture

That combination is the actual product gap.
